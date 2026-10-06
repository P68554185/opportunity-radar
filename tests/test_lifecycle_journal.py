import unittest
from lifecycle.journal import observe,tracked_lead,preserve_confirmed
class JournalTests(unittest.TestCase):
    def test_observation_never_backdates_or_resets(self):
        state=observe({},[dict(source_id="E",published="2023-07-27")],now="2026-10-06T09:00:00Z")
        observe(state,[dict(source_id="E",published="2023-07-27")],now="2026-10-07T09:00:00Z")
        self.assertEqual(state["E"]["first_tracked_seen_at"],"2026-10-06T09:00:00Z")
        self.assertIsNone(tracked_lead(state["E"],dict(published="2026-09-25")))
        self.assertEqual(tracked_lead(state["E"],dict(published="2026-11-05")),30)
    def test_only_confirmed_acquired_notice_is_archived(self):
        notice=dict(source_id="TED-1",title="Real",evidence=dict(policy_version="v1"))
        self.assertEqual(preserve_confirmed({},[notice],[]),{})
        archive=preserve_confirmed({},[notice],[dict(source_ids=["E","TED-1"])],now="2026-10-06T09:00:00Z")
        preserve_confirmed(archive,[dict(notice,title="Corrected")],[dict(source_ids=["E","TED-1"])],now="2026-10-07T09:00:00Z")
        self.assertEqual(archive["TED-1"]["first_tracked_seen_at"],"2026-10-06T09:00:00Z")
        self.assertEqual(archive["TED-1"]["notice"]["title"],"Corrected")
