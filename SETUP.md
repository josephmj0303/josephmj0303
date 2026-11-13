# Static GitHub Activity Graph replacement

This bundle replaces the external `github-readme-activity-graph.vercel.app` image with an SVG generated and stored in your own profile repository.

## Files
- `scripts/generate_activity_graph.py` — fetches the public contribution calendar through GitHub GraphQL and renders a dark-themed SVG.
- `.github/workflows/update-activity-graph.yml` — updates the SVG daily and supports manual runs.
- `README-section.md` — replacement for the existing GitHub Stats section.

## Setup

1. In the repository `josephmj0303/josephmj0303`, add the script and workflow at the exact paths shown in this bundle.
2. Create a GitHub Personal Access Token (classic) with the `read:user` scope. Store it in the profile repository as an Actions secret named `GH_ACTIVITY_TOKEN`.
   - Do not put the token in the README, script, or workflow.
   - The workflow's `GITHUB_TOKEN` is used only to commit the generated SVG; repository `contents: write` permission is enabled.
3. In the repository settings, ensure Actions are allowed to run and the workflow has permission to write repository contents.
4. Replace the existing Activity Graph Markdown line with `![Activity Graph](./assets/activity-graph.svg)`. You can use the full Stats section from `README-section.md` if preferred.
5. Commit and push the files. Run **Actions → Update GitHub Activity Graph → Run workflow** once.
6. Confirm `assets/activity-graph.svg` was committed and is visible in the profile README.

The scheduled workflow runs daily at 02:17 UTC (07:47 IST). GitHub scheduled workflows can be delayed during periods of high load, so use the manual workflow-dispatch option if you need an immediate refresh.

## Notes
- This graph visualizes GitHub's contribution calendar, not the full event-by-event activity graph provided by the retired third-party service. It shows contribution intensity over the last 365 days.
- The graph uses a dark background and green contribution levels. It does not rely on a third-party image proxy when displayed in your README.
- If you do not want to create a personal access token, you can test the GraphQL request with the repository's `GITHUB_TOKEN` first, but a classic token with `read:user` is the more explicit setup for querying your account's contribution calendar.
