#!/usr/bin/env python3
"""Render performance heatmaps from the joined analysis reports."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def draw_heatmap(matrix: np.ndarray, rows: list[str], columns: list[str], title: str, destination: Path) -> None:
    fig, axis = plt.subplots(figsize=(max(7, len(columns) * 1.4), max(5, len(rows) * 0.45)))
    image = axis.imshow(matrix, cmap="viridis", aspect="auto")
    axis.set_xticks(range(len(columns)), columns, rotation=30, ha="right")
    axis.set_yticks(range(len(rows)), rows)
    axis.set_title(title)
    axis.set_xlabel("Packaging / category bucket")
    axis.set_ylabel("Category")
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            value = matrix[row_index, column_index]
            if not np.isnan(value):
                axis.text(column_index, row_index, f"{value:.2f}", ha="center", va="center", fontsize=8, color="white")
    fig.colorbar(image, ax=axis, label="median log(1 + views)")
    fig.tight_layout()
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()

    root = args.root.resolve()
    report_dir = root / "reports"
    output_dir = report_dir / "performance-heatmaps"
    output_dir.mkdir(exist_ok=True)
    rows = read_csv(report_dir / "video-performance.csv")
    for row in rows:
        row["view_count"] = int(row["view_count"]) if row["view_count"] else None
        row["log_views"] = float(row["log_views"]) if row["log_views"] else None

    topics = sorted({row["topic"] for row in rows})
    title_buckets = ["<40c", "40-79c", "80c+"]
    topic_length_values = defaultdict(list)
    for row in rows:
        if row["log_views"] is not None:
            topic_length_values[(row["topic"], row["title_length_bucket"])].append(row["log_views"])
    topic_matrix = np.array(
        [
            [median(topic_length_values[(topic, bucket)]) if topic_length_values[(topic, bucket)] else np.nan for bucket in title_buckets]
            for topic in topics
        ]
    )
    draw_heatmap(
        topic_matrix,
        topics,
        title_buckets,
        "Topic × title length performance",
        output_dir / "topic-title-length-log-views.png",
    )

    emotions = sorted({row["emotion"] for row in rows})
    emotion_duration_values = defaultdict(list)
    duration_buckets = ["<5m", "5-10m", "10m+"]
    for row in rows:
        if row["log_views"] is not None:
            emotion_duration_values[(row["emotion"], row["duration_bucket"])].append(row["log_views"])
    emotion_matrix = np.array(
        [
            [median(emotion_duration_values[(emotion, bucket)]) if emotion_duration_values[(emotion, bucket)] else np.nan for bucket in duration_buckets]
            for emotion in emotions
        ]
    )
    draw_heatmap(
        emotion_matrix,
        emotions,
        duration_buckets,
        "Emotion × duration performance",
        output_dir / "emotion-duration-log-views.png",
    )

    thumbnail_rows = read_csv(report_dir / "thumbnail-features.csv")
    performance_by_id = {row["id"]: row for row in rows}
    feature_names = ["brightness_mean", "saturation_mean", "edge_density", "brightness_std"]
    thumbnail_summary = {}
    for feature in feature_names:
        pairs = [
            (float(row[feature]), performance_by_id[row["id"]]["log_views"])
            for row in thumbnail_rows
            if row["id"] in performance_by_id and performance_by_id[row["id"]]["log_views"] is not None
        ]
        if len(pairs) >= 2:
            x, y = zip(*pairs)
            correlation = float(np.corrcoef(x, y)[0, 1])
            thumbnail_summary[feature] = {"videos": len(pairs), "pearson_log_views": round(correlation, 6)}
    (report_dir / "thumbnail-performance.json").write_text(
        json.dumps(
            {
                "features": thumbnail_summary,
                "warning": "Correlations are exploratory and do not identify causal thumbnail effects.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    summary = {
        "heatmaps": [
            "performance-heatmaps/topic-title-length-log-views.png",
            "performance-heatmaps/emotion-duration-log-views.png",
        ],
        "thumbnail_performance": "thumbnail-performance.json",
        "videos": len(rows),
    }
    (report_dir / "performance-report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
