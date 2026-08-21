# Barış Özcan Channel Analysis

Source-backed data package for the video **“Barış Özcan'ın 849 Videosunu Yapay Zekâyla Analiz Ettim.”**

The analysis snapshot was collected on **2026-08-20**. View, like and comment counts are mutable snapshots—not timeless values.

## Video package

- [`video-assets/script/VIDEO_SCRIPT.md`](video-assets/script/VIDEO_SCRIPT.md) — full spoken script with edit and screen cues
- [`video-assets/script/RECORDING_TRANSCRIPT.txt`](video-assets/script/RECORDING_TRANSCRIPT.txt) — clean recording copy
- [`video-assets/script/AI_ASSISTED_INTRO.md`](video-assets/script/AI_ASSISTED_INTRO.md) — transcript-profile chatbot draft, evidence-corrected for recording
- [`video-assets/script/CLAIM_LEDGER.md`](video-assets/script/CLAIM_LEDGER.md) — claim-by-claim evidence and limitations
- [`video-assets/script/SOURCES.md`](video-assets/script/SOURCES.md) — auditable sources and opening clip
- [`video-assets/charts/`](video-assets/charts/) — six presentation-ready PNG charts
- [`video-assets/thumbnail-samples/contact-sheet-manifest.csv`](video-assets/thumbnail-samples/contact-sheet-manifest.csv) — source attribution for the locally reviewed thumbnail sample
- [`video-assets/presenter/`](video-assets/presenter/) — keyboard-controlled 16:9 metric deck with hidden speaker notes

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
3. **No magic thumbnail formula:** saturation and brightness show weak full-catalog correlations; a separate exploratory Qwen vision experiment also failed to improve its temporal baseline.
4. **Question-led voice fingerprint:** a rule-based classifier found question-oriented signals in the first 90 seconds of 550 of 800 transcript-backed videos; 209 were classified as surprising claims. Punctuation-sensitive measurements rely on manual captions.
5. **No measured style feature is a strong performance rule:** all year-centered style associations are weak and non-causal.

## Repository layout

```text
analysis/                 Analysis and chart-generation scripts
data/reports/             Curated aggregate JSON and CSV outputs
video-assets/charts/      Video-ready graphics
video-assets/script/      Script, claim ledger and sources
video-assets/presenter/   Screen-recordable metric deck
video-assets/thumbnail-samples/contact-sheet-manifest.csv
```

## Run the metric presenter

```bash
python -m http.server 8000 --directory video-assets
```

Open `http://localhost:8000/presenter/`. Use arrow keys or space to advance, `F` for fullscreen and `N` for speaker notes.

## Reproduce the analysis

```bash
python -m pip install -r requirements.txt
```

The analysis scripts document the transformations used for the video. Exact chart rebuilding additionally requires the local row-level reports and source material, which are intentionally excluded from the public repository. Presentation-ready charts and aggregate summaries are committed as the auditable release artifacts.

## Method limits

- Correlation is not causation.
- Views/day reduces but does not eliminate video-age and historical confounding.
- The 120-thumbnail vision analysis is exploratory, not population-level proof.
- Automatic captions flatten punctuation; manual captions define sentence-level style metrics.
- Rule-based topic, emotion and opening-hook labels are navigation aids, not human ground truth.
- No YouTube click-through, retention or impression data was available.

## Public release and exclusions

This is an independent editorial research snapshot, not an official YouTube or Barış Özcan data product. YouTube-sourced counts are dated **2026-08-20**. All ratios, labels, correlations, estimates and charts are independent calculations—not metrics supplied or endorsed by YouTube.

The public repository excludes raw subtitle files, downloaded thumbnails, row-level YouTube metadata, per-video derived tables, SQLite databases, model weights, embeddings, browser/session data, API credentials and chatbot implementation. The thumbnail manifest retains only source references; third-party images are not redistributed.

The repository is not affiliated with or endorsed by Barış Özcan or YouTube.

## Source terms and licensing

YouTube is the source of the dated public channel/video metadata referenced by this editorial analysis. See the [YouTube Terms of Service](https://www.youtube.com/t/terms), [YouTube API Services Developer Policies](https://developers.google.com/youtube/terms/developer-policies) and [Google Privacy Policy](https://policies.google.com/privacy).

See [`LICENSE`](LICENSE) for the scoped code, documentation and chart licenses. Third-party YouTube content, thumbnails, names and trademarks are excluded from the repository license.
