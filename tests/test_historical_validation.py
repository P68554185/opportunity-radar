import json
import unittest
from pathlib import Path
from lifecycle.matching import evaluate

ROOT=Path(__file__).resolve().parents[1]
class HistoricalTests(unittest.TestCase):
    def test_real_cases_do_not_claim_live_accuracy(self):
        events=json.loads((ROOT/"real_data/historical_early_events.json").read_text())
        notices=json.loads((ROOT/"real_data/historical_procurement_notices.json").read_text())["notices"]
        alsfeld=next(e for e in events if e["city"]=="Alsfeld")
        tender=next(n for n in notices if n["source_id"]=="TED-660397-2026")
        r=evaluate(alsfeld,tender)
        self.assertEqual(r["status"],"confirmed")
        self.assertEqual(r["publication_interval_days"],1156)
        warburg=next(e for e in events if e["city"]=="Warburg")
        award=next(n for n in notices if n["city"]=="Warburg")
        self.assertEqual(evaluate(warburg,award)["status"],"probable")
        th=next(e for e in events if e["city"]=="Köln")
        later=next(n for n in notices if n["city"]=="Köln")
        self.assertIsNone(evaluate(th,later)["publication_interval_days"])

    def test_known_real_negative_controls_never_confirm(self):
        events=json.loads((ROOT/"real_data/historical_early_events.json").read_text())
        notices=json.loads((ROOT/"real_data/historical_procurement_notices.json").read_text())["notices"]
        for early in events:
            for later in notices:
                if early["city"]!=later["city"]:
                    self.assertEqual(evaluate(early,later)["status"],"unlinked")
