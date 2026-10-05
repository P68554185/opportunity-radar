"""TED Search API adapter for Opportunity Engine v0.3.

Official API:
POST https://api.ted.europa.eu/v3/notices/search
Search of published notices is anonymous. This adapter intentionally keeps the
query and response field selection configurable because TED's field catalogue evolves.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Any
import json
from urllib.request import Request, urlopen

TED_SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"

DEFAULT_FIELDS = [
    "publication-number", "notice-title", "publication-date",
    "buyer-name", "place-of-performance", "classification-cpv",
    "estimated-value-procurement", "notice-type",
]

@dataclass
class TedConfig:
    query: str
    page_size: int = 100
    fields: list[str] | None = None

class TedSearchAdapter:
    def __init__(self, config: TedConfig):
        self.config = config

    def build_payload(self, page: int = 1) -> dict:
        return {
            "query": self.config.query,
            "page": page,
            "limit": self.config.page_size,
            "fields": self.config.fields or DEFAULT_FIELDS,
        }

    def fetch_page(self, page: int = 1) -> dict:
        payload = json.dumps(self.build_payload(page)).encode("utf-8")
        req = Request(TED_SEARCH_URL, data=payload,
                      headers={"Content-Type":"application/json","Accept":"application/json"},
                      method="POST")
        with urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))

    @staticmethod
    def _first(obj: dict, *keys, default=""):
        for k in keys:
            v = obj.get(k)
            if isinstance(v, list) and v:
                return v[0]
            if v not in (None, "", []):
                return v
        return default

    def normalize_notice(self, n: dict) -> dict:
        # Defensive mapping: exact returned field names can differ by selected TED fields.
        notice_id = str(self._first(n, "publication-number", "publicationNumber", "notice-id", "id"))
        title = str(self._first(n, "notice-title", "title", default=f"TED notice {notice_id}"))
        published = str(self._first(n, "publication-date", "publicationDate"))
        buyer = str(self._first(n, "buyer-name", "buyerName"))
        place = self._first(n, "place-of-performance", "placeOfPerformance", default="")
        cpv = self._first(n, "classification-cpv", "cpv", default=[])
        value = self._first(n, "estimated-value-procurement", "estimatedValue", default=None)
        notice_type = str(self._first(n, "notice-type", "noticeType", default="tender"))
        body = json.dumps({"cpv":cpv,"place":place,"notice_type":notice_type},
                          ensure_ascii=False)
        return {
            "source_id": f"TED-{notice_id}",
            "source_type": "ted_notice",
            "source_url": f"https://ted.europa.eu/en/notice/-/detail/{notice_id}" if notice_id else "https://ted.europa.eu/",
            "published": published,
            "title": title,
            "body": body,
            "authority": buyer,
            "city": "",
            "region": "",
            "country": "",
            "project_type": "",
            "phase": "tender",
            "value_eur": float(value) if isinstance(value,(int,float)) else None,
            "external_id": notice_id,
        }

    def iter_normalized(self, max_pages: int = 1) -> Iterable[dict]:
        for page in range(1, max_pages+1):
            data = self.fetch_page(page)
            notices = data.get("notices") or data.get("results") or []
            if not notices:
                return
            for n in notices:
                yield self.normalize_notice(n)
