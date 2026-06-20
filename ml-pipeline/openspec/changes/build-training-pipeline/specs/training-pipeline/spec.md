## ADDED Requirements

### Requirement: Ingest labelled CSV dataset
The system SHALL accept a path to a CSV file where one column is the target label and all remaining columns are features. The system SHALL validate that the file exists, is parseable, and contains at least 10 rows.

#### Scenario: Valid CSV provided
- **WHEN** the user runs `train --data dataset.csv --target label`
- **THEN** the system loads the file, prints row and column counts, and proceeds to preprocessing

#### Scenario: File does not exist
- **WHEN** the user provides a path to a non-existent file
- **THEN** the system exits with a clear error message and code 1

#### Scenario: Target column missing
- **WHEN** the CSV does not contain the specified target column
- **THEN** the system exits with an error listing the available columns

---

### Requirement: Preprocess features automatically
The system SHALL apply automatic preprocessing: numeric columns are standardised (zero mean, unit variance) and categorical columns (dtype object) are one-hot encoded. The fitted preprocessor SHALL be saved alongside the model so inference uses identical transformations.

#### Scenario: Mixed numeric and categorical columns
- **WHEN** the dataset contains both numeric and string columns
- **THEN** numeric columns are scaled and categorical columns are one-hot encoded with no manual configuration required

#### Scenario: Preprocessor persisted with model
- **WHEN** training completes successfully
- **THEN** the exported artifact contains both the trained model and the fitted preprocessor as a single pipeline object

---

### Requirement: Train a lightweight scikit-learn classifier
The system SHALL train a Logistic Regression model by default. The user MAY override the model type via `--model` flag, choosing from `logistic-regression`, `decision-tree`, or `random-forest`. Training SHALL complete in under 60 seconds on a dataset of 100 000 rows on commodity hardware.

#### Scenario: Default model training
- **WHEN** the user runs `train --data dataset.csv --target label` with no `--model` flag
- **THEN** a Logistic Regression model is trained

#### Scenario: Model override
- **WHEN** the user runs `train --data dataset.csv --target label --model random-forest`
- **THEN** a Random Forest classifier is trained

---

### Requirement: Evaluate and report metrics
The system SHALL split data into 80% train / 20% test using a fixed random seed and report accuracy, precision, recall, and F1-score (macro average) on the held-out test set.

#### Scenario: Evaluation output
- **WHEN** training completes
- **THEN** the CLI prints a metrics table with accuracy, precision, recall, and F1 for the test set

#### Scenario: Reproducible split
- **WHEN** the same dataset and command are run twice
- **THEN** the train/test split and reported metrics are identical

---

### Requirement: Export trained pipeline as a portable artifact
The system SHALL serialise the full sklearn Pipeline (preprocessor + model) to a `.joblib` file. The output path SHALL default to `./model.joblib` and be overridable via `--output`.

#### Scenario: Default export path
- **WHEN** no `--output` flag is provided
- **THEN** the artifact is saved to `./model.joblib`

#### Scenario: Custom export path
- **WHEN** the user runs `train ... --output models/v1.joblib`
- **THEN** the artifact is saved to the specified path, creating parent directories if needed
