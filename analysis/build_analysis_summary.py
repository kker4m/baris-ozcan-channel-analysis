#!/usr/bin/env python3
"""Consolidate lightweight channel-analysis findings for the video and chatbot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    args = parser.parse_args()
    reports = args.root.resolve() / "reports"
    baseline = load(reports / "baseline.json")
    distribution = load(reports / "channel-distribution.json")
    performance = load(reports / "performance-summary.json")
    packaging = load(reports / "packaging-ablation.json")
    thumbnail = load(reports / "thumbnail-performance.json")
    vision = load(reports / "thumbnail-vision-performance.json")
    vision_ablation = load(reports / "thumbnail-vision-ablation.json")
    semantic = load(reports / "semantic-summary.json")
    style = load(reports / "creator-style-summary.json")
    style_performance = load(reports / "creator-style-performance.json")
    profile = load(reports / "creator-chatbot-profile.json")

    manual_style = style["medians_by_caption_source"]["manual"]
    strongest_style = style_performance["ranked_year_centered_signals"][0]
    report = {
        "status": "complete_for_lightweight_video_analysis",
        "scope": {
            "catalog_videos": baseline["catalog_videos"],
            "transcript_videos": style["videos_analyzed"],
            "thumbnail_videos": thumbnail["features"]["brightness_mean"]["videos"],
            "vision_labeled_sample": vision["successfully_labeled"],
            "semantic_chunks": semantic["chunks"],
        },
        "channel_shape": {
            "total_views_snapshot": distribution["total_views_snapshot"],
            "median_views": distribution["median_views"],
            "view_gini": distribution["view_gini"],
            "top_10_view_share": distribution["concentration"]["top_10_view_share"],
            "catalog_share_for_80pct_views": distribution["concentration"]["videos_for_80pct_views"]["catalog_share"],
            "median_days_between_uploads": distribution["publishing_cadence"]["median_days_between_uploads"],
            "takeaway": "Views are distributed across a broad back catalog rather than being dominated by a handful of viral uploads.",
        },
        "packaging": {
            "duration_groups": performance["by_duration"],
            "title_length_groups": performance["by_title_length"],
            "basic_thumbnail_correlations": thumbnail["features"],
            "full_catalog_temporal_ablation": packaging["results"],
            "vision_sample_temporal_ablation": vision_ablation["results"],
            "takeaway": "Long-form format is the clearest descriptive packaging split. Basic full-catalog color features and exploratory Qwen labels, evaluated in separate temporal tests, did not add stable predictive value beyond their respective baselines.",
        },
        "content_baseline": {
            "topic_chunk_counts": semantic["topics"],
            "emotion_chunk_counts": semantic["emotions"],
            "takeaway": "Topic and emotion labels are usable as lightweight editorial navigation, not as ground-truth channel psychology.",
        },
        "creator_voice": {
            "manual_caption_videos": style["caption_sources"]["manual"],
            "median_words_per_sentence": manual_style["words_per_sentence"],
            "median_atesman_readability": manual_style["atesman_readability"],
            "questions_per_1000_words": manual_style["question_marks_per_1k"],
            "analogy_markers_per_1000_words": manual_style["analogy_per_1k"],
            "direct_address_per_1000_words": manual_style["direct_address_per_1k"],
            "intro_hook_types": style["intro_hook_types"],
            "recurring_transitions": style["recurring_phrases_by_video_coverage"][:10],
            "strongest_year_centered_style_signal": strongest_style,
            "takeaway": "The repeatable voice is accessible, question-led, analogy-friendly, and directly addressed; no measured style signal is strong enough to become a performance rule.",
        },
        "chatbot_readiness": {
            "interface": "chat_creator.py",
            "validator": "validate_chatbot.py",
            "profile": "creator-chatbot-profile.json",
            "retrieval_index": "retrieval-index.json",
            "retrieval_chunks": profile["corpus"]["retrieval_chunks"],
            "retrieval_dimensions": profile["corpus"]["retrieval_dimensions"],
            "ready": True,
            "next": "Use the local CLI in the video demo or add an optional visual interface.",
        },
        "editorial_guardrails": [
            "Use age-normalized views/day for performance comparisons.",
            "Treat all correlations and model gains as associations, not causes.",
            "Use manual captions for punctuation, sentence length, and readability claims.",
            "Describe the 120-thumbnail vision findings as an exploratory sample.",
            "Keep the video entertaining: lead with channel scale, back-catalog breadth, long-form dominance, and the question-led voice fingerprint.",
        ],
    }
    (reports / "analysis-summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
