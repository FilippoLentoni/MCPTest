## Why

Teams building ML prototypes spend hours writing boilerplate training code that is never reusable. There is no lightweight, reproducible pipeline that goes from a raw CSV dataset to a deployed prediction endpoint with a single command — so every project reinvents the same plumbing.

## What Changes

- New CLI command `train` that ingests a CSV, preprocesses features, trains a lightweight scikit-learn model, evaluates it, and exports a portable `.joblib` artifact
- New CLI command `serve` that loads the exported model and starts a FastAPI REST endpoint for real-time predictions
- No database, no GPU, no cloud dependency — runs entirely on a laptop

## Capabilities

### New Capabilities

- `training-pipeline`: End-to-end pipeline that takes a labelled CSV dataset through ingestion, preprocessing, training, evaluation, and model export as a single reproducible run
- `prediction-serving`: FastAPI REST API that loads a trained model artifact and exposes a `/predict` endpoint for single or batch inference

### Modified Capabilities

<!-- None — this is a greenfield project -->

## Impact

- New Python package `ml_pipeline` with `train` and `serve` entry points
- Dependencies: `scikit-learn`, `pandas`, `fastapi`, `uvicorn`, `joblib`, `click`
- No breaking changes (new project)
