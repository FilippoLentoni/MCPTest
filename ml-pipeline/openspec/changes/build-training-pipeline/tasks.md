## 1. Project Setup

- [ ] 1.1 Create `pyproject.toml` with metadata, dependencies (`scikit-learn`, `pandas`, `fastapi`, `uvicorn`, `click`, `joblib`), and entry points (`train`, `serve`)
- [ ] 1.2 Create `ml_pipeline/__init__.py`, `cli.py`, `pipeline.py`, `serving.py`, `utils.py`
- [ ] 1.3 Create `.gitignore` (venv, `__pycache__`, `*.joblib`, `*.csv`)
- [ ] 1.4 Create `requirements.txt` pinned from `pyproject.toml` for quick installs

## 2. Data Utilities (`utils.py`)

- [ ] 2.1 Implement `load_csv(path, target_col)` — loads CSV with pandas, validates file exists and target column is present, returns `(X: DataFrame, y: Series)`
- [ ] 2.2 Add row count guard: raise `ValueError` if fewer than 10 rows after loading
- [ ] 2.3 Write unit test: valid CSV loads correctly, missing file raises error, missing target column raises error with column list

## 3. Training Pipeline (`pipeline.py`)

- [ ] 3.1 Implement `build_preprocessor(X)` — returns a `ColumnTransformer` with `StandardScaler` on numeric columns and `OneHotEncoder(handle_unknown="ignore")` on object columns
- [ ] 3.2 Implement `build_pipeline(X, model_type)` — wraps preprocessor + chosen estimator in an `sklearn.Pipeline`; support `logistic-regression`, `decision-tree`, `random-forest`
- [ ] 3.3 Implement `train(X, y, model_type)` — splits 80/20 with `random_state=42`, fits pipeline on train split, returns `(pipeline, X_test, y_test)`
- [ ] 3.4 Implement `evaluate(pipeline, X_test, y_test)` — returns dict with `accuracy`, `precision`, `recall`, `f1` (macro average)
- [ ] 3.5 Write unit tests: pipeline builds correctly for each model type, evaluation returns correct keys, metrics are reproducible across two identical runs

## 4. CLI Entry Points (`cli.py`)

- [ ] 4.1 Implement `train` command with options: `--data` (required), `--target` (required, default `"label"`), `--model` (default `"logistic-regression"`), `--output` (default `"./model.joblib"`)
- [ ] 4.2 Print progress messages: loading data, preprocessing, training, evaluation table, export path
- [ ] 4.3 Implement `serve` command with options: `--model` (required), `--host` (default `"0.0.0.0"`), `--port` (default `8000`)
- [ ] 4.4 Exit with code 1 and descriptive message on all error conditions (missing file, invalid model type, etc.)

## 5. Serving API (`serving.py`)

- [ ] 5.1 Create FastAPI app with a module-level `pipeline` variable set on startup
- [ ] 5.2 Implement `GET /health` — returns `{"status": "ok", "model": "<filename>"}`
- [ ] 5.3 Implement `POST /predict` — accepts JSON object of features, runs `pipeline.predict(pd.DataFrame([body]))`, returns `{"prediction": str(result[0])}`
- [ ] 5.4 Implement `POST /predict/batch` — accepts JSON array of feature objects, returns array of `{"prediction": "..."}` in same order
- [ ] 5.5 Add 422 validation: if a required feature column is missing from the request, return HTTP 422 with missing field names
- [ ] 5.6 Write integration test: start server with a test model artifact, call all three endpoints, assert correct responses

## 6. End-to-End Verification

- [ ] 6.1 Download the Iris CSV dataset as a sample and save to `tests/fixtures/iris.csv`
- [ ] 6.2 Run `train --data tests/fixtures/iris.csv --target species` and confirm `model.joblib` is created and metrics are printed
- [ ] 6.3 Run `serve --model model.joblib` and call `/health`, `/predict`, `/predict/batch` with curl — confirm all return correct responses
- [ ] 6.4 Run the full pipeline twice and confirm metrics are identical (reproducibility check)
