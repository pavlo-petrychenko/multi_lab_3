"""Lossy step: keep only the largest-magnitude transform coefficients."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class SparseCoefficients:
    """Coefficients after compression, with bookkeeping for metrics.

    Attributes:
        values: Coefficient array of the original shape; dropped coefficients are 0.
        kept: Number of non-zero coefficients that survived.
        total: Total number of coefficients.
    """

    values: NDArray[np.float64]
    kept: int
    total: int

    @property
    def kept_ratio(self) -> float:
        """Fraction of coefficients that are still non-zero (0..1)."""
        return self.kept / self.total


def keep_largest(coefficients: NDArray[np.float64], keep_ratio: float) -> SparseCoefficients:
    """Zero out all coefficients except the ``keep_ratio`` share with the largest magnitude.

    Transforms such as DCT and DWT concentrate the image energy in a few large
    coefficients, so dropping the small ones loses little visible information.
    The selection is global: it compares coefficients across the whole image, and
    the same rule is used for both methods, which makes them comparable at an
    equal coefficient budget.

    Args:
        coefficients: Transform coefficients of any shape.
        keep_ratio: Share of coefficients to keep, in ``(0, 1]``. ``1`` means lossless.

    Returns:
        :class:`SparseCoefficients` with the filtered values and counts.

    Raises:
        ValueError: If ``keep_ratio`` is outside ``(0, 1]``.
    """
    if not 0 < keep_ratio <= 1:
        raise ValueError(f"keep_ratio must be in (0, 1], got {keep_ratio}")

    total = coefficients.size
    keep_count = max(1, round(total * keep_ratio))
    if keep_count >= total:
        values = coefficients.astype(np.float64, copy=True)
    else:
        magnitudes = np.abs(coefficients).ravel()
        largest = np.argpartition(magnitudes, total - keep_count)[total - keep_count :]
        mask = np.zeros(total, dtype=bool)
        mask[largest] = True
        values = np.where(mask.reshape(coefficients.shape), coefficients, 0.0)

    return SparseCoefficients(values=values, kept=int(np.count_nonzero(values)), total=total)
