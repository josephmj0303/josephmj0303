#!/usr/bin/env python3
"""Generate a dark-themed GitHub contribution activity graph as a static SVG."""
import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = os.environ.get("GITHUB_USERNAME", "josephmj0303")
TOKEN = os.environ["GH_TOKEN"]
OUTPUT = Path("assets/activity-graph.svg")

today = date.today()
start = today - timedelta(days=364)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""
payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start.isoformat() + "T00:00:00Z",
        "to": today.isoformat() + "T23:59:59Z",
    },
}
request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-activity-graph-generator",
    },
)
with urllib.request.urlopen(request, timeout=30) as response:
    result = json.loads(response.read())

if result.get("errors"):
    raise RuntimeError("GitHub GraphQL API error: " + json.dumps(result["errors"]))

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
days = [
    (date.fromisoformat(day["date"]), int(day["contributionCount"]))
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]
if not days:
    raise RuntimeError("GitHub returned no contribution days.")

# Draw a compact 52-week calendar heatmap in a dark card, matching a dark README.
cell, gap = 10, 3
left, top = 54, 58
cols = 53
rows = 7
plot_width = cols * (cell + gap)
plot_height = rows * (cell + gap)
width, height = left + plot_width + 28, top + plot_height + 48

max_count = max((count for _, count in days), default=0)
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def level(count):
    if count <= 0 or max_count == 0:
        return 0
    ratio = count / max_count
    if ratio <= 0.25:
        return 1
    if ratio <= 0.50:
        return 2
    if ratio <= 0.75:
        return 3
    return 4

# Align first date to its weekday; the calendar is filled column by column.
first_weekday = (days[0][0].weekday() + 1) % 7  # GitHub calendar weeks start on Sunday
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" rx="12" fill="#151522"/>',
    '<text x="28" y="34" fill="#ff3b91" font-family="Arial, sans-serif" font-size="22" font-weight="600">GitHub Contribution Activity</text>',
    f'<text x="28" y="52" fill="#a9b1d6" font-family="Arial, sans-serif" font-size="10">{escape(USERNAME)} · {calendar["totalContributions"]} contributions in the last year</text>',
]
month_labels = {}
for idx, (day, count) in enumerate(days):
    col = (idx + first_weekday) // 7
    row = (idx + first_weekday) % 7
    x = left + col * (cell + gap)
    y = top + row * (cell + gap)
    if day.day <= 7:
        month_labels[col] = day.strftime("%b")
    color = palette[level(count)]
    svg.append(
        f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}">'
        f'<title>{day.isoformat()}: {count} contributions</title></rect>'
    )

for col, label in month_labels.items():
    x = left + col * (cell + gap)
    svg.append(
        f'<text x="{x}" y="{top - 10}" fill="#a9b1d6" '
        f'font-family="Arial, sans-serif" font-size="10">{escape(label)}</text>'
    )

for row, label in [(0, "Sun"), (2, "Tue"), (4, "Thu")]:
    y = top + row * (cell + gap) + 9
    svg.append(
        f'<text x="15" y="{y}" fill="#a9b1d6" '
        f'font-family="Arial, sans-serif" font-size="9">{label}</text>'
    )

legend_y = top + plot_height + 25
svg.append(f'<text x="{left}" y="{legend_y}" fill="#a9b1d6" font-family="Arial, sans-serif" font-size="10">Less</text>')
for i, color in enumerate(palette):
    x = left + 31 + i * 15
    svg.append(f'<rect x="{x}" y="{legend_y - 9}" width="10" height="10" rx="2" fill="{color}"/>')
svg.append(f'<text x="{left + 111}" y="{legend_y}" fill="#a9b1d6" font-family="Arial, sans-serif" font-size="10">More</text>')
svg.append("</svg>")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(svg), encoding="utf-8")
print(f"Generated {OUTPUT}")
