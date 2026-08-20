# Barış Özcan Channel Analysis

Source-backed data package for the video **“Barış Özcan'ın 849 Videosunu Yapay Zekâyla Analiz Ettim.”**

The analysis snapshot was collected on **2026-08-20**. View, like and comment counts are mutable snapshots—not timeless values.

## Video package

- [`video-assets/script/VIDEO_SCRIPT.md`](video-assets/script/VIDEO_SCRIPT.md) — full spoken script with edit and screen cues
- [`video-assets/script/RECORDING_TRANSCRIPT.txt`](video-assets/script/RECORDING_TRANSCRIPT.txt) — clean recording copy
- [`video-assets/script/CLAIM_LEDGER.md`](video-assets/script/CLAIM_LEDGER.md) — claim-by-claim evidence and limitations
- [`video-assets/script/SOURCES.md`](video-assets/script/SOURCES.md) — auditable sources and opening clip
- [`video-assets/charts/`](video-assets/charts/) — six presentation-ready PNG charts
- [`video-assets/thumbnail-samples/`](video-assets/thumbnail-samples/) — 12-thumbnail contact sheet and manifest

## Analysis coverage

| Input | Coverage |
|---|---:|
| Catalog videos | 849 |
| Videos with Turkish transcripts | 800 |
| Manual captions used for punctuation-sensitive style metrics | 480 |
| Normalized transcript words | 1,200,642 |
| Thumbnail images analyzed | 849 |
| Vision-labeled thumbnail sample | 120 |
| Semantic transcript chunks | 3,775 |

## Main findings

1. **Broad back catalog:** the top 10 videos account for about 8.4% of snapshot views; roughly 45.1% of the catalog is required to reach 80% of views.
2. **Long form is the clearest descriptive split:** 10-minute-plus videos dominate the catalog and have the highest median views/day. This is association, not proof that extending a video causes views.
3. **No magic thumbnail formula:** saturation and brightness show weak full-catalog correlations; richer Qwen vision labels did not improve the out-of-time prediction test.
4. **Question-led voice fingerprint:** 550 of 800 transcript openings were classified as questions; 209 used a surprising claim. Punctuation-sensitive measurements rely on manual captions.
5. **No measured style feature is a strong performance rule:** all year-centered style associations are weak and non-causal.

## Repository layout

```text
analysis/                 Analysis and chart-generation scripts
data/reports/             Curated derived JSON, CSV and JSONL outputs
video-assets/charts/      Video-ready graphics
video-assets/script/      Script, transcript, claim ledger and sources
video-assets/thumbnail-samples/
```

## Rebuild the published charts

```bash
python -m pip install -r requirements.txt
python analysis/build_video_assets.py
```

The chart script rebuilds the six charts from committed aggregate/per-video reports. The contact sheet is committed as a video artifact; rebuilding it requires the original downloaded thumbnail directory, which is intentionally excluded.

## Method limits

- Correlation is not causation.
- Views/day reduces but does not eliminate video-age and historical confounding.
- The 120-thumbnail vision analysis is exploratory, not population-level proof.
- Automatic captions flatten punctuation; manual captions define sentence-level style metrics.
- Rule-based topic, emotion and opening-hook labels are navigation aids, not human ground truth.
- No YouTube click-through, retention or impression data was available.

## Exclusions

Raw subtitle files, 849 downloaded thumbnail files, YouTube metadata dumps, model weights, embeddings, API credentials and chatbot implementation are not included. The repository publishes derived evidence, reproducible chart code and the assets used in the video.
