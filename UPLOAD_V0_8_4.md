
# v0.8.4 Full Dataset Quality Gate
- Validator refuses the 50-card website feed.
- Uses a complete normalized live dataset (>=100 records).
- Strict CONFIDENT / REVIEW / UNKNOWN evidence gate.
- CONFIDENT requires project type + trade + CPV + textual evidence + confidence >= 0.70.
- Generates deterministic stratified audit sample up to 60 records.
- Verifies gate totals equal evaluated records.
- Website/status version corrected to 0.8.4.
- Stable GitHub workflow remains unchanged.

Expected log section:
=== Full dataset quality gate ===
