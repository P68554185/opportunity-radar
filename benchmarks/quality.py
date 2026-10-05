"""Quality metrics for ingestion runs."""
from collections import Counter

def report(raw_count, unique_event_count, projects, quarantine, opportunities=0):
    duplicates=max(0,raw_count-unique_event_count)
    types=Counter(getattr(p,"project_type","unknown") for p in projects)
    phases=Counter(getattr(p,"phase","unknown") for p in projects)
    return {
      "raw_records":raw_count,
      "unique_events":unique_event_count,
      "duplicate_events":duplicates,
      "duplicate_event_rate":round(duplicates/raw_count,4) if raw_count else 0,
      "master_projects":len(projects),
      "quarantine_records":len(quarantine),
      "quarantine_rate":round(len(quarantine)/raw_count,4) if raw_count else 0,
      "opportunities_generated":opportunities,
      "project_types":dict(types),
      "phases":dict(phases),
    }
