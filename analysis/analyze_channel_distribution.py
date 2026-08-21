#!/usr/bin/env python3
"""Summarize channel scale, publishing cadence, and view concentration."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import median


def gini(values: list[int]) -> float:
    ordered = sorted(value for value in values if value >= 0)
    if not ordered or sum(ordered) == 0:
        return 0.0
    count = len(ordered)
    weighted = sum((index + 1) * value for index, value in enumerate(ordered))
    return (2 * weighted) / (count * sum(ordered)) - (count + 1) / count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    report_dir = args.root.resolve() / "reports"
    with (report_dir / "video-performance.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows = [row for row in rows if row["view_count"]]
    ranked = sorted(rows, key=lambda row: int(row["view_count"]), reverse=True)
    total_views = sum(int(row["view_count"]) for row in ranked)

    concentration = {}
    for target_share in (0.5, 0.8, 0.9):
        running = 0
        videos = 0
        for row in ranked:
            running += int(row["view_count"])
            videos += 1
            if running >= total_views * target_share:
                break
        concentration[f"videos_for_{int(target_share * 100)}pct_views"] = {
            "videos": videos,
            "catalog_share": round(videos / len(ranked), 6),
        }
    top_shares = {
        f"top_{count}_view_share": round(
            sum(int(row["view_count"]) for row in ranked[:count]) / total_views, 6
        )
        for count in (10, 25, 50, 100)
    }

    dated = sorted(
        datetime.strptime(row["upload_date"], "%Y%m%d")
        for row in rows
        if row["upload_date"] and row["upload_date"].isdigit() and len(row["upload_date"]) == 8
    )
    upload_gaps = [(right - left).days for left, right in zip(dated, dated[1:])]
    years = {}
    for row in rows:
        year = row["upload_date"][:4] if row["upload_date"] else "unknown"
        years.setdefault(year, []).append(row)
    by_year = {
        year: {
            "videos": len(group),
            "median_views": round(median(int(row["view_count"]) for row in group)),
            "median_views_per_day": round(median(float(row["views_per_day"]) for row in group), 4),
        }
        for year, group in sorted(years.items())
    }
    report = {
        "videos": len(ranked),
        "total_views_snapshot": total_views,
        "median_views": round(median(int(row["view_count"]) for row in ranked)),
        "view_gini": round(gini([int(row["view_count"]) for row in ranked]), 6),
        "concentration": {**concentration, **top_shares},
        "publishing_cadence": {
            "median_days_between_uploads": median(upload_gaps) if upload_gaps else None,
            "videos_per_year": {year: values["videos"] for year, values in by_year.items()},
        },
        "by_year": by_year,
        "warning": "View counts are a current snapshot; older videos have had more time to accumulate lifetime views.",
    }
    (report_dir / "channel-distribution.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
