"""Registry of bundled sample images."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from app.config import SAMPLES_DIR
from app.services.image_io import decode_grayscale


@dataclass(frozen=True)
class Sample:
    """A bundled test image.

    Attributes:
        id: Stable identifier used by the API.
        name: Human-readable title.
        filename: File inside :data:`app.config.SAMPLES_DIR`.
    """

    id: str
    name: str
    filename: str


SAMPLES: tuple[Sample, ...] = (
    Sample(id="cameraman", name="Cameraman", filename="cameraman.png"),
    Sample(id="astronaut", name="Astronaut", filename="astronaut.png"),
    Sample(id="moon", name="Moon surface", filename="moon.png"),
)
"""Public-domain images taken from the scikit-image data set."""


class UnknownSampleError(LookupError):
    """Raised when a sample id does not exist."""


def find_sample(sample_id: str) -> Sample:
    """Look up a sample by id.

    Raises:
        UnknownSampleError: If no sample has this id.
    """
    for sample in SAMPLES:
        if sample.id == sample_id:
            return sample
    raise UnknownSampleError(f"Unknown sample '{sample_id}'")


def load_sample(sample_id: str) -> NDArray[np.float64]:
    """Load a sample as a grayscale array prepared like any uploaded image.

    Raises:
        UnknownSampleError: If no sample has this id.
    """
    sample = find_sample(sample_id)
    return decode_grayscale((SAMPLES_DIR / sample.filename).read_bytes())
