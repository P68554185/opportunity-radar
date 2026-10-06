"""Public evidence journal; tracked observation dates are never backdated."""
from datetime import datetime,timezone
from lifecycle.matching import published

def observe(state,events,now=None):
    now=now or datetime.now(timezone.utc).isoformat()
    for event in events:
        state.setdefault(event["source_id"],{"first_tracked_seen_at":now,
            "publication_date":event.get("published"),
            "note":"First observation tracked by this journal; earlier untracked discovery is unknown."})
    return state

def tracked_lead(observation,notice):
    first=published(observation.get("first_tracked_seen_at"))
    later=published(notice.get("published"))
    if not first or not later or later<=first: return None
    return (later-first).days

def preserve_confirmed(archive,current,confirmed,now=None):
    now=now or datetime.now(timezone.utc).isoformat()
    ids={pair["source_ids"][1] for pair in confirmed}
    for notice in current:
        sid=notice["source_id"]
        if sid in ids:
            previous=archive.get(sid,{})
            archive[sid]={"first_tracked_seen_at":previous.get("first_tracked_seen_at",now),
                "quality_policy_version":notice.get("evidence",{}).get("policy_version"),
                "notice":notice}
    return archive
