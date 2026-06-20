## Context

Greenfield Python package. No existing codebase to migrate from. The product must run locally with no cloud dependencies, GPU, or database. Target users are data scientists and ML engineers who want a reproducible, CLI-driven training loop they can plug a CSV into and immediately get a served model.

## Goals / Non-Goals

**Goals:**
- Single-command training: `train --data x.csv --target y`
- Portable artifact (one `.joblib` file contains everything needed for inference)
- Lightweight serving with zero-config startup: `serve --model model.joblib`
- Reproducible results (fixed random seed throughout)
- Pure Python, no Docker required to run locally

**Non-Goals:**
- Deep learning or GPU-accelerated models
- Hyperparameter tuning or AutoML
- Multi-class regression (classification only in v1)
- Authentication on the serving API
- Persistent request logging

## Decisions

### D1: scikit-learn Pipeline as the single artifact
Wrap preprocessor + model in a single `sklearn.pipeline.Pipeline` object and serialise with `joblib.dump`. This means the serving code never needs to know about preprocessing — it just calls `pipeline.predict(df)`.

**Alternatives considered:**
- Separate preprocessor and model files → fragile, easy to mismatch versions
- ONNX export → adds complexity, not needed for scikit-learn models on CPU

### D2: ColumnTransformer for automatic preprocessing
Use `sklearn.compose.ColumnTransformer` with `StandardScaler` on numeric columns and `OneHotEncoder(handle_unknown="ignore")` on object columns. Column types are inferred from pandas dtypes at fit time.

**Alternatives considered:**
- Manual feature type specification via CLI flags → poor UX, error-prone
- FeatureHasher → loses interpretability

### D3: Click for CLI, FastAPI for serving
`click` is idiomatic Python CLI and integrates cleanly with the package entry points. `fastapi` with `uvicorn` gives async serving with automatic OpenAPI docs at `/docs`.

**Alternatives considered:**
- argparse → more verbose, no sub-command nesting
- Flask → no async, no automatic schema validation

### D4: Package structure
```
ml_pipeline/
├── __init__.py
├── cli.py          ← click entry points (train, serve)
├── pipeline.py     ← build_pipeline(), train(), evaluate()
├── serving.py      ← FastAPI app, /predict, /predict/batch, /health
└── utils.py        ← load_csv(), validate_columns()
```
Single flat package — no nested subpackages needed at this scale.

### D5: Fixed random seed = 42
All random operations use `random_state=42`. Passed explicitly to train/test split and all model constructors.

## Risks / Trade-offs

- **OneHotEncoder cardinality explosion** → High-cardinality categoricals can blow up feature space. Mitigation: document the limitation; add `max_categories` guard in a future change.
- **Large CSV memory usage** → pandas loads entire file into memory. Mitigation: out of scope for v1; document 500 MB RAM guideline.
- **joblib security** → loading arbitrary `.joblib` files is equivalent to pickle (arbitrary code execution). Mitigation: document that users should only load artifacts they produced themselves.

## Open Questions

- Should `serve` reload the model on SIGHUP without restart? (Deferred to a future change)
- Should evaluation output be machine-readable JSON in addition to the CLI table? (Nice to have, not blocking v1)
