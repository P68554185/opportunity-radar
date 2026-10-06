import unittest
from lifecycle.matching import evaluate, history

class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.a = dict(source_id="EARLY-1", title="Neubau Grundschule Sonnenberg Nord",
            city="Roth", project_type="school", authority="Stadt Roth",
            published="2023-03-15", source_url="https://example.org/early", phase="funding")
        self.b = dict(self.a, source_id="TED-1", published="2023-08-20+02:00",
            phase="tender", title="Grundschule Sonnenberg Nord - Elektroarbeiten")

    def test_independent_identity_and_real_dates(self):
        r=evaluate(self.a,self.b)
        self.assertEqual(r["status"],"confirmed")
        self.assertEqual(r["publication_interval_days"],158)
        self.assertTrue(r["evidence"]["same_authority"])

    def test_generic_city_and_type_never_confirm(self):
        a=dict(self.a,title="Neubau Grundschule")
        b=dict(self.b,title="Grundschule Elektroarbeiten")
        self.assertEqual(evaluate(a,b)["status"],"unlinked")

    def test_each_contradiction_blocks_even_identical_names(self):
        for changes in [dict(city="Naila"),dict(project_type="hospital"),
            dict(published="2022-01-01"),dict(published=""),dict(phase="funding")]:
            with self.subTest(changes=changes):
                self.assertEqual(evaluate(self.a,dict(self.b,**changes))["status"],"unlinked")

    def test_building_component_and_address_conflicts(self):
        a=dict(self.a,title="Campus Deutz Gebäude B",project_address="Deutz 1")
        b=dict(self.b,title="Campus Deutz Gebäude C",project_address="Deutz 1")
        self.assertIn("different_building_component",evaluate(a,b)["blockers"])
        b=dict(b,title=a["title"],project_address="Deutz 2")
        self.assertIn("different_project_address",evaluate(a,b)["blockers"])

    def test_unknown_authority_is_not_identity(self):
        self.assertEqual(evaluate(self.a,dict(self.b,authority=""))["status"],"probable")
        self.assertEqual(evaluate(self.a,self.b,ambiguous=True)["status"],"unlinked")

    def test_award_is_not_tender_lead_and_history_is_chronological(self):
        result=evaluate(self.a,dict(self.b,phase="award"))
        self.assertEqual(result["interval_endpoint"],"award")
        self.assertEqual(history([self.b,self.a])[0]["source_id"],"EARLY-1")

    def test_shared_stage_does_not_hide_different_buildings(self):
        a=dict(self.a,title="Campus Deutz Gebäude B Bauabschnitt 1")
        b=dict(self.b,title="Campus Deutz Gebäude C Bauabschnitt 1")
        self.assertIn("different_building_component",evaluate(a,b)["blockers"])
