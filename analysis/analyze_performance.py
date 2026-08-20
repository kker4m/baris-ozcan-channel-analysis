#!/usr/bin/env python3
"""Join packaging, metadata, topic, and emotion signals into performance reports."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import median


def median_summary(rows: list[dict], key: str) -> dict:
    values = [row[key] for row in rows if row.get(key) is not None]
    if not values:
        return {"videos": 0, "median": None}
    return {"videos": len(values), "median": round(median(values), 6)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    parser.add_argument("--as-of", type=str, default=date.today().isoformat())
    args = parser.parse_args()

    root = args.root.resolve()
    report_dir = root / "reports"
    as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
    semantic_path = report_dir / "semantic-chunks.csv"
    semantic_by_video: dict[str, dict[str, Counter]] = defaultdict(lambda: {"topic": Counter(), "emotion": Counter()})
    if semantic_path.exists():
        with semantic_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                semantic_by_video[row["video_id"]]["topic"][row["primary_topic"]] += 1
                semantic_by_video[row["video_id"]]["emotion"][row["dominant_emotion"]] += 1

    title_topic_by_video = {}
    title_topic_path = report_dir / "topic-assignments.csv"
    if title_topic_path.exists():
        with title_topic_path.open(encoding="utf-8", newline="") as handle:
            title_topic_by_video = {
                row["id"]: row["primary_topic"] for row in csv.DictReader(handle)
            }

    with sqlite3.connect(root / "analysis.sqlite3") as connection:
        connection.row_factory = sqlite3.Row
        videos = connection.execute(
            """
            SELECT id, title, upload_date, duration_seconds, view_count,
                   like_count, comment_count, thumbnail_url
            FROM videos
            ORDER BY upload_date, id
            """
        ).fetchall()

    rows = []
    for video in videos:
        upload_date = video["upload_date"]
        try:
            published = datetime.strptime(upload_date, "%Y%m%d").date()
            age_days = max((as_of - published).days, 1)
        except (TypeError, ValueError):
            age_days = None
        views = video["view_count"]
        likes = video["like_count"] or 0
        comments = video["comment_count"] or 0
        signals = semantic_by_video[video["id"]]
        semantic_topic = signals["topic"].most_common(1)[0][0] if signals["topic"] else "unclassified"
        topic = title_topic_by_video.get(video["id"], "unclassified")
        emotion = signals["emotion"].most_common(1)[0][0] if signals["emotion"] else "nötr"
        chunk_count = sum(signals["topic"].values())
        rows.append(
            {
                "id": video["id"],
                "title": video["title"],
                "upload_date": upload_date,
                "duration_seconds": video["duration_seconds"] or 0,
                "view_count": views,
                "like_count": video["like_count"],
                "comment_count": video["comment_count"],
                "age_days": age_days,
                "views_per_day": round(views / age_days, 4) if views and age_days else None,
                "log_views": round(math.log1p(views), 6) if views is not None else None,
                "log_views_per_day": round(math.log1p(views / age_days), 6) if views and age_days else None,
                "engagement_rate": round((likes + comments) / views, 8) if views else None,
                "views_per_minute_of_video": round(views / ((video["duration_seconds"] or 0) / 60), 4)
                if views and video["duration_seconds"]
                else None,
                "topic": topic,
                "semantic_topic": semantic_topic,
                "semantic_topic_share": round(signals["topic"][semantic_topic] / chunk_count, 4)
                if chunk_count
                else 0,
                "emotion": emotion,
                "thumbnail_url": video["thumbnail_url"],
            }
        )

    def grouped_summary(field: str) -> dict:
        groups: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            groups[row[field]].append(row)
        return {
            str(group): {
                "videos": len(group_rows),
                "median_views": median_summary(group_rows, "view_count")["median"],
                "median_views_per_day": median_summary(group_rows, "views_per_day")["median"],
                "median_engagement_rate": median_summary(group_rows, "engagement_rate")["median"],
            }
            for group, group_rows in sorted(groups.items())
        }

    for row in rows:
        row["duration_bucket"] = "<5m" if row["duration_seconds"] < 300 else "5-10m" if row["duration_seconds"] < 600 else "10m+"
        title_chars = len(row["title"])
        row["title_length_bucket"] = "<40c" if title_chars < 40 else "40-79c" if title_chars < 80 else "80c+"
    report = {
        "as_of": args.as_of,
        "videos": len(rows),
        "metadata_coverage": {
            "view_count": sum(row["view_count"] is not None for row in rows),
            "like_count": sum(row["like_count"] is not None for row in rows),
            "comment_count": sum(row["comment_count"] is not None for row in rows),
            "thumbnail_url": sum(bool(row["thumbnail_url"]) for row in rows),
        },
        "overall": {
            "median_views": median_summary(rows, "view_count")["median"],
            "median_views_per_day": median_summary(rows, "views_per_day")["median"],
            "median_engagement_rate": median_summary(rows, "engagement_rate")["median"],
        },
        "by_topic": grouped_summary("topic"),
        "by_semantic_topic": grouped_summary("semantic_topic"),
        "by_emotion": grouped_summary("emotion"),
        "by_duration": grouped_summary("duration_bucket"),
        "by_title_length": grouped_summary("title_length_bucket"),
        "warning": "Associational snapshot only; view counts are current channel metadata, not lifetime-normalized ground truth.",
    }
    rows.sort(key=lambda row: row["view_count"] or 0, reverse=True)
    with (report_dir / "video-performance.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    (report_dir / "performance-summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
