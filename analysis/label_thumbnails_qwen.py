#!/usr/bin/env python3
"""Select a stratified thumbnail sample and label it with local Qwen2.5-VL."""

from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path
from PIL import Image

MODEL_PROMPT = """Analyze this YouTube thumbnail. Return exactly one JSON object, without markdown.
Visible facts and interpretation must remain separate. Use null or \"unknown\" when unclear.
Schema:
{
  "visible_text_verbatim": "string",
  "main_subject": "person|object|landscape|space|screen|illustration|mixed|unknown",
  "face_count": 0,
  "dominant_object_or_scene": "short factual description",
  "foreground_background_layout": "single_subject|split|collage|text_led|scene|unknown",
  "text_position": "none|left|center|right|top|bottom|multiple|unknown",
  "contrast_level": "low|medium|high|unknown",
  "color_palette": "warm|cool|neutral|mixed|unknown",
  "emotional_impression": "curiosity|wonder|urgency|fear|joy|serious|calm|neutral|unknown",
  "thumbnail_hook_type": "question|claim|number|mystery|transformation|event|person|object|scene|unknown",
  "visible_facts": ["short fact"],
  "interpretation": "short cautious interpretation"
}
Do not infer click-through rate, popularity, or viewer intent. face_count must be an integer."""
FALLBACK_PROMPT = """Return exactly one single-line JSON object. No explanations.
Use only these keys: visible_text_verbatim, main_subject, face_count,
dominant_object_or_scene, foreground_background_layout, text_position,
contrast_level, color_palette, emotional_impression, thumbnail_hook_type,
interpretation. Set visible_text_verbatim, dominant_object_or_scene, and
interpretation to \"unknown\". Use one short enum word for every other string."""
MINIMAL_PROMPT = """Return only one JSON object with main_subject and face_count.
main_subject must be person, object, landscape, space, screen, illustration,
mixed, or unknown. face_count must be an integer. No other text."""


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def year_band(upload_date: str) -> str:
    year = int(upload_date[:4])
    if year <= 2018:
        return "2010-2018"
    if year <= 2022:
        return "2019-2022"
    return "2023-2026"


def select_sample(rows: list[dict], per_group: int = 40) -> list[dict]:
    by_band: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("log_views_per_day") and row.get("upload_date"):
            by_band[year_band(row["upload_date"])].append(row)
    selected = []
    bands = sorted(by_band)
    allocation = {band: per_group // len(bands) for band in bands}
    for band in bands[: per_group % len(bands)]:
        allocation[band] += 1
    for band, band_rows in by_band.items():
        ordered = sorted(band_rows, key=lambda row: float(row["log_views_per_day"]))
        count = allocation[band]
        groups = {
            "low": ordered[:count],
            "middle": ordered[max(0, len(ordered) // 2 - count // 2) : max(0, len(ordered) // 2 - count // 2) + count],
            "high": ordered[-count:],
        }
        for performance_group, group_rows in groups.items():
            for row in group_rows:
                selected.append({**row, "year_band": band, "performance_group": performance_group})
    return selected


def parse_json_response(value: str) -> dict:
    value = value.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", value, re.DOTALL)
    if fenced:
        value = fenced.group(1)
    else:
        start, end = value.find("{"), value.rfind("}")
        if start >= 0 and end > start:
            value = value[start : end + 1]
    return json.loads(value)


def label_image(path: Path, model: str, prompt: str = MODEL_PROMPT) -> dict:
    image = Image.open(path).convert("RGB")
    image.thumbnail((768, 768))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=88)
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "images": [base64.b64encode(buffer.getvalue()).decode("ascii")],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0, "seed": 42, "num_predict": 700},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read())
    return parse_json_response(result["response"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    parser.add_argument("--model", default="qwen2.5vl:7b")
    args = parser.parse_args()
    root = args.root.resolve()
    report_dir = root / "reports"
    sample_path = report_dir / "thumbnail-vision-sample.csv"
    output_path = report_dir / "thumbnail-vision-labels.jsonl"

    sample = select_sample(read_rows(report_dir / "video-performance.csv"))
    sample_fields = ["id", "title", "upload_date", "year_band", "performance_group", "log_views_per_day"]
    with sample_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sample_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sample)

    completed = {}
    if output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing = json.loads(line)
                if "error" not in existing:
                    completed[existing["id"]] = existing
    for index, row in enumerate(sample, 1):
        if row["id"] in completed:
            continue
        try:
            labels = label_image(root / "thumbnails" / f"{row['id']}.webp", args.model)
            result = {
                "id": row["id"],
                "title": row["title"],
                "upload_date": row["upload_date"],
                "year_band": row["year_band"],
                "performance_group": row["performance_group"],
                "log_views_per_day": float(row["log_views_per_day"]),
                "model": args.model,
                **labels,
            }
        except Exception as primary_error:
            try:
                labels = label_image(
                    root / "thumbnails" / f"{row['id']}.webp",
                    args.model,
                    FALLBACK_PROMPT,
                )
                result = {
                    "id": row["id"],
                    "title": row["title"],
                    "upload_date": row["upload_date"],
                    "year_band": row["year_band"],
                    "performance_group": row["performance_group"],
                    "log_views_per_day": float(row["log_views_per_day"]),
                    "model": args.model,
                    "fallback_prompt": True,
                    **labels,
                }
            except Exception as fallback_error:
                try:
                    labels = label_image(
                        root / "thumbnails" / f"{row['id']}.webp",
                        args.model,
                        MINIMAL_PROMPT,
                    )
                    result = {
                        "id": row["id"],
                        "title": row["title"],
                        "upload_date": row["upload_date"],
                        "year_band": row["year_band"],
                        "performance_group": row["performance_group"],
                        "log_views_per_day": float(row["log_views_per_day"]),
                        "model": args.model,
                        "minimal_prompt": True,
                        **labels,
                    }
                except Exception as minimal_error:
                    result = {
                        "id": row["id"],
                        "error": (
                            f"primary: {primary_error}; fallback: {fallback_error}; "
                            f"minimal: {minimal_error}"
                        ),
                        "model": args.model,
                    }
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(f"{index}/{len(sample)} {row['id']}", flush=True)

    latest = {}
    for line in output_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            label = json.loads(line)
            latest[label["id"]] = label
    sample_ids = {item["id"] for item in sample}
    summary = {
        "model": args.model,
        "sample_rows": len(sample),
        "labeled": sum("error" not in row for video_id, row in latest.items() if video_id in sample_ids),
        "errors": sum("error" in row for video_id, row in latest.items() if video_id in sample_ids),
        "sample": "thumbnail-vision-sample.csv",
        "labels": "thumbnail-vision-labels.jsonl",
    }
    (report_dir / "thumbnail-vision-labeling-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
