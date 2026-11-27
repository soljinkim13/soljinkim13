"""프로필 README의 SVG를 만든다.  python3 scripts/build.py

글자는 모두 글꼴 윤곽(path)으로 바꿔 넣는다. GitHub는 README 이미지에서 외부 글꼴을 불러오지 않기 때문에,
이렇게 해야 어느 기기에서나 같은 모양으로 보인다. 필요한 것: pip install fonttools
"""
import json
import math
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets")
sys.path.insert(0, HERE)
import data as D  # noqa: E402

ICONS = json.load(open(os.path.join(HERE, "icons.json"), encoding="utf-8"))


# ---------------------------------------------------------------- 글꼴
class Font:
    def __init__(self, file):
        self.tt = TTFont(os.path.join(HERE, "fonts", file))
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.upm = self.tt["head"].unitsPerEm
        self.hmtx = self.tt["hmtx"]


F = {
    "b": Font("SpoqaHanSansNeo-Bold.otf"),
    "r": Font("SpoqaHanSansNeo-Regular.otf"),
    "mb": Font("JetBrainsMono-Bold.ttf"),
    "m": Font("JetBrainsMono-Regular.ttf"),
}
FALLBACK = {"b": ["mb", "r"], "r": ["m", "b"], "mb": ["b", "m"], "m": ["r", "mb"]}


def _fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _pick(face, ch):
    for k in [face] + FALLBACK[face]:
        if ord(ch) in F[k].cmap:
            return F[k]
    raise SystemExit(f"글꼴에 없는 글자: {ch!r}")


def width(s, face, size, ls=0):
    w = 0
    for ch in s:
        f = _pick(face, ch)
        w += f.hmtx[f.cmap[ord(ch)]][0] * size / f.upm + ls
    return w - (ls if s else 0)


def text(s, x, y, face, size, fill, anchor="start", ls=0, extra=""):
    """글자를 path 하나로 바꾼다. y는 글자 기준선."""
    w = width(s, face, size, ls)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    d = []
    for ch in s:
        f = _pick(face, ch)
        g = f.cmap[ord(ch)]
        sc = size / f.upm
        if ch != " ":
            pen = SVGPathPen(f.gs, ntos=_fmt)
            f.gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, y)))
            d.append(pen.getCommands())
        x += f.hmtx[g][0] * sc + ls
    return f'<path fill="{fill}" {extra} d="{"".join(d)}"/>', w


def wrap(s, face, size, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if width(t, face, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


# ---------------------------------------------------------------- 색
THEMES = {
    "light": dict(
        bg="#FFFFFF", card="#F5F9F6", card2="#EEF5F0", line="#DCE8DF",
        text="#1F2328", sub="#57606A", muted="#8B949E",
        green="#2F8050", green2="#6DAA7C", greenSoft="#E2F0E5", onGreen="#FFFFFF",
        orange="#D9752F", orangeSoft="#FCEBDD", pill="#FFFFFF",
        lanes=["#2F8050", "#6DAA7C", "#E0823D", "#7FA8C9"],
        heroA="#F3F9F4", heroB="#E3F0E7",
    ),
    "dark": dict(
        bg="#0D1117", card="#121C17", card2="#17241D", line="#253A2D",
        text="#E6EDF3", sub="#A3ADB8", muted="#6E7781",
        green="#7CC48F", green2="#4F9463", greenSoft="#1B3324", onGreen="#0D1117",
        orange="#F0A061", orangeSoft="#3A2617", pill="#0F1713",
        lanes=["#7CC48F", "#4F9463", "#F0A061", "#8DB6D6"],
        heroA="#0F1A14", heroB="#132A1C",
    ),
}


def _lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def icon_color(slug, T, against):
    c = "#" + ICONS[slug]["hex"]
    return c if _contrast(c, against) >= 1.9 else T["text"]


def parse_tech(t):
    """'python' / 'langchain:LangGraph' / '=WebSocket' → (아이콘 슬러그 또는 None, 이름)"""
    if t.startswith("="):
        return None, t[1:]
    if ":" in t:
        slug, label = t.split(":", 1)
        return slug, label
    return t, ICONS[t]["title"]


def icon(slug, x, y, size, color):
    s = size / 24
    return f'<path transform="translate({_fmt(x)} {_fmt(y)}) scale({s:.4f})" fill="{color}" d="{ICONS[slug]["path"]}"/>'


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def save(name, theme, content):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}-{theme}.svg")
    open(p, "w", encoding="utf-8").write(content)
    return p


# ---------------------------------------------------------------- 작은 부품
def chip(x, y, label, T, kind="fill", h=24, size=12):
    w = width(label, "b", size) + 20
    if kind == "fill":
        bg = f'<rect x="{_fmt(x)}" y="{y}" width="{_fmt(w)}" height="{h}" rx="7" fill="{T["green"]}"/>'
        t, _ = text(label, x + 10, y + h / 2 + size * 0.36, "b", size, T["onGreen"])
    else:
        bg = (f'<rect x="{_fmt(x + .5)}" y="{y + .5}" width="{_fmt(w - 1)}" height="{h - 1}" rx="7" '
              f'fill="none" stroke="{T["line"]}"/>')
        t, _ = text(label, x + 10, y + h / 2 + size * 0.36, "b", size, T["sub"])
    return bg + t, w


def pill(x, y, tech, T, h=26):
    slug, label = parse_tech(tech)
    size = 11.5
    tw = width(label, "b", size)
    pad = 9
    if slug:
        w = pad + 14 + 6 + tw + pad
    else:
        w = pad + 6 + 6 + tw + pad
    out = (f'<rect x="{_fmt(x + .5)}" y="{y + .5}" width="{_fmt(w - 1)}" height="{h - 1}" rx="{h / 2 - .5}" '
           f'fill="{T["pill"]}" stroke="{T["line"]}"/>')
    if slug:
        out += icon(slug, x + pad, y + (h - 14) / 2, 14, icon_color(slug, T, T["pill"]))
        tx = x + pad + 14 + 6
    else:
        out += f'<circle cx="{_fmt(x + pad + 3)}" cy="{y + h / 2}" r="3" fill="{T["green2"]}"/>'
        tx = x + pad + 6 + 6
    t, _ = text(label, tx, y + h / 2 + size * 0.36, "b", size, T["text"])
    return out + t, w


def pills(x, y, techs, T, maxw, gap=6, h=26):
    """기술 이름표를 maxw 안에서 줄을 바꿔 가며 놓는다. (svg, 전체 높이)"""
    out, cx, cy = "", x, y
    for t in techs:
        _, w = pill(0, 0, t, T, h)
        if cx > x and cx + w > x + maxw:
            cx, cy = x, cy + h + gap
        s, w = pill(cx, cy, t, T, h)
        out += s
        cx += w + gap
    return out, cy + h - y


# ---------------------------------------------------------------- 표지
def hero(T, theme):
    W, H = 900, 300
    b = [f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
         f'<stop offset="0" stop-color="{T["heroA"]}"/><stop offset="1" stop-color="{T["heroB"]}"/></linearGradient>'
         f'<linearGradient id="em" x1="0" y1="0" x2="1" y2="0">'
         f'<stop offset="0" stop-color="{T["green"]}"/><stop offset="1" stop-color="{T["lanes"][3]}"/></linearGradient></defs>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="url(#bg)" stroke="{T["line"]}"/>']
    x0 = 52
    b.append(text("~/soljinkim13", x0, 66, "m", 13, T["muted"])[0])
    b.append(text("(main)", x0 + width("~/soljinkim13 ", "m", 13), 66, "m", 13, T["green"])[0])
    t, nw = text(D.NAME, x0, 140, "b", 58, T["text"])
    b.append(t)
    b.append(text(D.ROLE, x0 + nw + 20, 138, "mb", 19, T["green"])[0])
    b.append(text(D.NAME_EN, x0 + nw + 20, 112, "m", 13, T["muted"])[0])
    b.append(text(D.HOOK[0], x0, 196, "r", 23, T["sub"])[0])
    t, ew = text(D.HOOK[1], x0, 236, "b", 28, "url(#em)")
    b.append(t)
    b.append(text(D.HOOK[2], x0 + ew, 236, "b", 28, T["text"])[0])

    # 오른쪽: 갈래가 합쳐지는 커밋 그래프
    gx0, gx1, mx, my = 560, 724, 828, 150
    lanes = [78, 124, 170, 216]
    for i, (ly, name) in enumerate(zip(lanes, D.BRANCHES)):
        c = T["lanes"][i]
        b.append(f'<path d="M{gx0} {ly} H{gx1} C{gx1 + 52} {ly} {mx - 50} {my} {mx - 14} {my}" '
                 f'fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/>')
        for k, cx in enumerate((gx0, gx0 + 82, gx1)):
            b.append(f'<circle cx="{cx}" cy="{ly}" r="{6 if k == 0 else 5}" fill="{T["heroA"] if k else c}" '
                     f'stroke="{c}" stroke-width="3"/>')
        b.append(text(name, gx0 + 14, ly - 10, "b", 11.5, T["sub"])[0])
    b.append(f'<circle cx="{mx}" cy="{my}" r="14" fill="{T["green"]}"/>'
             f'<circle cx="{mx}" cy="{my}" r="14" fill="none" stroke="{T["green"]}" stroke-width="2">'
             f'<animate attributeName="r" values="14;26;14" dur="2.6s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".8;0;.8" dur="2.6s" repeatCount="indefinite"/></circle>')
    b.append(text("backend", mx, my + 40, "mb", 13, T["green"], anchor="middle")[0])
    b.append(text("HEAD", mx, my - 26, "m", 11, T["muted"], anchor="middle")[0])
    return svg(W, H, "".join(b), f"{D.NAME} · {D.ROLE} · {' '.join(D.HOOK)}")


# ---------------------------------------------------------------- 구역 제목
def section(key, T):
    W, H = 900, 64
    ko, cmd = D.SECTIONS[key]
    b = [f'<rect x="0" y="22" width="5" height="28" rx="2.5" fill="{T["green"]}"/>']
    t, w = text(ko, 20, 46, "b", 24, T["text"])
    b.append(t)
    b.append(text("$ " + cmd, 20 + w + 16, 45, "m", 13.5, T["muted"])[0])
    b.append(f'<line x1="{_fmt(20 + w + 16 + width("$ " + cmd, "m", 13.5) + 16)}" y1="40" x2="{W}" y2="40" '
             f'stroke="{T["line"]}" stroke-dasharray="2 5"/>')
    return svg(W, H, "".join(b), ko)


# ---------------------------------------------------------------- 걸어온 길
def journey(T):
    W, H = 900, 150
    y = 52
    xs = [80, 300, 530, 770]
    b = [f'<line x1="30" y1="{y}" x2="{W - 30}" y2="{y}" stroke="{T["line"]}" stroke-width="3" stroke-linecap="round"/>',
         f'<line x1="30" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{T["green2"]}" stroke-width="3" stroke-linecap="round"/>']
    for i, (x, (date, title, sub)) in enumerate(zip(xs, D.JOURNEY)):
        last = i == len(xs) - 1
        b.append(f'<circle cx="{x}" cy="{y}" r="{10 if last else 8}" fill="{T["green"] if last else T["bg"]}" '
                 f'stroke="{T["green"]}" stroke-width="3"/>')
        b.append(text(date, x, y - 24, "mb", 13, T["green"], anchor="middle")[0])
        b.append(text(title, x, y + 40, "b", 15.5, T["text"], anchor="middle")[0])
        b.append(text(sub, x, y + 63, "r", 12.5, T["sub"], anchor="middle")[0])
    s, w = chip(0, 0, "HEAD → now", T, h=22, size=11)
    b.append(f'<g transform="translate({xs[-1] + 22} {y - 11})">{s}</g>')
    return svg(W, H, "".join(b), "걸어온 길: " + " → ".join(j[1] for j in D.JOURNEY))


# ---------------------------------------------------------------- 프로젝트 카드
def card(p, idx, T, big, H=None):
    """프로젝트 카드. H를 주지 않으면 필요한 높이만 돌려준다(같은 줄 카드 높이를 맞추려고)."""
    W, P = 440, 24
    acc = T["orange"] if p.get("orange") else T["green"]
    b = []
    y = 42
    t, nw = text(f"{idx:02d}", P, y, "mb", 12.5, acc)
    b.append(t)
    b.append(text(p["tag"], P + nw + 10, y, "m", 12, T["muted"], ls=0.6)[0])
    b.append(text(p["period"], W - P, y, "m", 12, T["muted"], anchor="end")[0])
    y += 38 if big else 34
    b.append(text(p["name"], P, y, "b", 26 if big else 21, T["text"])[0])
    y += 24 if big else 23
    for line in wrap(p["desc"], "r", 14 if big else 13, W - 2 * P)[:2]:
        b.append(text(line, P, y, "r", 14 if big else 13, T["sub"])[0])
        y += 20
    y += 2
    s, w = chip(P, y, p["role"], T)
    b.append(s)
    s2, _ = chip(P + w + 6, y, p["team"], T, kind="line")
    b.append(s2)
    y += 24
    if big:
        mv, ml = p["metric"]
        y += 50
        t, mw = text(mv, P, y, "b", 34, acc)
        b.append(t)
        b.append(text(ml, P + mw + 12, y - 4, "r", 13, T["sub"])[0])
        y += 8
    _, ph = pills(0, 0, p["tech"], T, W - 2 * P)
    need = y + 20 + ph + P
    if H is None:
        return need
    ps, _ = pills(P, H - P - ph, p["tech"], T, W - 2 * P)
    b.append(ps)
    frame = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{T["card"]}" stroke="{T["line"]}"/>'
             f'<rect x="0" y="24" width="4" height="{40 if big else 30}" rx="2" fill="{acc}"/>')
    return svg(W, H, frame + "".join(b), f'{p["name"]}: {p["desc"]} ({p["role"]}, {p["team"]})')


# ---------------------------------------------------------------- 기술 스택
def stack(T):
    W = 900
    bw, bh, gap = 438, 150, 24
    rows = math.ceil(len(D.STACK) / 2)
    H = rows * bh + (rows - 1) * 16
    b = []
    for i, (en, ko, items) in enumerate(D.STACK):
        bx = (i % 2) * (bw + gap)
        by = (i // 2) * (bh + 16)
        b.append(f'<rect x="{bx + .5}" y="{by + .5}" width="{bw - 1}" height="{bh - 1}" rx="16" fill="{T["card"]}" stroke="{T["line"]}"/>')
        t, w = text(ko, bx + 22, by + 34, "b", 16, T["text"])
        b.append(t)
        b.append(text(en, bx + 22 + w + 10, by + 33, "m", 11.5, T["green"], ls=0.8)[0])
        for k, tech in enumerate(items):
            slug, label = parse_tech(tech)
            tx = bx + 22 + k * 82
            ty = by + 52
            b.append(f'<rect x="{tx + .5}" y="{ty + .5}" width="55" height="55" rx="14" fill="{T["pill"]}" stroke="{T["line"]}"/>')
            if slug:
                b.append(icon(slug, tx + 14, ty + 14, 27, icon_color(slug, T, T["pill"])))
            else:
                ab = "".join(ch for ch in label if ch.isupper())[:2] or label[:2]
                b.append(text(ab, tx + 28, ty + 34, "mb", 16, T["green"], anchor="middle")[0])
            size = 11.5 if width(label, "b", 11.5) <= 78 else 10
            b.append(text(label, tx + 28, ty + 76, "b", size, T["sub"], anchor="middle")[0])
    return svg(W, H, "".join(b), "기술 스택: " + ", ".join(parse_tech(t)[1] for _, _, it in D.STACK for t in it))


# ---------------------------------------------------------------- 기록과 활동
def activity(T):
    W = 900
    n = len(D.STATS)
    gap = 16
    tw = (W - gap * (n - 1)) / n
    th = 112
    b = []
    for i, (v, l) in enumerate(D.STATS):
        x = i * (tw + gap)
        b.append(f'<rect x="{_fmt(x + .5)}" y=".5" width="{_fmt(tw - 1)}" height="{th - 1}" rx="16" fill="{T["card"]}" stroke="{T["line"]}"/>')
        b.append(text(v, x + 22, 58, "b", 34, T["green"])[0])
        b.append(text(l, x + 22, 88, "r", 13.5, T["sub"])[0])
    y = th + 18
    x = 0
    for c in D.CERTS:
        s, w = chip(x, y, c, T, kind="line", h=28, size=12.5)
        b.append(s)
        x += w + 8
    H = y + 28
    return svg(W, H, "".join(b), "기록과 활동: " + ", ".join(f"{l} {v}" for v, l in D.STATS) + " · " + ", ".join(D.CERTS))


# ---------------------------------------------------------------- README
def _pic(name, alt, w="100%", link=None):
    s = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">'
         f'<img src="./assets/{name}-light.svg" width="{w}" alt="{alt}"></picture>')
    return f'<a href="{link}">{s}</a>' if link else s


def _sec(k):
    return "<p>" + _pic(f"section-{k}", D.SECTIONS[k][0]) + "</p>"


def _grid(items, start):
    rows = []
    for i in range(0, len(items), 2):
        cells = []
        for j, p in enumerate(items[i:i + 2]):
            techs = ", ".join(parse_tech(t)[1] for t in p["tech"])
            alt = f'{p["name"]}: {p["desc"]}. 역할 {p["role"]} ({p["team"]}). 기술 {techs}'
            cells.append(_pic(f"project-{start + i + j:02d}", alt, "49%", p.get("link")))
        rows.append('<p align="center">\n' + "\n".join(cells) + "\n</p>")
    return "\n".join(rows)


def readme():
    hook = "".join(D.HOOK)
    L = [
        '<div align="center">',
        "",
        _pic("hero", f"{D.NAME} · {D.ROLE} · {hook}"),
        "",
        "".join(f'<a href="{u}"><img src="https://img.shields.io/badge/{b}?style=flat-square&logo={lg}&logoColor=white" alt="{a}"></a> '
                for a, b, lg, u in D.LINKS).strip(),
        "",
        "</div>",
        "",
        _sec("journey"),
        "<p>" + _pic("journey", "걸어온 길: " + " → ".join(f"{d} {t}" for d, t, _ in D.JOURNEY)) + "</p>",
        "",
        _sec("projects"),
        _grid(D.FEATURED, 1),
        "",
        _sec("more"),
        _grid(D.MORE, len(D.FEATURED) + 1),
        "",
        _sec("stack"),
        "<p>" + _pic("stack", "기술 스택: " + ", ".join(parse_tech(t)[1] for _, _, it in D.STACK for t in it)) + "</p>",
        "",
        _sec("activity"),
        "<p>" + _pic("activity", "기록과 활동: " + ", ".join(f"{l} {v}" for v, l in D.STATS)) + "</p>",
        "",
        _sec("grass"),
        '<p><picture><source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-green.svg">'
        '<img src="./profile-3d-contrib/profile-green-animate.svg" width="100%" alt="최근 1년 커밋 기록을 입체 막대로 그린 잔디"></picture></p>',
        "",
        "<!-- 이 파일은 scripts/build.py가 만든다. 내용은 scripts/data.py에서 고치고 python3 scripts/build.py를 실행한다. "
        "잔디 그림은 .github/workflows/profile-3d.yml이 매일 새로 그린다. -->",
        "",
    ]
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(L))


def main():
    made = []
    for theme, T in THEMES.items():
        made.append(save("hero", theme, hero(T, theme)))
        for k in D.SECTIONS:
            made.append(save(f"section-{k}", theme, section(k, T)))
        made.append(save("journey", theme, journey(T)))
        for items, start, big in ((D.FEATURED, 1, True), (D.MORE, len(D.FEATURED) + 1, False)):
            H = max(card(p, 0, T, big) for p in items)
            for i, p in enumerate(items, start):
                made.append(save(f"project-{i:02d}", theme, card(p, i, T, big, H)))
        made.append(save("stack", theme, stack(T)))
        made.append(save("activity", theme, activity(T)))
    readme()
    total = sum(os.path.getsize(p) for p in made)
    print(f"{len(made)} files, {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
