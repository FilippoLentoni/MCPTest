"""
Download UCI Adult Income dataset, engineer features, split, upload to S3.
"""
import argparse
import io
import os

import boto3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

BUCKET = "ml-pipeline-columbia-169976659173"

COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education-num",
    "marital-status", "occupation", "relationship", "race", "sex",
    "capital-gain", "capital-loss", "hours-per-week", "native-country", "income",
]

CATEGORICAL_COLS = [
    "workclass", "education", "marital-status", "occupation",
    "relationship", "race", "sex", "native-country",
]

TRAIN_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
TEST_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test"


def load_data() -> pd.DataFrame:
    train_df = pd.read_csv(TRAIN_URL, header=None, names=COLUMNS,
                           skipinitialspace=True, na_values="?")
    test_df = pd.read_csv(TEST_URL, header=None, names=COLUMNS,
                          skipinitialspace=True, na_values="?", skiprows=1)
    test_df["income"] = test_df["income"].str.rstrip(".")
    df = pd.concat([train_df, test_df], ignore_index=True)
    return df


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["fnlwgt"])
    for col in CATEGORICAL_COLS:
        df[col] = df[col].fillna(df[col].mode()[0])
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    df["income"] = (df["income"].str.strip() == ">50K").astype(int)
    return df


def encode(df: pd.DataFrame, encoder=None):
    if encoder is None:
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        df[CATEGORICAL_COLS] = encoder.fit_transform(df[CATEGORICAL_COLS])
    else:
        df[CATEGORICAL_COLS] = encoder.transform(df[CATEGORICAL_COLS])
    return df, encoder


def upload(df: pd.DataFrame, s3_client, key: str):
    buf = io.StringIO()
    # SageMaker built-in XGBoost requires no header, label in first column
    df.to_csv(buf, index=False, header=False)
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())
    print(f"  Uploaded s3://{BUCKET}/{key} ({len(df)} rows)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    s3 = session.client("s3", region_name="us-east-1")

    print("Loading data...")
    df = load_data()
    print(f"  Total rows: {len(df)}")

    print("Engineering features...")
    df = engineer(df)

    # Split: 70% train+val, 30% test (stratified)
    train_val, test = train_test_split(df, test_size=0.20, random_state=42,
                                       stratify=df["income"])
    train, val = train_test_split(train_val, test_size=0.125, random_state=42,
                                  stratify=train_val["income"])

    # Encode — fit only on train
    train, encoder = encode(train)
    val, _ = encode(val, encoder)
    test, _ = encode(test, encoder)

    # XGBoost expects label in first column
    cols = ["income"] + [c for c in train.columns if c != "income"]
    train, val, test = train[cols], val[cols], test[cols]

    print("Uploading to S3...")
    upload(train, s3, "data/train.csv")
    upload(val, s3, "data/val.csv")
    upload(test, s3, "data/test.csv")
    print("Preprocessing complete.")


if __name__ == "__main__":
    main()
