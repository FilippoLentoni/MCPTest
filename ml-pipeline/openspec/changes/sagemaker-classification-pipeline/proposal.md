## Why

We want to validate the end-to-end ML workflow on AWS: ingest a public dataset, train a classifier using SageMaker, evaluate it against a holdout set, and register the model if it meets the accuracy threshold. This also serves as the first test of the ralph-loop pattern — the agent iterates until `evaluate.py` exits 0.

## What Changes

- New CDK stack `MlPipelineStack` — S3 bucket for data/artifacts + SageMaker execution role
- `scripts/preprocess.py` — downloads UCI Adult Income dataset, engineers features, splits train/val/test, uploads to S3
- `scripts/train.py` — launches SageMaker Training Job using built-in XGBoost algorithm
- `scripts/evaluate.py` — downloads model artifacts from S3, runs inference on holdout test set, exits 0 if accuracy >= 0.80, exits 1 otherwise
- `scripts/pipeline.py` — orchestrates preprocess → train → evaluate in sequence

## Capabilities

### New Capabilities

- `ml-pipeline`: End-to-end SageMaker classification pipeline — data ingestion, training, evaluation, and model registration with a machine-checkable accuracy gate

### Modified Capabilities

_(none)_

## Impact

- New source tree: `src/ml_pipeline/` for shared utilities
- New scripts: `scripts/preprocess.py`, `scripts/train.py`, `scripts/evaluate.py`, `scripts/pipeline.py`
- New CDK stack: `cdk/stacks/ml_pipeline_stack.py` registered in `cdk/app.py`
- Dataset: UCI Adult Income (https://archive.ics.uci.edu/ml/machine-learning-databases/adult/) — no auth required, public domain
- New Python dependencies: `scikit-learn`, `xgboost`, `pandas`, `boto3` (already present)
- S3 bucket: `ml-pipeline-columbia-169976659173` created by CDK in `columbia` account
- SageMaker execution role: `ml-pipeline-execution-role` with S3 and SageMaker permissions
