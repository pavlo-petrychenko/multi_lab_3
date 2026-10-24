"""Pydantic models describing the JSON returned by the API."""

from pydantic import BaseModel, Field


class SampleInfo(BaseModel):
    """A bundled sample image the user can pick instead of uploading."""

    id: str
    name: str
    thumbnail: str = Field(description="PNG data URL of the prepared grayscale image")


class MethodMetrics(BaseModel):
    """Size and quality numbers of one compression result."""

    kept: int = Field(description="Number of non-zero coefficients after compression")
    total: int = Field(description="Total number of coefficients")
    kept_ratio: float = Field(description="kept / total, between 0 and 1")
    psnr: float | None = Field(description="PSNR in dB; null means identical images (infinite PSNR)")
    compression_ratio: float | None = Field(description="total / kept; null when nothing was kept")


class MethodResult(MethodMetrics):
    """One method's output in the comparison view."""

    image: str = Field(description="PNG data URL of the reconstruction")
    coefficients: str = Field(description="PNG data URL of the log-magnitude coefficient map")
    error: str = Field(description="PNG data URL of the amplified absolute error")


class CompareResponse(BaseModel):
    """Original | DCT | DWT for one compression level."""

    original: str = Field(description="PNG data URL of the prepared grayscale input")
    width: int
    height: int
    keep_ratio: float
    dwt_levels: int
    dct: MethodResult
    dwt: MethodResult


class ExperimentMethodResult(MethodMetrics):
    """One method's output in a single experiment row."""

    image: str = Field(description="PNG data URL of the reconstruction")


class ExperimentLevel(BaseModel):
    """DCT and DWT results at one compression level."""

    keep_ratio: float
    dct: ExperimentMethodResult
    dwt: ExperimentMethodResult


class ExperimentsResponse(BaseModel):
    """Results of the multi-level experiment sweep."""

    original: str = Field(description="PNG data URL of the prepared grayscale input")
    dwt_levels: int
    levels: list[ExperimentLevel]
