"""Tests for the Haar wavelet transform."""

import numpy as np
import pytest

from app.core.haar import forward_haar2d, haar2d_level, haar_step, inverse_haar2d, inverse_haar_step

S = np.sqrt(2)


def test_haar_step_known_values():
    np.testing.assert_allclose(haar_step(np.array([1.0, 3.0, 6.0, 8.0])), [4 / S, 14 / S, -2 / S, -2 / S])


def test_haar_step_round_trip():
    signal = np.random.default_rng(0).uniform(0, 255, 64)
    np.testing.assert_allclose(inverse_haar_step(haar_step(signal)), signal, atol=1e-12)


def test_2d_level_sub_bands_of_known_block():
    block = np.array([[1.0, 2.0], [3.0, 4.0]])
    coefficients = haar2d_level(block)
    np.testing.assert_allclose(coefficients, [[5.0, -1.0], [-2.0, 0.0]], atol=1e-12)


def test_constant_image_has_energy_only_in_ll():
    coefficients = forward_haar2d(np.full((16, 16), 10.0), levels=2)
    assert coefficients[:4, :4] == pytest.approx(np.full((4, 4), 40.0))
    coefficients[:4, :4] = 0
    np.testing.assert_allclose(coefficients, 0, atol=1e-12)


@pytest.mark.parametrize("levels", [1, 2, 3, 5])
def test_multi_level_round_trip(levels):
    image = np.random.default_rng(levels).uniform(0, 255, (64, 96))
    np.testing.assert_allclose(inverse_haar2d(forward_haar2d(image, levels), levels), image, atol=1e-9)


def test_transform_preserves_energy():
    image = np.random.default_rng(7).uniform(0, 255, (64, 64))
    coefficients = forward_haar2d(image, levels=3)
    assert np.sum(coefficients**2) == pytest.approx(np.sum(image**2))


def test_rejects_size_not_divisible_by_power_of_two():
    with pytest.raises(ValueError):
        forward_haar2d(np.zeros((24, 24)), levels=4)
