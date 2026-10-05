"""Cached geocoding abstraction.

Production should use a licensed geocoding provider with terms appropriate for
commercial use. v0.3 deliberately does not hard-wire a free public endpoint.
"""
from dataclasses import dataclass
import sqlite3

@dataclass
class GeoPoint:
    lat: float
    lon: float
    provider: str

class GeocodeCache:
    def __init__(self, db_path="geocode_cache.sqlite"):
        self.db=sqlite3.connect(db_path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS geocode_cache(
          query TEXT PRIMARY KEY, lat REAL NOT NULL, lon REAL NOT NULL,
          provider TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        self.db.commit()

    def get(self, query):
        row=self.db.execute("SELECT lat,lon,provider FROM geocode_cache WHERE query=?",(query,)).fetchone()
        return GeoPoint(*row) if row else None

    def put(self, query, point):
        self.db.execute("""INSERT INTO geocode_cache(query,lat,lon,provider)
          VALUES(?,?,?,?) ON CONFLICT(query) DO UPDATE SET
          lat=excluded.lat,lon=excluded.lon,provider=excluded.provider,
          updated_at=CURRENT_TIMESTAMP""",(query,point.lat,point.lon,point.provider))
        self.db.commit()
