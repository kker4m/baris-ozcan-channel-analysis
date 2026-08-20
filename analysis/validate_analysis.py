#!/usr/bin/env python3
"""Validate report joins against the canonical SQLite corpus."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    root = args.root.resolve()
    report_dir = root / "reports"

    with sqlite3.connect(root / "analysis.sqlite3") as connection:
        canonical = {
            row[0]: row[1:]
            for row in connection.execute(
                "SELECT id, view_count, thumbnail_url FROM videos"
            )
        }
    performance = read_csv(report_dir / "video-performance.csv")
    thumbnails = read_csv(report_dir / "thumbnail-features.csv")
    semantic = read_csv(report_dir / "semantic-chunks.csv")
    topic_assignments = read_csv(report_dir / "topic-assignments.csv")
    vision_sample = read_csv(report_dir / "thumbnail-vision-sample.csv")
    vision_performance = read_csv(report_dir / "thumbnail-vision-performance.csv")
    creator_style = read_csv(report_dir / "creator-style-videos.csv")
    creator_style_summary = json.loads((report_dir / "creator-style-summary.json").read_text(encoding="utf-8"))
    creator_profile = json.loads((report_dir / "creator-chatbot-profile.json").read_text(encoding="utf-8"))
    vision_ablation = json.loads((report_dir / "thumbnail-vision-ablation.json").read_text(encoding="utf-8"))
    analysis_summary = json.loads((report_dir / "analysis-summary.json").read_text(encoding="utf-8"))
    latest_vision = {}
    for line in (report_dir / "thumbnail-vision-labels.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            latest_vision[row["id"]] = row
    vision_successes = [row for row in latest_vision.values() if "error" not in row]
    assert len(canonical) == 849
    assert {row["id"] for row in performance} == set(canonical)
    assert {row["id"] for row in thumbnails} == set(canonical)
    assert {row["id"] for row in topic_assignments} == set(canonical)
    assert set(row["video_id"] for row in semantic) <= set(canonical)
    assert len(vision_sample) == 120
    assert len({row["id"] for row in vision_sample}) == 120
    assert {row["id"] for row in vision_sample} <= set(canonical)
    assert len(vision_successes) >= 114
    assert {row["id"] for row in vision_performance} == {row["id"] for row in vision_successes}
    assert len(creator_style) == 800
    assert len({row["id"] for row in creator_style}) == 800
    assert {row["id"] for row in creator_style} <= set(canonical)
    assert creator_style_summary["videos_analyzed"] == len(creator_style)
    assert creator_profile["corpus"]["transcript_videos"] == len(creator_style)
    assert sum(vision_ablation["counts"].values()) == len(vision_sample)
    assert analysis_summary["status"] == "complete_for_lightweight_video_analysis"
    assert analysis_summary["scope"]["catalog_videos"] == len(canonical)
    for row in performance:
        view_count, thumbnail_url = canonical[row["id"]]
        assert int(row["view_count"]) == view_count
        assert row["thumbnail_url"] == thumbnail_url
    for name in (
        "performance-summary.json",
        "thumbnail-summary.json",
        "thumbnail-performance.json",
        "performance-report.json",
        "channel-distribution.json",
        "creator-style-summary.json",
        "creator-style-performance.json",
        "creator-chatbot-profile.json",
        "thumbnail-vision-ablation.json",
        "analysis-summary.json",
    ):
        assert (report_dir / name).exists(), name
    for name in (
        "topic-title-length-log-views.png",
        "emotion-duration-log-views.png",
    ):
        assert (report_dir / "performance-heatmaps" / name).stat().st_size > 0, name
    result = {
        "canonical_videos": len(canonical),
        "performance_rows": len(performance),
        "thumbnail_rows": len(thumbnails),
        "semantic_rows": len(semantic),
        "topic_rows": len(topic_assignments),
        "vision_sample_rows": len(vision_sample),
        "vision_labeled_rows": len(vision_successes),
        "creator_style_rows": len(creator_style),
        "vision_failed_rows": len(vision_sample) - len(vision_successes),
        "status": "PASS",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
