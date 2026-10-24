"""Application-wide constants and environment-driven settings."""

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

IMAGE_SIZE = 512
"""Side length every input image is cropped and resized to (divisible by 8 and 2^MAX_DWT_LEVELS)."""

DCT_BLOCK_SIZE = 8
"""Block size of the blockwise DCT."""

DEFAULT_DWT_LEVELS = 3
"""Haar decomposition depth used when the client does not specify one."""

MAX_DWT_LEVELS = 5
"""Deepest Haar decomposition the API accepts."""

DEFAULT_KEEP_RATIOS = (0.5, 0.2, 0.1, 0.05, 0.02, 0.01)
"""Compression levels (share of kept coefficients) used by the experiment sweep."""

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
"""Largest accepted upload size."""

SAMPLES_DIR = APP_DIR / "assets" / "samples"
"""Folder with bundled sample images."""

STATIC_DIR = Path(os.environ.get("LAB3_STATIC_DIR", APP_DIR.parent.parent / "frontend" / "dist"))
"""Built React UI served at ``/``; skipped when the folder does not exist (dev mode)."""
