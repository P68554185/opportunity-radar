import unittest
from intelligence.customer_feed import collapse_confirmed

class GroupingTests(unittest.TestCase):
    def notice(self,sid,trade,phase="tender"):
        return dict(id=sid,source_id=sid,title="Los",published="2026-10-06",quality_status="CONFIDENT",trades=[trade],phase=phase)
    def timeline(self):
        return dict(master_project_id="PRJ-1",title="Neubau Krankenhaus",
            history=[dict(source_id="EARLY-1"),dict(source_id="TED-1"),dict(source_id="TED-2")])
    def test_only_confirmed_timeline_collapses_and_preserves_aliases(self):
        records=[self.notice("TED-1","facade"),self.notice("TED-2","electrical"),self.notice("TED-3","roof")]
        self.assertEqual(len(collapse_confirmed(records,[])),3)
        merged=collapse_confirmed(records,[self.timeline()])
        self.assertEqual(len(merged),2)
        project=next(r for r in merged if r["id"]=="PRJ-1")
        self.assertEqual(project["aliases"],["TED-1","TED-2"])
        self.assertEqual(project["trades"],["electrical","facade"])
        self.assertEqual(project["procurement_notice_count"],2)
    def test_one_award_does_not_mark_all_other_lots_awarded(self):
        records=[self.notice("TED-1","facade"),self.notice("TED-2","electrical","award")]
        self.assertEqual(collapse_confirmed(records,[self.timeline()])[0]["phase"],"procurement")
