# EARLY / Lifecycle: evidence and delivery ledger

Baseline 2026-10-06: 2,000 unique TED notices, 1,926 classified opportunities,
654 qualified TED cards, 37 curated early signals / 36 master projects; zero legacy links.
Published customer feed: 690 cards. Existing CI and Pages/Render checks green.

## New historical audit
Run `python lifecycle/validate_history.py`; report is internal in `reports/`.
Actual acquired TED notice facts are frozen separately, so the rolling 2,000-notice
window cannot silently erase the selected historical examples.
Sources are primary public hospital, municipality and university publications.
Only minimal factual summaries are stored; publication and acquisition are separate.

- Alsfeld: primary hospital announcement 2023-07-27, selected later metal/glass facade notices September 2026.
- Warburg: municipal funding/spatenstich publication 2024-11-19, selected later award October 2026.
  Different issuer/buyer: probable only, no fabricated identity confirmation.
- TH Köln: documented event 2023-06-19, webpage publication unproven.
  No guessed publication date or lead calculation.

Name, city, type, construction address/reference, owner, building component and
chronology are explainable inputs. Unknown fields never provide positive evidence.
Conflicting cities, types, addresses, buildings or dates block links.
Candidates/probable results stay internal; no score is labelled a probability.
An office address must never masquerade as a construction address.

This small, deliberately selected set proves technical replay and provides real
examples. It cannot measure accuracy, precision, recall, missing matches or
prospectively observed detection lead. A publication interval to a selected lot is
not a guaranteed lead before the project's first tender.

## Remaining block acceptance
Reproducible source discovery/collection, broader active sources, conservative
master integration, customer project history, independent labelled validation,
CI/main integration and post-deployment checks are still open.

## Implemented second milestone (PR #8)
- Active corpus now adds 13 hospital / nursing-school construction measures and
  six specifically announced Hamburg school building projects.
- Primary-source refresh checks publication anchors and reviewed project anchors;
  bounded official press discovery accepts only dated construction measures with
  unambiguous municipality, otherwise queues them internally.
- HTTPS same-host redirects, robots policy, time/size/request bounds, source hashes,
  observed_at and safe retention prevent blind imports and data loss on outages.
- Master replay searches all prior event memberships; conflicting construction
  addresses, explicit references and building components block merges. Specific
  names are required; history and current phase follow publication chronology.
- Lifecycle computation now runs after the customer qualification gate, grouping
  ambiguous matches by master instead of competing procurement lots.
- Only confirmed source histories are passed to customer cards, with plain dates,
  phases and original-source links. Candidates and probabilities are not shown.
- Real negative controls and known-positive replay counts are explicit; no accuracy,
  precision, recall or live lead is claimed for this deliberately selected set.

Still limited: two active federal states, manifest-reviewed layouts for Hamburg
and hospital programs, no address/geocode completeness, no independent representative
gold dataset, no guarantee of first-tender coverage. Network failures retain previously
verified sources and are reported internally rather than fabricated as successful refresh.
Render requires deployment of the extended source host allowlist before accepting
Hamburg cards; the previous server safely retains its last validated feed meanwhile.

## Persistence and customer grouping
Confirmed qualified TED notices are retained in a public evidence archive with
the evidence policy version and first tracked observation time. Future runs
re-evaluate archived and current notice facts; publication history survives the
rolling acquisition window. Historical facts are not automatically reintroduced
as current customer opportunities.
The observation ledger records now, never a historical publication date. A
tracked lead is reported only where a later publication follows that recorded
observation; it is still a lead to that notice, not proof of the first tender.
Confirmed notices collapse to one customer master card with a union of actual
qualified notice trades and source links; old watched notice IDs remain usable.
Mixed tender/award lots are labelled as published procurements rather than
incorrectly marking the entire project awarded.
