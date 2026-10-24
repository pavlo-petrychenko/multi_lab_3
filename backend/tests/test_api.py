"""End-to-end tests of the HTTP API."""

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def png_bytes(width: int, height: int) -> bytes:
    pixels = np.random.default_rng(0).integers(0, 256, (height, width), dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(pixels).convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_samples_listed_with_thumbnails(client):
    samples = client.get("/api/samples").json()
    assert {sample["id"] for sample in samples} >= {"cameraman"}
    assert all(sample["thumbnail"].startswith("data:image/png;base64,") for sample in samples)


def test_compress_sample_returns_both_methods(client):
    body = client.post("/api/compress", data={"sample_id": "cameraman", "keep_ratio": "0.1"}).json()
    assert (body["width"], body["height"]) == (512, 512)
    for method in ("dct", "dwt"):
        result = body[method]
        assert result["kept"] == round(512 * 512 * 0.1)
        assert 20 < result["psnr"] < 60
        assert result["compression_ratio"] == pytest.approx(10, rel=1e-3)
        assert result["coefficients"].startswith("data:image/png")


def test_full_ratio_reports_infinite_psnr_as_null(client):
    body = client.post("/api/compress", data={"sample_id": "moon", "keep_ratio": "1"}).json()
    assert body["dct"]["psnr"] is None and body["dwt"]["psnr"] is None


def test_compress_uploaded_non_square_rgb_image(client):
    response = client.post(
        "/api/compress",
        files={"file": ("photo.png", png_bytes(800, 600), "image/png")},
        data={"keep_ratio": "0.05", "dwt_levels": "4"},
    )
    assert response.status_code == 200
    assert response.json()["dwt_levels"] == 4


def test_experiments_sorted_and_quality_decreasing(client):
    response = client.post(
        "/api/experiments",
        data={"sample_id": "astronaut", "keep_ratios": ["0.05", "0.5", "0.2"]},
    )
    levels = response.json()["levels"]
    assert [level["keep_ratio"] for level in levels] == [0.5, 0.2, 0.05]
    for method in ("dct", "dwt"):
        psnrs = [level[method]["psnr"] for level in levels]
        assert psnrs == sorted(psnrs, reverse=True)


@pytest.mark.parametrize(
    ("data", "files", "status"),
    [
        ({"keep_ratio": "0.1"}, None, 400),
        ({"sample_id": "nope", "keep_ratio": "0.1"}, None, 404),
        ({"sample_id": "cameraman", "keep_ratio": "0"}, None, 422),
        ({"sample_id": "cameraman", "keep_ratio": "0.1", "dwt_levels": "9"}, None, 422),
        ({"keep_ratio": "0.1"}, {"file": ("x.png", b"not an image", "image/png")}, 400),
    ],
)
def test_invalid_requests(client, data, files, status):
    assert client.post("/api/compress", data=data, files=files).status_code == status
