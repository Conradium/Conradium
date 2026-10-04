"""Shared drawing kit for the profile SVGs.

Mirrors the portfolio's retro pastel, neo-brutalist look: thick ink outlines,
hard offset shadows, OS-window title bars and bold uppercase Archivo.
Fonts are pre-subset into fonts.json (woff2 + advance widths) so building
needs nothing beyond the Python standard library.
"""

import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
FONTS = json.loads((HERE / "fonts.json").read_text())

# Palette: Cream, Amethyst, Lavender, Butter, Mint, Ink
CREAM = "#fff8ec"
PAPER = "#fffdf7"
AMETHYST = "#8b42b8"
AMETHYST_DEEP = "#5b2380"
LAVENDER = "#cdb8ff"
BUTTER = "#ffe17a"
MINT = "#b6f0d2"
INK = "#1d1528"

FAMILY = {
    "head": ("Archivo", 900),
    "head8": ("Archivo", 800),
    "body": ("DM Sans", 400),
    "body7": ("DM Sans", 700),
    "mono": ("Space Mono", 400),
    "mono7": ("Space Mono", 700),
}

# Surface tokens, as in styles.css (:root and :root[data-theme='dark'])
THEMES = {
    "light": {
        "fg": INK,
        "muted": "rgba(29,21,40,.74)",
        "card": PAPER,
        "band": CREAM,
        "line": INK,
        "shadow": INK,
        "accent": AMETHYST,
        "bar": INK,
        "term": INK,
        "grid": "rgba(29,21,40,.06)",
        "rule": "rgba(29,21,40,.16)",
    },
    "dark": {
        "fg": CREAM,
        "muted": "rgba(255,248,236,.74)",
        "card": "#251b33",
        "band": INK,
        "line": "#0d0913",
        "shadow": LAVENDER,
        "accent": LAVENDER,
        "bar": "#140e1c",
        "term": "#140e1c",
        "grid": "rgba(205,184,255,.07)",
        "rule": "rgba(255,248,236,.14)",
    },
}

BW = 2.5  # border width
RADIUS = 8


def e(text):
    return escape(text, {'"': "&quot;"})


def width(text, font, size, tracking=0.0):
    """Rendered width of a single line. tracking is in em, like letter-spacing."""
    widths = FONTS[font]["widths"]
    fallback = widths.get("n", 0.55)
    return sum(widths.get(ch, fallback) for ch in text) * size + tracking * size * len(text)


def wrap(text, font, size, max_w, tracking=0.0):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}" if line else word
        if line and width(trial, font, size, tracking) > max_w:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def text(x, y, s, font, size, fill, tracking=0.0, anchor=None, upper=False, extra=""):
    fam, weight = FAMILY[font]
    s = s.upper() if upper else s
    attrs = f'x="{x:g}" y="{y:g}" font-family="{fam}" font-weight="{weight}" font-size="{size:g}" fill="{fill}"'
    if tracking:
        attrs += f' letter-spacing="{tracking * size:.2f}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if extra:
        attrs += " " + extra
    return f"<text {attrs}>{e(s)}</text>"


def lines(x, y, rows, font, size, fill, leading, **kw):
    return "".join(text(x, y + i * leading, r, font, size, fill, **kw) for i, r in enumerate(rows))


def box(x, y, w, h, fill, line, shadow=None, off=6, rx=RADIUS, bw=BW, extra=""):
    """A filled, outlined rectangle with an optional hard offset shadow."""
    out = ""
    if shadow:
        out += f'<rect x="{x + off:g}" y="{y + off:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{shadow}"/>'
    out += (
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" '
        f'stroke="{line}" stroke-width="{bw:g}" {extra}/>'
    )
    return out


def dots(x, cy):
    """The three title-bar dots: amethyst, butter, mint."""
    return "".join(
        f'<circle cx="{x + 5.5 + i * 17:g}" cy="{cy:g}" r="4.5" fill="{c}" stroke="{INK}" stroke-width="2"/>'
        for i, c in enumerate((AMETHYST, BUTTER, MINT))
    )


_clip_ids = iter(range(1, 10_000))


def window(x, y, w, h, title, t, body="", fill=None, bar=None, bar_fg=CREAM, shadow=None, off=6):
    """An OS-style window: outlined card, title bar with dots, clipped body content."""
    cid = f"w{next(_clip_ids)}"
    fill = fill or t["card"]
    bar = bar or t["bar"]
    shadow = shadow or t["shadow"]
    return (
        f'<rect x="{x + off:g}" y="{y + off:g}" width="{w:g}" height="{h:g}" rx="{RADIUS}" fill="{shadow}"/>'
        f'<clipPath id="{cid}"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{RADIUS}"/></clipPath>'
        f'<g clip-path="url(#{cid})">'
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"/>'
        f"{body}"
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="38" fill="{bar}"/>'
        f'<path d="M{x:g} {y + 38:g}h{w:g}" stroke="{t["line"]}" stroke-width="{BW}"/>'
        f"{dots(x + 14, y + 19)}"
        f'{text(x + 74, y + 23.5, title, "mono7", 11.5, bar_fg, tracking=0.04, upper=True)}'
        f"</g>"
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{RADIUS}" fill="none" '
        f'stroke="{t["line"]}" stroke-width="{BW}"/>'
    )


def triangle(x, cy, size, fill):
    """Stand-in for ▸, which the subset fonts don't carry."""
    return f'<path d="M{x:g} {cy - size / 2:g}l{size * 0.85:g} {size / 2:g}l{-size * 0.85:g} {size / 2:g}z" fill="{fill}"/>'


def svg(w, h, body, title, css=""):
    used = [f for f, (fam, wt) in FAMILY.items() if f'font-family="{fam}" font-weight="{wt}"' in body]
    faces = "".join(
        f'@font-face{{font-family:"{FAMILY[f][0]}";font-weight:{FAMILY[f][1]};'
        f'src:url(data:font/woff2;base64,{FONTS[f]["woff2"]}) format("woff2")}}'
        for f in used
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="0 0 {w:g} {h:g}" '
        f'role="img" aria-label="{e(title)}"><title>{e(title)}</title>'
        f"<style>{faces}{css}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>"
        f"{body}</svg>"
    )
