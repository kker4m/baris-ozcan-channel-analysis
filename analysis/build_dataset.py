#!/usr/bin/env python3
"""Build the local SQLite corpus and baseline reports for a channel dataset."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from statistics import median
from pathlib import Path

CUE_RE = re.compile(
    r"(?P<index>\d+)\s*\n"
    r"(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})\s*\n"
    r"(?P<text>.*?)(?=\n\s*\n|\Z)",
    re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[\wÀ-ÖØ-öø-ÿ]+(?:['’][\wÀ-ÖØ-öø-ÿ]+)?", re.UNICODE)
SOUND_RE = re.compile(r"^\s*[\[\(].*[\]\)]\s*$")
MUSIC_RE = re.compile(r"^[♪♫\s\[\]\(\)]+$")


TURKISH_STOPWORDS = {
    "acaba", "ama", "ben", "bile", "bir", "bu", "çok", "da", "de", "daha",
    "en", "gibi", "için", "ile", "ise", "mi", "mı", "mu", "mü", "nasıl",
    "ne", "neden", "o", "olan", "olarak", "onun", "sanki", "sen", "şey",
    "ve", "veya", "ya", "yani", "yok", "zaten",
}
TOPIC_KEYWORDS = {
    "bilim": ("bilim", "deney", "fizik", "kimya", "biyoloji", "evrim"),
    "uzay": ("uzay", "gezegen", "mars", "ay ", "yıldız", "astronot", "evren", "ufo"),
    "teknoloji": ("teknoloji", "yapay zeka", "yazılım", "internet", "telefon", "bilgisayar"),
    "psikoloji": ("psikoloji", "beyin", "hafıza", "uyku", "alışkanlık", "zihin"),
    "tarih": ("tarih", "savaş", "osmanlı", "antik", "mısır", "roma"),
    "sanat_tasarım": ("sanat", "tasarım", "ressam", "resim", "fotoğraf", "filografi"),
    "sinema": ("film", "sinema", "dizi", "odyssey", "netflix"),
    "kitap": ("kitap", "okuma", "yazar", "roman", "şiir"),
    "günlük_hayat": ("günlük", "hayat", "insanlar", "neden", "nasıl"),
}


def parse_timestamp(value: str) -> float:
    value = value.replace(",", ".")
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def clean_cue_text(value: str) -> str:
    value = html.unescape(TAG_RE.sub("", value))
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    cues = []
    for match in CUE_RE.finditer(text):
        cue_text = " ".join(
            clean_cue_text(line)
            for line in match.group("text").splitlines()
            if clean_cue_text(line)
        )
        if not cue_text:
            continue
        cues.append(
            {
                "cue_index": int(match.group("index")),
                "start_seconds": parse_timestamp(match.group("start")),
                "end_seconds": parse_timestamp(match.group("end")),
                "text": cue_text,
            }
        )
    return cues


def is_speech(cue_text: str) -> bool:
    if MUSIC_RE.fullmatch(cue_text):
        return False
    if SOUND_RE.fullmatch(cue_text):
        return False
    return bool(WORD_RE.search(cue_text))


def normalize_cues(cues: list[dict]) -> str:
    parts = []
    previous = None
    for cue in cues:
        text = cue["text"]
        if not is_speech(text):
            continue
        if text == previous:
            continue
        parts.append(text)
        previous = text
    return " ".join(parts).strip()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            channel_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            upload_date TEXT,
            duration_seconds INTEGER,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            thumbnail_url TEXT,
            description TEXT,
            is_live INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL UNIQUE,
            language TEXT NOT NULL,
            source TEXT NOT NULL CHECK(source IN ('manual', 'automatic', 'missing')),
            raw_srt_path TEXT,
            raw_text TEXT,
            normalized_text TEXT,
            cue_count INTEGER NOT NULL DEFAULT 0,
            word_count INTEGER NOT NULL DEFAULT 0,
            downloaded_at TEXT,
            FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS transcript_cues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript_id INTEGER NOT NULL,
            cue_index INTEGER NOT NULL,
            start_seconds REAL NOT NULL,
            end_seconds REAL NOT NULL,
            text TEXT NOT NULL,
            is_speech INTEGER NOT NULL,
            FOREIGN KEY (transcript_id) REFERENCES transcripts(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_videos_upload_date ON videos(upload_date);
        CREATE INDEX IF NOT EXISTS idx_videos_duration ON videos(duration_seconds);
        CREATE INDEX IF NOT EXISTS idx_transcripts_source ON transcripts(source);
        CREATE INDEX IF NOT EXISTS idx_cues_transcript ON transcript_cues(transcript_id);
        """
    )


def build_dataset(root: Path) -> dict:
    manifest = {row["id"]: row for row in load_jsonl(root / "manifest.jsonl")}
    catalog = load_jsonl(root / "catalog.jsonl")
    metadata_path = root / "metadata-enrichment.jsonl"
    metadata_by_id = (
        {row["id"]: row for row in load_jsonl(metadata_path)}
        if metadata_path.exists()
        else {}
    )
    subtitle_dir = root / "subtitles"
    database_path = root / "analysis.sqlite3"
    now = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(database_path)
    init_db(connection)
    connection.execute("DELETE FROM transcript_cues")
    connection.execute("DELETE FROM transcripts")
    connection.execute("DELETE FROM videos")

    source_counts = Counter()
    year_counts = Counter()
    year_words = Counter()
    duration_buckets = Counter()
    total_cues = 0
    total_words = 0
    with_subtitles = 0

    for video in catalog:
        video_id = video["id"]
        video = {**video, **metadata_by_id.get(video_id, {})}
        row = manifest[video_id]
        source = row["caption_source"]
        subtitle_path = root / row["subtitle_file"] if row["subtitle_file"] else None
        cues = parse_srt(subtitle_path) if subtitle_path else []
        raw_text = " ".join(cue["text"] for cue in cues)
        normalized_text = normalize_cues(cues)
        word_count = len(WORD_RE.findall(normalized_text))
        cue_count = len(cues)
        year = (row.get("upload_date") or "unknown")[:4]
        duration = row.get("duration") or 0

        connection.execute(
            """
            INSERT INTO videos
              (id, channel_id, title, url, upload_date, duration_seconds,
               view_count, like_count, comment_count, thumbnail_url, description,
               created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                row.get("channel_id") or "UCv6jcPwFujuTIwFQ11jt1Yw",
                row["title"],
                row["url"],
                row.get("upload_date"),
                duration,
                video.get("view_count"),
                video.get("like_count"),
                video.get("comment_count"),
                video.get("thumbnail") or video.get("thumbnail_url"),
                video.get("description"),
                now,
            ),
        )
        cursor = connection.execute(
            """
            INSERT INTO transcripts
              (video_id, language, source, raw_srt_path, raw_text,
               normalized_text, cue_count, word_count, downloaded_at)
            VALUES (?, 'tr', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                source,
                str(subtitle_path.relative_to(root)) if subtitle_path else None,
                raw_text or None,
                normalized_text or None,
                cue_count,
                word_count,
                now if subtitle_path else None,
            ),
        )
        transcript_id = cursor.lastrowid
        connection.executemany(
            """
            INSERT INTO transcript_cues
              (transcript_id, cue_index, start_seconds, end_seconds, text, is_speech)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    transcript_id,
                    cue["cue_index"],
                    cue["start_seconds"],
                    cue["end_seconds"],
                    cue["text"],
                    int(is_speech(cue["text"])),
                )
                for cue in cues
            ],
        )

        source_counts[source] += 1
        year_counts[year] += 1
        year_words[year] += word_count
        if subtitle_path:
            with_subtitles += 1
            total_cues += cue_count
            total_words += word_count
        if duration < 300:
            duration_buckets["<5m"] += 1
        elif duration < 600:
            duration_buckets["5-10m"] += 1
        else:
            duration_buckets["10m+"] += 1

    connection.commit()

    report_dir = root / "reports"
    report_dir.mkdir(exist_ok=True)
    baseline = {
        "channel": "Barış Özcan",
        "catalog_videos": len(catalog),
        "videos_with_turkish_subtitles": with_subtitles,
        "caption_source_counts": dict(source_counts),
        "total_duration_hours": round(sum((row.get("duration") or 0) for row in catalog) / 3600, 2),
        "subtitle_duration_hours": round(
            sum((row.get("duration") or 0) for row in catalog if manifest[row["id"]]["subtitle_file"]) / 3600,
            2,
        ),
        "normalized_caption_words": total_words,
        "subtitle_cues": total_cues,
        "duration_buckets": dict(duration_buckets),
        "year_video_counts": dict(sorted(year_counts.items())),
        "year_normalized_word_counts": dict(sorted(year_words.items())),
        "notes": [
            "View, like, comment, thumbnail and description metadata are loaded from metadata-enrichment.jsonl.",
            "comment_count remains nullable when YouTube returns NA.",
            "Raw SRT and normalized transcript are both retained.",
            "Manual captions take precedence over automatic captions when both exist.",
        ],
    }
    (report_dir / "baseline.json").write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (report_dir / "yearly.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["year", "video_count", "normalized_words"])
        for year in sorted(year_counts):
            writer.writerow([year, year_counts[year], year_words[year]])

    title_duration_rows = []
    title_length_buckets = Counter()
    views_by_duration = defaultdict(list)
    views_by_title_length = defaultdict(list)
    for row in catalog:
        title = row["title"]
        metadata = metadata_by_id.get(row["id"], {})
        title_words = len(WORD_RE.findall(title))
        title_chars = len(title)
        duration = manifest[row["id"]].get("duration") or row.get("duration") or 0
        duration_bucket = "<5m" if duration < 300 else ("5-10m" if duration < 600 else "10m+")
        title_length_bucket = "<40c" if title_chars < 40 else ("40-79c" if title_chars < 80 else "80c+")
        title_length_buckets[title_length_bucket] += 1
        view_count = metadata.get("view_count")
        if view_count is not None:
            views_by_duration[duration_bucket].append(view_count)
            views_by_title_length[title_length_bucket].append(view_count)
        title_duration_rows.append(
            {
                "id": row["id"],
                "title": title,
                "upload_date": row.get("upload_date"),
                "duration_seconds": duration,
                "duration_bucket": duration_bucket,
                "title_chars": title_chars,
                "title_words": title_words,
                "view_count": view_count,
                "like_count": metadata.get("like_count"),
                "thumbnail_url": metadata.get("thumbnail") or metadata.get("thumbnail_url"),
                "caption_source": manifest[row["id"]]["caption_source"],
                "has_turkish_subtitles": bool(manifest[row["id"]]["subtitle_file"]),
            }
        )
    performance_summary = {
        "duration_bucket_median_views": {
            bucket: {"videos": len(views), "median_views": median(views)}
            for bucket, views in sorted(views_by_duration.items())
        },
        "title_length_bucket_median_views": {
            bucket: {"videos": len(views), "median_views": median(views)}
            for bucket, views in sorted(views_by_title_length.items())
        },
        "warning": "These are descriptive associations, not causal conclusions; control for upload year and topic before strategy decisions.",
    }
    (report_dir / "title-duration.json").write_text(
        json.dumps(
            {
                "title_length_buckets": dict(title_length_buckets),
                "performance_summary": performance_summary,
                "rows": title_duration_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    with (report_dir / "title-duration.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=title_duration_rows[0].keys())
        writer.writeheader()
        writer.writerows(title_duration_rows)
    topic_rows = []
    topic_counts = Counter()
    word_counts = Counter()
    word_counts_by_source = defaultdict(Counter)
    for row in connection.execute(
        """
        SELECT v.id, v.title, t.source, t.normalized_text
        FROM videos AS v
        JOIN transcripts AS t ON t.video_id = v.id
        """
    ):
        video_id, title, source, normalized_text = row
        title_lower = title.casefold()
        matches = [
            topic
            for topic, keywords in TOPIC_KEYWORDS.items()
            if any(keyword in title_lower for keyword in keywords)
        ]
        primary_topic = matches[0] if matches else "unclassified"
        topic_counts[primary_topic] += 1
        topic_rows.append(
            {
                "id": video_id,
                "title": title,
                "caption_source": source,
                "primary_topic": primary_topic,
                "topic_matches": ",".join(matches),
            }
        )
        for word in WORD_RE.findall(normalized_text or ""):
            word = word.casefold()
            if len(word) >= 3 and word not in TURKISH_STOPWORDS:
                word_counts[word] += 1
                word_counts_by_source[source][word] += 1
    topic_report = {
        "method": "title keyword baseline; not a semantic classifier",
        "topic_counts": dict(topic_counts),
        "top_words": word_counts.most_common(100),
        "top_words_by_caption_source": {
            source: counts.most_common(30)
            for source, counts in word_counts_by_source.items()
        },
        "next_step": "Replace title keyword labels with Turkish multilingual embeddings or LLM classification after metadata enrichment.",
    }
    (report_dir / "topic-language.json").write_text(
        json.dumps(topic_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (report_dir / "topic-assignments.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=topic_rows[0].keys())
        writer.writeheader()
        writer.writerows(topic_rows)


    connection.close()
    return baseline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    result = build_dataset(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
