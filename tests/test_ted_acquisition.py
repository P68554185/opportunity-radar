import json
import tempfile
import unittest
from live.ted_fetch import LiveTedFetcher

class AcquisitionTests(unittest.TestCase):
    def test_overlapping_pages_are_deduplicated_and_backfilled(self):
        with tempfile.TemporaryDirectory() as d:
            fetcher=LiveTedFetcher(d,page_size=2)
            pages={1:[{"publication-number":"a"},{"publication-number":"b"}],
                2:[{"publication-number":"b"},{"publication-number":"c"}],
                3:[{"publication-number":"d"}]}
            fetcher._request=lambda p:(json.dumps({"notices":pages.get(p,[])}),None)
            records,errors=fetcher.fetch(target=4,max_pages=3)
            self.assertEqual([r["publication-number"] for r in records],["a","b","c","d"])
            self.assertEqual(errors,[]);self.assertEqual(fetcher.duplicate_count,1)

    def test_missing_identity_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            fetcher=LiveTedFetcher(d)
            fetcher._request=lambda p:(json.dumps({"notices":[{"title":"unknown"}]}),None)
            records,errors=fetcher.fetch(target=1,max_pages=1)
            self.assertEqual(records,[]);self.assertEqual(errors[0]["type"],"identity")

if __name__=="__main__": unittest.main()
