"""Generate the figures and numbers used in the lab report (``report/звіт.md``).

Usage (from ``backend/``)::

    uv run python -m scripts.report_figures

Outputs in ``../report/figures``:

* ``dct_basis.png`` — the 64 basis images of the 8×8 DCT;
* ``haar_pyramid.png`` — the image and its 3-level Haar mosaic with sub-band labels;
* ``psnr.png`` — PSNR vs share of kept coefficients (DCT and Haar 1/3/5 levels);
* ``comparison.png`` — zoomed Original | DCT | DWT at several compression levels.

The PSNR table for every method and level is printed to stdout.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from app.core.compression import keep_largest
from app.core.dct import dct_matrix, forward_dct_blockwise
from app.core.haar import forward_haar2d
from app.services.comparison import compare
from app.services.compressors import DctCompressor, HaarCompressor, compress
from app.services.samples import load_sample
from app.services.visualize import coefficient_map

OUT_DIR = Path(__file__).resolve().parents[2] / "report" / "figures"
KEEP_RATIOS = (0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005)
HAAR_DEPTHS = (1, 3, 5)
GRID_RATIOS = (0.1, 0.05, 0.02)
CROP = (slice(60, 316), slice(130, 386))

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "mathtext.fontset": "stix"})


def plot_dct_basis(path: Path) -> None:
    """Draw every basis image ``T[u]ᵀ · T[v]`` of the 8×8 DCT in an 8×8 grid."""
    matrix = dct_matrix(8)
    figure, axes = plt.subplots(8, 8, figsize=(4.2, 4.2))
    for u in range(8):
        for v in range(8):
            axes[u, v].imshow(np.outer(matrix[u], matrix[v]), cmap="gray", vmin=-0.25, vmax=0.25)
            axes[u, v].set_xticks([])
            axes[u, v].set_yticks([])
    figure.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.08, hspace=0.08)
    figure.savefig(path, dpi=200)
    plt.close(figure)


def plot_haar_pyramid(image: NDArray[np.float64], path: Path) -> None:
    """Draw the 3-level Haar mosaic of the image with every sub-band labelled."""
    mosaic = coefficient_map(forward_haar2d(image, 3))
    size = image.shape[0]
    figure, axis = plt.subplots(figsize=(4, 4))
    axis.imshow(mosaic, cmap="gray")
    for level in range(1, 4):
        half = size >> level
        axis.axhline(half - 0.5, xmax=2 * half / size, color="#e8a33d", linewidth=1)
        axis.axvline(half - 0.5, ymin=1 - 2 * half / size, color="#e8a33d", linewidth=1)
        for name, (x, y) in {"HL": (1.5, 0.5), "LH": (0.5, 1.5), "HH": (1.5, 1.5)}.items():
            axis.text(x * half, y * half, f"{name}{level}", color="#e8a33d", ha="center", va="center",
                      fontsize=16 - 3 * level, fontweight="bold")
    axis.text(size >> 4, size >> 4, "LL3", color="#e8a33d", ha="center", va="center", fontsize=7, fontweight="bold")
    axis.axis("off")
    figure.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    figure.savefig(path, dpi=200)
    plt.close(figure)


def psnr_table(image: NDArray[np.float64]) -> dict[str, list[float]]:
    """Compute PSNR for DCT and every Haar depth at every compression level."""
    table = {"DCT 8×8": [compress(DctCompressor(), image, ratio).psnr for ratio in KEEP_RATIOS]}
    for levels in HAAR_DEPTHS:
        table[f"Хаар, {levels} рівн."] = [compress(HaarCompressor(levels), image, ratio).psnr for ratio in KEEP_RATIOS]
    return table


def plot_psnr(table: dict[str, list[float]], path: Path) -> None:
    """Plot PSNR against the kept share on a logarithmic axis."""
    percents = [ratio * 100 for ratio in KEEP_RATIOS]
    figure, axes = plt.subplots(figsize=(7, 4))
    styles = [("o-", "black"), ("s--", "#c0392b"), ("s--", "#2e86c1"), ("s--", "#27ae60")]
    for (name, values), (marker, color) in zip(table.items(), styles, strict=True):
        axes.plot(percents, values, marker, color=color, linewidth=1.8, label=name)
    axes.set_xscale("log")
    axes.set_xticks(percents, [f"{percent:g}" for percent in percents])
    axes.minorticks_off()
    axes.invert_xaxis()
    axes.set_xlabel("Частка збережених коефіцієнтів, % (логарифмічна шкала)")
    axes.set_ylabel("PSNR, дБ")
    axes.grid(True, alpha=0.3)
    axes.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)


def plot_comparison(image: NDArray[np.float64], path: Path) -> None:
    """Save a zoomed grid: the original, then DCT and DWT (3 levels) at every level of ``GRID_RATIOS``."""
    figure, axes = plt.subplots(2, len(GRID_RATIOS) + 1, figsize=(10, 5.4))
    for axis, title in zip(axes[:, 0], ("Оригінал", "Оригінал"), strict=True):
        axis.imshow(image[CROP], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        axis.set_title(title, fontsize=15)
    for column, ratio in enumerate(GRID_RATIOS, start=1):
        result = compare(image, ratio, 3)
        for axis, (name, method) in zip(axes[:, column], (("DCT", result.dct), ("DWT", result.dwt)), strict=True):
            axis.imshow(method.reconstruction[CROP], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
            axis.set_title(f"{name}, {ratio * 100:g} %: {method.psnr:.2f} дБ", fontsize=15)
    for axis in axes.flat:
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)


def energy_share(coefficients: NDArray[np.float64], keep_ratio: float) -> float:
    """Share of total energy held by the ``keep_ratio`` largest coefficients."""
    kept = keep_largest(coefficients, keep_ratio).values
    return float(np.sum(kept**2) / np.sum(coefficients**2))


def main() -> None:
    """Generate every figure and print the numbers quoted in the report."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = load_sample("cameraman")

    plot_dct_basis(OUT_DIR / "dct_basis.png")
    plot_haar_pyramid(image, OUT_DIR / "haar_pyramid.png")
    table = psnr_table(image)
    plot_psnr(table, OUT_DIR / "psnr.png")
    plot_comparison(image, OUT_DIR / "comparison.png")

    print("keep%", *(f"{ratio * 100:g}" for ratio in KEEP_RATIOS), sep="\t")
    for name, values in table.items():
        print(name, *(f"{value:.2f}" for value in values), sep="\t")
    for name, coefficients in (
        ("pixels", image),
        ("dct", forward_dct_blockwise(image)),
        ("haar3", forward_haar2d(image, 3)),
    ):
        print(f"energy in top 5% ({name}): {energy_share(coefficients, 0.05) * 100:.2f}%")
    print(f"Saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
