"""Build the profile README's SVGs. Run from the repo root: python3 scripts/build_svgs.py
Needs the gh CLI (GH_TOKEN in Actions) for the contributions calendar."""
import datetime, json, re, subprocess, urllib.request

USER = "jaztulsi"
NAVY, PANEL, LINE = "#0A1A33", "#10264A", "#1D3A66"
BLUE, GOLD, GOLD2, WHITE, MUTED = "#3D7BFF", "#F2C14E", "#C99A2E", "#FFFFFF", "#9FB2D1"
FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',Helvetica,Arial,sans-serif"
REDUCE = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

# (label, simple-icons slug, bar fill). Bars show strength only; no numbers are printed.
TOOLS = [("PyTorch", "pytorch", .97), ("CUDA", "nvidia", .90),
         ("ROCm · AMD MI300X", "amd", .90), ("Hugging Face", "huggingface", .91),
         ("Python", "python", .96), ("Ollama", "ollama", .90),
         ("LangChain · LangGraph", "langchain", .92), ("Claude API", "anthropic", .94),
         ("TypeScript", "typescript", .95), ("React", "react", .94),
         ("Next.js", "nextdotjs", .91), ("Electron", "electron", .92),
         ("Tailwind CSS", "tailwindcss", .93), ("Supabase", "supabase", .89)]
# Share of code bytes across public, non-fork repos (gh api repos/*/languages), Nov 2026
LANGS = [("TypeScript", 43.5, GOLD), ("Python", 24.4, BLUE), ("JavaScript", 20.6, WHITE),
         ("HTML", 6.7, GOLD2), ("CSS", 3.5, "#6E93D6"), ("Other", 1.3, "#50627F")]
# GitHub's own dark-theme greens; empty cells lifted a touch so they show on navy
LEVELS = {"NONE": "#1A2A42", "FIRST_QUARTILE": "#0E4429", "SECOND_QUARTILE": "#006D32",
          "THIRD_QUARTILE": "#26A641", "FOURTH_QUARTILE": "#39D353"}

esc = lambda s: s.replace("&", "&amp;")


def frame(w, h):
    """Navy card, solid gold edge, heavy gold under-border, inner blue rule, gold corner brackets."""
    L, i = 22, 8
    corners = "".join(
        f'<path d="M{x0},{y0 + dy * L} V{y0} H{x0 + dx * L}" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="square"/>'
        for x0, y0, dx, dy in ((i, i, 1, 1), (w - i, i, -1, 1), (i, h - i - 6, 1, -1), (w - i, h - i - 6, -1, -1)))
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="6" fill="{NAVY}" stroke="{GOLD}" stroke-width="2"/>'
            f'<path d="M1,{h - 9} H{w - 1} V{h - 7} a6,6 0 0 1 -6,6 H7 a6,6 0 0 1 -6,-6z" fill="{GOLD}"/>'
            f'<rect x="{i + 5}" y="{i + 5}" width="{w - 2 * i - 10}" height="{h - 2 * i - 16}" rx="3" fill="none" stroke="{LINE}"/>{corners}')


def section(title):
    """Section title bar: navy band, gold rule on top, heavy gold rule underneath, gold end blocks."""
    body = (f'<rect x="0" y="0" width="840" height="52" rx="4" fill="{NAVY}"/>'
            f'<rect x="0" y="0" width="840" height="2.5" fill="{GOLD}"/>'
            f'<rect x="0" y="46" width="840" height="6" fill="{GOLD}"/>'
            f'<rect x="0" y="0" width="7" height="52" fill="{GOLD}"/><rect x="833" y="0" width="7" height="52" fill="{GOLD}"/>'
            f'<rect x="22" y="14" width="4" height="20" fill="{GOLD}"/>'
            f'<text x="36" y="31.5" class="h">{esc(title)}</text>'
            f'<rect x="802" y="21" width="6" height="6" fill="{GOLD}"/><rect x="788" y="21" width="6" height="6" fill="{GOLD2}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="840" height="52" viewBox="0 0 840 52" role="img"><title>{esc(title)}</title>'
            f'<style>text{{font-family:{FONT}}}.h{{font-size:19px;font-weight:700;fill:{WHITE};letter-spacing:-.2px}}</style>{body}</svg>\n')


def svg(w, h, body, style, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{esc(title)}</title><style>text{{font-family:{FONT}}}{style}{REDUCE}</style>{frame(w, h)}{body}</svg>\n')


def icon_path(slug):
    raw = urllib.request.urlopen(f"https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{slug}.svg").read().decode()
    d = re.search(r' d="([^"]+)"', raw).group(1)
    assert re.fullmatch(r"[0-9A-Za-z.,\- ]+", d), slug  # path data only, nothing else gets in
    return d


LINKEDIN_D = ("M4 9h3.5v11H4zM5.75 3.5a2 2 0 110 4 2 2 0 010-4zM9.5 9h3.4v1.6c.5-.9 1.7-1.85 3.5-1.85 3.6 0 4.3 2.4 4.3 5.4V20h-3.5v-5.2"
              "c0-1.25 0-2.85-1.75-2.85S13 13.3 13 14.7V20H9.5z")
HEADLINE = "LLM training research  ·  Voice software  ·  Organizer of Dublin HacX"
CONTACT = [("github", "github.com/jaztulsi"), ("gmail", "jaztulsi99@gmail.com"), (None, "linkedin.com/in/jasraj-tulsi")]


def header():
    # ponytail: text width estimated at 7.3px/char for 13.5px text; fine for this fixed copy
    items, gap = [(icon_path(s) if s else LINKEDIN_D, t, 22 + len(t) * 7.3) for s, t in CONTACT], 40
    x = 420 - (sum(w for *_, w in items) + gap * (len(items) - 1)) / 2
    row = []
    for d, t, w in items:
        row.append(f'<path d="{d}" fill="{GOLD}" transform="translate({x:.1f},200) scale(.6667)"/>'
                   f'<text x="{x + 22:.1f}" y="212" class="c">{esc(t)}</text>')
        x += w + gap
    body = f'''<text x="420" y="100" class="n" text-anchor="middle">Jasraj Tulsi</text>
<rect x="396" y="118" width="48" height="3" rx="1.5" fill="{GOLD}"/>
<text x="420" y="152" class="s" text-anchor="middle">{esc(HEADLINE)}</text>
<line x1="150" x2="690" y1="178" y2="178" stroke="{LINE}"/>{"".join(row)}'''
    style = (f".n{{font-size:54px;font-weight:700;letter-spacing:-1.6px;fill:{WHITE}}}"
             f".s{{font-size:17px;font-weight:500;fill:{GOLD}}}.c{{font-size:13.5px;fill:#D4DEEE}}")
    return svg(840, 244, body, style, f"Jasraj Tulsi. {HEADLINE}. " + ", ".join(t for _, t in CONTACT))


def meter(x, y, w, pct, n=24, g=3):
    """Solid segmented bar: gold blocks filled, panel blocks empty."""
    sw = (w - g * (n - 1)) / n
    return "".join(f'<rect x="{x + k * (sw + g):.1f}" y="{y}" width="{sw:.1f}" height="9" rx="1" fill="{GOLD if k < round(pct * n) else PANEL}"/>'
                   for k in range(n))


def toolbox():
    cw, gap, top, rh = 362, 36, 44, 54
    out = [f'<text x="40" y="38" class="h">Toolbox</text>']
    for n, (label, slug, pct) in enumerate(TOOLS):
        x, y = 40 + (n % 2) * (cw + gap), top + 12 + (n // 2) * rh
        bw = cw - 50
        out.append(f'''<rect x="{x}" y="{y}" width="36" height="36" rx="4" fill="{PANEL}" stroke="{GOLD2}" stroke-width="1.5"/>
<path d="{icon_path(slug)}" fill="{WHITE}" transform="translate({x + 8} {y + 8}) scale(.8333)"/>
<text x="{x + 50}" y="{y + 14}" class="t">{esc(label)}</text>
{meter(x + 50, y + 23, bw, pct)}''')
    h = top + 12 + 7 * rh + 24
    style = f".h{{font-size:15px;font-weight:700;fill:{GOLD}}}.t{{font-size:14px;font-weight:600;fill:{WHITE}}}"
    return svg(840, h, "".join(out), style, "Toolbox: " + ", ".join(t[0] for t in TOOLS))


def languages():
    x, usable = 40, 760 - 3 * (len(LANGS) - 1)
    out = [f'<text x="40" y="44" class="h">Languages across my public repos</text>',
           '<clipPath id="r"><rect x="40" y="62" width="760" height="12" rx="6"/></clipPath><g clip-path="url(#r)">']
    for _, pct, col in LANGS:
        w = usable * pct / 100
        out.append(f'<rect x="{x:.1f}" y="62" width="{w:.1f}" height="12" fill="{col}"/>')
        x += w + 3
    out.append("</g>")
    for n, (name, pct, col) in enumerate(LANGS):
        lx, ly = 40 + (n % 3) * 256, 108 + (n // 3) * 26
        out.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{col}"/>'
                   f'<text x="{lx + 18}" y="{ly}" class="t">{name}<tspan dx="8" class="p">{pct}%</tspan></text>')
    style = f".h{{font-size:15px;font-weight:600;fill:{WHITE}}}.t{{font-size:13px;font-weight:500;fill:{WHITE}}}.p{{fill:{MUTED}}}"
    return svg(840, 164, "".join(out), style, "Languages: " + ", ".join(f"{n} {p}%" for n, p, _ in LANGS))


def contributions():
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}' % USER
    cal = json.loads(subprocess.check_output(["gh", "api", "graphql", "-f", f"query={q}"]))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks, total = cal["weeks"], cal["totalContributions"]
    pitch, cell, gx, gy = 14, 11, 72, 84
    out = [f'<text x="40" y="44" class="h">{total:,} contributions in the last year</text>']
    last_label = -9
    for wi, wk in enumerate(weeks):
        days = wk["contributionDays"]
        first = datetime.date.fromisoformat(days[0]["date"])
        if first.day <= 7 and wi - last_label >= 3:
            out.append(f'<text x="{gx + wi * pitch}" y="{gy - 10}" class="a">{first.strftime("%b")}</text>')
            last_label = wi
        for day in days:
            row = (datetime.date.fromisoformat(day["date"]).weekday() + 1) % 7  # Sunday on top, like GitHub
            n = day["contributionCount"]
            out.append(f'<rect x="{gx + wi * pitch}" y="{gy + row * pitch}" width="{cell}" height="{cell}" rx="2.5" '
                       f'fill="{LEVELS[day["contributionLevel"]]}"><title>{n} on {day["date"]}</title></rect>')
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="40" y="{gy + row * pitch + 9}" class="a">{name}</text>')
    ly, lx = gy + 7 * pitch + 22, 800 - 5 * pitch - 34
    out.append(f'<text x="{lx - 8}" y="{ly + 9}" class="a" text-anchor="end">Less</text>')
    out += [f'<rect x="{lx + k * pitch}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" fill="{c}"/>' for k, c in enumerate(LEVELS.values())]
    out.append(f'<text x="{lx + 5 * pitch + 4}" y="{ly + 9}" class="a">More</text>')
    style = f".h{{font-size:15px;font-weight:600;fill:{WHITE}}}.a{{font-size:11px;fill:{MUTED}}}"
    return svg(840, ly + 40, "".join(out), style, f"{total} GitHub contributions in the last year")


if __name__ == "__main__":
    for name, fn in (("header", header), ("toolbox", toolbox), ("languages", languages), ("contributions", contributions)):
        open(f"assets/{name}.svg", "w").write(fn())
    for title in ("About", "Projects", "GitHub", "Contact"):
        open(f"assets/section-{title.lower()}.svg", "w").write(section(title))
