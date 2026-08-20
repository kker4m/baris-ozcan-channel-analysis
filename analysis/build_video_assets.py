#!/usr/bin/env python3
"""Build presentation-ready charts and a thumbnail contact sheet for the video."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "data" / "reports"
THUMBNAILS = ROOT / "data" / "thumbnails"
OUTPUT = ROOT / "video-assets"
CHARTS = OUTPUT / "charts"
SAMPLES = OUTPUT / "thumbnail-samples"

INK = "#171814"
PAPER = "#eee9dc"
ORANGE = "#ff5c35"
SAGE = "#7f9270"
MUTED = "#777168"


def load_json(name: str) -> dict:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


def load_csv(name: str) -> list[dict[str, str]]:
    with (REPORTS / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def setup() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
    })


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def channel_scale(summary: dict) -> None:
    values = [
        ("849", "video"),
        ("800", "transcript"),
        ("1,2M", "normalize kelime"),
        ("891,6M", "toplam izlenme\n(anlık görüntü)"),
    ]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis("off")
    for index, (value, label) in enumerate(values):
        x = (index + 0.5) / len(values)
        ax.text(x, 0.62, value, ha="center", va="center", fontsize=36, fontweight="bold")
        ax.text(x, 0.32, label.upper(), ha="center", va="center", fontsize=11, color=MUTED)
        if index:
            ax.plot([index / len(values)] * 2, [0.2, 0.78], color="#c9c1b0", linewidth=1)
    ax.set_title("BARIŞ ÖZCAN KANALI — ANALİZ KAPSAMI", loc="left", fontsize=17, pad=20)
    save(fig, "01-channel-scale.png")


def catalog_lorenz(rows: list[dict[str, str]], summary: dict) -> None:
    views = np.sort(np.array([int(row["view_count"]) for row in rows], dtype=float))
    cumulative = np.insert(np.cumsum(views) / views.sum(), 0, 0)
    share = np.linspace(0, 1, len(cumulative))
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(share * 100, cumulative * 100, color=ORANGE, linewidth=3, label="Gerçek katalog")
    ax.plot([0, 100], [0, 100], color=MUTED, linestyle="--", linewidth=1.5, label="Eşit dağılım")
    ax.axvline(summary["channel_shape"]["catalog_share_for_80pct_views"] * 100, color=SAGE, linestyle=":", linewidth=2)
    ax.axhline(80, color=SAGE, linestyle=":", linewidth=2)
    ax.set(xlabel="Videoların kümülatif payı (%)", ylabel="İzlenmelerin kümülatif payı (%)", title="İzlenme yalnızca birkaç viral videoya bağlı değil")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(alpha=.15)
    save(fig, "02-catalog-lorenz.png")


def duration_performance(summary: dict) -> None:
    groups = summary["packaging"]["duration_groups"]
    order = ["<5m", "5-10m", "10m+"]
    labels = ["5 dk altı", "5–10 dk", "10 dk üzeri"]
    values = [groups[key]["median_views_per_day"] for key in order]
    counts = [groups[key]["videos"] for key in order]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(labels, values, color=["#b8ae9c", SAGE, ORANGE], width=.62)
    for bar, value, count in zip(bars, values, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 18, f"{value:,.0f}/gün\n{count} video", ha="center", fontsize=11)
    ax.set(ylabel="Medyan izlenme / gün", title="En net betimsel ayrım: uzun format")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "03-duration-performance.png")


def thumbnail_correlations(summary: dict) -> None:
    data = summary["packaging"]["basic_thumbnail_correlations"]
    order = ["saturation_mean", "brightness_mean", "brightness_std", "edge_density"]
    labels = ["Doygunluk", "Parlaklık", "Parlaklık değişimi", "Kenar yoğunluğu"]
    values = [data[key]["pearson_log_views"] for key in order]
    colors = [ORANGE if value >= 0 else SAGE for value in values]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.axvline(0, color=INK, linewidth=1)
    for bar, value in zip(bars, values[::-1]):
        ax.text(value + (.008 if value >= 0 else -.008), bar.get_y() + bar.get_height() / 2, f"{value:+.3f}", va="center", ha="left" if value >= 0 else "right")
    ax.set(xlabel="Pearson korelasyonu — log izlenme", title="Thumbnail renk sinyalleri zayıf ilişkiler gösteriyor")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "04-thumbnail-correlations.png")


def hook_mix(summary: dict) -> None:
    hooks = summary["creator_voice"]["intro_hook_types"]
    order = ["question", "surprising_claim", "story", "direct_address", "statement"]
    labels = ["Soru", "Şaşırtıcı iddia", "Hikâye", "Doğrudan hitap", "Düz ifade"]
    values = [hooks[key]["videos"] for key in order]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(labels, values, color=[ORANGE, SAGE, "#b8ae9c", "#91856f", "#d5cdbc"])
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 9, str(value), ha="center", fontweight="bold")
    ax.set(ylabel="Video sayısı", title="Açılışların çoğu bir soruyla başlıyor")
    ax.tick_params(axis="x", rotation=12)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "05-intro-hooks.png")


def model_ablation(summary: dict) -> None:
    test = summary["packaging"]["full_catalog_temporal_ablation"]
    order = ["global_median", "baseline_packaging", "baseline_plus_content", "baseline_plus_content_plus_thumbnail"]
    labels = ["Global medyan", "Paketleme", "+ içerik", "+ thumbnail"]
    values = [test[key]["test_2025_plus"]["spearman"] for key in order]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(labels, values, color=["#b8ae9c", ORANGE, SAGE, "#837865"])
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + .012, f"{value:.3f}", ha="center", fontweight="bold")
    ax.set(ylim=(0, .42), ylabel="Spearman — 2025+ test", title="Daha fazla özellik, daha iyi tahmin demek değil")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "06-temporal-ablation.png")


def contact_sheet(sample: list[dict[str, str]]) -> None:
    chosen = sample[::10][:12]
    tile_w, tile_h = 320, 210
    sheet = Image.new("RGB", (tile_w * 3, tile_h * 4), PAPER)
    draw = ImageDraw.Draw(sheet)
    manifest = []
    for index, row in enumerate(chosen):
        source = THUMBNAILS / f"{row['id']}.webp"
        if not source.exists():
            continue
        image = Image.open(source).convert("RGB")
        image = ImageOps.fit(image, (tile_w, 180), method=Image.Resampling.LANCZOS)
        x = index % 3 * tile_w
        y = index // 3 * tile_h
        sheet.paste(image, (x, y))
        label = f"{row['performance_group'].upper()} · {row['year_band']}"
        draw.rectangle((x, y + 180, x + tile_w, y + tile_h), fill=INK)
        draw.text((x + 10, y + 188), label, fill=PAPER)
        manifest.append(row)
    sheet.save(SAMPLES / "qwen-vision-sample-contact-sheet.jpg", quality=92)
    with (SAMPLES / "contact-sheet-manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sample[0].keys())
        writer.writeheader()
        writer.writerows(manifest)


def main() -> None:
    setup()
    summary = load_json("analysis-summary.json")
    performance = load_csv("video-performance.csv")
    sample = load_csv("thumbnail-vision-sample.csv")
    channel_scale(summary)
    catalog_lorenz(performance, summary)
    duration_performance(summary)
    thumbnail_correlations(summary)
    hook_mix(summary)
    model_ablation(summary)
    if THUMBNAILS.is_dir():
        contact_sheet(sample)
    print(json.dumps({"charts": 6, "output": str(OUTPUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
