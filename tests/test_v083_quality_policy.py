"""Legacy entry point now exercises the actual shared evidence policy."""
import unittest
from intelligence.evidence import classify_evidence

class QualityPolicyTests(unittest.TestCase):
    def test_high_legacy_score_cannot_open_customer_gate(self):
        status,_=classify_evidence({"project_type":"school","trades":["electrical"],
            "title":"Grundschule Elektroarbeiten","cpv":[],"confidence":1,"score":100})
        self.assertNotEqual(status,"CONFIDENT")
