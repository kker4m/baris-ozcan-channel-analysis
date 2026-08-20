#!/usr/bin/env python3
"""Download channel thumbnails and extract reproducible visual packaging features."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def download_one(item: tuple[str, str, Path]) -> tuple[str, str | None]:
    video_id, url, destination = item
    if destination.exists() and destination.stat().st_size > 0:
        return video_id, None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "channel-analysis/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            destination.write_bytes(response.read())
        return video_id, None
    except Exception as exc:  # network failures are recorded and do not abort the batch
        return video_id, str(exc)


def features_for(path: Path) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    height, width = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return {
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 6) if height else None,
        "mean_red": round(float(image[:, :, 0].mean()), 4),
        "mean_green": round(float(image[:, :, 1].mean()), 4),
        "mean_blue": round(float(image[:, :, 2].mean()), 4),
        "brightness_mean": round(float(hsv[:, :, 2].mean()), 4),
        "brightness_std": round(float(hsv[:, :, 2].std()), 4),
        "saturation_mean": round(float(hsv[:, :, 1].mean()), 4),
        "edge_density": round(float((edges > 0).mean()), 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    root = args.root.resolve()
    report_dir = root / "reports"
    thumbnail_dir = root / "thumbnails"
    thumbnail_dir.mkdir(exist_ok=True)
    with sqlite3.connect(root / "analysis.sqlite3") as connection:
        videos = connection.execute(
            "SELECT id, title, view_count, thumbnail_url FROM videos WHERE thumbnail_url IS NOT NULL"
        ).fetchall()
    jobs = [(video_id, url, thumbnail_dir / f"{video_id}.webp") for video_id, _, _, url in videos]
    failures = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(download_one, job) for job in jobs]
        for future in as_completed(futures):
            video_id, error = future.result()
            if error:
                failures[video_id] = error

    feature_rows = []
    for video_id, title, view_count, _ in videos:
        path = thumbnail_dir / f"{video_id}.webp"
        if not path.exists():
            continue
        try:
            feature_rows.append(
                {
                    "id": video_id,
                    "title": title,
                    "view_count": view_count,
                    **features_for(path),
                }
            )
        except Exception as exc:
            failures[video_id] = f"feature extraction: {exc}"
    feature_rows.sort(key=lambda row: row["view_count"] or 0, reverse=True)
    with (report_dir / "thumbnail-features.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=feature_rows[0].keys())
        writer.writeheader()
        writer.writerows(feature_rows)
    summary = {
        "videos_with_thumbnail_urls": len(videos),
        "downloaded_and_analyzed": len(feature_rows),
        "failures": len(failures),
        "failure_ids": sorted(failures),
        "features": [
            "aspect_ratio", "mean_red", "mean_green", "mean_blue",
            "brightness_mean", "brightness_std", "saturation_mean", "edge_density",
        ],
        "warning": "Color and edge features are packaging proxies; they do not identify objects or text without a vision model.",
    }
    (report_dir / "thumbnail-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (report_dir / "thumbnail-download.json").write_text(
        json.dumps({"failures": failures}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
