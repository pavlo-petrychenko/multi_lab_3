"""Mapping of service-layer results to API response schemas."""

import math

import numpy as np
from numpy.typing import NDArray

from app.api.schemas import (
    CompareResponse,
    ExperimentLevel,
    ExperimentMethodResult,
    ExperimentsResponse,
    MethodMetrics,
    MethodResult,
)
from app.services.comparison import Comparison
from app.services.compressors import CompressionResult
from app.services.image_io import encode_png_data_url, to_pixels
from app.services.visualize import coefficient_map, error_map


def present_comparison(image: NDArray[np.float64], comparison: Comparison, dwt_levels: int) -> CompareResponse:
    """Build the response of ``POST /api/compress``."""
    height, width = image.shape
    return CompareResponse(
        original=encode_png_data_url(to_pixels(image)),
        width=width,
        height=height,
        keep_ratio=comparison.keep_ratio,
        dwt_levels=dwt_levels,
        dct=_method_result(image, comparison.dct),
        dwt=_method_result(image, comparison.dwt),
    )


def present_experiments(
    image: NDArray[np.float64], comparisons: list[Comparison], dwt_levels: int
) -> ExperimentsResponse:
    """Build the response of ``POST /api/experiments``."""
    return ExperimentsResponse(
        original=encode_png_data_url(to_pixels(image)),
        dwt_levels=dwt_levels,
        levels=[
            ExperimentLevel(
                keep_ratio=comparison.keep_ratio,
                dct=_experiment_result(comparison.dct),
                dwt=_experiment_result(comparison.dwt),
            )
            for comparison in comparisons
        ],
    )


def _metrics(result: CompressionResult) -> MethodMetrics:
    """Extract JSON-safe metrics; infinities become ``None`` because JSON has no ``Infinity``."""
    return MethodMetrics(
        kept=result.kept,
        total=result.total,
        kept_ratio=result.kept_ratio,
        psnr=_finite_or_none(result.psnr),
        compression_ratio=_finite_or_none(result.compression_ratio),
    )


def _method_result(image: NDArray[np.float64], result: CompressionResult) -> MethodResult:
    """Metrics plus reconstruction, coefficient map and error map."""
    return MethodResult(
        **_metrics(result).model_dump(),
        image=encode_png_data_url(result.reconstruction),
        coefficients=encode_png_data_url(coefficient_map(result.coefficients)),
        error=encode_png_data_url(error_map(image, result.reconstruction)),
    )


def _experiment_result(result: CompressionResult) -> ExperimentMethodResult:
    """Metrics plus reconstruction only, to keep sweep responses small."""
    return ExperimentMethodResult(**_metrics(result).model_dump(), image=encode_png_data_url(result.reconstruction))


def _finite_or_none(value: float) -> float | None:
    """Return ``value`` unless it is infinite."""
    return None if math.isinf(value) else value
