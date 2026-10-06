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
