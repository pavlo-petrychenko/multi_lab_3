"""Use cases: side-by-side comparison and multi-level experiment sweep."""

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from app.services.compressors import CompressionResult, DctCompressor, HaarCompressor, compress


@dataclass(frozen=True)
class Comparison:
    """DCT and DWT results for the same image and the same coefficient budget."""

    keep_ratio: float
    dct: CompressionResult
    dwt: CompressionResult


def compare(image: NDArray[np.float64], keep_ratio: float, dwt_levels: int) -> Comparison:
    """Compress one image with both methods at the same ``keep_ratio``.

    Args:
        image: Grayscale image with values in ``0..255``.
        keep_ratio: Share of coefficients to keep, in ``(0, 1]``.
        dwt_levels: Haar decomposition depth.

    Returns:
        Both results, ready to be shown next to the original.
    """
    return Comparison(
        keep_ratio=keep_ratio,
        dct=compress(DctCompressor(), image, keep_ratio),
        dwt=compress(HaarCompressor(levels=dwt_levels), image, keep_ratio),
    )


def run_experiments(image: NDArray[np.float64], keep_ratios: Iterable[float], dwt_levels: int) -> list[Comparison]:
    """Compare both methods at several compression levels.

    Args:
        image: Grayscale image with values in ``0..255``.
        keep_ratios: Compression levels to test; returned from least to most aggressive.
        dwt_levels: Haar decomposition depth.

    Returns:
        One :class:`Comparison` per distinct level, sorted by ``keep_ratio`` descending.
    """
    return [compare(image, ratio, dwt_levels) for ratio in sorted(set(keep_ratios), reverse=True)]
