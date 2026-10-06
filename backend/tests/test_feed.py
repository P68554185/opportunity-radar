import copy
import unittest
from unittest.mock import patch
from backend.feed import FeedCache, validate
from intelligence.evidence import POLICY_VERSION

def sample():
    return {"policy_version": POLICY_VERSION, "count": 1, "opportunities": [
        {"id": "one", "title": "Schulbau", "trades": ["electrical"],
         "quality_status": "CONFIDENT", "source_url": "https://ted.europa.eu/en/notice/1"}]}, {
        "opportunities": 1, "last_sync": "2026-10-06T09:00:00"}

class FeedTests(unittest.TestCase):
    def test_rejects_unqualified_duplicate_and_untrusted_rows(self):
        for change in ("quality", "duplicate", "source", "policy", "count"):
            feed,status = sample()
            if change == "quality": feed["opportunities"][0]["quality_status"] = "REVIEW"
            if change == "source": feed["opportunities"][0]["source_url"] = "https://attacker.example"
            if change == "policy": feed["policy_version"] = "unknown"
            if change == "count": status["opportunities"] = 2
            if change == "duplicate":
                feed["opportunities"].append(copy.deepcopy(feed["opportunities"][0]))
                feed["count"] = status["opportunities"] = 2
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(feed,status)

    def test_atomic_refresh_and_failure_retains_previous(self):
        cache = FeedCache(); old = sample(); cache.snapshot = old
        feed,status = sample(); status["last_sync"] = "2026-10-06T10:00:00"
        with patch.dict("os.environ", {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}):
            with patch("backend.feed.download", side_effect=[feed,status]) as fetch:
                self.assertEqual(cache.get(), (feed,status))
                cache.get(); self.assertEqual(fetch.call_count,2)
            cache.next_refresh = 0
            with patch("backend.feed.download", side_effect=TimeoutError):
                self.assertEqual(cache.get(),(feed,status))
            cache.next_refresh = 0
            with patch("backend.feed.download", side_effect=list(old)):
                self.assertEqual(cache.get(),(feed,status))
