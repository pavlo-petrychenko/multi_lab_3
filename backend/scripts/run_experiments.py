"""Generate report material: PSNR table, PSNR chart and visual comparison grid.

Usage (from ``backend/``)::

    uv run python -m scripts.run_experiments --sample cameraman
    uv run python -m scripts.run_experiments --image ~/photo.jpg --levels 4 --out ../reports

Outputs in ``--out`` (default ``../reports``):

* ``experiments.md`` — Markdown table for the lab report;
* ``psnr.png`` — PSNR vs share of kept coefficients, DCT vs DWT at several Haar depths;
* ``comparison.png`` — Original | DCT | DWT for every compression level.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from app.config import DEFAULT_DWT_LEVELS, DEFAULT_KEEP_RATIOS, MAX_DWT_LEVELS
from app.services.comparison import Comparison, run_experiments
from app.services.image_io import decode_grayscale
from app.services.samples import load_sample


def parse_args() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--sample", default="cameraman", help="Bundled sample id (default: cameraman)")
    source.add_argument("--image", type=Path, help="Path to your own image")
    parser.add_argument("--levels", type=int, default=DEFAULT_DWT_LEVELS, help="Haar depth for the table and grid")
    parser.add_argument(
        "--ratios",
        type=float,
        nargs="+",
        default=list(DEFAULT_KEEP_RATIOS),
        help="Shares of kept coefficients, e.g. 0.2 0.1 0.05",
    )
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "reports")
    return parser.parse_args()


def load_image(args: argparse.Namespace) -> tuple[NDArray[np.float64], str]:
    """Load the requested image and return it with a display name."""
    if args.image:
        return decode_grayscale(args.image.expanduser().read_bytes()), args.image.name
    return load_sample(args.sample), args.sample


def format_psnr(value: float) -> str:
    """Format a PSNR value, showing ``∞`` for lossless results."""
    return "∞" if np.isinf(value) else f"{value:.2f}"


def write_table(comparisons: list[Comparison], image_name: str, levels: int, path: Path) -> None:
    """Write the Markdown results table."""
    lines = [
        f"# Experiments — {image_name}",
        "",
        f"512×512 grayscale, DCT 8×8 blocks, Haar DWT with {levels} levels, "
        "global top-k coefficient selection.",
        "Compression ratio = total coefficients / non-zero coefficients (no entropy coding).",
        "",
        "| Kept, % | Kept coefficients | Compression ratio | DCT PSNR, dB | DWT PSNR, dB | Better |",
        "|---:|---:|---:|---:|---:|:---:|",
    ]
    for comparison in comparisons:
        dct, dwt = comparison.dct, comparison.dwt
        better = "DCT" if dct.psnr > dwt.psnr else "DWT" if dwt.psnr > dct.psnr else "="
        lines.append(
            f"| {comparison.keep_ratio * 100:g} | {dct.kept:,} / {dct.total:,} | {dct.compression_ratio:.1f}:1 "
            f"| {format_psnr(dct.psnr)} | {format_psnr(dwt.psnr)} | {better} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_psnr(image: NDArray[np.float64], ratios: list[float], path: Path) -> None:
    """Plot PSNR vs kept share for DCT and for Haar at every depth."""
    figure, axes = plt.subplots(figsize=(8, 5))
    percents = sorted((ratio * 100 for ratio in ratios), reverse=True)
    for levels in range(1, MAX_DWT_LEVELS + 1):
        comparisons = run_experiments(image, ratios, levels)
        if levels == 1:
            axes.plot(percents, [c.dct.psnr for c in comparisons], "o-", color="black", linewidth=2, label="DCT 8×8")
        axes.plot(percents, [c.dwt.psnr for c in comparisons], "s--", label=f"Haar DWT, {levels} level(s)")
    axes.set_xscale("log")
    axes.set_xticks(percents, [f"{percent:g}" for percent in percents])
    axes.minorticks_off()
    axes.invert_xaxis()
    axes.set_xlabel("Kept coefficients, % (log scale)")
    axes.set_ylabel("PSNR, dB")
    axes.set_title("Quality vs compression")
    axes.grid(True, which="both", alpha=0.3)
    axes.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def plot_grid(image: NDArray[np.float64], comparisons: list[Comparison], path: Path) -> None:
    """Save an Original | DCT | DWT grid with one row per compression level."""
    figure, axes = plt.subplots(len(comparisons), 3, figsize=(9, 3 * len(comparisons)), squeeze=False)
    for row, comparison in zip(axes, comparisons, strict=True):
        panels = (
            ("Original", image),
            (f"DCT — {format_psnr(comparison.dct.psnr)} dB", comparison.dct.reconstruction),
            (f"DWT — {format_psnr(comparison.dwt.psnr)} dB", comparison.dwt.reconstruction),
        )
        for axis, (title, pixels) in zip(row, panels, strict=True):
            axis.imshow(pixels, cmap="gray", vmin=0, vmax=255)
            axis.set_title(f"{title}\nkept {comparison.keep_ratio * 100:g}%", fontsize=9)
            axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=110)
    plt.close(figure)


def main() -> None:
    """Run the sweep and write all report files."""
    args = parse_args()
    image, image_name = load_image(args)
    args.out.mkdir(parents=True, exist_ok=True)

    comparisons = run_experiments(image, args.ratios, args.levels)
    write_table(comparisons, image_name, args.levels, args.out / "experiments.md")
    plot_psnr(image, args.ratios, args.out / "psnr.png")
    plot_grid(image, comparisons, args.out / "comparison.png")
    print((args.out / "experiments.md").read_text(encoding="utf-8"))
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
