"""Rebuild and verify a complete website snapshot without network acquisition."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STEPS=["intelligence/build.py","intelligence/quality.py","intelligence/full_quality_gate.py",
       "intelligence/audit_precision.py","intelligence/smart_validation.py",
       "intelligence/customer_feed.py","github_status.py","tests/check_generated_feed.py"]
if __name__=="__main__":
    for step in STEPS:
        subprocess.run([sys.executable,step],cwd=ROOT,check=True)
