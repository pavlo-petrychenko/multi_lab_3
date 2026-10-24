"""Splitting an image into square blocks and assembling it back."""

import numpy as np
from numpy.typing import NDArray


def split_into_blocks(image: NDArray[np.float64], block_size: int) -> NDArray[np.float64]:
    """Cut a 2-D image into non-overlapping square blocks.

    The result is a 4-D view where ``blocks[r, c]`` is the ``block_size × block_size``
    block located in block-row ``r`` and block-column ``c``. Keeping the blocks in a
    single array lets the transforms process all of them in one vectorised step.

    Args:
        image: 2-D array whose height and width are multiples of ``block_size``.
        block_size: Side length of a block in pixels (8 for JPEG-style DCT).

    Returns:
        Array of shape ``(height // block_size, width // block_size, block_size, block_size)``.

    Raises:
        ValueError: If the image is not 2-D or its sides are not divisible by ``block_size``.
    """
    if image.ndim != 2:
        raise ValueError(f"Expected a 2-D image, got shape {image.shape}")
    height, width = image.shape
    if height % block_size or width % block_size:
        raise ValueError(f"Image size {height}x{width} is not divisible by block size {block_size}")
    return image.reshape(height // block_size, block_size, width // block_size, block_size).swapaxes(1, 2)


def merge_blocks(blocks: NDArray[np.float64]) -> NDArray[np.float64]:
    """Assemble blocks produced by :func:`split_into_blocks` back into a 2-D image.

    Args:
        blocks: Array of shape ``(block_rows, block_cols, block_size, block_size)``.

    Returns:
        2-D array of shape ``(block_rows * block_size, block_cols * block_size)``.
    """
    block_rows, block_cols, block_size, _ = blocks.shape
    return blocks.swapaxes(1, 2).reshape(block_rows * block_size, block_cols * block_size)
