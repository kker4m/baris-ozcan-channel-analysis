#!/usr/bin/env python3
"""Measure lightweight associations between creator style signals and performance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

FEATURES = [
    "words_per_sentence", "syllables_per_word", "atesman_readability", "msttr_500",
    "question_marks_per_1k", "exclamation_marks_per_1k", "profanity_per_1k",
    "curiosity_per_1k", "uncertainty_per_1k", "analogy_per_1k", "emphasis_per_1k",
    "story_per_1k", "direct_address_per_1k", "first_person_per_1k",
    "call_to_action_per_1k", "intro_curiosity_per_1k", "outro_cta_per_1k",
]
PUNCTUATION_DEPENDENT_FEATURES = {
    "words_per_sentence",
    "atesman_readability",
    "question_marks_per_1k",
    "exclamation_marks_per_1k",
}


def correlation(left: pd.Series, right: pd.Series, method: str) -> float | None:
    value = left.corr(right, method=method)
    return None if pd.isna(value) else round(float(value), 6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    report_dir = args.root.resolve() / "reports"
    frame = pd.read_csv(report_dir / "creator-style-videos.csv")
    frame = frame.dropna(subset=["log_views_per_day"]).copy()
    frame["year"] = frame["upload_date"].astype(str).str[:4]
    frame["year_centered_target"] = frame["log_views_per_day"] - frame.groupby("year")["log_views_per_day"].transform("median")

    associations = {}
    for feature in FEATURES:
        feature_frame = frame[frame["caption_source"] == "manual"] if feature in PUNCTUATION_DEPENDENT_FEATURES else frame
        valid = feature_frame[[feature, "log_views_per_day", "year_centered_target"]].dropna()
        associations[feature] = {
            "videos": len(valid),
            "caption_scope": "manual_only" if feature in PUNCTUATION_DEPENDENT_FEATURES else "all",
            "pearson_log_views_per_day": correlation(valid[feature], valid["log_views_per_day"], "pearson"),
            "spearman_log_views_per_day": correlation(valid[feature], valid["log_views_per_day"], "spearman"),
            "pearson_year_centered": correlation(valid[feature], valid["year_centered_target"], "pearson"),
            "spearman_year_centered": correlation(valid[feature], valid["year_centered_target"], "spearman"),
        }

    hook_summary = {}
    for hook, group in frame.groupby("intro_hook_type"):
        hook_summary[str(hook)] = {
            "videos": len(group),
            "median_log_views_per_day": round(float(group["log_views_per_day"].median()), 6),
            "median_year_centered_target": round(float(group["year_centered_target"].median()), 6),
            "years": int(group["year"].nunique()),
        }
    caption_quality = {}
    for source, group in frame.groupby("caption_source"):
        caption_quality[str(source)] = {
            "videos": len(group),
            "median_words_per_sentence": round(float(group["words_per_sentence"].median()), 6),
            "median_question_marks_per_1k": round(float(group["question_marks_per_1k"].median()), 6),
            "median_readability": round(float(group["atesman_readability"].median()), 6),
        }
    ranked = sorted(
        (
            {
                "feature": feature,
                "absolute_year_centered_spearman": round(abs(values["spearman_year_centered"] or 0), 6),
                "direction": "positive" if (values["spearman_year_centered"] or 0) > 0 else "negative",
            }
            for feature, values in associations.items()
        ),
        key=lambda row: row["absolute_year_centered_spearman"],
        reverse=True,
    )
    report = {
        "videos": len(frame),
        "target": "log_views_per_day",
        "year_control": "Target centered by upload-year median before correlation.",
        "associations": associations,
        "ranked_year_centered_signals": ranked,
        "intro_hooks": hook_summary,
        "caption_quality_check": caption_quality,
        "interpretation": [
            "Absolute correlations below 0.10 are negligible and 0.10-0.20 are weak exploratory signals.",
            "Subtitle punctuation quality differs between manual and automatic captions.",
            "No association in this report establishes a causal content rule.",
        ],
    }
    (report_dir / "creator-style-performance.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
