## 1. AWS Infrastructure

- [x] 1.1 Create `cdk/stacks/ml_pipeline_stack.py` with `MlPipelineStack` — S3 bucket `ml-pipeline-columbia-169976659173` and IAM role `ml-pipeline-execution-role` with `AmazonSageMakerFullAccess` and S3 read/write on the bucket
- [x] 1.2 Register `MlPipelineStack` in `cdk/app.py`
- [x] 1.3 Run `cdk deploy MlPipelineStack --profile columbia` and confirm stack reaches `CREATE_COMPLETE`

## 2. Preprocessing

- [x] 2.1 Create `scripts/preprocess.py` — download UCI Adult Income dataset from `https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data` and `adult.test`
- [x] 2.2 Apply feature engineering: drop `fnlwgt`, ordinal-encode 8 categorical columns, fill missing values (mode for categoricals, median for numerics), encode target as 0/1
- [x] 2.3 Split 70/10/20 train/val/test, upload all three CSVs to `s3://ml-pipeline-columbia-169976659173/data/`
- [x] 2.4 Run `python scripts/preprocess.py --profile columbia` and confirm 3 S3 keys exist

## 3. Training

- [x] 3.1 Create `scripts/train.py` — configure SageMaker XGBoost estimator with `max_depth=6`, `n_estimators=200`, `early_stopping_rounds=10`, `objective=binary:logistic`
- [x] 3.2 Pass `data/train.csv` as train channel and `data/val.csv` as validation channel
- [x] 3.3 Write latest training job name to `models/latest_job.txt` after launch
- [x] 3.4 Run `python scripts/train.py --profile columbia` and confirm training job reaches `Completed`

## 4. Evaluation

- [x] 4.1 Create `scripts/evaluate.py` — accept `--profile` flag, read job name from `models/latest_job.txt`, download `model.tar.gz` from S3, extract XGBoost model
- [x] 4.2 Load `data/test.csv` from S3, run `model.predict()`, compute accuracy
- [x] 4.3 Write `metrics.json` with `accuracy`, `threshold: 0.80`, `passed: true/false`
- [x] 4.4 Exit 0 if `accuracy >= 0.80`, exit 1 otherwise
- [x] 4.5 Run `python scripts/evaluate.py --profile columbia` and confirm exit code matches accuracy

## 5. Pipeline Orchestrator

- [x] 5.1 Create `scripts/pipeline.py` — calls preprocess → train → evaluate in sequence, propagates exit code from evaluate
- [x] 5.2 Run `python scripts/pipeline.py --profile columbia` end-to-end and confirm `metrics.json` is written with `passed: true`
