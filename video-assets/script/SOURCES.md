# Sources

Accessed 2026-08-20 unless otherwise stated.

## Opening clip

1. **Barış Özcan — “Neden tişörtlerimin veritabanı var?”** YouTube. Opening line at approximately 00:00.
   https://www.youtube.com/watch?v=n1ybNDk9NUo&t=0s

   Brief quoted line used in the cold open:

   > “Buradan ve şuradan giren veri miktarını hiç merak ettiniz mi?”

## Repository evidence

The database construction and separation workflow is implemented in `analysis/build_dataset.py`: it joins catalog, metadata, caption manifest and SRT inputs by video ID; creates the SQLite schema; retains raw, normalized and timed transcript layers; and emits baseline reports.

The following aggregate and editorial files are generated from the dated channel snapshot and committed under `data/reports/`:

- `analysis-summary.json` — consolidated scope, channel shape, packaging, content and voice results.
- `baseline.json` — aggregate collection coverage and caption-source counts.
- `channel-distribution.json` — aggregate view concentration, Gini coefficient and upload cadence.
- `performance-summary.json` — grouped duration, title-length and year-normalized descriptive performance results.
- `thumbnail-performance.json` and `thumbnail-ocr-summary.json` — aggregate thumbnail findings.
- `thumbnail-vision-ablation.json` and `thumbnail-vision-labeling-summary.json` — aggregate local vision-model experiment results.
- `packaging-ablation.json` — aggregate temporal model comparisons.
- `creator-style-summary.json` and `creator-style-performance.json` — aggregate transcript-derived style findings.
- `semantic-summary.json` and `topic-language.json` — aggregate content-navigation labels.
- `revenue-estimate.json` — auditable RPM scenarios, live-channel view input, current-rate TRY conversion and per-word calculation.

Row-level YouTube metadata and per-video derived tables are intentionally retained only in the local research workspace.

## Revenue estimate sources

1. **YouTube Help — “Understand ad revenue analytics.”** RPM definition and exclusions. Accessed 2026-08-20.
   https://support.google.com/youtube/answer/9314357?hl=en
2. **Social Blade — “Barış Özcan's YouTube Statistics.”** Live 2026-08-20 channel snapshot: 1,000,694,083 views and 946 videos. Accessed 2026-08-20.
   https://socialblade.com/youtube/handle/barisozcan
3. **RevenueLab — “YouTube Revenue Calculator — Turkey (2026).”** Directional Turkey RPM scenarios: $0.50 low, $1.10 typical, $2.80 high. Editorial review dated 2026-05-16. Accessed 2026-08-20.
   https://www.revenuelab.fyi/youtube-revenue-calculator/turkey
4. **Central Bank of the Republic of Türkiye — Indicative Exchange Rates, 2026-08-20.** USD forex buying 47.8642, selling 47.9504; model uses their midpoint 47.9073. Accessed 2026-08-20.
   https://www.tcmb.gov.tr/kurlar/202608/20082026.xml

## Method and reproducibility notes

- View, like and comment counts are mutable YouTube metadata snapshots, not timeless values.
- Performance comparisons use views/day where practical to reduce—but not eliminate—video-age confounding.
- Correlation and feature-ablation results are associations, not causal evidence.
- Punctuation-sensitive language claims rely on 480 manual-caption videos.
- The Qwen thumbnail labels cover a stratified 120-video sample and are exploratory.
- Raw subtitle files, downloaded thumbnails, row-level YouTube metadata, per-video derived tables, SQLite databases, embeddings, model files and chatbot implementation are intentionally excluded from the public GitHub package. The repository contains aggregate reports, source-attribution manifests and scripts documenting the analysis.
