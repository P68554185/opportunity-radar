import unittest
from intelligence.customer_feed import next_action

class CustomerActionsTests(unittest.TestCase):
    def test_preannouncement_is_not_presented_as_an_award(self):
        action=next_action("prior_information")
        self.assertIn("Vorankündigung",action)
        self.assertNotIn("Zuschlag",action)
        self.assertNotIn("Auftragnehmer",action)
    def test_unknown_phase_does_not_invent_tender_or_award(self):
        action=next_action("unknown")
        self.assertIn("Projektphase",action)
        self.assertNotIn("Zuschlag",action)
        self.assertNotIn("Vergabeunterlagen",action)
    def test_active_tender_has_document_check(self):
        self.assertIn("Vergabeunterlagen",next_action("tender"))
    def test_award_has_award_check(self):
        self.assertIn("Zuschlag",next_action("award"))

if __name__=="__main__":unittest.main()
