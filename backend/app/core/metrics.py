"""Image quality and compression metrics."""

import math

import numpy as np
from numpy.typing import NDArray

MAX_PIXEL_VALUE = 255.0


def mse(original: NDArray, reconstructed: NDArray) -> float:
    """Mean squared error between two images of the same shape.

    Args:
        original: Reference image.
        reconstructed: Image to compare against the reference.

    Returns:
        Average of squared per-pixel differences.

    Raises:
        ValueError: If the shapes differ.
    """
    if original.shape != reconstructed.shape:
        raise ValueError(f"Shape mismatch: {original.shape} vs {reconstructed.shape}")
    difference = original.astype(np.float64) - reconstructed.astype(np.float64)
    return float(np.mean(difference**2))


def psnr(original: NDArray, reconstructed: NDArray, max_value: float = MAX_PIXEL_VALUE) -> float:
    """Peak signal-to-noise ratio in decibels: ``10 · log10(MAX² / MSE)``.

    Higher is better. Typical lossy images are in the 25–45 dB range;
    above ~40 dB differences are hard to see.

    Args:
        original: Reference image.
        reconstructed: Image to compare against the reference.
        max_value: Largest possible pixel value (255 for 8-bit images).

    Returns:
        PSNR in dB, or ``math.inf`` if the images are identical.
    """
    error = mse(original, reconstructed)
    if error == 0:
        return math.inf
    return 10.0 * math.log10(max_value**2 / error)


def compression_ratio(total: int, kept: int) -> float:
    """Coefficient-count compression ratio: ``total / kept``.

    This counts non-zero coefficients only. A real codec also has to store the
    positions of those coefficients and entropy-code them, so the actual file-size
    ratio would differ.

    Args:
        total: Total number of coefficients.
        kept: Number of non-zero coefficients.

    Returns:
        The ratio, or ``math.inf`` if nothing was kept.
    """
    if kept == 0:
        return math.inf
    return total / kept
