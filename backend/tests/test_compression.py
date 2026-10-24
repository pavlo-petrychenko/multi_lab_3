"""Tests for coefficient selection and the end-to-end compressors."""

import math

import numpy as np
import pytest

from app.core.compression import keep_largest
from app.services.compressors import DctCompressor, HaarCompressor, compress
from app.services.samples import load_sample


def test_keeps_exact_number_of_largest_coefficients():
    coefficients = np.arange(1.0, 101.0).reshape(10, 10)
    sparse = keep_largest(coefficients, 0.1)
    assert sparse.kept == 10
    assert set(sparse.values[sparse.values != 0]) == set(range(91, 101))


def test_selection_uses_magnitude_not_sign():
    sparse = keep_largest(np.array([1.0, -50.0, 3.0, 40.0]), 0.5)
    np.testing.assert_array_equal(sparse.values, [0.0, -50.0, 0.0, 40.0])


def test_full_ratio_is_lossless_copy():
    coefficients = np.random.default_rng(0).normal(size=(8, 8))
    sparse = keep_largest(coefficients, 1.0)
    np.testing.assert_array_equal(sparse.values, coefficients)
    assert sparse.values is not coefficients


@pytest.mark.parametrize("ratio", [0, -0.1, 1.5])
def test_rejects_invalid_ratio(ratio):
    with pytest.raises(ValueError):
        keep_largest(np.ones(4), ratio)


@pytest.mark.parametrize("compressor", [DctCompressor(), HaarCompressor(levels=3)])
def test_lossless_at_full_ratio(compressor):
    image = load_sample("cameraman")
    assert math.isinf(compress(compressor, image, 1.0).psnr)


@pytest.mark.parametrize("compressor", [DctCompressor(), HaarCompressor(levels=3)])
def test_quality_drops_as_fewer_coefficients_are_kept(compressor):
    image = load_sample("cameraman")
    values = [compress(compressor, image, ratio).psnr for ratio in (0.5, 0.1, 0.02)]
    assert values[0] > values[1] > values[2] > 15
