"""Builds the static README panels into ../assets, one light and one dark copy each.

    python scripts/build.py

Stack icons are devicon SVGs kept in scripts/icons/.
"""

import base64
from pathlib import Path

from svgkit import (
    AMETHYST, BUTTER, CREAM, LAVENDER, MINT, PAPER, THEMES,
    box, lines, svg, text, width, window, wrap,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ICONS = Path(__file__).resolve().parent / "icons"


def mark(x, y, s, size, t, rotate=-1.5):
    """The amethyst highlight block with a butter shadow, as on conradium.my.id."""
    s = s.upper()
    w = width(s, "head", size, -0.02) + 0.32 * size
    h = size * 1.0
    top = y - size * 0.82
    cx, cy = x + w / 2, top + h / 2
    return (
        f'<g transform="rotate({rotate} {cx:g} {cy:g})">'
        f'<rect x="{x + 6:g}" y="{top + 6:g}" width="{w:g}" height="{h:g}" fill="{BUTTER}"/>'
        f'<rect x="{x:g}" y="{top:g}" width="{w:g}" height="{h:g}" fill="{AMETHYST}" stroke="{t["line"]}" stroke-width="3"/>'
        f'{text(x + 0.16 * size, y, s, "head", size, CREAM, tracking=-0.02)}'
        "</g>"
    )


def grid(x, y, w, h, t, step=32):
    d = "".join(f"M{x + i:g} {y:g}v{h:g}" for i in range(step, int(w), step))
    d += "".join(f"M{x:g} {y + j:g}h{w:g}" for j in range(step, int(h), step))
    return f'<path d="{d}" stroke="{t["grid"]}" stroke-width="1"/>'


# ---------------------------------------------------------------- intro

def intro(t):
    W, H = 880, 236
    x, y, w, h = 2, 2, W - 12, H - 12
    pad = 36
    b = grid(x, y + 38, w, h - 38, t)
    b += text(x + pad, y + 80, "Benedictus Sebastian · Bogor, Indonesia", "mono7", 12, t["accent"], tracking=0.1, upper=True)
    hi = "Hi, I'm "
    b += text(x + pad, y + 138, hi, "head", 50, t["fg"], tracking=-0.02, upper=True)
    b += mark(x + pad + width(hi.upper(), "head", 50, -0.02) + 4, y + 138, "Ben.", 50, t)
    about = (
        "Software engineer. I build data pipelines, edge backends and web apps. "
        "B.Sc. Digital Business & Innovation, Tokyo International University (2026)."
    )
    b += lines(x + pad, y + 182, wrap(about, "body", 16, w - pad * 2), "body", 16, t["muted"], 25)
    body = window(x, y, w, h, "hello.txt", t, body=b, fill=t["band"])
    return svg(W, H, body, "Hi, I'm Ben. " + about)


# ---------------------------------------------------------------- stack

STACK = [
    ("python", "Python"), ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("react", "React"),
    ("nextjs", "Next.js"), ("vuejs", "Vue"), ("threejs", "Three.js"), ("tailwindcss", "Tailwind"),
    ("fastapi", "FastAPI"), ("pandas", "Pandas"), ("scikitlearn", "scikit-learn"), ("cloudflare", "Cloudflare"),
    ("docker", "Docker"), ("postgresql", "Postgres"), ("supabase", "Supabase"), ("firebase", "Firebase"),
]
TILES = [LAVENDER, BUTTER, MINT, PAPER]


def stack(t):
    W = 880
    cols = 8
    pad = 30
    x, y, w = 2, 2, W - 12
    col_w = (w - pad * 2) / cols
    tile = 62
    row_h = tile + 40
    rows = -(-len(STACK) // cols)
    h = 38 + 28 + rows * row_h + 8
    b = ""
    for i, (slug, label) in enumerate(STACK):
        r, c = divmod(i, cols)
        cx = x + pad + c * col_w + col_w / 2
        ty = y + 38 + 28 + r * row_h
        tx = cx - tile / 2
        b += box(tx, ty, tile, tile, TILES[(r + c) % len(TILES)], t["line"], t["shadow"], off=4, rx=8)
        icon = base64.b64encode((ICONS / f"{slug}.svg").read_bytes()).decode()
        b += f'<image href="data:image/svg+xml;base64,{icon}" x="{tx + 14:g}" y="{ty + 14:g}" width="{tile - 28}" height="{tile - 28}"/>'
        b += text(cx, ty + tile + 24, label, "mono7", 10.5, t["fg"], tracking=0.04, anchor="middle", upper=True)
    body = window(x, y, w, h, "stack.cfg", t, body=b)
    return svg(W, h + 12, body, "Stack: " + ", ".join(label for _, label in STACK))


# ---------------------------------------------------------------- main

def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for name, t in THEMES.items():
        for key, data in {"intro": intro(t), "stack": stack(t)}.items():
            (OUT / f"{key}-{name}.svg").write_text(data, encoding="utf-8")
    print("built", len(list(OUT.glob("*.svg"))), "files into", OUT)


if __name__ == "__main__":
    main()
