"""
Evaluate the trained XGBoost model against the test set.
Exits 0 if accuracy >= 0.80, exits 1 otherwise.
Writes models/metrics.json with accuracy, threshold, and passed fields.
"""
import argparse
import io
import json
import os
import sys
import tarfile
import tempfile

import boto3
import numpy as np
import pandas as pd
import xgboost as xgb

BUCKET = "ml-pipeline-columbia-169976659173"
THRESHOLD = 0.80


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name="us-east-1") if args.profile else boto3.Session(region_name="us-east-1")
    s3 = session.client("s3")
    sm = session.client("sagemaker")

    with open("models/latest_job.txt") as f:
        job_name = f.read().strip()
    print(f"Evaluating job: {job_name}")

    resp = sm.describe_training_job(TrainingJobName=job_name)
    model_s3_uri = resp["ModelArtifacts"]["S3ModelArtifacts"]
    bucket_prefix = model_s3_uri.replace("s3://", "").split("/", 1)
    model_bucket, model_key = bucket_prefix[0], bucket_prefix[1]

    print(f"Downloading model: s3://{model_bucket}/{model_key}")
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, "model.tar.gz")
        s3.download_file(model_bucket, model_key, tar_path)
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(tmpdir)
        model_file = next(
            os.path.join(tmpdir, f) for f in os.listdir(tmpdir)
            if f.endswith(".model") or f == "xgboost-model"
        )
        booster = xgb.Booster()
        booster.load_model(model_file)

    print("Loading test data from S3...")
    obj = s3.get_object(Bucket=BUCKET, Key="data/test.csv")
    test_df = pd.read_csv(io.BytesIO(obj["Body"].read()), header=None)
    y_true = test_df.iloc[:, 0].values
    X_test = test_df.iloc[:, 1:].values

    dmatrix = xgb.DMatrix(X_test)
    y_prob = booster.predict(dmatrix)
    y_pred = (y_prob >= 0.5).astype(int)

    accuracy = float(np.mean(y_pred == y_true))
    passed = accuracy >= THRESHOLD

    metrics = {"accuracy": round(accuracy, 4), "threshold": THRESHOLD, "passed": passed}
    os.makedirs("models", exist_ok=True)
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Accuracy: {accuracy:.4f} (threshold: {THRESHOLD})")
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Metrics written to models/metrics.json")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
