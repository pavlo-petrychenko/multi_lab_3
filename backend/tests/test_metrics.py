"""Tests for PSNR and compression ratio."""

import math

import numpy as np
import pytest

from app.core.metrics import compression_ratio, mse, psnr


def test_identical_images_have_infinite_psnr():
    image = np.full((4, 4), 7.0)
    assert math.isinf(psnr(image, image))


def test_psnr_for_known_mse():
    original = np.zeros((10, 10))
    reconstructed = np.full((10, 10), 10.0)
    assert mse(original, reconstructed) == 100.0
    assert psnr(original, reconstructed) == pytest.approx(10 * math.log10(255**2 / 100))


def test_psnr_rejects_shape_mismatch():
    with pytest.raises(ValueError):
        psnr(np.zeros((2, 2)), np.zeros((3, 3)))


def test_compression_ratio():
    assert compression_ratio(1000, 50) == 20
    assert math.isinf(compression_ratio(1000, 0))
