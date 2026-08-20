#!/usr/bin/env python3
"""Join Qwen thumbnail labels with normalized performance and summarize patterns."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

CATEGORICAL_FIELDS = (
    "main_subject",
    "foreground_background_layout",
    "text_position",
    "contrast_level",
    "color_palette",
    "emotional_impression",
    "thumbnail_hook_type",
)
ALLOWED_VALUES = {
    "main_subject": {"person", "object", "landscape", "space", "screen", "illustration", "mixed", "unknown"},
    "foreground_background_layout": {"single_subject", "split", "collage", "text_led", "scene", "unknown"},
    "text_position": {"none", "left", "center", "right", "top", "bottom", "multiple", "unknown"},
    "contrast_level": {"low", "medium", "high", "unknown"},
    "color_palette": {"warm", "cool", "neutral", "mixed", "unknown"},
    "emotional_impression": {"curiosity", "wonder", "urgency", "fear", "joy", "serious", "calm", "neutral", "unknown"},
    "thumbnail_hook_type": {"question", "claim", "number", "mystery", "transformation", "event", "person", "object", "scene", "unknown"},
}


def normalized_value(field: str, value: object) -> str:
    value = str(value or "unknown")
    if field == "text_position" and "|" in value:
        return "multiple"
    return value if value in ALLOWED_VALUES[field] else "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    report_dir = args.root.resolve() / "reports"
    labels_path = report_dir / "thumbnail-vision-labels.jsonl"
    latest = {}
    for line in labels_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            latest[row["id"]] = row
    labels = [row for row in latest.values() if "error" not in row]

    output_fields = (
        "id", "title", "upload_date", "year_band", "performance_group",
        "log_views_per_day", "visible_text_verbatim", "main_subject", "face_count",
        "dominant_object_or_scene", "foreground_background_layout", "text_position",
        "contrast_level", "color_palette", "emotional_impression", "thumbnail_hook_type",
        "interpretation",
    )
    with (report_dir / "thumbnail-vision-performance.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(labels)

    field_summaries = {}
    schema_adjustments = Counter()
    for field in CATEGORICAL_FIELDS:
        by_value = defaultdict(list)
        group_counts = defaultdict(Counter)
        for row in labels:
            original = str(row.get(field) or "unknown")
            value = normalized_value(field, original)
            if value != original:
                schema_adjustments[f"{field}:{original}->{value}"] += 1
            by_value[value].append(float(row["log_views_per_day"]))
            group_counts[value][row["performance_group"]] += 1
        field_summaries[field] = {
            value: {
                "videos": len(values),
                "median_log_views_per_day": round(median(values), 6),
                "performance_groups": dict(group_counts[value]),
            }
            for value, values in sorted(by_value.items())
        }

    face_groups = defaultdict(list)
    for row in labels:
        try:
            count = int(row.get("face_count", 0))
        except (TypeError, ValueError):
            count = 0
        bucket = "0" if count == 0 else "1" if count == 1 else "2+"
        face_groups[bucket].append(float(row["log_views_per_day"]))
    report = {
        "sample_requested": 120,
        "successfully_labeled": len(labels),
        "failed": 120 - len(labels),
        "fields": field_summaries,
        "face_count": {
            bucket: {"videos": len(values), "median_log_views_per_day": round(median(values), 6)}
            for bucket, values in sorted(face_groups.items())
        },
        "schema_adjustments": dict(schema_adjustments),
        "interpretation_rule": "Treat groups with fewer than 10 videos as exploratory only. Labels describe sampled thumbnails and do not establish causal CTR effects.",
    }
    (report_dir / "thumbnail-vision-performance.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
