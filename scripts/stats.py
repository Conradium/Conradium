"""Draws the GitHub activity panel from live data (run by the profile workflow).

    GITHUB_TOKEN=... python scripts/stats.py <login> <out-dir>

Writes stats-light.svg and stats-dark.svg.
"""

import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

from svgkit import AMETHYST, BUTTER, CREAM, INK, LAVENDER, MINT, THEMES, box, svg, text, width, window

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


SKIP_LANGS = {"Jupyter Notebook"}


def gql(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def fetch(login, token):
    user = gql(QUERY, {"login": login}, token)
    # Commit search covers every public repo and branch, all time; the GraphQL
    # contribution counts only see default branches.
    req = urllib.request.Request(
        f"https://api.github.com/search/commits?q=author:{login}&per_page=1",
        headers={"Authorization": f"bearer {token}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        user["commits"] = json.load(r)["total_count"]
    return user


def summarise(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])

    # Current streak: today may still be empty, so it doesn't break the run.
    streak = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            streak += 1
        elif i > 0:
            break
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)

    repos = user["repositories"]
    # Notebook JSON is mostly output cells, so its byte count drowns out real code.
    langs = {}
    for node in repos["nodes"]:
        for edge in node["languages"]["edges"]:
            if edge["node"]["name"] in SKIP_LANGS:
                continue
            langs[edge["node"]["name"]] = langs.get(edge["node"]["name"], 0) + edge["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])
    shares = [(name, size / total) for name, size in top[:5]]
    rest = 1 - sum(s for _, s in shares)
    if rest > 0.005:
        shares.append(("Other", rest))

    return {
        "commits": user["commits"],
        "contributions": cal["totalContributions"],
        "streak": streak,
        "longest": longest,
        "repos": repos["totalCount"],
        "languages": shares,
    }


TILES = [
    ("commits", "Commits", "all time", LAVENDER, INK),
    ("contributions", "Contributions", "last 12 months", BUTTER, INK),
    ("streak", "Current streak", "longest: {longest} days", MINT, INK),
    ("repos", "Public repos", "and counting", AMETHYST, CREAM),
]


def panel(s, t, updated):
    W, H = 880, 330
    x, y, w, h = 2, 2, W - 12, H - 12
    pad = 28
    gap = 18
    tw = (w - pad * 2 - gap * 3) / 4
    b = ""
    for i, (key, label, sub, fill, ink) in enumerate(TILES):
        tx = x + pad + i * (tw + gap)
        ty = y + 38 + 28
        b += box(tx, ty, tw, 112, fill, t["line"], t["shadow"], off=4, rx=6)
        b += text(tx + 16, ty + 26, label, "mono7", 10.5, ink, tracking=0.1, upper=True)
        b += text(tx + 16, ty + 72, f"{s[key]:,}", "head", 40, ink, tracking=-0.02)
        b += text(tx + 16, ty + 96, sub.format(**s), "mono", 10.5, ink, tracking=0.04, upper=True, extra='opacity=".75"')

    # Top languages as one stacked bar
    ly = y + 38 + 28 + 112 + 36
    b += text(x + pad, ly, "Top languages · by bytes", "mono7", 11, t["accent"], tracking=0.1, upper=True)
    bar_y, bar_h, bar_w = ly + 14, 26, w - pad * 2
    colours = [AMETHYST, LAVENDER, BUTTER, MINT, CREAM, t["fg"]]
    cx = x + pad
    segs = ""
    legend = ""
    lx = x + pad
    for i, (name, share) in enumerate(s["languages"]):
        sw = bar_w * share
        segs += f'<rect x="{cx:g}" y="{bar_y:g}" width="{sw:g}" height="{bar_h}" fill="{colours[i % len(colours)]}"/>'
        if i:
            segs += f'<path d="M{cx:g} {bar_y:g}v{bar_h}" stroke="{t["line"]}" stroke-width="2.5"/>'
        cx += sw
        label = f"{name} {share * 100:.1f}%"
        legend += box(lx, bar_y + bar_h + 20, 12, 12, colours[i % len(colours)], t["line"], rx=2, bw=2)
        legend += text(lx + 19, bar_y + bar_h + 31, label, "mono", 11.5, t["fg"])
        lx += 19 + width(label, "mono", 11.5) + 24
    b += f'<rect x="{x + pad + 4:g}" y="{bar_y + 4:g}" width="{bar_w:g}" height="{bar_h}" rx="5" fill="{t["shadow"]}"/>'
    b += f'<clipPath id="bar"><rect x="{x + pad:g}" y="{bar_y:g}" width="{bar_w:g}" height="{bar_h}" rx="5"/></clipPath>'
    b += f'<g clip-path="url(#bar)">{segs}</g>'
    b += f'<rect x="{x + pad:g}" y="{bar_y:g}" width="{bar_w:g}" height="{bar_h}" rx="5" fill="none" stroke="{t["line"]}" stroke-width="2.5"/>'
    b += legend

    body = window(x, y, w, h, "github.stats", t, body=b)
    # The "updated" stamp sits on the title bar, so it goes on after the window.
    body += text(x + w - pad, y + 23.5, f"updated {updated}", "mono7", 10.5, CREAM, tracking=0.04, anchor="end", upper=True, extra='opacity=".7"')
    return svg(W, H, body, f"GitHub activity: {s['contributions']} contributions in the last year, {s['repos']} public repos")


def main():
    login, out = sys.argv[1], Path(sys.argv[2])
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN")
    s = summarise(fetch(login, token))
    out.mkdir(parents=True, exist_ok=True)
    updated = dt.date.today().strftime("%d %b %Y")
    for name, t in THEMES.items():
        (out / f"stats-{name}.svg").write_text(panel(s, t, updated), encoding="utf-8")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
