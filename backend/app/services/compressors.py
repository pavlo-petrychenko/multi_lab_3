"""Transform-coding pipeline shared by DCT and DWT.

Every method follows the same three steps::

    image ──forward──► coefficients ──keep_largest──► sparse coefficients ──inverse──► reconstruction

Only the transform differs, so each method is a small :class:`Compressor`
and :func:`compress` runs the common pipeline.
"""

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from app.config import DCT_BLOCK_SIZE, DEFAULT_DWT_LEVELS
from app.core.compression import keep_largest
from app.core.dct import forward_dct_blockwise, inverse_dct_blockwise
from app.core.haar import forward_haar2d, inverse_haar2d
from app.core.metrics import compression_ratio, psnr
from app.services.image_io import to_pixels


class Compressor(Protocol):
    """A reversible transform used for transform coding."""

    name: str
    """Short identifier of the method (``"dct"`` or ``"dwt"``)."""

    def forward(self, image: NDArray[np.float64]) -> NDArray[np.float64]:
        """Transform an image into coefficients of the same shape."""
        ...

    def inverse(self, coefficients: NDArray[np.float64]) -> NDArray[np.float64]:
        """Reconstruct an image from (possibly sparsified) coefficients."""
        ...


@dataclass(frozen=True)
class DctCompressor:
    """Blockwise 2-D DCT (JPEG-style 8×8 blocks)."""

    block_size: int = DCT_BLOCK_SIZE
    name: str = "dct"

    def forward(self, image: NDArray[np.float64]) -> NDArray[np.float64]:
        """Blockwise forward DCT, see :func:`app.core.dct.forward_dct_blockwise`."""
        return forward_dct_blockwise(image, self.block_size)

    def inverse(self, coefficients: NDArray[np.float64]) -> NDArray[np.float64]:
        """Blockwise inverse DCT, see :func:`app.core.dct.inverse_dct_blockwise`."""
        return inverse_dct_blockwise(coefficients, self.block_size)


@dataclass(frozen=True)
class HaarCompressor:
    """Multi-level 2-D Haar wavelet transform over the whole image."""

    levels: int = DEFAULT_DWT_LEVELS
    name: str = "dwt"

    def forward(self, image: NDArray[np.float64]) -> NDArray[np.float64]:
        """Forward Haar DWT, see :func:`app.core.haar.forward_haar2d`."""
        return forward_haar2d(image, self.levels)

    def inverse(self, coefficients: NDArray[np.float64]) -> NDArray[np.float64]:
        """Inverse Haar DWT, see :func:`app.core.haar.inverse_haar2d`."""
        return inverse_haar2d(coefficients, self.levels)


@dataclass(frozen=True)
class CompressionResult:
    """Outcome of compressing one image with one method at one level.

    Attributes:
        method: Name of the compressor.
        keep_ratio: Requested share of kept coefficients.
        coefficients: Sparse coefficients that were actually used for reconstruction.
        reconstruction: Decoded 8-bit image.
        kept: Number of non-zero coefficients.
        total: Total number of coefficients.
        psnr: Quality in dB (``inf`` when lossless).
        compression_ratio: ``total / kept``.
    """

    method: str
    keep_ratio: float
    coefficients: NDArray[np.float64]
    reconstruction: NDArray[np.uint8]
    kept: int
    total: int
    psnr: float
    compression_ratio: float

    @property
    def kept_ratio(self) -> float:
        """Actual share of non-zero coefficients (0..1)."""
        return self.kept / self.total


def compress(compressor: Compressor, image: NDArray[np.float64], keep_ratio: float) -> CompressionResult:
    """Run the full transform-coding pipeline and measure the result.

    Args:
        compressor: Transform to use.
        image: Grayscale image with values in ``0..255``.
        keep_ratio: Share of largest coefficients to keep, in ``(0, 1]``.

    Returns:
        Reconstruction together with quality and size metrics.
    """
    sparse = keep_largest(compressor.forward(image), keep_ratio)
    reconstruction = to_pixels(compressor.inverse(sparse.values))
    return CompressionResult(
        method=compressor.name,
        keep_ratio=keep_ratio,
        coefficients=sparse.values,
        reconstruction=reconstruction,
        kept=sparse.kept,
        total=sparse.total,
        psnr=psnr(image, reconstruction),
        compression_ratio=compression_ratio(sparse.total, sparse.kept),
    )
