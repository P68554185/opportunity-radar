import unittest
from live.normalize import normalize,notice_phase

class NoticePhaseTests(unittest.TestCase):
    def test_unknown_type_is_not_a_tender(self):
        self.assertEqual(notice_phase(""),"unknown")
        self.assertEqual(notice_phase("unexpected-type"),"unknown")
    def test_known_procurement_phases(self):
        self.assertEqual(notice_phase("cn-standard"),"tender")
        self.assertEqual(notice_phase("can-standard"),"award")
        self.assertEqual(notice_phase("pin-only"),"prior_information")
        self.assertEqual(notice_phase("pin-cfc-standard"),"tender")
    def test_buyer_name_does_not_define_project_type(self):
        r=normalize({"publication-number":"1","title-proc":"Elektroarbeiten Los 1",
            "buyer-name":"Grundschule Sonnenberg","classification-cpv":["45310000"],
            "notice-type":"cn-standard"})
        self.assertEqual(r["project_type"],"")
        self.assertIn("electrical",r["_trades"])

if __name__=="__main__": unittest.main()
