"""Conversion between image files and NumPy arrays."""

import base64
import io

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import IMAGE_SIZE


class InvalidImageError(ValueError):
    """Raised when uploaded bytes cannot be decoded as an image."""


def decode_grayscale(data: bytes, size: int = IMAGE_SIZE) -> NDArray[np.float64]:
    """Decode image bytes into a square grayscale array ready for the transforms.

    The image is converted to 8-bit grayscale (``L`` mode), center-cropped to a
    square and resized to ``size × size``, so its sides are divisible by both the
    DCT block size and ``2 ** levels`` of the Haar transform.

    Args:
        data: Raw bytes of any format Pillow understands (PNG, JPEG, BMP, ...).
        size: Output side length in pixels.

    Returns:
        ``size × size`` float64 array with integer values in ``0..255``.

    Raises:
        InvalidImageError: If the bytes are not a readable image.
    """
    try:
        with Image.open(io.BytesIO(data)) as source:
            grayscale = ImageOps.exif_transpose(source).convert("L")
    except (UnidentifiedImageError, OSError) as error:
        raise InvalidImageError("The uploaded file is not a supported image") from error

    square = ImageOps.fit(grayscale, (size, size), method=Image.Resampling.LANCZOS)
    return np.asarray(square, dtype=np.float64)


def to_pixels(image: NDArray[np.float64]) -> NDArray[np.uint8]:
    """Round and clip a floating-point reconstruction to valid 8-bit pixels.

    Inverse transforms of compressed coefficients can produce values slightly
    outside ``0..255`` or between integers; a real decoder would do the same.

    Args:
        image: Floating-point image.

    Returns:
        ``uint8`` image.
    """
    return np.clip(np.rint(image), 0, 255).astype(np.uint8)


def encode_png_data_url(pixels: NDArray[np.uint8]) -> str:
    """Encode an 8-bit grayscale image as a ``data:image/png;base64,...`` URL.

    Args:
        pixels: 2-D ``uint8`` array.

    Returns:
        Data URL that a browser can display directly in ``<img src>``.
    """
    buffer = io.BytesIO()
    Image.fromarray(pixels, mode="L").save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
