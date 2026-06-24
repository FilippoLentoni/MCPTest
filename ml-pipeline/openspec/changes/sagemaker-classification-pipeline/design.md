## Context

We are training a binary classifier on the UCI Adult Income dataset (predict if income >50K). The pipeline runs on AWS SageMaker in the `columbia` account using the CDK-provisioned execution role and S3 bucket. The exit criteria for ralph-loop is `evaluate.py` exiting 0, which happens only when accuracy on the holdout test set is >= 0.80.

**Dataset**: UCI Adult Income  
- 48,842 rows, 14 features (age, workclass, education, marital-status, occupation, etc.)  
- Binary target: income `<=50K` or `>50K`  
- XGBoost baseline accuracy: ~87% — well above the 80% threshold  

## Goals / Non-Goals

**Goals:**
- Reproducible pipeline: `python scripts/pipeline.py --profile columbia` runs end-to-end
- Machine-checkable exit: `python scripts/evaluate.py --profile columbia` exits 0 if accuracy >= 0.80
- SageMaker Training Job for actual model training (not local sklearn)
- Model artifacts stored in S3 for reproducibility

**Non-Goals:**
- SageMaker Pipelines orchestration service (overkill for one model — plain sequential script is sufficient)
- Real-time inference endpoint (evaluation runs batch inference locally against downloaded model)
- Hyperparameter tuning jobs
- MLflow or experiment tracking

## Decisions

### D1 — SageMaker built-in XGBoost algorithm (not custom container)

SageMaker's built-in XGBoost (`sagemaker.image_uris.retrieve("xgboost", ...)`) requires only a CSV input and hyperparameters — no Docker image to build. Faster iteration, no ECR push step. Random Forest would require a custom script container; XGBoost doesn't.

### D2 — Preprocessing runs locally, not as a SageMaker Processing Job

A Processing Job adds 3-5 minutes of spin-up per ralph-loop iteration. Local preprocessing with `pandas` + `scikit-learn` is instant and sufficient for a 48k-row CSV. Processed CSVs are uploaded to S3 before training starts.

### D3 — evaluate.py downloads model artifacts and runs local inference

SageMaker Batch Transform takes 5+ minutes per run. For the ralph-loop to iterate quickly, `evaluate.py` downloads `model.tar.gz` from S3, extracts the XGBoost model, and runs `predict()` locally using the `xgboost` Python library. Sub-10-second evaluation.

### D4 — Feature encoding: ordinal for tree models

XGBoost handles ordinal-encoded categoricals well without one-hot expansion. `sklearn.preprocessing.OrdinalEncoder` keeps feature count low and avoids sparse matrix issues. Missing values filled with mode for categoricals, median for numerics.

### D5 — Train/val/test split: 70/10/20

70% training, 10% validation (passed to SageMaker as early-stopping set), 20% holdout test (used only in `evaluate.py`). Holdout is uploaded to `s3://<bucket>/data/test.csv` and never touched during training.

## Risks / Trade-offs

- **[Risk] SageMaker Training Job takes 5-10 min** → ralph-loop iteration is slow. Mitigated by D2/D3 — preprocessing and evaluation are local and fast.
- **[Risk] UCI Adult dataset has class imbalance (~75% <=50K)** → XGBoost handles this naturally; accuracy of 87% is achievable without resampling.
- **[Risk] `evaluate.py` downloads model from S3 each run** → Small model (~1MB), download takes <1s. Acceptable.
