
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STEPS=[
 ("Classifier regression",[sys.executable,"benchmarks/classifier_regression.py"]),
 ("Acquire and normalize 500 TED notices",[sys.executable,"benchmarks/live_ted_500.py"]),
 ("Build intelligence layer",[sys.executable,"intelligence/build.py"]),
 ("Analyze opportunity quality",[sys.executable,"intelligence/quality.py"]),
 ("Full dataset quality gate",[sys.executable,"intelligence/full_quality_gate.py"]),
 ("Update website status",[sys.executable,"github_status.py"]),
]
for name,cmd in STEPS:
    print(f"\n=== {name} ===",flush=True)
    p=subprocess.run(cmd,cwd=ROOT)
    if p.returncode: raise SystemExit(f"{name} failed with exit code {p.returncode}")
print("\n=== Opportunity Radar pipeline complete ===",flush=True)
