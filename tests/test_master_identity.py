import unittest
from engine import ingest, SourceEvent, resolve_project

def event(**changes):
    return dict(source_id="a",source_type="planning",source_url="https://example.org/a",
        published="2023-01-01",title="Grundschule Sonnenberg Nord",body="",
        city="Roth",project_type="school",authority="Stadt Roth",phase="funding",**changes)
class MasterTests(unittest.TestCase):
    def test_different_addresses_never_merge(self):
        a=event(); b=dict(a,source_id="b",source_url="https://example.org/b")
        a["project_address"]="Straße 1";b["project_address"]="Straße 2"
        self.assertEqual(len(ingest([a,b])),2)

    def test_specific_project_history_and_chronology(self):
        a=event();b=dict(a,source_id="b",source_url="https://example.org/b",published="2024-01-01",phase="object_planning")
        projects=ingest([b,a,b])
        self.assertEqual(len(projects),1)
        self.assertEqual(len(projects[0].history),2)
        self.assertEqual(projects[0].phase,"object_planning")

    def test_distinct_named_schools_and_campus_buildings(self):
        a=event(); b=dict(a,source_id="b",source_url="https://example.org/b",title="Grundschule Birkenhain Ost")
        self.assertEqual(len(ingest([a,b])),2)
        a["title"]="Campus Deutz Gebäude B";b["title"]="Campus Deutz Gebäude C"
        self.assertEqual(len(ingest([a,b])),2)

    def test_replay_finds_original_event_even_when_another_candidate_is_closer(self):
        a=event(); projects=ingest([a])
        self.assertIs(resolve_project(projects,SourceEvent(**a)),projects[0])
        self.assertEqual(len(projects),1)

    def test_same_generic_school_action_is_not_a_shared_project_name(self):
        a=event();a["title"]="Zu- und Ersatzbau Gymnasium Hochrad";a["city"]="Hamburg"
        b=dict(a,source_id="b",source_url="https://example.org/b",title="Zu- und Ersatzbau Gymnasium Hummelsbüttel und Grundschule Grützmühlenweg")
        self.assertEqual(len(ingest([a,b])),2)
