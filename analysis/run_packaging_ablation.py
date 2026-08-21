#!/usr/bin/env python3
"""Evaluate whether packaging signals predict age-normalized performance."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def score(y_true: np.ndarray, prediction: np.ndarray) -> dict:
    spearman = None
    if len(np.unique(y_true)) > 1 and len(np.unique(prediction)) > 1:
        spearman = round(float(pd.Series(y_true).corr(pd.Series(prediction), method="spearman")), 6)
    return {
        "videos": int(len(y_true)),
        "mae": round(float(mean_absolute_error(y_true, prediction)), 6),
        "rmse": round(float(math.sqrt(mean_squared_error(y_true, prediction))), 6),
        "r2": round(float(r2_score(y_true, prediction)), 6),
        "spearman": spearman,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    parser.add_argument("--as-of", type=str, default="2026-08-20")
    args = parser.parse_args()
    report_dir = args.root.resolve() / "reports"
    rows = read_csv(report_dir / "video-performance.csv")
    thumbnails = {row["id"]: row for row in read_csv(report_dir / "thumbnail-features.csv")}

    records = []
    for row in rows:
        if not row["log_views_per_day"] or not row["upload_date"]:
            continue
        thumb = thumbnails.get(row["id"], {})
        records.append(
            {
                "target": float(row["log_views_per_day"]),
                "year": int(row["upload_date"][:4]),
                "duration_seconds": float(row["duration_seconds"]),
                "title_chars": float(len(row["title"])),
                "title_words": float(len(row["title"].split())),
                "topic": row["topic"],
                "emotion": row["emotion"],
                "semantic_topic_share": float(row["semantic_topic_share"]),
                "brightness_mean": float(thumb.get("brightness_mean", 0) or 0),
                "brightness_std": float(thumb.get("brightness_std", 0) or 0),
                "saturation_mean": float(thumb.get("saturation_mean", 0) or 0),
                "edge_density": float(thumb.get("edge_density", 0) or 0),
                "aspect_ratio": float(thumb.get("aspect_ratio", 0) or 0),
            }
        )

    train = [row for row in records if row["year"] <= 2023]
    validation = [row for row in records if row["year"] == 2024]
    test = [row for row in records if row["year"] >= 2025]
    feature_groups = {
        "baseline_packaging": ["duration_seconds", "title_chars", "title_words", "year"],
        "baseline_plus_content": ["duration_seconds", "title_chars", "title_words", "year", "topic", "emotion", "semantic_topic_share"],
        "baseline_plus_content_plus_thumbnail": [
            "duration_seconds", "title_chars", "title_words", "year", "topic", "emotion", "semantic_topic_share",
            "brightness_mean", "brightness_std", "saturation_mean", "edge_density", "aspect_ratio",
        ],
    }
    all_results = {"global_median": {}}
    y_train = np.array([row["target"] for row in train])
    for split_name, split_rows in (("validation_2024", validation), ("test_2025_plus", test)):
        y_split = np.array([row["target"] for row in split_rows])
        all_results["global_median"][split_name] = score(y_split, np.full(len(y_split), np.median(y_train)))

    for model_name, features in feature_groups.items():
        categorical = [feature for feature in features if feature in {"topic", "emotion"}]
        numeric = [feature for feature in features if feature not in categorical]
        preprocess = ColumnTransformer(
            [
                ("numeric", SimpleImputer(strategy="median"), numeric),
                ("categorical", Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ]), categorical),
            ],
            remainder="drop",
        )
        model = Pipeline([
            ("preprocess", preprocess),
            ("regressor", RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1)),
        ])
        x_train = pd.DataFrame([{feature: row[feature] for feature in features} for row in train])
        model.fit(x_train, y_train)
        all_results[model_name] = {}
        for split_name, split_rows in (("validation_2024", validation), ("test_2025_plus", test)):
            x_split = pd.DataFrame([{feature: row[feature] for feature in features} for row in split_rows])
            y_split = np.array([row["target"] for row in split_rows])
            all_results[model_name][split_name] = score(y_split, model.predict(x_split))

    report = {
        "as_of": args.as_of,
        "target": "log_views_per_day",
        "split": {"train": "<=2023", "validation": "2024", "test": ">=2025"},
        "counts": {"train": len(train), "validation": len(validation), "test": len(test)},
        "results": all_results,
        "interpretation": "Predictive ablation only; feature gains do not establish causal thumbnail or topic effects.",
    }
    (report_dir / "packaging-ablation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
