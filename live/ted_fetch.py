"""Resilient TED Search API v3 fetcher for Opportunity Radar."""
import json, os, time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = "https://api.ted.europa.eu/v3/notices/search"
DEFAULT_QUERY = "RC = DEU AND classification-cpv = 45* SORT BY publication-date DESC"

class LiveTedFetcher:
    def __init__(self, raw_dir, query=DEFAULT_QUERY, page_size=250, retries=3):
        self.raw_dir = raw_dir
        os.makedirs(raw_dir, exist_ok=True)
        self.query = query
        self.page_size = min(int(page_size), 250)
        self.retries = max(1, int(retries))

    def _request(self, page):
        payload = {
            "query": self.query,
            "page": page,
            "limit": self.page_size,
            "scope": "ALL",
            "paginationMode": "PAGE_NUMBER",
            "fields": [
                "publication-number", "title-proc", "notice-title", "publication-date",
                "buyer-name", "buyer-country", "place-of-performance",
                "place-of-performance-city-proc", "place-of-performance-country-proc",
                "classification-cpv", "notice-type"
            ],
        }
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                req = Request(URL, data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"OpportunityRadar/0.9.3"},
                    method="POST")
                with urlopen(req, timeout=90) as response:
                    raw = response.read().decode("utf-8")
                return raw, None
            except HTTPError as ex:
                body = ex.read().decode("utf-8", errors="replace")[:2000]
                last_error = {"type":"http","status":ex.code,"message":str(ex),"body":body,"attempt":attempt}
            except (URLError, TimeoutError, OSError) as ex:
                last_error = {"type":"network","message":repr(ex),"attempt":attempt}
            if attempt < self.retries: time.sleep(attempt * 2)
        return None, last_error

    def fetch(self, target=2000, max_pages=12):
        notices, errors, seen = [], [], set()
        self.duplicate_count=0
        target=max(1,int(target))
        for page in range(1,int(max_pages)+1):
            raw,error=self._request(page)
            if error: errors.append({"page":page,**error}); break
            with open(os.path.join(self.raw_dir,f"ted_page_{page:03d}.json"),"w",encoding="utf-8") as f:f.write(raw)
            try:data=json.loads(raw)
            except json.JSONDecodeError as ex: errors.append({"page":page,"type":"json","message":repr(ex)}); break
            batch=data.get("notices") or data.get("results") or []
            if not isinstance(batch,list): errors.append({"page":page,"type":"schema","message":"TED response contains no notice list"}); break
            for notice in batch:
                if not isinstance(notice,dict):
                    errors.append({"page":page,"type":"schema","message":"Invalid notice"}); continue
                identity=notice.get("publication-number") or notice.get("publicationNumber") or notice.get("id")
                if not identity:
                    errors.append({"page":page,"type":"identity","message":"Notice has no publication identity"}); continue
                key=json.dumps(identity,sort_keys=True)
                if key in seen:
                    self.duplicate_count+=1; continue
                seen.add(key);notices.append(notice)
                if len(notices)>=target:break
            if not batch or len(notices)>=target: break
        return notices[:target], errors
