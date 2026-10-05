"""CPV regression cases grounded in the official EU code list.
Source: https://docs.ted.europa.eu/eforms/latest/reference/code-lists/cpv.html
"""
import unittest
from classification.rules import classify
from intelligence.evidence import evidence_for

class CPVTradeSemantics(unittest.TestCase):
    def test_university_is_not_a_school_substring(self):
        project,_=classify("Neubau Hochschule Elektroarbeiten",["45310000"])
        self.assertEqual(project,"university_research")

    def test_standalone_sports_hall_is_not_a_school(self):
        project,_=classify("Neubau Sporthalle Elektroarbeiten",["45310000"])
        self.assertEqual(project,"sports_leisure")

    def test_ambiguous_campus_requires_structured_or_explicit_context(self):
        project,_=classify("Campus Elektroarbeiten",["45310000"])
        self.assertEqual(project,"")

    def test_general_insulation_is_not_fire_prevention(self):
        for code in ("45320000","45321000","45323000"):
            _,trades=classify("",[code])
            self.assertIn("insulation",trades)
            self.assertNotIn("fire_protection",trades)

    def test_fencing_and_railings_are_not_fire_prevention(self):
        for code in ("45340000","45341000","45342000"):
            _,trades=classify("",[code])
            self.assertIn("fencing",trades)
            self.assertNotIn("fire_protection",trades)

    def test_specific_fire_prevention_prefix_is_preserved(self):
        _,trades=classify("",["45343000","45343200"])
        self.assertIn("fire_protection",trades)
        self.assertNotIn("fencing",trades)

    def test_sanitary_notice_does_not_imply_heating_or_air_conditioning(self):
        _,trades=classify("Neubau Grundschule Sanitärinstallation",["45332000"])
        self.assertIn("plumbing",trades)
        self.assertNotIn("hvac",trades)

    def test_evidence_uses_correct_trade_dimension(self):
        p,trades,strength,_=evidence_for("Neubau Grundschule Wärmedämmarbeiten",["45321000"])
        self.assertEqual(p,"school")
        self.assertIn("insulation",trades)
        self.assertNotIn("fire_protection",trades)
        self.assertGreaterEqual(strength,.7)

if __name__=="__main__":unittest.main()
