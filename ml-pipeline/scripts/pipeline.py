"""
End-to-end ML pipeline: preprocess → train → evaluate.
Propagates evaluate.py exit code (0 = accuracy >= 0.80, 1 = below threshold).
"""
import argparse
import subprocess
import sys

PYTHON = sys.executable
SCRIPTS = ["scripts/preprocess.py", "scripts/train.py", "scripts/evaluate.py"]


def run(script, profile):
    cmd = [PYTHON, script]
    if profile:
        cmd += ["--profile", profile]
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print("="*60)
    result = subprocess.run(cmd)
    if result.returncode != 0 and script != "scripts/evaluate.py":
        print(f"ERROR: {script} exited with code {result.returncode}")
        sys.exit(result.returncode)
    return result.returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    args = parser.parse_args()

    for script in SCRIPTS:
        rc = run(script, args.profile)

    sys.exit(rc)


if __name__ == "__main__":
    main()
