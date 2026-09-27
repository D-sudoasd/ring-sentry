"""Reproducible publication graphics; no experimental measurements are synthesized."""

import argparse
import numpy as np
from pathlib import Path
import sys
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#142C3D"
MUTED = "#516570"
RULE = "#CCD7DC"
ACCENT = "#087F8C"
LIGHT = "#EFF7F8"
WARM = "#B86B20"


def style():
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": RULE,
            "axes.linewidth": 0.7,
            "lines.linewidth": 1.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "publication-20260927",
            "pdf.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def canvas(height=4.6):
    fig = plt.figure(figsize=(7.2, height), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    return fig, ax


def label(ax, x, y, text, size=10, weight="normal", color=INK, ha="left", va="center"):
    return ax.text(
        x, y, text, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, linespacing=1.45
    )


def panel(ax, x, y, letter, title):
    label(ax, x, y, letter, 12, "bold", ACCENT)
    label(ax, x + 0.038, y, title, 11, "bold")


def box(ax, x, y, w, h, title, body="", accent=ACCENT, face=LIGHT, size=9.5):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=0.012",
            linewidth=0.7,
            edgecolor=RULE,
            facecolor=face,
        )
    )
    ax.plot(
        [x + 0.015, x + 0.015],
        [y + 0.02, y + h - 0.02],
        color=accent,
        lw=2.1,
        solid_capstyle="round",
    )
    label(ax, x + 0.034, y + h - 0.037, title, 10, "bold", accent, va="top")
    if body:
        label(ax, x + 0.034, y + h - 0.099, body, size, va="top")


def arrow(ax, a, b, color=MUTED, style="-"):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1,
            color=color,
            linestyle=style,
            shrinkA=2,
            shrinkB=2,
        )
    )


def save(fig, folder, stem, formats=("png", "svg", "pdf")):
    folder.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        meta = (
            {"Date": None}
            if ext == "svg"
            else ({"CreationDate": None, "ModDate": None} if ext == "pdf" else {})
        )
        fig.savefig(folder / f"{stem}.{ext}", dpi=450, metadata=meta)
    plt.close(fig)


def clean_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3, width=0.6, color=RULE)
    ax.grid(axis="y", color=RULE, linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.processing import apply_processing
from core.quality import analyze_image_quality
from examples.minimal_preprocessing import (
    PROCESSING_OPTIONS,
    SYNTHETIC_SEED,
    generate_synthetic_detector_image,
)


def create_architecture_workflow():
    fig, ax = canvas(5.5)
    panel(ax, 0.035, 0.95, "a", "Batch workflow")
    names = [
        ("01  Configure", "GUI settings"),
        ("02  Load", "Detector arrays"),
        ("03  Inspect", "Read-only QC"),
        ("04  Process", "Ordered steps"),
        ("05  Export", "Data + reports"),
    ]
    for i, (title, body) in enumerate(names):
        x = 0.035 + i * 0.192
        box(ax, x, 0.75, 0.165, 0.135, title, body, size=8.8)
        if i < 4:
            arrow(ax, (x + 0.165, 0.814), (x + 0.192, 0.814))
    panel(ax, 0.035, 0.68, "b", "Fixed numerical operation order")
    operations = [
        "Dark subtraction",
        "Flat correction",
        "Background offset",
        "Validate clipping",
        "Region of interest",
        "Mask",
        "Absolute clipping",
        "Percentile clipping",
        "Negative clipping",
        "Hot-pixel suppression",
        "Rotate / flip",
        "Block-mean binning",
        "Intensity transform",
        "Gamma",
        "Normalization",
    ]
    for i, t in enumerate(operations):
        col, row = divmod(i, 5)
        x = 0.048 + col * 0.32
        y = 0.608 - row * 0.053
        label(ax, x, y, f"{i + 1:02d}", 9, "bold", ACCENT)
        label(ax, x + 0.049, y, t, 9.2)
    panel(ax, 0.035, 0.30, "c", "Independent tools")
    box(
        ax,
        0.035,
        0.068,
        0.448,
        0.177,
        "CBF zero-value repair",
        "Target mask → write → verify\nConfigured zeros; not saturation recovery",
        accent=WARM,
        face="#FCF6EF",
        size=8.8,
    )
    box(
        ax,
        0.515,
        0.068,
        0.448,
        0.177,
        "Ideal planar geometry",
        "Wavelength + detector geometry\nQ, 2θ, radius and d-spacing conversion",
        size=8.8,
    )
    label(
        ax,
        0.035,
        0.025,
        "Preprocessing and QC precede downstream integration or fitting.",
        8.8,
        color=MUTED,
    )
    return fig


def _radial_mean(arr, radius_scale=1.0):
    data = np.asarray(arr, dtype=float)
    yy, xx = np.indices(data.shape, dtype=float)
    r = np.floor(
        np.hypot(xx - (data.shape[1] - 1) / 2, yy - (data.shape[0] - 1) / 2) * radius_scale
    ).astype(int)
    finite = np.isfinite(data)
    sums = np.bincount(r[finite], weights=data[finite])
    counts = np.bincount(r[finite])
    means = np.full(counts.shape, np.nan)
    means[counts > 0] = sums[counts > 0] / counts[counts > 0]
    return np.arange(len(means)) + 0.5, means


def _display_normalize(a):
    return (a - np.nanmin(a)) / (np.nanmax(a) - np.nanmin(a))


def create_synthetic_processing():
    raw = generate_synthetic_detector_image()
    processed = apply_processing(raw, **PROCESSING_OPTIONS)
    qc = analyze_image_quality(
        raw,
        metadata={
            "source_kind": "synthetic",
            "source_name": "synthetic_diffraction_rings",
            "dtype": str(raw.dtype),
        },
        source_name="synthetic_diffraction_rings",
    )
    assert np.isfinite(raw).all() and np.isfinite(processed).all()
    assert qc is not None
    fig = plt.figure(figsize=(7.2, 5.7))
    a = fig.add_axes([0.10, 0.52, 0.31, 0.38])
    b = fig.add_axes([0.59, 0.52, 0.31, 0.38])
    for ax, arr, title, xlab, unit in [
        (a, raw, "a   Raw synthetic image", "Detector", "Intensity (a.u.)"),
        (b, processed, "b   Processed image", "Output", "Normalized value"),
    ]:
        im = ax.imshow(arr, cmap="cividis", origin="upper", interpolation="nearest")
        ax.set_title(title, loc="left", fontweight="bold", pad=12)
        ax.set_xlabel(f"{xlab} x (pixels)")
        ax.set_ylabel(f"{xlab} y (pixels)")
        cb = fig.colorbar(im, ax=ax, fraction=0.047, pad=0.025)
        cb.set_label(unit, fontsize=9)
        cb.ax.tick_params(labelsize=8, length=2)
    c = fig.add_axes([0.10, 0.12, 0.8, 0.245])
    for arr, scale, color, ls, mark, title in [
        (raw, 1.0, ACCENT, "-", "o", "Raw"),
        (processed, float(PROCESSING_OPTIONS.get("bin_factor", 1)), WARM, "--", "s", "Processed"),
    ]:
        r, p = _radial_mean(arr, scale)
        c.plot(
            r,
            _display_normalize(p),
            color=color,
            ls=ls,
            marker=mark,
            markevery=9,
            ms=3,
            label=title,
        )
    c.set_title(
        "c   Radial means · independently normalized for display",
        loc="left",
        fontweight="bold",
        pad=9,
    )
    c.set(xlabel="Radius (input-pixel equivalent)", ylabel="Scaled intensity", ylim=(-0.04, 1.1))
    c.legend(frameon=False, loc="upper right", ncol=2, fontsize=9)
    clean_axes(c)
    fig.text(
        0.10,
        0.025,
        f"Synthetic example · seed {SYNTHETIC_SEED} · 128 × 128 → 64 × 64 pixels",
        fontsize=9,
        color=MUTED,
    )
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--formats", nargs="+", choices=["png", "svg", "pdf"], default=["png", "svg", "pdf"]
    )
    args = parser.parse_args()
    style()
    save(create_architecture_workflow(), args.output_dir, "architecture_workflow", args.formats)
    save(create_synthetic_processing(), args.output_dir, "synthetic_processing", args.formats)


if __name__ == "__main__":
    main()
