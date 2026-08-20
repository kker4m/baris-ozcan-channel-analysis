# Sources

Accessed 2026-08-20 unless otherwise stated.

## Opening clip

1. **Barış Özcan — “Neden tişörtlerimin veritabanı var?”** YouTube. Opening line at approximately 00:00.
   https://www.youtube.com/watch?v=n1ybNDk9NUo&t=0s

   Brief quoted line used in the cold open:

   > “Buradan ve şuradan giren veri miktarını hiç merak ettiniz mi?”

## Repository evidence

These files are generated from the channel catalog snapshot and are committed under `data/reports/`:

- `analysis-summary.json` — consolidated scope, channel shape, packaging, content and voice results.
- `channel-distribution.json` — view concentration, Gini coefficient, top-video shares and upload cadence.
- `performance-summary.json` — duration, title length and year-normalized descriptive performance groups.
- `video-performance.csv` — per-video analysis table used for distributions and charts.
- `thumbnail-performance.json` — full-catalog basic thumbnail correlations.
- `thumbnail-features.csv` — per-video color, brightness and edge-density features.
- `thumbnail-vision-sample.csv` — balanced 120-thumbnail vision sample.
- `thumbnail-vision-performance.csv` — sample labels joined to performance.
- `thumbnail-vision-ablation.json` — temporal ablation on the vision sample.
- `packaging-ablation.json` — full-catalog temporal model comparisons.
- `creator-style-summary.json` — transcript-derived language, opening-hook and recurring-structure metrics.
- `creator-style-performance.json` — year-centered exploratory style/performance associations.
- `creator-style-videos.csv` — per-video style features for the 800 transcript-backed videos.
- `topic-assignments.csv` and `semantic-summary.json` — lightweight content-navigation labels.
- `thumbnail-ocr.csv` and `thumbnail-ocr-summary.json` — OCR-derived thumbnail text features.
- `thumbnail-vision-labels.jsonl` and `thumbnail-vision-labeling-summary.json` — local vision-model outputs and coverage.

## Method and reproducibility notes

- View, like and comment counts are mutable YouTube metadata snapshots, not timeless values.
- Performance comparisons use views/day where practical to reduce—but not eliminate—video-age confounding.
- Correlation and feature-ablation results are associations, not causal evidence.
- Punctuation-sensitive language claims rely on 480 manual-caption videos.
- The Qwen thumbnail labels cover a stratified 120-video sample and are exploratory.
- Raw subtitle files, 849 downloaded thumbnails, embeddings, model files and chatbot implementation are intentionally excluded from the GitHub package. The repository contains derived tables, a 12-image contact sheet and scripts needed to understand or reproduce the presented outputs.
