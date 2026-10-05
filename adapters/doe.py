"""German public procurement (DÖE/Bekanntmachungsservice) adapter.

The official service exposes open-data reuse in eForms-DE, CSV and OCDS.
v0.4 deliberately separates transport from normalization: feed OCDS JSON records or CSV
rows downloaded from the official open-data interface into these functions.
"""
from __future__ import annotations
import json, csv, io

class DoeAdapter:
    @staticmethod
    def _amount(v):
        try: return float(v) if v not in ("",None) else None
        except (TypeError,ValueError): return None

    def normalize_ocds_release(self, r: dict) -> dict:
        tender=r.get("tender") or {}
        buyer=r.get("buyer") or {}
        parties=r.get("parties") or []
        addr={}
        for p in parties:
            if p.get("id")==buyer.get("id"):
                addr=p.get("address") or {}; break
        value=(tender.get("value") or {}).get("amount")
        title=tender.get("title") or r.get("ocid") or "DÖE notice"
        status=tender.get("status","")
        phase="award" if r.get("awards") else "tender"
        return {
          "source_id":"DOE-"+str(r.get("ocid") or r.get("id") or ""),
          "source_type":"doe_ocds",
          "source_url":str(r.get("url") or r.get("source_url") or ""),
          "published":str(r.get("date") or ""),
          "title":str(title),
          "body":json.dumps({"description":tender.get("description",""),
                             "procurementMethod":tender.get("procurementMethod",""),
                             "status":status},ensure_ascii=False),
          "authority":str(buyer.get("name") or ""),
          "city":str(addr.get("locality") or ""),
          "region":str(addr.get("region") or ""),
          "country":str((addr.get("countryName") or "DE")),
          "project_type":"",
          "phase":phase,
          "value_eur":self._amount(value),
          "external_id":str(r.get("ocid") or r.get("id") or ""),
        }

    def normalize_csv(self, text: str):
        for row in csv.DictReader(io.StringIO(text)):
            low={k.lower():v for k,v in row.items()}
            yield {
              "source_id":"DOE-"+str(low.get("id") or low.get("ocid") or ""),
              "source_type":"doe_csv",
              "source_url":str(low.get("url") or ""),
              "published":str(low.get("date") or low.get("publicationdate") or ""),
              "title":str(low.get("title") or low.get("tendertitle") or "DÖE notice"),
              "body":json.dumps(row,ensure_ascii=False),
              "authority":str(low.get("buyer") or low.get("buyername") or ""),
              "city":str(low.get("city") or low.get("locality") or ""),
              "region":str(low.get("region") or ""),
              "country":str(low.get("country") or "DE"),
              "project_type":"",
              "phase":"tender",
              "value_eur":self._amount(low.get("value") or low.get("amount")),
              "external_id":str(low.get("ocid") or low.get("id") or ""),
            }
