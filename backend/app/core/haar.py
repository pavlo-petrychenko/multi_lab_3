"""Two-dimensional multi-level Haar wavelet transform (DWT).

One Haar step replaces every pair of neighbouring samples ``(x0, x1)`` with

* an approximation ``a = (x0 + x1) / √2`` (scaled average), and
* a detail ``d = (x0 − x1) / √2`` (scaled difference).

Applying the step to all rows and then all columns splits the image into four
sub-bands::

    +------+------+
    |  LL  |  HL  |      LL: half-size approximation of the image
    +------+------+      HL: vertical edges     (rows: high, columns: low)
    |  LH  |  HH  |      LH: horizontal edges   (rows: low,  columns: high)
    +------+------+      HH: diagonal detail

Multi-level decomposition repeats the 2-D step on the ``LL`` quadrant only.
The ``1/√2`` factor makes the transform orthonormal: it keeps the signal energy,
so coefficient magnitudes are directly comparable with the DCT ones.
"""

import numpy as np
from numpy.typing import NDArray

SQRT2 = np.sqrt(2.0)


def haar_step(signal: NDArray[np.float64]) -> NDArray[np.float64]:
    """One level of the 1-D Haar transform along the last axis.

    Args:
        signal: Array whose last dimension has even length ``n``.

    Returns:
        Array of the same shape: the first ``n / 2`` values along the last axis are
        approximations, the remaining ``n / 2`` are details.

    Example:
        ``haar_step([1, 3, 6, 8]) == [4/√2, 14/√2, −2/√2, −2/√2]``
    """
    even = signal[..., 0::2]
    odd = signal[..., 1::2]
    return np.concatenate(((even + odd) / SQRT2, (even - odd) / SQRT2), axis=-1)


def inverse_haar_step(coefficients: NDArray[np.float64]) -> NDArray[np.float64]:
    """Undo :func:`haar_step` along the last axis.

    From ``a = (x0 + x1)/√2`` and ``d = (x0 − x1)/√2`` it follows that
    ``x0 = (a + d)/√2`` and ``x1 = (a − d)/√2``.

    Args:
        coefficients: Array laid out as ``[approximations | details]`` along the last axis.

    Returns:
        Reconstructed signal with samples interleaved back into their original order.
    """
    half = coefficients.shape[-1] // 2
    approximation = coefficients[..., :half]
    detail = coefficients[..., half:]
    signal = np.empty_like(coefficients)
    signal[..., 0::2] = (approximation + detail) / SQRT2
    signal[..., 1::2] = (approximation - detail) / SQRT2
    return signal


def haar2d_level(image: NDArray[np.float64]) -> NDArray[np.float64]:
    """One level of the 2-D Haar transform: rows first, then columns.

    Args:
        image: 2-D array with even height and width.

    Returns:
        Array of the same shape arranged as ``[[LL, HL], [LH, HH]]``.
    """
    rows_transformed = haar_step(image)
    return haar_step(rows_transformed.T).T


def inverse_haar2d_level(coefficients: NDArray[np.float64]) -> NDArray[np.float64]:
    """Undo :func:`haar2d_level`: columns first, then rows (reverse order).

    Args:
        coefficients: 2-D array arranged as ``[[LL, HL], [LH, HH]]``.

    Returns:
        Reconstructed 2-D array.
    """
    columns_restored = inverse_haar_step(coefficients.T).T
    return inverse_haar_step(columns_restored)


def forward_haar2d(image: NDArray[np.float64], levels: int) -> NDArray[np.float64]:
    """Multi-level 2-D Haar decomposition.

    Level 1 transforms the whole image; every next level transforms only the
    current ``LL`` quadrant (top-left), producing the classic pyramid mosaic.

    Args:
        image: 2-D image whose sides are divisible by ``2 ** levels``.
        levels: Number of decomposition levels (≥ 1).

    Returns:
        Coefficient image of the same shape.

    Raises:
        ValueError: If ``levels`` < 1 or the image size is not divisible by ``2 ** levels``.
    """
    _validate(image.shape, levels)
    coefficients = image.astype(np.float64, copy=True)
    height, width = coefficients.shape
    for _ in range(levels):
        coefficients[:height, :width] = haar2d_level(coefficients[:height, :width])
        height, width = height // 2, width // 2
    return coefficients


def inverse_haar2d(coefficients: NDArray[np.float64], levels: int) -> NDArray[np.float64]:
    """Reconstruct an image from its multi-level Haar decomposition.

    Levels are undone in reverse order: starting from the smallest ``LL`` corner
    and growing back to the full image.

    Args:
        coefficients: Output of :func:`forward_haar2d` (possibly with dropped coefficients).
        levels: Number of levels used in the forward transform.

    Returns:
        Reconstructed 2-D image (floating point, not yet clipped to 0..255).
    """
    _validate(coefficients.shape, levels)
    image = coefficients.astype(np.float64, copy=True)
    height = coefficients.shape[0] >> (levels - 1)
    width = coefficients.shape[1] >> (levels - 1)
    for _ in range(levels):
        image[:height, :width] = inverse_haar2d_level(image[:height, :width])
        height, width = height * 2, width * 2
    return image


def _validate(shape: tuple[int, ...], levels: int) -> None:
    """Check that a 2-D array of ``shape`` can be decomposed ``levels`` times.

    Raises:
        ValueError: If the input cannot be decomposed.
    """
    if len(shape) != 2:
        raise ValueError(f"Expected a 2-D image, got shape {shape}")
    if levels < 1:
        raise ValueError(f"Number of levels must be >= 1, got {levels}")
    factor = 2**levels
    if shape[0] % factor or shape[1] % factor:
        raise ValueError(f"Image size {shape[0]}x{shape[1]} is not divisible by 2^{levels}={factor}")
