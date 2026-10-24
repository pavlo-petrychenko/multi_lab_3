"""Reusable FastAPI dependencies."""

from typing import Annotated

import numpy as np
from fastapi import File, Form, HTTPException, UploadFile, status
from numpy.typing import NDArray

from app.config import MAX_UPLOAD_BYTES
from app.services.image_io import InvalidImageError, decode_grayscale
from app.services.samples import UnknownSampleError, load_sample


def source_image(
    file: Annotated[UploadFile | None, File(description="Image to compress")] = None,
    sample_id: Annotated[str | None, Form(description="Id of a bundled sample, used when no file is sent")] = None,
) -> NDArray[np.float64]:
    """Resolve the input image from either an uploaded file or a sample id.

    Returns:
        Prepared ``512 × 512`` grayscale array.

    Raises:
        HTTPException: 400 when no source / a broken file is given, 413 when the file
            is too large, 404 for an unknown sample.
    """
    if file is not None:
        data = file.file.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image is larger than 10 MB")
        try:
            return decode_grayscale(data)
        except InvalidImageError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    if sample_id is not None:
        try:
            return load_sample(sample_id)
        except UnknownSampleError as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Send either 'file' or 'sample_id'")
