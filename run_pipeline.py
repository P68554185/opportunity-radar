
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ("Classifier regression", [sys.executable, "benchmarks/classifier_regression.py"]),
    ("Acquire and normalize 500 TED notices", [sys.executable, "benchmarks/live_ted_500.py"]),
    ("Build intelligence layer", [sys.executable, "intelligence/build.py"]),
    ("Analyze opportunity quality", [sys.executable, "intelligence/quality.py"]),
    ("Validate quality and build audit sample", [sys.executable, "intelligence/validate_quality.py"]),
    ("Update website status", [sys.executable, "github_status.py"]),
]
def run_step(name, cmd):
    print(f"\n=== {name} ===", flush=True)
    p = subprocess.run(cmd, cwd=ROOT)
    if p.returncode:
        raise SystemExit(f"{name} failed with exit code {p.returncode}")
def main():
    for name, cmd in STEPS:
        run_step(name, cmd)
    print("\n=== Opportunity Radar pipeline complete ===", flush=True)
if __name__ == "__main__":
    main()
