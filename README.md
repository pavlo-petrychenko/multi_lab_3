# Lab 3 — Lossy image compression: DCT vs DWT

A web app that compresses a grayscale image with a **hand-written 8×8 matrix DCT** and a **hand-written Haar wavelet transform (DWT)**. It shows **Original | DCT | DWT** side by side with **PSNR**, and the compression level is adjustable.

> New to the topic? Start with the **[learning path](docs/README.md)**. It walks from "what is an image" to "how to defend this lab" in 7 short chapters.

---

## Quick start

```bash
docker compose up --build
```

Open **http://localhost:8080**. One container serves both the UI and the API.

### Without Docker (for development)

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. Vite forwards `/api` to :8000.

### Tests and report material

```bash
cd backend
uv run pytest
uv run python -m scripts.run_experiments --sample cameraman
```

The second command writes `reports/experiments.md` (table), `reports/psnr.png` (chart) and `reports/comparison.png` (image grid).

---

## How the lab requirements map to the code

| Requirement (from the assignment) | Where |
|---|---|
| DCT on 8×8 blocks, **matrix form**, forward + inverse | [`backend/app/core/dct.py`](backend/app/core/dct.py) |
| Haar DWT, forward + inverse | [`backend/app/core/haar.py`](backend/app/core/haar.py) |
| Reduce the number of significant coefficients, adjustable level | [`backend/app/core/compression.py`](backend/app/core/compression.py) + slider in the UI |
| PSNR | [`backend/app/core/metrics.py`](backend/app/core/metrics.py) |
| Same pipeline for both methods | [`backend/app/services/compressors.py`](backend/app/services/compressors.py) |
| ≥ 3 compression levels per method, comparison | *Experiments* tab, [`backend/app/services/comparison.py`](backend/app/services/comparison.py), [`backend/scripts/run_experiments.py`](backend/scripts/run_experiments.py) |
| Visual comparison Original \| DCT \| DWT with PSNR | *Compare* tab, [`frontend/src/features/compare/`](frontend/src/features/compare/) |
| No ready-made `dct()/idct()/dwt()/idwt()` | Only NumPy (arrays, `@` matmul) and Pillow (file I/O) are used, see [`backend/pyproject.toml`](backend/pyproject.toml) |

---

## Project map

```
multi_lab_3/
├── Dockerfile               build UI (Node) → copy into Python image → one container
├── docker-compose.yml       `docker compose up --build` → :8080
├── docs/                    learning path and algorithm guides
├── reports/                 generated tables/charts for the written report
│
├── backend/                 Python 3.12 · FastAPI · NumPy
│   ├── app/
│   │   ├── core/            ★ pure math, no web, no files — this is what gets defended
│   │   │   ├── dct.py           DCT matrix, dct2/idct2, blockwise forward/inverse
│   │   │   ├── haar.py          Haar step, 2-D level, multi-level forward/inverse
│   │   │   ├── blocks.py        split image into 8×8 blocks and back
│   │   │   ├── compression.py   keep_largest(): the lossy step
│   │   │   └── metrics.py       MSE, PSNR, compression ratio
│   │   ├── services/        use cases built from core
│   │   │   ├── compressors.py   Compressor protocol, DctCompressor, HaarCompressor, compress()
│   │   │   ├── comparison.py    compare() one level, run_experiments() many levels
│   │   │   ├── image_io.py      bytes → 512×512 grayscale array, array → PNG
│   │   │   ├── samples.py       bundled sample images
│   │   │   └── visualize.py     coefficient maps, error maps
│   │   ├── api/             HTTP only: parse request → call service → present JSON
│   │   │   ├── routes.py        /api/health, /api/samples, /api/compress, /api/experiments
│   │   │   ├── dependencies.py  "uploaded file or sample id" → image array
│   │   │   ├── presenters.py    service results → response schemas
│   │   │   └── schemas.py       Pydantic response models
│   │   ├── config.py        constants (512 px, 8×8, levels, default sweep)
│   │   └── main.py          create_app(): API + static UI
│   ├── scripts/run_experiments.py   CLI for report tables and charts
│   └── tests/               pytest: math correctness + API
│
└── frontend/                React 18 · TypeScript · Vite · Recharts
    └── src/
        ├── api/             client.ts (fetch wrappers), types.ts (mirrors schemas.py)
        ├── features/
        │   ├── source/      SourcePicker: samples + upload
        │   ├── compare/     CompareView, ControlsPanel, ImagePanel, useCompression
        │   └── experiments/ ExperimentsView, ResultsTable, PsnrChart, useExperiments
        ├── components/      Card, SegmentedControl, Lightbox, ErrorBanner
        ├── lib/             formatting, log-scale slider math, debounce hook
        └── App.tsx          header, tabs, shared image source
```

**Dependency rule:** `api → services → core`. Nothing points the other way. `core` has no idea that a web server exists. It only receives and returns NumPy arrays.

## API

| Method | Path | Body (multipart form) | Returns |
|---|---|---|---|
| GET | `/api/health` | – | `{"status": "ok"}` |
| GET | `/api/samples` | – | `[{id, name, thumbnail}]` |
| POST | `/api/compress` | `file` or `sample_id`, `keep_ratio` ∈ (0, 1], `dwt_levels` 1–5 | original + DCT/DWT reconstructions, coefficient maps, error maps, PSNR, kept, ratio |
| POST | `/api/experiments` | `file` or `sample_id`, repeated `keep_ratios`, `dwt_levels` | one row per level with both methods |

Interactive docs are at http://localhost:8080/docs (FastAPI Swagger).

## Code conventions

- All documentation lives in **docstrings** (Python, Google style) and **JSDoc/TSDoc** (TypeScript). The code has no inline comments. If something needs explaining, it goes into the docstring of the function or class.
- `core/` functions are pure: they take arrays, return arrays, and never mutate their input.
- The frontend is feature-based. Each folder in `features/` owns its components, hook and styles.
