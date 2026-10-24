"""API endpoints. Each handler only parses input, calls a service and presents the result."""

from typing import Annotated

import numpy as np
from fastapi import APIRouter, Depends, Form
from numpy.typing import NDArray
from pydantic import Field

from app.api.dependencies import source_image
from app.api.presenters import present_comparison, present_experiments
from app.api.schemas import CompareResponse, ExperimentsResponse, SampleInfo
from app.config import DEFAULT_DWT_LEVELS, DEFAULT_KEEP_RATIOS, MAX_DWT_LEVELS
from app.services.comparison import compare, run_experiments
from app.services.image_io import encode_png_data_url, to_pixels
from app.services.samples import SAMPLES, load_sample

router = APIRouter(prefix="/api")

SourceImage = Annotated[NDArray[np.float64], Depends(source_image)]
KeepRatio = Annotated[float, Form(gt=0, le=1, description="Share of coefficients to keep, (0, 1]")]
KeepRatioItem = Annotated[float, Field(gt=0, le=1)]
DwtLevels = Annotated[int, Form(ge=1, le=MAX_DWT_LEVELS, description="Haar decomposition depth")]


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker."""
    return {"status": "ok"}


@router.get("/samples", response_model=list[SampleInfo])
def list_samples() -> list[SampleInfo]:
    """List bundled sample images with thumbnails."""
    return [
        SampleInfo(id=sample.id, name=sample.name, thumbnail=encode_png_data_url(to_pixels(load_sample(sample.id))))
        for sample in SAMPLES
    ]


@router.post("/compress", response_model=CompareResponse)
def compress_image(
    image: SourceImage,
    keep_ratio: KeepRatio,
    dwt_levels: DwtLevels = DEFAULT_DWT_LEVELS,
) -> CompareResponse:
    """Compress the image with DCT and DWT at the same level and return Original | DCT | DWT."""
    comparison = compare(image, keep_ratio, dwt_levels)
    return present_comparison(image, comparison, dwt_levels)


@router.post("/experiments", response_model=ExperimentsResponse)
def experiments(
    image: SourceImage,
    keep_ratios: Annotated[list[KeepRatioItem], Form(description="Compression levels to test")] = list(
        DEFAULT_KEEP_RATIOS
    ),
    dwt_levels: DwtLevels = DEFAULT_DWT_LEVELS,
) -> ExperimentsResponse:
    """Run both methods at several compression levels for the report table and chart."""
    comparisons = run_experiments(image, keep_ratios, dwt_levels)
    return present_experiments(image, comparisons, dwt_levels)
