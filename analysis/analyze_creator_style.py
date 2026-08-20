#!/usr/bin/env python3
"""Measure lightweight Turkish language, hook, and narrative style signals."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

WORD_RE = re.compile(r"[a-zçğıöşü0-9]+(?:['’][a-zçğıöşü0-9]+)?", re.IGNORECASE)
SENTENCE_RE = re.compile(r"[.!?]+")
VOWELS = set("aeıioöuü")
STOPWORDS = {
    "acaba", "ama", "ancak", "artık", "ben", "bir", "biz", "bu", "böyle",
    "çok", "da", "daha", "de", "diye", "en", "gibi", "hem", "her", "için",
    "ile", "ise", "ki", "mi", "mı", "mu", "mü", "ne", "neden", "o", "olan",
    "olarak", "onun", "sonra", "şey", "ve", "veya", "ya", "yani",
}
MARKERS = {
    "curiosity": ("merak", "neden", "nasıl", "acaba", "ne olur", "düşünün"),
    "uncertainty": ("belki", "sanırım", "galiba", "bilmiyorum", "emin değil", "muhtemelen"),
    "analogy": ("gibi", "sanki", "tıpkı", "benzet", "adeta"),
    "emphasis": ("aslında", "işte", "özellikle", "tam olarak", "inanılmaz", "gerçekten"),
    "story": ("bir gün", "yıllar önce", "hikaye", "başladı", "sonra", "o sırada"),
    "direct_address": ("siz", "sizin", "size", "sen", "senin", "sana", "düşünün", "bakın"),
    "first_person": ("ben", "benim", "bana", "bence", "biz", "bizim", "bize", "düşünüyorum"),
    "call_to_action": ("abone", "yorum", "beğen", "paylaş", "bildirim"),
}
PROFANITY = {"aptal", "bok", "lan", "salak", "saçma", "siktir", "ulan"}


def tokens(text: str) -> list[str]:
    return [token.casefold() for token in WORD_RE.findall(text)]


def syllable_count(words: list[str]) -> int:
    return sum(max(1, sum(char in VOWELS for char in word)) for word in words)


def sentence_count(text: str) -> int:
    return max(1, len([part for part in SENTENCE_RE.split(text) if part.strip()]))


def msttr(words: list[str], window: int = 500) -> float | None:
    if not words:
        return None
    windows = [words[start : start + window] for start in range(0, len(words), window)]
    values = [len(set(part)) / len(part) for part in windows if part]
    return sum(values) / len(values)


def marker_rate(text: str, terms: tuple[str, ...], total_words: int) -> float:
    lowered = text.casefold()
    hits = sum(lowered.count(term) for term in terms)
    return round(hits * 1000 / total_words, 6) if total_words else 0.0


def hook_type(intro: str) -> str:
    lowered = intro.casefold()
    if "?" in intro or any(term in lowered for term in ("neden", "nasıl", "acaba", "ne olur")):
        return "question"
    if any(term in lowered for term in ("inanılmaz", "dünyanın", "ilk kez", "hiçbir", "asla")) or re.search(r"\d", intro):
        return "surprising_claim"
    if any(term in lowered for term in MARKERS["story"]):
        return "story"
    if any(term in lowered for term in MARKERS["direct_address"]):
        return "direct_address"
    return "statement"


def readability_label(score: float) -> str:
    if score >= 90:
        return "çok_kolay"
    if score >= 70:
        return "kolay"
    if score >= 50:
        return "orta"
    if score >= 30:
        return "zor"
    return "çok_zor"


def median_or_none(values: list[float]) -> float | None:
    return round(median(values), 6) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    root = args.root.resolve()
    report_dir = root / "reports"

    performance = {}
    with (report_dir / "video-performance.csv").open(encoding="utf-8", newline="") as handle:
        performance = {row["id"]: row for row in csv.DictReader(handle)}

    with sqlite3.connect(root / "analysis.sqlite3") as connection:
        connection.row_factory = sqlite3.Row
        transcripts = connection.execute(
            """
            SELECT v.id, v.title, v.upload_date, v.duration_seconds, t.source,
                   t.normalized_text, t.word_count
            FROM videos AS v JOIN transcripts AS t ON t.video_id = v.id
            WHERE t.normalized_text IS NOT NULL
            ORDER BY v.upload_date, v.id
            """
        ).fetchall()
        cue_rows = connection.execute(
            """
            SELECT v.id, c.start_seconds, c.end_seconds, c.text
            FROM videos AS v
            JOIN transcripts AS t ON t.video_id = v.id
            JOIN transcript_cues AS c ON c.transcript_id = t.id
            ORDER BY v.id, c.cue_index
            """
        ).fetchall()

    cues_by_video = defaultdict(list)
    for cue in cue_rows:
        cues_by_video[cue["id"]].append(cue)

    rows = []
    word_frequency = Counter()
    phrase_documents = Counter()
    for transcript in transcripts:
        video_id = transcript["id"]
        text = transcript["normalized_text"]
        word_list = tokens(text)
        total_words = len(word_list)
        sentences = sentence_count(text)
        syllables = syllable_count(word_list)
        readability = 198.825 - 40.175 * (syllables / max(total_words, 1)) - 2.610 * (total_words / sentences)
        readability = round(max(0.0, min(100.0, readability)), 4)
        cues = cues_by_video[video_id]
        duration = transcript["duration_seconds"] or (cues[-1]["end_seconds"] if cues else 0)
        intro = " ".join(cue["text"] for cue in cues if cue["start_seconds"] < 90)
        outro_start = max(0, duration - 90)
        outro = " ".join(cue["text"] for cue in cues if cue["end_seconds"] >= outro_start)
        intro_words = tokens(intro)
        outro_words = tokens(outro)
        marker_rates = {
            f"{name}_per_1k": marker_rate(text, terms, total_words)
            for name, terms in MARKERS.items()
        }
        profanity_hits = sum(word in PROFANITY for word in word_list)
        perf = performance.get(video_id, {})
        rows.append(
            {
                "id": video_id,
                "title": transcript["title"],
                "upload_date": transcript["upload_date"],
                "caption_source": transcript["source"],
                "duration_seconds": duration,
                "word_count": total_words,
                "sentence_count": sentences,
                "words_per_sentence": round(total_words / sentences, 6),
                "syllables_per_word": round(syllables / max(total_words, 1), 6),
                "atesman_readability": readability,
                "readability_label": readability_label(readability),
                "msttr_500": round(msttr(word_list) or 0, 6),
                "question_marks_per_1k": round(text.count("?") * 1000 / max(total_words, 1), 6),
                "exclamation_marks_per_1k": round(text.count("!") * 1000 / max(total_words, 1), 6),
                "profanity_per_1k": round(profanity_hits * 1000 / max(total_words, 1), 6),
                "intro_word_count": len(intro_words),
                "intro_question_marks": intro.count("?"),
                "intro_hook_type": hook_type(intro),
                "intro_curiosity_per_1k": marker_rate(intro, MARKERS["curiosity"], len(intro_words)),
                "outro_word_count": len(outro_words),
                "outro_cta_per_1k": marker_rate(outro, MARKERS["call_to_action"], len(outro_words)),
                "view_count": perf.get("view_count"),
                "log_views_per_day": perf.get("log_views_per_day"),
                **marker_rates,
            }
        )
        word_frequency.update(word for word in word_list if len(word) >= 3 and word not in STOPWORDS)
        meaningful = [word for word in word_list if len(word) >= 3]
        document_phrases = set()
        for size in (2, 3):
            for index in range(len(meaningful) - size + 1):
                phrase_words = meaningful[index : index + size]
                if not all(word in STOPWORDS for word in phrase_words):
                    document_phrases.add(" ".join(phrase_words))
        phrase_documents.update(document_phrases)

    with (report_dir / "creator-style-videos.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    numeric_fields = [
        "words_per_sentence", "syllables_per_word", "atesman_readability", "msttr_500",
        "question_marks_per_1k", "exclamation_marks_per_1k", "profanity_per_1k",
        "curiosity_per_1k", "uncertainty_per_1k", "analogy_per_1k", "emphasis_per_1k",
        "story_per_1k", "direct_address_per_1k", "first_person_per_1k",
        "call_to_action_per_1k", "intro_curiosity_per_1k", "outro_cta_per_1k",
    ]
    medians = {
        field: median_or_none([float(row[field]) for row in rows if row[field] not in (None, "")])
        for field in numeric_fields
    }
    hook_groups = defaultdict(list)
    for row in rows:
        if row["log_views_per_day"] not in (None, ""):
            hook_groups[row["intro_hook_type"]].append(float(row["log_views_per_day"]))
    recurring_phrases = [
        {"phrase": phrase, "videos": count}
        for phrase, count in phrase_documents.most_common(100)
        if count >= 10
    ][:50]
    medians_by_caption_source = {
        source: {
            field: median_or_none(
                [float(row[field]) for row in rows if row["caption_source"] == source and row[field] not in (None, "")]
            )
            for field in numeric_fields
        }
        for source in sorted({row["caption_source"] for row in rows})
    }
    summary = {
        "videos_analyzed": len(rows),
        "caption_sources": dict(Counter(row["caption_source"] for row in rows)),
        "medians": medians,
        "medians_by_caption_source": medians_by_caption_source,
        "readability_labels": dict(Counter(row["readability_label"] for row in rows)),
        "intro_hook_types": {
            hook: {
                "videos": sum(row["intro_hook_type"] == hook for row in rows),
                "performance_videos": len(values),
                "median_log_views_per_day": median_or_none(values),
            }
            for hook, values in sorted(hook_groups.items())
        },
        "top_content_words": [
            {"word": word, "count": count} for word, count in word_frequency.most_common(100)
        ],
        "recurring_phrases_by_video_coverage": recurring_phrases,
        "warnings": [
            "Ateşman and sentence metrics depend on subtitle punctuation quality.",
            "Automatic captions may suppress punctuation and distort sentence or hook measurements.",
            "Style-performance associations are observational and must not be interpreted as causal.",
        ],
    }
    (report_dir / "creator-style-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
