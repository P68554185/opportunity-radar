import unittest
from intelligence.evidence import evidence_for, classify_evidence
from intelligence.build import lifecycle_link_score, enrich
from lifecycle.graph import classify_link

class EvidenceTests(unittest.TestCase):
    def record(self, **changes):
        record = {"title": "Neubau Grundschule Elektroarbeiten", "project_type": "school",
            "trades": ["electrical"], "cpv": ["45310000"], "country": "DE",
            "source_url": "https://ted.europa.eu/en/notice/-/detail/1",
            "classification_confidence": .85, "score": 1}
        return dict(record, **changes)

    def test_commercial_score_does_not_control_eligibility(self):
        self.assertEqual(classify_evidence(self.record(score=1))[0], "CONFIDENT")
        self.assertEqual(classify_evidence(self.record(score=100, classification_confidence=.4))[0], "REVIEW")

    def test_legacy_confidence_never_substitutes_for_evidence(self):
        r=self.record(); r.pop("classification_confidence"); r["confidence"]=1
        self.assertEqual(classify_evidence(r)[0], "REVIEW")

    def test_empty_invalid_or_nonconstruction_cpv(self):
        for cpv in ([], "", ["garbage"], ["72000000"], ["45"]):
            with self.subTest(cpv=cpv):
                self.assertNotEqual(classify_evidence(self.record(cpv=cpv))[0], "CONFIDENT")

    def test_country_source_and_nonfinite_confidence(self):
        for changes in ({"country": ""}, {"country": "AT"}, {"source_url": "javascript:alert(1)"},
                        {"classification_confidence": float("nan")}, {"classification_confidence": float("inf")}):
            self.assertNotEqual(classify_evidence(self.record(**changes))[0], "CONFIDENT")

    def test_cpv_only_project_is_review(self):
        p,t,c,e=evidence_for("Bauleistungen Los 1", ["45211000", "45310000"])
        self.assertLess(c, .7)

    def test_text_and_structured_evidence(self):
        p,t,c,e=evidence_for("Neubau Grundschule Elektroarbeiten", ["45310000"])
        self.assertEqual(p, "school"); self.assertIn("electrical",t); self.assertGreaterEqual(c,.7)

    def test_enrichment_separates_scores(self):
        import json
        r=enrich({"title":"Neubau Grundschule Elektroarbeiten","body":json.dumps({"cpv":["45310000"]})})
        self.assertEqual(r["classification_confidence"],.85)
        self.assertNotEqual(r["confidence"],r["score"]/100)

class LifecycleTests(unittest.TestCase):
    def test_contradictions(self):
        a={"city":"Roth","project_type":"school","title":"Grundschule"}
        self.assertEqual(lifecycle_link_score(a,dict(a,city="Naila"))[0],0)
        self.assertEqual(lifecycle_link_score(a,dict(a,project_type="hospital"))[0],0)

    def test_ambiguity_is_never_auto_linked(self):
        self.assertEqual(classify_link(.95,.01),"review")
        self.assertEqual(classify_link(.95,.12),"auto_link")

if __name__=="__main__": unittest.main()
