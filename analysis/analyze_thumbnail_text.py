#!/usr/bin/env python3
"""Extract Turkish thumbnail text and relate wording to performance."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median
from concurrent.futures import ThreadPoolExecutor

import pytesseract
from PIL import Image, ImageEnhance, ImageOps

WORD_RE = re.compile(r"[\wÀ-ÖØ-öø-ÿ]+(?:['’][\wÀ-ÖØ-öø-ÿ]+)?", re.UNICODE)


def ocr_thumbnail(path: Path) -> str:
    image = Image.open(path).convert("RGB")
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Sharpness(image).enhance(1.5)
    return pytesseract.image_to_string(image, lang="tur+eng", config="--psm 11").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.root.resolve()
    report_dir = root / "reports"
    thumbnail_dir = root / "thumbnails"
    performance = {}
    with (report_dir / "video-performance.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            performance[row["id"]] = row

    paths = sorted(thumbnail_dir.glob("*.webp"))
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        texts = list(executor.map(ocr_thumbnail, paths))
    rows = []
    for path, text in zip(paths, texts):
        video_id = path.stem
        words = WORD_RE.findall(text.casefold())
        performance_row = performance.get(video_id, {})
        rows.append(
            {
                "id": video_id,
                "ocr_text": re.sub(r"\s+", " ", text),
                "ocr_word_count": len(words),
                "ocr_char_count": len(text),
                "has_digits": int(any(char.isdigit() for char in text)),
                "exclamation_count": text.count("!"),
                "question_count": text.count("?"),
                "view_count": performance_row.get("view_count"),
                "log_views_per_day": performance_row.get("log_views_per_day"),
            }
        )
    with (report_dir / "thumbnail-ocr.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    buckets = defaultdict(list)
    for row in rows:
        if row["log_views_per_day"]:
            bucket = "0" if row["ocr_word_count"] == 0 else "1-3" if row["ocr_word_count"] <= 3 else "4+"
            buckets[bucket].append(float(row["log_views_per_day"]))
    token_stats = defaultdict(list)
    for row in rows:
        if not row["log_views_per_day"]:
            continue
        for token in set(WORD_RE.findall(row["ocr_text"].casefold())):
            if len(token) >= 3:
                token_stats[token].append(float(row["log_views_per_day"]))
    token_summary = [
        {"token": token, "videos": len(values), "median_log_views_per_day": round(median(values), 6)}
        for token, values in token_stats.items()
        if len(values) >= 3
    ]
    token_summary.sort(key=lambda row: (row["median_log_views_per_day"], row["videos"]), reverse=True)
    summary = {
        "thumbnails": len(rows),
        "with_ocr_text": sum(row["ocr_word_count"] > 0 for row in rows),
        "median_log_views_per_day_by_text_count": {
            bucket: {"videos": len(values), "median": round(median(values), 6)}
            for bucket, values in sorted(buckets.items())
        },
        "top_tokens_by_median_performance": token_summary[:50],
        "warning": "OCR is noisy and token groups are observational; manually review candidates before using them as title or thumbnail rules.",
    }
    (report_dir / "thumbnail-ocr-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
