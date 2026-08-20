#!/usr/bin/env python3
"""Assign semantic topic scores and deterministic Turkish emotion signals."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

TOPIC_DESCRIPTIONS = {
    "bilim": "bilimsel keşifler, deneyler, fizik, kimya ve biyoloji",
    "uzay": "uzay, gezegenler, yıldızlar, evren ve astronotlar",
    "teknoloji": "teknoloji, yazılım, internet, bilgisayarlar ve yapay zeka",
    "psikoloji": "psikoloji, insan zihni, beyin, hafıza ve alışkanlıklar",
    "tarih": "tarih, geçmiş uygarlıklar, savaşlar ve tarihsel olaylar",
    "sanat_tasarım": "sanat, tasarım, resim, fotoğraf ve görsel kültür",
    "sinema": "sinema, filmler, diziler ve televizyon hikayeleri",
    "kitap": "kitaplar, okuma, yazarlar, romanlar ve şiir",
    "günlük_hayat": "günlük hayat, insanlar, toplum ve kişisel deneyimler",
}
EMOTION_WORDS = {
    "merak": ("merak", "acaba", "keşfet", "soru", "öğrenmek"),
    "şaşkınlık": ("şaşırt", "inanılmaz", "hayret", "şok", "beklenmedik"),
    "hayranlık": ("muhteşem", "harika", "olağanüstü", "etkileyici", "hayran"),
    "eğlence": ("komik", "şaka", "gül", "eğlenceli", "espri"),
    "öfke": ("öfke", "kızgın", "sinir", "adaletsiz", "nefret"),
    "korku": ("korku", "tehlike", "ölüm", "kâbus", "panik"),
    "üzüntü": ("üzgün", "acı", "kayb", "yas", "hüzün"),
    "mutluluk": ("mutlu", "sevinç", "neşe", "başarı", "kutla"),
}


def encode_texts(texts: list[str], model_path: str) -> np.ndarray:
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModel.from_pretrained(model_path, local_files_only=True)
    model.eval()
    vectors = []
    for start in range(0, len(texts), 8):
        encoded = tokenizer(
            texts[start : start + 8],
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt",
        )
        with torch.inference_mode():
            output = model(**encoded).last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1)
        pooled = (output * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
        vectors.append(torch.nn.functional.normalize(pooled, p=2, dim=1).cpu().numpy())
    return np.concatenate(vectors, axis=0).astype(np.float32)


def emotion_signal(text: str) -> tuple[str, dict[str, int]]:
    lowered = text.casefold()
    scores = {
        emotion: sum(lowered.count(term) for term in terms)
        for emotion, terms in EMOTION_WORDS.items()
    }
    if not any(scores.values()):
        return "nötr", scores
    return max(scores, key=scores.get), scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/baris-ozcan"))
    parser.add_argument("--model", required=True)
    parser.add_argument("--top-topics", type=int, default=2)
    args = parser.parse_args()

    report_dir = args.root.resolve() / "reports"
    index = json.loads((report_dir / "retrieval-index.json").read_text(encoding="utf-8"))
    vectors = np.load(report_dir / index["vectors"])
    chunks = [
        json.loads(line)
        for line in (report_dir / index["metadata"]).read_text(encoding="utf-8").splitlines()
        if line
    ]
    topic_names = list(TOPIC_DESCRIPTIONS)
    topic_vectors = encode_texts(
        [f"Bu video {description} hakkında." for description in TOPIC_DESCRIPTIONS.values()],
        args.model,
    )
    topic_scores = vectors @ topic_vectors.T
    topic_counts = Counter()
    emotion_counts = Counter()
    rows = []
    for index_row, chunk in enumerate(chunks):
        order = np.argsort(topic_scores[index_row])[::-1][: args.top_topics]
        topics = [(topic_names[int(i)], round(float(topic_scores[index_row, i]), 5)) for i in order]
        emotion, scores = emotion_signal(chunk["text"])
        topic_counts[topics[0][0]] += 1
        emotion_counts[emotion] += 1
        rows.append(
            {
                "video_id": chunk["video_id"],
                "title": chunk["title"],
                "start_seconds": chunk["start_seconds"],
                "end_seconds": chunk["end_seconds"],
                "primary_topic": topics[0][0],
                "primary_topic_score": topics[0][1],
                "secondary_topic": topics[1][0] if len(topics) > 1 else "",
                "secondary_topic_score": topics[1][1] if len(topics) > 1 else "",
                "dominant_emotion": emotion,
                "emotion_hits": sum(scores.values()),
            }
        )

    with (report_dir / "semantic-chunks.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "method": "multilingual BERT chunk-to-label cosine similarity plus Turkish lexicon signals",
        "topics": dict(topic_counts),
        "emotions": dict(emotion_counts),
        "chunks": len(rows),
        "warning": "This is a reproducible baseline, not human-labeled ground truth; validate labels before training or publication.",
    }
    (report_dir / "semantic-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
