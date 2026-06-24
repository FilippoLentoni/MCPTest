"""
Launch a SageMaker Training Job using boto3 directly (no sagemaker SDK).
Writes the job name to models/latest_job.txt on completion.
"""
import argparse
import datetime
import json
import os
import time

import boto3

BUCKET = "ml-pipeline-columbia-169976659173"
ROLE_NAME = "ml-pipeline-execution-role"
REGION = "us-east-1"
XGBOOST_IMAGE = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.7-1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=REGION) if args.profile else boto3.Session(region_name=REGION)
    sm = session.client("sagemaker")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    role_arn = f"arn:aws:iam::{account_id}:role/{ROLE_NAME}"
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    job_name = f"adult-income-xgb-{timestamp}"

    print(f"Starting training job: {job_name}")

    sm.create_training_job(
        TrainingJobName=job_name,
        RoleArn=role_arn,
        AlgorithmSpecification={
            "TrainingImage": XGBOOST_IMAGE,
            "TrainingInputMode": "File",
        },
        HyperParameters={
            "max_depth": "6",
            "eta": "0.1",
            "gamma": "0",
            "min_child_weight": "1",
            "subsample": "0.8",
            "objective": "binary:logistic",
            "num_round": "200",
            "early_stopping_rounds": "10",
            "eval_metric": "error",
        },
        InputDataConfig=[
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"s3://{BUCKET}/data/train.csv",
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
                "ContentType": "text/csv",
            },
            {
                "ChannelName": "validation",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"s3://{BUCKET}/data/val.csv",
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
                "ContentType": "text/csv",
            },
        ],
        OutputDataConfig={"S3OutputPath": f"s3://{BUCKET}/models"},
        ResourceConfig={
            "InstanceType": "ml.m5.large",
            "InstanceCount": 1,
            "VolumeSizeInGB": 10,
        },
        StoppingCondition={"MaxRuntimeInSeconds": 3600},
    )

    print("Waiting for training job to complete (this takes ~5-8 minutes)...")
    while True:
        resp = sm.describe_training_job(TrainingJobName=job_name)
        status = resp["TrainingJobStatus"]
        print(f"  Status: {status}")
        if status == "Completed":
            break
        if status in ("Failed", "Stopped"):
            reason = resp.get("FailureReason", "unknown")
            raise RuntimeError(f"Training job {status}: {reason}")
        time.sleep(30)

    os.makedirs("models", exist_ok=True)
    with open("models/latest_job.txt", "w") as f:
        f.write(job_name)
    print(f"Training complete. Job name: {job_name}")
    print(f"Model artifacts: s3://{BUCKET}/models/{job_name}/output/model.tar.gz")


if __name__ == "__main__":
    main()
