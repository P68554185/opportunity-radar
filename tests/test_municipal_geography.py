import unittest
from unittest.mock import patch
from geography.dresden import parse_features, area_location, locations
from early.collect import validate_reviewed
class MunicipalGeographyTests(unittest.TestCase):
    def test_wfs_axis_and_invalid_crs(self):
        xml='<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"><wfs:member><plan><gml:posList>51.05 13.73 51.06 13.74</gml:posList></plan></wfs:member></wfs:FeatureCollection>'
        rows,_=parse_features(xml)
        self.assertEqual(rows[0]["bbox"],[13.73,51.05,13.74,51.06])
        with self.assertRaises(ValueError):parse_features(xml.replace("51.05 13.73","13.73 51.05"))
        with self.assertRaises(ValueError):parse_features("<ExceptionReport/>")
    def test_area_uncertainty_covers_corners(self):
        from engine import haversine
        loc=area_location({"bbox":[13.73,51.05,13.74,51.06]},"https://example.invalid/")
        for lat in (51.05,51.06):
            for lon in (13.73,13.74):
                self.assertGreaterEqual(loc["extent_km"],haversine(loc["lat"],loc["lon"],lat,lon))
        self.assertEqual(loc["basis"],"plan_area")
    def test_date_and_project_identity_gate(self):
        doc={"source_url":"https://example.invalid/","published":"2026-03-27","date_anchor":"Dresden, 27.03.2026","records":[{"required_anchor":"Königsbrücker Straße Nord","required_terms":["3068"],"event":{"source_url":"https://example.invalid/","published":"2026-03-27"}}]}
        text="Dresden, 27.03.2026 Plan 3068 Königsbrücker Straße Nord"
        self.assertEqual(len(validate_reviewed(doc,text)),1)
        with self.assertRaises(ValueError):validate_reviewed(doc,text.replace("3068","3000"))
        with self.assertRaises(ValueError):validate_reviewed(doc,text.replace("27.03.2026","01.01.2026"))
    def test_amended_plans_do_not_match_base_identity(self):
        import json
        from pathlib import Path
        import geography.dresden as module
        path=module.ROOT/"real_data/dresden_plan_reference.json"
        if not path.exists():return
        events=[{"source_id":"x","source_type":"municipal_planning","city":"Dresden","project_reference":"DRESDEN-PLAN-3065.999"}]
        self.assertEqual(locations(events),{})
