# Opportunity Radar v0.7.1 — GitHub Edition

This version follows the ATLAS deployment workflow:
1. Download the complete ZIP from ChatGPT.
2. Upload/replace the repository files in GitHub.
3. GitHub Pages publishes `/docs` as the development website.
4. GitHub Actions runs the live TED ingestion in the cloud.
5. The website reads `docs/data/status.json` and displays the latest development/data state.

## First GitHub setup
Create a new repository, upload the complete contents of this ZIP to the repository root,
and use the `main` branch.

In GitHub open **Settings → Pages** and choose **GitHub Actions** as the source.

Then open **Actions → Live Data Ingestion → Run workflow**.
No Python installation or administrator rights are needed on your PC.

## Files
- `docs/` — public development website
- `.github/workflows/pages.yml` — website deployment
- `.github/workflows/live-ingestion.yml` — scheduled/manual TED ingestion
- `github_status.py` — transfers engine state to website
- `real_data/` — official raw/normalized datasets
- `reports/` — benchmark/run reports
- all v0.7 engine files remain included

## Development rule
Every future release will again be supplied as a complete downloadable ZIP so it can be
uploaded/replaced in GitHub in the same way.
