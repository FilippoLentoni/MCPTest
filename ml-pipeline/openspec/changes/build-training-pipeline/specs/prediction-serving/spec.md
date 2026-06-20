## ADDED Requirements

### Requirement: Load model artifact on startup
The system SHALL accept a path to a `.joblib` model artifact via `--model` flag and load it into memory before accepting requests. If the file is missing or corrupt, the server SHALL exit with a clear error.

#### Scenario: Valid model loaded
- **WHEN** the user runs `serve --model model.joblib`
- **THEN** the server starts, prints the listening address, and is ready to accept requests

#### Scenario: Missing model file
- **WHEN** the path provided via `--model` does not exist
- **THEN** the server exits immediately with error code 1 and a descriptive message

---

### Requirement: Expose a single-item prediction endpoint
The system SHALL expose `POST /predict` accepting a JSON object whose keys are feature names and values are the feature values. The system SHALL return a JSON object with a `prediction` field containing the predicted class label.

#### Scenario: Valid prediction request
- **WHEN** a POST request is sent to `/predict` with `{"feature_a": 1.5, "feature_b": "cat"}`
- **THEN** the server returns HTTP 200 with `{"prediction": "<class_label>"}`

#### Scenario: Missing feature in request
- **WHEN** the request body omits a feature that the model requires
- **THEN** the server returns HTTP 422 with a message listing the missing fields

---

### Requirement: Expose a batch prediction endpoint
The system SHALL expose `POST /predict/batch` accepting a JSON array of feature objects and returning a JSON array of prediction objects in the same order.

#### Scenario: Batch prediction
- **WHEN** a POST request is sent to `/predict/batch` with an array of 10 feature objects
- **THEN** the server returns HTTP 200 with an array of 10 `{"prediction": "..."}` objects in the same order

---

### Requirement: Expose a health check endpoint
The system SHALL expose `GET /health` that returns HTTP 200 with `{"status": "ok", "model": "<artifact filename>"}` when the model is loaded and ready.

#### Scenario: Health check when ready
- **WHEN** a GET request is sent to `/health`
- **THEN** the server returns HTTP 200 with status ok and the model filename
