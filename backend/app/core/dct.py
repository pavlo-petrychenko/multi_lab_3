"""Two-dimensional Discrete Cosine Transform (DCT-II) in matrix form.

For an ``N × N`` block ``B`` the 2-D DCT is ``C = T · B · Tᵀ``, where ``T`` is the
orthonormal DCT basis matrix. Because ``T`` is orthonormal, ``T⁻¹ = Tᵀ`` and the
inverse transform is ``B = Tᵀ · C · T``.

The image is processed in independent 8×8 blocks, like in JPEG.
"""

from functools import cache

import numpy as np
from numpy.typing import NDArray

from app.core.blocks import merge_blocks, split_into_blocks

DEFAULT_BLOCK_SIZE = 8


@cache
def dct_matrix(size: int = DEFAULT_BLOCK_SIZE) -> NDArray[np.float64]:
    """Build the orthonormal DCT-II basis matrix ``T``.

    Row ``u`` of the matrix is a sampled cosine of frequency ``u``::

        T[0, x] = sqrt(1 / N)
        T[u, x] = sqrt(2 / N) · cos((2x + 1) · u · π / (2N)),   u > 0

    Row 0 is constant (the average, "DC"); higher rows oscillate faster and
    capture finer detail. The result is cached and read-only.

    Args:
        size: Matrix size ``N`` (block side length).

    Returns:
        ``N × N`` matrix with orthonormal rows, so ``T @ T.T == I``.
    """
    frequencies = np.arange(size).reshape(-1, 1)
    positions = np.arange(size).reshape(1, -1)
    matrix = np.sqrt(2.0 / size) * np.cos((2 * positions + 1) * frequencies * np.pi / (2 * size))
    matrix[0, :] = np.sqrt(1.0 / size)
    matrix.setflags(write=False)
    return matrix


def dct2(block: NDArray[np.float64]) -> NDArray[np.float64]:
    """Forward 2-D DCT of a single square block: ``C = T · B · Tᵀ``.

    Multiplying by ``T`` on the left transforms every column, multiplying by
    ``Tᵀ`` on the right transforms every row.

    Args:
        block: Square ``N × N`` block of pixel values.

    Returns:
        ``N × N`` coefficients; ``C[0, 0]`` is the DC term, frequency grows to the
        bottom-right.
    """
    matrix = dct_matrix(block.shape[0])
    return matrix @ block @ matrix.T


def idct2(coefficients: NDArray[np.float64]) -> NDArray[np.float64]:
    """Inverse 2-D DCT of a single square block: ``B = Tᵀ · C · T``.

    Args:
        coefficients: ``N × N`` DCT coefficients.

    Returns:
        Reconstructed ``N × N`` block of pixel values.
    """
    matrix = dct_matrix(coefficients.shape[0])
    return matrix.T @ coefficients @ matrix


def forward_dct_blockwise(image: NDArray[np.float64], block_size: int = DEFAULT_BLOCK_SIZE) -> NDArray[np.float64]:
    """Apply :func:`dct2` to every ``block_size × block_size`` block of an image.

    All blocks are transformed at once: ``T @ blocks @ T.T`` broadcasts the matrix
    product over the leading block-grid dimensions.

    Args:
        image: 2-D grayscale image with sides divisible by ``block_size``.
        block_size: Block side length.

    Returns:
        Coefficient image of the same shape; each block holds the DCT coefficients
        of the corresponding image block.
    """
    matrix = dct_matrix(block_size)
    blocks = split_into_blocks(image.astype(np.float64), block_size)
    return merge_blocks(matrix @ blocks @ matrix.T)


def inverse_dct_blockwise(
    coefficients: NDArray[np.float64], block_size: int = DEFAULT_BLOCK_SIZE
) -> NDArray[np.float64]:
    """Apply :func:`idct2` to every block of a coefficient image.

    Args:
        coefficients: Coefficient image produced by :func:`forward_dct_blockwise`.
        block_size: Block side length used in the forward transform.

    Returns:
        Reconstructed 2-D image (floating point, not yet clipped to 0..255).
    """
    matrix = dct_matrix(block_size)
    blocks = split_into_blocks(coefficients, block_size)
    return merge_blocks(matrix.T @ blocks @ matrix)
