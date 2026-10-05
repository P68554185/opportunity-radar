import os,sys,json,tempfile,random
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,ROOT)
sys.path.insert(0,os.path.join(ROOT,'benchmarks'))
from adapters.bavaria_funding import parse_measure
from pipeline import run
from engine import trade_opportunities
from quality import report

templates=[
 ("Stadt Teststadt {i}", "1,5 Millionen Euro für den Neubau einer Grundschule mit Sporthalle"),
 ("Gemeinde Kinderort {i}", "1,2 Millionen Euro für die Erweiterung der Kindertageseinrichtung Sonnenweg"),
 ("Landkreis Klinikland {i}", "2,5 Millionen Euro für die Erweiterung des Klinikums Nord"),
 ("Gemeinde Feuerort {i}", "1,1 Millionen Euro für den Neubau eines Feuerwehrhauses"),
]
events=[]; quarantine=[]
for i in range(500):
    auth,body=templates[i%len(templates)]
    line=f"{auth.format(i=i)}: {body}"
    ev,err=parse_measure(line,"https://example.invalid/benchmark","2026-05-18")
    if ev: events.append(ev)
    else: quarantine.append({"line":line,"reason":err})
# add 20 exact duplicates to test event de-duplication
raw=events+events[:20]
with tempfile.TemporaryDirectory() as d:
    projects=run(raw,os.path.join(d,"v04.sqlite"))
    opp=sum(1 for p in projects for _ in trade_opportunities(p))
    unique=len({e["source_id"] for e in raw})
    r=report(len(raw),unique,projects,quarantine,opp)
    assert len(projects)==500, len(projects)
    assert r["duplicate_events"]==20
    assert r["opportunities_generated"]>3000
    print(json.dumps(r,indent=2))
