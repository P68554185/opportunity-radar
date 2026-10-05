from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = [
    ("Classifier regression", [sys.executable, "benchmarks/classifier_regression.py"]),
    ("Acquire and normalize 500 TED notices", [sys.executable, "benchmarks/live_ted_500.py"]),
    ("Build intelligence layer", [sys.executable, "intelligence/build.py"]),
    ("Analyze opportunity quality", [sys.executable, "intelligence/quality.py"]),
    ("Update website status", [sys.executable, "github_status.py"]),
]

def run_step(name: str, command: list[str]) -> None:
    print(f"\n=== {name} ===", flush=True)
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(f"{name} failed with exit code {completed.returncode}")

def main() -> None:
    for name, command in STEPS:
        run_step(name, command)
    print("\n=== Opportunity Radar pipeline complete ===", flush=True)

if __name__ == "__main__":
    main()
