"""Builds the static README panels into ../assets, one light and one dark copy each.

    python scripts/build.py

Copy lives here; keep it in step with conradium.my.id.
"""

import base64
from pathlib import Path

from svgkit import (
    AMETHYST, AMETHYST_DEEP, BUTTER, BW, CREAM, INK, LAVENDER, MINT, PAPER, THEMES,
    box, e, lines, svg, text, triangle, width, window, wrap,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
SHOTS = Path(__file__).resolve().parent / "shots"

FADE_CSS = (
    "@keyframes in{from{opacity:0}}"
    "@keyframes blink{50%{opacity:0}}"
    "@keyframes ping{from{transform:scale(1);opacity:.7}to{transform:scale(2.4);opacity:0}}"
    ".ln{animation:in .01s backwards}"
    ".cur{animation:blink 1s steps(1) infinite}"
    ".ping{transform-box:fill-box;transform-origin:center;animation:ping 1.6s ease-out infinite}"
)


def heading(x, y, parts, size, t, font="head", tracking=-0.015):
    """One line of uppercase heading where (text, accent) parts switch colour."""
    from svgkit import FAMILY
    fam, wt = FAMILY[font]
    spans = "".join(
        f'<tspan fill="{t["accent"] if accent else t["fg"]}">{e(s.upper())}</tspan>' for s, accent in parts
    )
    return (
        f'<text x="{x:g}" y="{y:g}" font-family="{fam}" font-weight="{wt}" font-size="{size:g}" '
        f'letter-spacing="{tracking * size:.2f}">{spans}</text>'
    )


def mark(x, y, s, size, t, rotate=-1):
    """The amethyst highlight block with a butter shadow, as on the hero title."""
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
    ), w


def grid(x, y, w, h, t, step=32):
    d = "".join(f"M{x + i:g} {y:g}v{h:g}" for i in range(step, int(w), step))
    d += "".join(f"M{x:g} {y + j:g}h{w:g}" for j in range(step, int(h), step))
    return f'<path d="{d}" stroke="{t["grid"]}" stroke-width="1"/>'


# ---------------------------------------------------------------- hero

def hero(t):
    W, H = 880, 566
    wx, wy, ww, wh = 1.5, 1.5, W - 10, H - 10
    x0 = 38
    b = ""

    b += text(x0, 88, "Benedictus Sebastian", "mono7", 12, t["accent"], tracking=0.1, upper=True)
    b += text(x0, 106, "Software engineer & business development", "mono7", 12, t["accent"], tracking=0.1, upper=True)

    size = 54
    b += text(x0, 172, "I build", "head", size, t["fg"], tracking=-0.02, upper=True)
    b += text(x0, 225, "systems that", "head", size, t["fg"], tracking=-0.02, upper=True)
    m, _ = mark(x0, 284, "hold up.", size, t)
    b += m

    body = (
        "Data pipelines, edge backends and the products on top of them. Forecasts a shop owner "
        "can act on, APIs that assume the client is lying, and infrastructure that costs nothing "
        "while nobody is using it."
    )
    rows = wrap(body, "body", 15.5, 432)
    b += lines(x0, 336, rows, "body", 15.5, t["muted"], 24)

    fy = 336 + len(rows) * 24 + 10
    facts = [("Based in", "Bogor, ID", "UTC+7"), ("Studied", "TIU, Tokyo", "B.Sc. 2026"), ("Speaks", "ID · EN · JP", "")]
    fw = 138
    for i, (dt, dd, sub) in enumerate(facts):
        fx = x0 + i * (fw + 12)
        b += box(fx, fy, fw, 62, t["card"], t["line"], t["shadow"], off=3, rx=6)
        b += text(fx + 12, fy + 19, dt, "mono", 10.5, t["accent"], tracking=0.1, upper=True)
        b += text(fx + 12, fy + 37, dd, "head8", 15, t["fg"])
        if sub:
            b += text(fx + 12, fy + 53, sub, "body", 12.5, t["muted"])

    # Terminal
    tx, tw = 516, 316
    ty = 104
    ln = []  # (svg, height)
    lead = 22
    mono = 12.5

    def prompt(cmd):
        return (
            text(0, 0, "$", "mono7", mono, BUTTER) + text(14, 0, cmd, "mono", mono, CREAM),
            lead,
        )

    def out(s, fill=LAVENDER):
        rows = wrap(s, "mono", mono, tw - 44)
        return lines(0, 0, rows, "mono", mono, fill, lead), lead * len(rows)

    def row(s):
        g = box(0, -16, tw - 44, 27, AMETHYST, "#0d0913", "#0d0913", off=3, rx=4, bw=2)
        g += triangle(10, -2.5, 8, CREAM)
        g += text(24, 2, s, "mono7", 12, CREAM)
        return g, 36

    ln.append(prompt("whoami"))
    ln.append(out("benedictus sebastian — software engineer & business development"))
    ln.append(prompt("cat focus.txt"))
    ln[-1] = (ln[-1][0], lead + 6)
    for s in ("data pipelines & forecasting", "edge backends on cloudflare", "products & web apps"):
        ln.append(row(s))
    ln.append(prompt("ls ~/shipped"))
    ln.append(
        (
            lines(0, 0, ["himotoki/    snacktrack/", "aimflicks/   nightbot-to-discord/"], "mono", mono, MINT, lead, extra='xml:space="preserve"'),
            lead * 2,
        )
    )
    cursor = (
        text(0, 0, "$", "mono7", mono, BUTTER)
        + f'<rect class="cur" x="14" y="-11" width="8" height="14" fill="{CREAM}"/>'
    )
    ln.append((cursor, lead))

    inner = ""
    yy = ty + 38 + 30
    for i, (g, h) in enumerate(ln):
        inner += f'<g class="ln" style="animation-delay:{0.35 + i * 0.32:.2f}s" transform="translate({tx + 22} {yy})">{g}</g>'
        yy += h
    th = yy - ty + 22
    b += window(tx, ty, tw, th, "benedictus@conradium: ~", t, body=inner, fill=t["term"], bar=BUTTER, bar_fg=INK, shadow=AMETHYST, off=10)

    # Floating cards
    sx, sy = tx + tw - 132, ty - 30
    b += (
        f'<g transform="rotate(3 {sx + 66} {sy + 24})">'
        + box(sx, sy, 136, 50, BUTTER, t["line"], t["shadow"], off=4, rx=6)
        + text(sx + 14, sy + 20, "Status", "mono7", 10, INK, tracking=0.1, upper=True)
        + text(sx + 14, sy + 39, "Open to roles", "head8", 15, INK)
        + "</g>"
    )
    lx, ly = tx - 22, ty + th - 30
    b += (
        f'<g transform="rotate(-2 {lx + 90} {ly + 25})">'
        + box(lx, ly, 182, 50, MINT, t["line"], t["shadow"], off=4, rx=6)
        + f'<circle class="ping" cx="{lx + 22}" cy="{ly + 25}" r="6" fill="{AMETHYST}"/>'
        + f'<circle cx="{lx + 22}" cy="{ly + 25}" r="6" fill="{AMETHYST}" stroke="{INK}" stroke-width="2"/>'
        + text(lx + 38, ly + 23, "4 projects live", "head8", 15, INK)
        + text(lx + 38, ly + 38, "and still running", "mono7", 9.5, "rgba(29,21,40,.7)", tracking=0.08, upper=True)
        + "</g>"
    )

    content = grid(wx, wy + 38, ww, wh - 38, t) + b
    out_svg = window(wx, wy, ww, wh, "conradium.my.id", t, body=content, fill=t["band"], off=8)
    return svg(W, H, out_svg, "Benedictus Sebastian — I build systems that hold up.", FADE_CSS)


# ---------------------------------------------------------------- section heads

BANDS = {
    # band: (light fill, light accent, dark fill, dark accent), as in styles.css
    "lavender": (LAVENDER, AMETHYST_DEEP, "#2a1f3a", LAVENDER),
    "butter": (BUTTER, AMETHYST_DEEP, "#231a30", BUTTER),
    "mint": (MINT, AMETHYST_DEEP, "#140e1c", MINT),
}


def band_colours(band, t):
    lf, la, df, da = BANDS[band]
    return (lf, la) if t is THEMES["light"] else (df, da)


def section_head(label, parts, t, band, sub=None):
    W = 880
    fill, accent = band_colours(band, t)
    tt = dict(t, accent=accent)
    rows = wrap(sub, "body", 16, 760) if sub else []
    H = 116 + (len(rows) * 25 + 8 if rows else 0)
    x, y, w, h = 2, 2, W - 12, H - 12
    b = box(x, y, w, h, fill, t["line"], t["shadow"], off=6)
    b += grid(x + 1, y + 1, w - 2, h - 2, t, step=24)
    b += text(x + 28, y + 34, label, "mono7", 13, accent, tracking=0.1, upper=True)
    b += heading(x + 26, y + 80, parts, 38, tt)
    b += lines(x + 28, y + 112, rows, "body", 16, t["muted"], 25)
    title = label + " — " + "".join(s for s, _ in parts)
    return svg(W, H, b, title)


# ---------------------------------------------------------------- project cards

PROJECTS = [
    {
        "slug": "himotoki",
        "window": "himotoki.web.app",
        "color": BUTTER,
        "shot": "himotoki-home.webp",
        "meta": "2026 · Lead engineer & product engineer",
        "name": "Himotoki",
        "summary": (
            "A Japanese–English dictionary for learners. Search by kanji, reading, romaji, English or "
            "handwriting, paste a sentence to see how it breaks down, and turn what you find into "
            "spaced-repetition flashcards."
        ),
        "stack": "React · Vite · Firebase · PWA · Dictionary API",
        "link": "Live site ↗",
    },
    {
        "slug": "snacktrack",
        "window": "snacktrack.conradium.my.id",
        "color": MINT,
        "shot": "snacktrack-home.webp",
        "meta": "2025 – 2026 · Technical lead — full stack & ML",
        "name": "SnackTrack",
        "summary": (
            "A marketplace for small snack sellers in Indonesia with sales forecasting built in. Sellers "
            "take orders, get paid through Midtrans, and receive a weekly per-product forecast with "
            "stock recommendations."
        ),
        "stack": "Python · XGBoost · FastAPI · Supabase · React · Vercel Edge · Docker",
        "link": "Live site ↗",
    },
    {
        "slug": "aimflicks",
        "window": "aimflicks-beta.vercel.app",
        "color": LAVENDER,
        "shot": "aimflicks-home.webp",
        "meta": "2025 – 2026 · Solo — engine, backend, infrastructure",
        "name": "AimFlicks",
        "summary": (
            "A browser-based 3D aim trainer modelled on Valorant's aiming feel. Matches in-game "
            "sensitivity 1:1 and syncs profiles, replays, parties and weekly leaderboards through a "
            "single Cloudflare Worker."
        ),
        "stack": "React · Three.js · TypeScript · Cloudflare Workers · D1 · R2 · Durable Objects",
        "link": "Live site ↗",
    },
    {
        "slug": "hirepassport",
        "window": "hirepassport · hackathon demo",
        "color": AMETHYST,
        "shot": "hiring-home.webp",
        "meta": "2026 · Technical product & UI lead",
        "name": "HirePassport",
        "summary": (
            "An AI hiring platform that takes first-round and screening interviews off companies' "
            "hands. Candidates do one AI interview, and that result is reused to match them with many "
            "jobs. Built at the SDGs to Startups Hackathon."
        ),
        "stack": "Next.js · Python · LLM agents · JSON Schema",
        "link": "Engineering notes ↗",
    },
]

CARD_W = 428
PAD = 24


def project_layout(p):
    tw = CARD_W - PAD * 2
    meta = wrap(p["meta"].upper(), "mono7", 11, tw, 0.04)
    summary = wrap(p["summary"], "body", 14.5, tw)
    stack = wrap(p["stack"], "mono", 11.5, tw)
    return meta, summary, stack


def project_body_height(p):
    meta, summary, stack = project_layout(p)
    return 26 + len(meta) * 16 + 38 + len(summary) * 22 + 10 + len(stack) * 18 + 40


def project(p, t, body_h):
    W = CARD_W + 12
    x, y = 2, 2
    vis_h = CARD_W / 2
    H = 38 + vis_h + body_h
    meta, summary, stack = project_layout(p)
    shot = base64.b64encode((SHOTS / p["shot"]).read_bytes()).decode()

    vy = y + 38
    sx, sy = x + CARD_W * 0.08, vy + vis_h * 0.13
    sw = CARD_W * 0.84
    sh = sw * 10 / 16
    b = f'<clipPath id="v-{p["slug"]}"><rect x="{x}" y="{vy}" width="{CARD_W}" height="{vis_h:g}"/></clipPath>'
    b += f'<g clip-path="url(#v-{p["slug"]})">'
    b += f'<rect x="{x}" y="{vy}" width="{CARD_W}" height="{vis_h:g}" fill="{p["color"]}"/>'
    b += (
        f'<pattern id="d-{p["slug"]}" width="14" height="14" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.3" fill="{INK}" opacity=".14"/></pattern>'
        f'<rect x="{x}" y="{vy}" width="{CARD_W}" height="{vis_h:g}" fill="url(#d-{p["slug"]})"/>'
    )
    b += f'<rect x="{sx + 6:g}" y="{sy + 6:g}" width="{sw:g}" height="{sh:g}" rx="6" fill="{INK}"/>'
    b += (
        f'<clipPath id="s-{p["slug"]}"><rect x="{sx:g}" y="{sy:g}" width="{sw:g}" height="{sh:g}" rx="6"/></clipPath>'
        f'<image href="data:image/webp;base64,{shot}" x="{sx:g}" y="{sy:g}" width="{sw:g}" height="{sh:g}" '
        f'preserveAspectRatio="xMidYMin slice" clip-path="url(#s-{p["slug"]})"/>'
        f'<rect x="{sx:g}" y="{sy:g}" width="{sw:g}" height="{sh:g}" rx="6" fill="none" stroke="{INK}" stroke-width="{BW}"/>'
    )
    b += "</g>"
    b += f'<path d="M{x} {vy + vis_h:g}h{CARD_W}" stroke="{t["line"]}" stroke-width="{BW}"/>'

    bx = x + PAD
    by = vy + vis_h + 26 + 10
    b += lines(bx, by, meta, "mono7", 11, t["accent"], 16, tracking=0.04)
    by += (len(meta) - 1) * 16 + 36
    b += text(bx, by, p["name"], "head", 26, t["fg"], tracking=-0.01, upper=True)
    by += 28
    b += lines(bx, by, summary, "body", 14.5, t["muted"], 22)
    by += len(summary) * 22 + 6
    b += lines(bx, by, stack, "mono", 11.5, t["accent"], 18)

    ly = y + H - 26
    lw = width(p["link"], "body7", 14.5)
    b += text(bx, ly, p["link"], "body7", 14.5, t["fg"])
    b += f'<path d="M{bx} {ly + 5}h{lw:g}" stroke="{t["fg"]}" stroke-width="2"/>'

    body = window(x, y, CARD_W, H, p["window"], t, body=b)
    return svg(W, H + 12, body, f'{p["name"]} — {p["summary"]}')


# ---------------------------------------------------------------- more work

MORE = [
    (
        "nightbot-to-discord ↗",
        "A Cloudflare Worker bridging a GET-only chat bot to POST-only Discord webhooks, so a !clip "
        "command drops a timestamped marker into Discord. Cut the YouTube live-stream lookup from 100 "
        "quota units to 2.",
        "2026 · Solo",
    ),
    (
        "Copiya",
        "A full-stack e-commerce platform, taken from wireframes to deployment with a focus on UI/UX "
        "and customer journey mapping.",
        "2026 · Lead developer",
    ),
    (
        "Chromaticas",
        "Landing page for an Indonesian VTuber agency, with clickable planets that reveal talent "
        "profiles animated with transparent WebM.",
        "2025 · Frontend, client",
    ),
    (
        "RslStore Discord bot",
        "A ticket system for a Discord-based online shop, with auto-role assignment, moderation "
        "tooling and order handling.",
        "2025 · Solo, client",
    ),
]


def more_work(t):
    W = 880
    x, y, w = 2, 2, W - 12
    rows = []
    for name, desc, meta in MORE:
        d = wrap(desc, "body", 14.5, 600)
        rows.append((name, d, meta, 30 + 22 + len(d) * 22))
    H = 38 + 8 + sum(r[3] for r in rows) + 8
    b = ""
    yy = y + 38 + 8
    for i, (name, d, meta, h) in enumerate(rows):
        if i:
            b += f'<path d="M{x + PAD} {yy:g}h{w - PAD * 2}" stroke="{t["rule"]}" stroke-width="1.5" stroke-dasharray="5 5"/>'
        b += text(x + PAD, yy + 34, name, "head8", 17, t["fg"])
        b += lines(x + PAD, yy + 58, d, "body", 14.5, t["muted"], 22)
        b += text(x + w - PAD, yy + 34, meta, "mono7", 11, t["accent"], tracking=0.04, anchor="end", upper=True)
        yy += h
    body = window(x, y, w, H, "more_work.txt", t, body=b)
    return svg(W, H + 12, body, "More work: " + ", ".join(m[0].rstrip(" ↗") for m in MORE))


# ---------------------------------------------------------------- toolbox

TOOLBOXES = [
    (
        "Data & ML", LAVENDER, INK,
        "Forecasting and feature engineering, from notebook to an endpoint that always answers.",
        [
            ("Python · Pandas · NumPy", "SnackTrack, capstone project"),
            ("XGBoost", "Per-product sales forecasts"),
            ("scikit-learn", "Data Science & AI capstone"),
            ("Feature engineering", "Holiday, payday, lag & rolling features"),
            ("Model evaluation", "MAPE-based accuracy for non-technical users"),
        ],
    ),
    (
        "Backend & edge", BUTTER, INK,
        "APIs and storage that stay cheap when idle and stay honest under load.",
        [
            ("Cloudflare Workers · D1 · R2", "AimFlicks, nightbot-to-discord"),
            ("Durable Objects", "Real-time parties over WebSockets"),
            ("FastAPI · Docker", "SnackTrack forecasting service"),
            ("Supabase · PostgreSQL", "19 tables with row-level security"),
            ("Redis · SQLite · MariaDB", "Caching and smaller services"),
        ],
    ),
    (
        "Frontend & 3D", AMETHYST, CREAM,
        "Typed interfaces and WebGL that load fast and degrade instead of breaking.",
        [
            ("React · TypeScript", "Himotoki, SnackTrack, AimFlicks"),
            ("Next.js", "HirePassport, Chromaticas"),
            ("Three.js · WebGL", "AimFlicks FPS engine"),
            ("Vue · Vite · Tailwind CSS", "Previous portfolio, tooling"),
            ("WebSockets · Web Audio", "Live lobbies and game feedback"),
        ],
    ),
    (
        "Product & security", PAPER, INK,
        "Scoping what to build, then making sure nobody can abuse it.",
        [
            ("HMAC signing · rate limiting", "AimFlicks anti-cheat"),
            ("Payment verification", "SnackTrack Midtrans callbacks"),
            ("PRDs · user workflows", "HirePassport"),
            ("Pitching & live demos", "SDGs to Startups Hackathon"),
            ("Figma · Photoshop", "Wireframes to UI"),
        ],
    ),
]


def toolbox(t):
    W = 880
    gap = 26
    cw = (W - 12 - gap) / 2
    lid = 58
    inner_w = cw - 44

    def layout(tb):
        desc = wrap(tb[3], "body", 14, inner_w)
        return desc, lid + 18 + len(desc) * 21 + 10 + len(tb[4]) * 44 + 16

    heights = [layout(tb)[1] for tb in TOOLBOXES]
    ch = max(heights)
    H = 16 + 2 * ch + gap + 12
    b = ""
    for i, tb in enumerate(TOOLBOXES):
        name, color, ink, _, items = tb
        desc, _ = layout(tb)
        cx = 2 + (i % 2) * (cw + gap)
        cy = 16 + (i // 2) * (ch + gap)
        cid = f"tb{i}"
        # handle on the lid
        b += f'<rect x="{cx + cw / 2 - 36:g}" y="{cy - 12:g}" width="72" height="22" rx="6" fill="none" stroke="{t["line"] if t is THEMES["light"] else t["shadow"]}" stroke-width="{BW}"/>'
        b += f'<rect x="{cx + 6:g}" y="{cy + 6:g}" width="{cw:g}" height="{ch:g}" rx="8" fill="{t["shadow"]}"/>'
        b += f'<clipPath id="{cid}"><rect x="{cx:g}" y="{cy:g}" width="{cw:g}" height="{ch:g}" rx="8"/></clipPath>'
        b += f'<g clip-path="url(#{cid})"><rect x="{cx:g}" y="{cy:g}" width="{cw:g}" height="{ch:g}" fill="{t["card"]}"/>'
        b += f'<rect x="{cx:g}" y="{cy:g}" width="{cw:g}" height="{lid}" fill="{color}"/>'
        b += f'<path d="M{cx:g} {cy + lid:g}h{cw:g}" stroke="{t["line"]}" stroke-width="{BW}"/></g>'
        b += f'<rect x="{cx:g}" y="{cy:g}" width="{cw:g}" height="{ch:g}" rx="8" fill="none" stroke="{t["line"]}" stroke-width="{BW}"/>'
        # latch
        b += f'<rect x="{cx + cw / 2 - 12:g}" y="{cy + lid - 8:g}" width="24" height="16" rx="3" fill="{BUTTER if color != BUTTER else LAVENDER}" stroke="{t["line"]}" stroke-width="2"/>'
        b += text(cx + 22, cy + 37, name, "head", 21, ink, tracking=-0.01, upper=True)
        b += text(cx + cw - 22, cy + 35, f"{len(items):02d} tools", "mono7", 10.5, ink, tracking=0.08, anchor="end", upper=True)
        yy = cy + lid + 34
        b += lines(cx + 22, yy, desc, "body", 14, t["muted"], 21)
        yy += (len(desc) - 1) * 21 + 22
        for j, (tool, where) in enumerate(items):
            b += f'<path d="M{cx + 22:g} {yy:g}h{inner_w:g}" stroke="{t["rule"]}" stroke-width="1.5" stroke-dasharray="5 5"/>'
            b += text(cx + 22, yy + 20, tool, "mono7", 12.5, t["fg"])
            b += text(cx + 22, yy + 37, where, "body", 13, t["muted"])
            yy += 44
    return svg(W, H, b, "Toolbox: " + "; ".join(f"{n}: " + ", ".join(i[0] for i in it) for n, _, _, _, it in TOOLBOXES))


# ---------------------------------------------------------------- contact

EMAIL = "benedictus.sebastian5@gmail.com"


def contact(t):
    W, H = 880, 372
    x, y, w, h = 2, 2, W - 12, H - 12
    fill = LAVENDER if t is THEMES["light"] else "#2a1f3a"
    accent = "#5b2380" if t is THEMES["light"] else LAVENDER
    b = text(x + 38, y + 84, "[04] Contact", "mono7", 13, accent, tracking=0.1, upper=True)
    b += text(x + 38, y + 136, "Let's build something", "head", 44, t["fg"], tracking=-0.015, upper=True)
    m, _ = mark(x + 38, y + 194, "that holds up.", 44, t)
    b += m
    sub = "Hiring, collaborating, or curious about one of the projects? Email is the fastest way to reach me."
    b += lines(x + 38, y + 240, wrap(sub, "body", 16, 760), "body", 16, t["muted"] if t is THEMES["dark"] else "rgba(29,21,40,.78)", 24)
    # email button
    bw_ = width(EMAIL.upper(), "head8", 14, 0.04) + 44
    bx, by = x + 38, y + 270
    b += box(bx, by, bw_, 52, AMETHYST, t["line"], t["shadow"], off=4, rx=6)
    b += text(bx + bw_ / 2, by + 31, EMAIL, "head8", 14, CREAM, tracking=0.04, anchor="middle", upper=True)
    body = window(x, y, w, h, "contact.txt", t, body=grid(x, y + 38, w, h - 38, t) + b, fill=fill)
    return svg(W, H, body, f"Let's build something that holds up. Email {EMAIL}")


BUTTONS = [
    ("website", "conradium.my.id ↗"),
    ("linkedin", "LinkedIn ↗"),
    ("x", "X ↗"),
    ("discord", "Discord ↗"),
]


def button(label, t, accent=False):
    bw_ = width(label.upper(), "head8", 13, 0.04) + 40
    W, H = bw_ + 10, 56
    fill, fg = (BUTTER, INK) if accent else (t["card"], t["fg"])
    b = box(2, 2, bw_, 46, fill, t["line"], t["shadow"], off=4, rx=6)
    b += text(2 + bw_ / 2, 30, label, "head8", 13, fg, tracking=0.04, anchor="middle", upper=True)
    return svg(W, H, b, label.replace(" ↗", ""))


# ---------------------------------------------------------------- main

def main():
    OUT.mkdir(exist_ok=True)
    body_h = max(project_body_height(p) for p in PROJECTS)
    for name, t in THEMES.items():
        files = {
            "hero": hero(t),
            "head-work": section_head("[01] Selected work", [("Things I've ", False), ("shipped.", True)], t, "lavender",
                                      "Four projects, each with engineering notes on the decisions that mattered."),
            "more-work": more_work(t),
            "head-toolbox": section_head("[02] Toolbox", [("What's in the ", False), ("toolbox?", True)], t, "mint"),
            "toolbox": toolbox(t),
            "head-activity": section_head("[03] Activity", [("Still ", False), ("shipping.", True)], t, "butter"),
            "contact": contact(t),
        }
        for p in PROJECTS:
            files[f"work-{p['slug']}"] = project(p, t, body_h)
        for slug, label in BUTTONS:
            files[f"btn-{slug}"] = button(label, t, accent=slug == "website")
        for key, data in files.items():
            (OUT / f"{key}-{name}.svg").write_text(data, encoding="utf-8")
    print("built", len(list(OUT.glob("*.svg"))), "files into", OUT)


if __name__ == "__main__":
    main()
