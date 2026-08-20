#!/usr/bin/env python3
"""Compare visual-semantic thumbnail features on the fixed Qwen sample."""

from __future__ import annotations

import argparse
import csv
import json
import math
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
        "videos": len(y_true),
        "mae": round(float(mean_absolute_error(y_true, prediction)), 6),
        "rmse": round(float(math.sqrt(mean_squared_error(y_true, prediction))), 6),
        "r2": round(float(r2_score(y_true, prediction)), 6),
        "spearman": spearman,
    }


def face_bucket(value: str) -> str:
    try:
        count = int(value)
    except (TypeError, ValueError):
        return "unknown"
    return "2+" if count >= 2 else str(max(0, count))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    report_dir = args.root.resolve() / "reports"
    performance = {row["id"]: row for row in read_csv(report_dir / "video-performance.csv")}
    basic_thumbnails = {row["id"]: row for row in read_csv(report_dir / "thumbnail-features.csv")}
    vision_rows = read_csv(report_dir / "thumbnail-vision-performance.csv")

    records = []
    for vision in vision_rows:
        perf = performance[vision["id"]]
        basic = basic_thumbnails[vision["id"]]
        visible_text = vision.get("visible_text_verbatim", "") or ""
        records.append(
            {
                "target": float(perf["log_views_per_day"]),
                "year": int(perf["upload_date"][:4]),
                "duration_seconds": float(perf["duration_seconds"]),
                "title_chars": len(perf["title"]),
                "title_words": len(perf["title"].split()),
                "topic": perf["topic"],
                "emotion": perf["emotion"],
                "semantic_topic_share": float(perf["semantic_topic_share"]),
                "brightness_mean": float(basic["brightness_mean"]),
                "brightness_std": float(basic["brightness_std"]),
                "saturation_mean": float(basic["saturation_mean"]),
                "edge_density": float(basic["edge_density"]),
                "aspect_ratio": float(basic["aspect_ratio"]),
                "visible_text_chars": len(visible_text),
                "visible_text_words": len(visible_text.split()),
                "main_subject": vision["main_subject"],
                "face_bucket": face_bucket(vision["face_count"]),
                "layout": vision["foreground_background_layout"],
                "text_position": vision["text_position"],
                "contrast_level": vision["contrast_level"],
                "color_palette": vision["color_palette"],
                "emotional_impression": vision["emotional_impression"],
                "thumbnail_hook_type": vision["thumbnail_hook_type"],
            }
        )

    train = [row for row in records if row["year"] <= 2022]
    test = [row for row in records if row["year"] >= 2023]
    feature_groups = {
        "baseline": ["duration_seconds", "title_chars", "title_words", "year"],
        "baseline_plus_content": [
            "duration_seconds", "title_chars", "title_words", "year",
            "topic", "emotion", "semantic_topic_share",
        ],
        "baseline_plus_content_plus_basic_thumbnail": [
            "duration_seconds", "title_chars", "title_words", "year",
            "topic", "emotion", "semantic_topic_share", "brightness_mean",
            "brightness_std", "saturation_mean", "edge_density", "aspect_ratio",
        ],
        "baseline_plus_content_plus_basic_plus_vision": [
            "duration_seconds", "title_chars", "title_words", "year",
            "topic", "emotion", "semantic_topic_share", "brightness_mean",
            "brightness_std", "saturation_mean", "edge_density", "aspect_ratio",
            "visible_text_chars", "visible_text_words", "main_subject", "face_bucket",
            "layout", "text_position", "contrast_level", "color_palette",
            "emotional_impression", "thumbnail_hook_type",
        ],
    }
    categorical_features = {
        "topic", "emotion", "main_subject", "face_bucket", "layout", "text_position",
        "contrast_level", "color_palette", "emotional_impression", "thumbnail_hook_type",
    }
    y_train = np.array([row["target"] for row in train])
    y_test = np.array([row["target"] for row in test])
    results = {
        "train_median": score(y_test, np.full(len(test), np.median(y_train))),
    }
    for model_name, features in feature_groups.items():
        categorical = [feature for feature in features if feature in categorical_features]
        numeric = [feature for feature in features if feature not in categorical_features]
        preprocess = ColumnTransformer(
            [
                ("numeric", SimpleImputer(strategy="median"), numeric),
                ("categorical", Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ]), categorical),
            ]
        )
        model = Pipeline([
            ("preprocess", preprocess),
            ("regressor", RandomForestRegressor(
                n_estimators=500, max_depth=5, min_samples_leaf=3, random_state=42, n_jobs=-1
            )),
        ])
        x_train = pd.DataFrame([{feature: row[feature] for feature in features} for row in train])
        x_test = pd.DataFrame([{feature: row[feature] for feature in features} for row in test])
        model.fit(x_train, y_train)
        results[model_name] = score(y_test, model.predict(x_test))

    report = {
        "target": "log_views_per_day",
        "sample": "120 thumbnails stratified by period and low/middle/high performance",
        "split": {"train": "<=2022", "test": ">=2023"},
        "counts": {"train": len(train), "test": len(test)},
        "results": results,
        "interpretation": [
            "Compare models only on this same fixed sample; lower MAE/RMSE and higher Spearman are better.",
            "The outcome-stratified 120-video sample is useful for exploration but not population-level causal inference.",
            "Vision labels are Qwen2.5-VL observations, not human-labeled ground truth.",
        ],
    }
    (report_dir / "thumbnail-vision-ablation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
