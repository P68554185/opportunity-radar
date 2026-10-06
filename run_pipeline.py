
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STEPS=[
 ("Refresh approved EARLY sources",[sys.executable,"early/collect.py"]),
 ("Classifier regression",[sys.executable,"benchmarks/classifier_regression.py"]),
 ("Acquire and normalize 2000 TED notices",[sys.executable,"benchmarks/live_ted_500.py"]),
 ("Build intelligence layer",[sys.executable,"intelligence/build.py"]),
 ("Analyze opportunity quality",[sys.executable,"intelligence/quality.py"]),
 ("Full dataset quality gate",[sys.executable,"intelligence/full_quality_gate.py"]),
 ("Build audit and precision layer",[sys.executable,"intelligence/audit_precision.py"]),
 ("Smart validation and error analysis",[sys.executable,"intelligence/smart_validation.py"]),
 ("Validate historical lifecycle cases",[sys.executable,"lifecycle/validate_history.py"]),
 ("Build BauRadar customer feed",[sys.executable,"intelligence/customer_feed.py"]),
 ("Update website status",[sys.executable,"github_status.py"]),
 ("Verify generated feed",[sys.executable,"tests/check_generated_feed.py"]),
]
for name,cmd in STEPS:
    print(f"\n=== {name} ===",flush=True)
    p=subprocess.run(cmd,cwd=ROOT)
    if p.returncode: raise SystemExit(f"{name} failed with exit code {p.returncode}")
print("\n=== Opportunity Radar pipeline complete ===",flush=True)
