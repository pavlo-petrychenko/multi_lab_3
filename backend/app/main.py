"""Application entry point: ``uvicorn app.main:app``."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import STATIC_DIR


def create_app() -> FastAPI:
    """Create the FastAPI application.

    The JSON API is mounted under ``/api``. When the built React UI exists in
    :data:`app.config.STATIC_DIR` it is served at ``/``, so a single process (and a
    single container) delivers the whole app. Without it the API runs alone and
    the UI is served by the Vite dev server.

    Returns:
        Configured application instance.
    """
    app = FastAPI(
        title="Lab 3 — Lossy image compression",
        description="Hand-written DCT and Haar DWT compression with PSNR comparison.",
        version="1.0.0",
    )
    app.include_router(router)
    if STATIC_DIR.is_dir():
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
    return app


app = create_app()
