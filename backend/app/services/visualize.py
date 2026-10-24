"""Turning coefficients and errors into viewable 8-bit images."""

import numpy as np
from numpy.typing import NDArray

ERROR_GAIN = 5.0
"""Multiplier applied to absolute errors so small differences become visible."""


def coefficient_map(coefficients: NDArray[np.float64]) -> NDArray[np.uint8]:
    """Render coefficient magnitudes on a logarithmic scale.

    Coefficient magnitudes span several orders of magnitude (a DC term can be
    ~2000 while most details are below 1), so ``log(1 + |c|)`` is used and
    normalised to ``0..255``. Black pixels are zeroed coefficients.

    Args:
        coefficients: Coefficient image (DCT blocks or Haar mosaic).

    Returns:
        ``uint8`` visualisation of the same shape.
    """
    magnitude = np.log1p(np.abs(coefficients))
    peak = magnitude.max()
    if peak == 0:
        return np.zeros(coefficients.shape, dtype=np.uint8)
    return np.rint(magnitude / peak * 255).astype(np.uint8)


def error_map(original: NDArray[np.float64], reconstruction: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Render ``|original − reconstruction|`` amplified by :data:`ERROR_GAIN`.

    A fixed gain (instead of per-image normalisation) keeps error maps of
    different methods visually comparable.

    Args:
        original: Reference image.
        reconstruction: Decoded image.

    Returns:
        ``uint8`` image where brighter means larger error.
    """
    difference = np.abs(original.astype(np.float64) - reconstruction.astype(np.float64))
    return np.clip(difference * ERROR_GAIN, 0, 255).astype(np.uint8)
