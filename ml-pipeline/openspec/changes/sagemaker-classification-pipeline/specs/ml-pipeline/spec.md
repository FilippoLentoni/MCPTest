## ADDED Requirements

### Requirement: Dataset preprocessed and available in S3
The system SHALL download the UCI Adult Income dataset, apply feature engineering, split into train/val/test sets, and upload all three splits to the project S3 bucket before training begins.

#### Scenario: Preprocessing completes successfully
- **WHEN** `python scripts/preprocess.py --profile columbia` is run
- **THEN** the following S3 keys exist in `s3://ml-pipeline-columbia-169976659173/`:
  - `data/train.csv`
  - `data/val.csv`
  - `data/test.csv`
- **AND** the script exits with code 0

#### Scenario: Feature encoding is consistent between train and test
- **WHEN** `preprocess.py` runs
- **THEN** the same `OrdinalEncoder` fitted on train is applied to val and test
- **AND** no data leakage occurs (encoder is fit only on training rows)

---

### Requirement: Model trained on SageMaker using XGBoost
The system SHALL launch a SageMaker Training Job using the built-in XGBoost algorithm, reading from S3 and writing model artifacts back to S3.

#### Scenario: Training job reaches Completed status
- **WHEN** `python scripts/train.py --profile columbia` is run
- **THEN** a SageMaker Training Job with name prefix `adult-income-xgb-` reaches status `Completed`
- **AND** model artifacts are stored at `s3://ml-pipeline-columbia-169976659173/models/<job-name>/output/model.tar.gz`

#### Scenario: Training uses val set for early stopping
- **WHEN** the training job is configured
- **THEN** `data/val.csv` is passed as the validation channel
- **AND** `early_stopping_rounds=10` is set to prevent overfitting

---

### Requirement: Evaluation script is machine-checkable
The system SHALL provide `scripts/evaluate.py` that downloads model artifacts from S3, runs inference on the holdout test set, and exits with a code that reflects whether the accuracy threshold is met.

#### Scenario: Accuracy meets threshold — exits 0
- **WHEN** `python scripts/evaluate.py --profile columbia` is run after a successful training job
- **AND** the model achieves accuracy >= 0.80 on `data/test.csv`
- **THEN** the script prints the accuracy value
- **AND** exits with code 0

#### Scenario: Accuracy below threshold — exits 1
- **WHEN** the model achieves accuracy < 0.80 on `data/test.csv`
- **THEN** the script prints the accuracy value and the gap to threshold
- **AND** exits with code 1

#### Scenario: Metrics written to file
- **WHEN** `evaluate.py` completes
- **THEN** `metrics.json` is written to the project root containing `accuracy`, `threshold`, and `passed` fields

---

### Requirement: Pipeline runs end-to-end from a single script
The system SHALL provide `scripts/pipeline.py` that runs preprocess → train → evaluate in sequence.

#### Scenario: Full pipeline succeeds
- **WHEN** `python scripts/pipeline.py --profile columbia` is run
- **THEN** preprocessing, training, and evaluation all complete
- **AND** the final exit code matches `evaluate.py`'s exit code

---

### Requirement: AWS infrastructure provisioned via CDK
The system SHALL provision all required AWS resources via CDK with no manual console steps.

#### Scenario: CDK stack deploys successfully
- **WHEN** `cdk deploy MlPipelineStack --profile columbia` is run
- **THEN** the CloudFormation stack reaches `CREATE_COMPLETE` or `UPDATE_COMPLETE`
- **AND** the S3 bucket `ml-pipeline-columbia-169976659173` exists
- **AND** the IAM role `ml-pipeline-execution-role` exists with SageMaker and S3 permissions
