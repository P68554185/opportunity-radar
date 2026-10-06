"""Read-only refresh of the published, quality-screened feed; no customer data leaves host."""
import json
import logging
import os
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from intelligence.evidence import POLICY_VERSION

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "https://p68554185.github.io/opportunity-radar/data/"
log = logging.getLogger(__name__)

def validate(feed, status):
    rows = feed.get("opportunities")
    if feed.get("policy_version") != POLICY_VERSION:
        raise ValueError("Feed policy mismatch")
    if not isinstance(rows, list) or not rows or feed.get("count") != len(rows):
        raise ValueError("Incomplete feed")
    if status.get("opportunities") != len(rows):
        raise ValueError("Feed and status differ")
    identities = set()
    for row in rows:
        identity = row.get("id")
        source = urlparse(row.get("source_url", ""))
        allowed = ("ted.europa.eu",) if row.get("quality_status") == "CONFIDENT" else ("www.stmfh.bayern.de", "hibb.hamburg.de", "buergerbeteiligung.sachsen.de")
        if (row.get("quality_status") not in ("CONFIDENT", "VERIFIED_EARLY")
                or not isinstance(identity, str) or not identity or identity in identities
                or not isinstance(row.get("trades"), list)
                or not row.get("title") or source.scheme != "https" or source.hostname not in allowed):
            raise ValueError("Unqualified feed row")
        identities.add(identity)
    return feed, status

def download(name):
    request = Request(PUBLIC + name, headers={"Cache-Control": "no-cache", "User-Agent": "BauRadar/1"})
    with urlopen(request, timeout=10) as response:
        if response.geturl().split("/data/")[0] != PUBLIC.split("/data/")[0]:
            raise ValueError("Unexpected feed redirect")
        raw = response.read(12_000_001)
        if len(raw) > 12_000_000:
            raise ValueError("Feed exceeds size limit")
        return json.loads(raw)

class FeedCache:
    def __init__(self):
        self.lock = threading.Lock()
        self.snapshot = None
        self.next_refresh = 0

    def get(self):
        with self.lock:
            if self.snapshot is None:
                data = ROOT / "docs" / "data"
                self.snapshot = validate(json.loads((data / "bauradar_feed.json").read_text()),
                                         json.loads((data / "status.json").read_text()))
            if os.environ.get("RENDER_EXTERNAL_URL") and time.monotonic() >= self.next_refresh:
                try:
                    candidate = validate(download("bauradar_feed.json"), download("status.json"))
                    # Never replace a newer accepted snapshot with an older published deployment.
                    old_sync = str(self.snapshot[1].get("last_sync", ""))
                    new_sync = str(candidate[1].get("last_sync", ""))
                    if not new_sync or (old_sync and new_sync < old_sync):
                        raise ValueError("Feed timestamp regressed")
                    self.snapshot = candidate
                    self.next_refresh = time.monotonic() + 900
                except Exception:
                    log.warning("Public feed refresh failed; keeping the last validated snapshot.")
                    self.next_refresh = time.monotonic() + 60
            return self.snapshot

cache = FeedCache()
