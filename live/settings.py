"""Bounded ingestion volume, separate from evidence and customer eligibility."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(data):
    target=data.get("ted_target",2000);pages=data.get("ted_max_pages",12)
    if type(target) is not int or not 1<=target<=15000:raise ValueError("TED target must be 1..15000 in page-number mode")
    if type(pages) is not int or not math.ceil(target/250)<=pages<=60:raise ValueError("TED page budget cannot cover target or exceeds API page-number limit")
    return target,pages
def volume():
    path=ROOT/"config/data_volume.json"
    return validate(json.loads(path.read_text())) if path.exists() else validate({})
