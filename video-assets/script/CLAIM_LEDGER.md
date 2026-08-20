# Claim-source ledger

Analysis snapshot: **2026-08-20**. All view and engagement values are dated snapshots.

| ID | Planned claim | Source | Evidence type | Confidence | Limits |
|---|---|---|---|---|---|
| C01 | Catalog contains 849 videos, 800 transcript-backed videos, 849 thumbnails and 3,775 semantic chunks. | `data/reports/analysis-summary.json`, scope | Full-catalog derived count | High | Transcript coverage is 800/849, not complete. |
| C02 | Normalized transcript corpus contains about 1.2 million words. | `data/reports/creator-style-summary.json`; `data/reports/creator-chatbot-profile.json` | Derived corpus count | High | Normalization changes raw caption tokenization. |
| C03 | Total view snapshot is 891,593,029; median video views are 718,106. | `data/reports/analysis-summary.json`, channel_shape | Full-catalog metadata snapshot | High | Values continue changing after collection. |
| C04 | Top 10 videos hold 8.3935% of views; 45.1119% of the catalog is needed to reach 80% of views; Gini is 0.502897. | `data/reports/channel-distribution.json`; `data/reports/analysis-summary.json` | Full-catalog distribution | High | Describes this snapshot, not future traffic. |
| C05 | Long-form is the clearest descriptive packaging split: 577 videos over 10 minutes have median 843,727 views and 627.4 views/day. | `data/reports/performance-summary.json`; `data/reports/analysis-summary.json` | Full-catalog descriptive grouping | High | Not causal; years, subjects and channel maturity differ. |
| C06 | 5–10 minute videos: 189 videos, median 543,500 views, 186.5 views/day. Under 5 minutes: 83 videos, median 68,644 views, 17.2 views/day. | Same as C05 | Full-catalog descriptive grouping | High | Same confounding limits as C05. |
| C07 | Title length does not yield a clean universal rule. Under-40 titles have higher total median views, while 40–79 character titles have higher median views/day. | `data/reports/analysis-summary.json`, title_length_groups | Full-catalog descriptive grouping | High | Bucket boundaries are editorial choices. |
| C08 | Basic thumbnail correlations with log views: saturation +0.232684, brightness +0.152197, edge density −0.086117. | `data/reports/thumbnail-performance.json`; `data/reports/analysis-summary.json` | Full-catalog Pearson association | High | Correlation is not causal; no click-through rate was available. |
| C09 | The Qwen vision experiment labels a temporally and outcome-stratified sample of 120 thumbnails. | `data/reports/thumbnail-vision-labeling-summary.json`; `data/reports/thumbnail-vision-sample.csv` | Exploratory sampled analysis | High | Not population-level evidence. |
| C10 | On the 2025+ temporal test, baseline packaging Spearman is 0.288357; adding content and thumbnail features lowers it to 0.103379. | `data/reports/packaging-ablation.json`; `data/reports/analysis-summary.json` | Temporal predictive ablation | High | One model specification and one time split; not a universal benchmark. |
| C11 | Style metrics use 480 manual-caption videos; median sentence length is 10.7678 words and median Ateşman readability is 66.86045. | `data/reports/creator-style-summary.json`; `data/reports/creator-chatbot-profile.json` | Manual-caption corpus statistics | High | Automatic captions are excluded from punctuation-sensitive claims. |
| C12 | Intro classifier finds 550 question openings, 209 surprising-claim openings and nine statement openings across 800 transcript videos. | `data/reports/creator-style-summary.json`; `data/reports/analysis-summary.json` | Rule-based full transcript classification | Medium | Pattern classifier is not human annotation and may miss nuanced openings. |
| C13 | Strongest year-centered measured style/performance association has absolute Spearman 0.152044. | `data/reports/creator-style-performance.json`; `data/reports/analysis-summary.json` | Year-centered exploratory association | Medium-high | Weak and non-causal; do not present as a success rule. |
| C14 | Chatbot retrieval index has 3,775 chunks and 384 embedding dimensions. | `data/reports/retrieval-index.json`; `data/reports/creator-chatbot-profile.json` | Built artifact metadata | High | Chatbot implementation is intentionally omitted from this public video-data package. |
| C15 | Opening quotation: “Buradan ve şuradan giren veri miktarını hiç merak ettiniz mi?” | Barış Özcan, “Neden tişörtlerimin veritabanı var?”, 00:00, manual transcript | Brief direct quotation | High | Keep clip brief and attribute the source video. Confirm final editorial permission/usage. |

## Editorial interpretation

The script's conclusion—that the channel looks more like a durable editorial system than a single viral formula—is an interpretation supported by C04, C05 and C11–C13. It is not a causal model result.
