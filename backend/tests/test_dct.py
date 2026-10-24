"""Tests for the matrix-form DCT."""

import numpy as np
import pytest

from app.core.dct import dct2, dct_matrix, forward_dct_blockwise, idct2, inverse_dct_blockwise


def reference_dct2(block: np.ndarray) -> np.ndarray:
    """Textbook double-sum DCT-II definition, used as an independent reference."""
    n = block.shape[0]
    result = np.zeros((n, n))
    for u in range(n):
        for v in range(n):
            alpha_u = np.sqrt(1 / n) if u == 0 else np.sqrt(2 / n)
            alpha_v = np.sqrt(1 / n) if v == 0 else np.sqrt(2 / n)
            total = 0.0
            for x in range(n):
                for y in range(n):
                    total += (
                        block[x, y]
                        * np.cos((2 * x + 1) * u * np.pi / (2 * n))
                        * np.cos((2 * y + 1) * v * np.pi / (2 * n))
                    )
            result[u, v] = alpha_u * alpha_v * total
    return result


def test_dct_matrix_is_orthonormal():
    matrix = dct_matrix(8)
    np.testing.assert_allclose(matrix @ matrix.T, np.eye(8), atol=1e-12)


def test_dct2_matches_textbook_definition():
    block = np.random.default_rng(0).uniform(0, 255, (8, 8))
    np.testing.assert_allclose(dct2(block), reference_dct2(block), atol=1e-9)


def test_constant_block_has_only_dc_coefficient():
    coefficients = dct2(np.full((8, 8), 100.0))
    assert coefficients[0, 0] == pytest.approx(8 * 100.0)
    coefficients[0, 0] = 0
    np.testing.assert_allclose(coefficients, 0, atol=1e-9)


def test_single_block_round_trip():
    block = np.random.default_rng(1).uniform(0, 255, (8, 8))
    np.testing.assert_allclose(idct2(dct2(block)), block, atol=1e-9)


def test_blockwise_matches_per_block_transform():
    image = np.random.default_rng(2).uniform(0, 255, (32, 48))
    coefficients = forward_dct_blockwise(image)
    np.testing.assert_allclose(coefficients[8:16, 16:24], dct2(image[8:16, 16:24]), atol=1e-9)


def test_blockwise_round_trip():
    image = np.random.default_rng(3).uniform(0, 255, (512, 512))
    np.testing.assert_allclose(inverse_dct_blockwise(forward_dct_blockwise(image)), image, atol=1e-9)


def test_rejects_size_not_divisible_by_block():
    with pytest.raises(ValueError):
        forward_dct_blockwise(np.zeros((10, 16)))
