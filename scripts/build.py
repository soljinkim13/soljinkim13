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
    "k": Font("Pretendard-Black.ttf"),
}
FALLBACK = {"b": ["mb", "r"], "r": ["m", "b"], "mb": ["b", "m"], "m": ["r", "mb"], "k": ["b", "mb"]}


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

# ---------------------------------------------------------------- 색 (포트폴리오 Git 버전과 같은 팔레트)
THEMES = {
    "light": dict(
        bg="#FFFFFF", text="#1F2328", sub="#57606A", muted="#8B949E", line="#DADDE1",
        green="#2F8050", green2="#6DAA7C", tag="#E2F0E5", hl="#DDEFE0", chip="#2F8050", onChip="#FFFFFF",
        orange="#E0823D", orangeText="#C2672A", orangeHl="#FCEBDD", gray="#8B949E",
    ),
    "dark": dict(
        bg="#0D1117", text="#E6EDF3", sub="#A3ADB8", muted="#7D8590", line="#30363D",
        green="#7CC48F", green2="#A9D1B1", tag="#1B3324", hl="#1F3A29", chip="#3E9160", onChip="#FFFFFF",
        orange="#F0A061", orangeText="#F0A061", orangeHl="#3A2617", gray="#7D8590",
    ),
}

FEATHER = json.load(open(os.path.join(HERE, "feather.json"), encoding="utf-8"))


def _lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_tech(t):
    """'python' / 'langchain:LangGraph' / '=WebSocket' → (아이콘 슬러그 또는 None, 이름)"""
    if t.startswith("="):
        return None, t[1:]
    if ":" in t:
        return tuple(t.split(":", 1))
    return t, ICONS[t]["title"]


def brand(slug, T):
    c = "#" + ICONS[slug]["hex"]
    return c if _contrast(c, T["bg"]) >= 1.9 else T["text"]


def icon(slug, x, y, size, color):
    return (f'<path transform="translate({_fmt(x)} {_fmt(y)}) scale({size / 24:.4f})" fill="{color}" '
            f'd="{ICONS[slug]["path"]}"/>')


def feather(name, x, y, size, color, sw=2):
    return (f'<g transform="translate({_fmt(x)} {_fmt(y)}) scale({size / 24:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{FEATHER[name]}</g>')


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def save(name, theme, content):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}-{theme}.svg")
    open(p, "w", encoding="utf-8").write(content)
    return p


def tech_row(x, y, techs, T, size=14, isz=15, gap=18, face="r", color=None):
    """아이콘 + 이름을 테두리 없이 한 줄로. y는 글자 기준선. 끝 x를 돌려준다."""
    out = []
    for t in techs:
        slug, label = parse_tech(t)
        if slug:
            out.append(icon(slug, x, y - isz * 0.82, isz, brand(slug, T)))
            x += isz + 6
        else:
            out.append(f'<rect x="{_fmt(x + isz / 2 - 3)}" y="{_fmt(y - isz * 0.82 + isz / 2 - 3)}" width="6" height="6" fill="{T["green2"]}"/>')
            x += isz + 6
        s, w = text(label, x, y, face, size, color or T["text"])
        out.append(s)
        x += w + gap
    return "".join(out), x - gap


def highlight(x, y, parts, T, size, orange=False):
    """(앞, 강조, 뒤): 강조 부분에 옅은 초록 바탕과 굵은 초록 글씨 (포트폴리오의 형광펜 강조)."""
    pre, em, post = parts
    out = []
    s, w = text(pre, x, y, "r", size, T["text"])
    out.append(s)
    x += w
    ew = width(em, "b", size)
    out.append(f'<rect x="{_fmt(x - 2)}" y="{_fmt(y - size * 0.95)}" width="{_fmt(ew + 4)}" height="{_fmt(size * 1.3)}" '
               f'fill="{T["orangeHl"] if orange else T["hl"]}"/>')
    out.append(text(em, x, y, "b", size, T["orangeText"] if orange else T["green"])[0])
    x += ew
    out.append(text(post, x, y, "r", size, T["text"])[0])
    return "".join(out)


def name_tag(x, y, label, T, size, padx, h):
    """옅은 초록 바탕 위의 굵은 이름 (모서리 직각)."""
    w = width(label, "b", size) + padx * 2
    return (f'<rect x="{_fmt(x)}" y="{_fmt(y)}" width="{_fmt(w)}" height="{h}" fill="{T["tag"]}"/>'
            + text(label, x + padx, y + h / 2 + size * 0.36, "b", size, T["text"])[0]), w


def chip(x, y, label, T, size=13, h=26):
    """진한 초록 바탕의 흰 글씨 (담당 업무 표시)."""
    w = width(label, "b", size) + 24
    return (f'<rect x="{_fmt(x)}" y="{y}" width="{_fmt(w)}" height="{h}" fill="{T["chip"]}"/>'
            + text(label, x + 12, y + h / 2 + size * 0.36, "b", size, T["onChip"])[0]), w


# ---------------------------------------------------------------- 표지 배너 (README에 들어가는 유일한 큰 그림)
BANNER = {
    "light": dict(bgA="#EEF7F0", bgB="#FFFFFF", dot="#BFD6C5", glow="#7CC48F", glowOp=".28",
                  emA="#2F8050", emB="#5DB37E", lanes=["#7FA8C9", "#E0823D", "#4FAE9F", "#D4A43A"]),
    "dark": dict(bgA="#10211A", bgB="#0D1117", dot="#22382A", glow="#3E9160", glowOp=".30",
                 emA="#7CC48F", emB="#C4ECCF", lanes=["#8DB6D6", "#F0A061", "#6CC9BA", "#E3B95A"]),
}


def hero(T, theme):
    B = BANNER[theme]
    W, H = 1280, 440
    X0 = 76
    d = [
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{B["bgA"]}"/>'
        f'<stop offset=".75" stop-color="{B["bgB"]}"/></linearGradient>',
        f'<linearGradient id="em" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{B["emA"]}"/>'
        f'<stop offset="1" stop-color="{B["emB"]}"/></linearGradient>',
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["green"]}"/>'
        f'<stop offset=".7" stop-color="{B["emB"]}"/><stop offset="1" stop-color="{T["orange"]}"/></linearGradient>',
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="11" cy="11" r="1.2" fill="{B["dot"]}"/></pattern>',
        '<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset=".38" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".7" stop-color="#fff" stop-opacity="1"/></linearGradient>',
        '<mask id="m"><rect width="100%" height="100%" fill="url(#fade)"/></mask>',
        f'<radialGradient id="glow" cx="1090" cy="230" r="330" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{B["glow"]}" stop-opacity="{B["glowOp"]}"/>'
        f'<stop offset="1" stop-color="{B["glow"]}" stop-opacity="0"/></radialGradient>',
    ]
    b = [f'<defs>{"".join(d)}</defs>',
         f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#m)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
         f'<rect width="{W}" height="6" fill="url(#bar)"/>']

    # 왼쪽 글
    t, ww = text("$ whoami", X0, 100, "m", 19, T["sub"])
    b.append(t)
    b.append(f'<rect x="{_fmt(X0 + ww + 8)}" y="84" width="11" height="20" fill="{T["green"]}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    b.append(text(D.HOOK[0], X0, 186, "b", 58, T["text"])[0])
    t, ew = text(D.HOOK[1], X0, 266, "k", 58, "url(#em)")
    b.append(t)
    b.append(text(D.HOOK[2], X0 + ew, 266, "b", 58, T["text"])[0])
    s, nw = name_tag(X0, 314, D.NAME, T, 27, 26, 56)
    b.append(s)
    b.append(text(D.ROLE, X0 + nw + 24, 352, "r", 27, T["sub"])[0])
    b.append(text("github.com/soljinkim13", W - 40, H - 30, "m", 13, T["muted"], anchor="end")[0])

    # 오른쪽: main에서 갈라져 나갔다가 다시 합쳐지는 커밋 그래프
    my, fx, mx = 230, 800, 1092
    lanes = [96, 163, 297, 364]
    labels = D.BRANCHES
    def draw(path, color, wdt, delay):
        return (f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{wdt}" stroke-linecap="round" '
                f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="0">'
                f'<animate attributeName="stroke-dashoffset" values="1;0" dur="1.3s" begin="{delay}s" '
                f'calcMode="spline" keySplines=".3 0 .2 1" fill="freeze"/></path>')
    def dot(cx, cy, r, color, hollow, delay):
        fill = B["bgB"] if hollow else color
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="3" opacity="1">'
                f'<animate attributeName="opacity" values="0;1" dur=".4s" begin="{delay}s" fill="freeze"/></circle>')
    b.append(draw(f"M{fx} {my} H{W + 10}", T["green"], 5, 0))
    for i, (ly, label) in enumerate(zip(lanes, labels)):
        c = B["lanes"][i]
        dl = 0.25 + i * 0.15
        b.append(draw(f"M{fx} {my} C{fx + 46} {my} {fx + 40} {ly} {fx + 92} {ly} H990 "
                      f"C{1046} {ly} {1040} {my} {mx} {my}", c, 3.5, dl))
        for k, cx in enumerate((900, 960)):
            b.append(dot(cx, ly, 6, c, k == 1, dl + 0.5 + k * 0.15))
        hsh = ["a1f3c2e", "7d2b9e1", "3b9d0f4", "c4e8a07"][i]
        t, hw = text(hsh, 892, ly - 16, "m", 12.5, T["muted"])
        b.append(t)
        b.append(text(label, 892 + hw + 10, ly - 16, "b", 14, T["sub"])[0])
    b.append(dot(fx, my, 8, T["green"], False, 0))
    b.append(dot(mx, my, 11, T["green"], False, 1.4))
    hx = 1186
    b.append(f'<circle cx="{hx}" cy="{my}" r="13" fill="{T["green"]}"/>'
             f'<circle cx="{hx}" cy="{my}" r="13" fill="none" stroke="{T["green"]}" stroke-width="2.5">'
             f'<animate attributeName="r" values="13;30" dur="2.2s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".9;0" dur="2.2s" repeatCount="indefinite"/></circle>')
    b.append(text("HEAD → main", hx, my - 30, "mb", 14, T["green"], anchor="middle")[0])
    b.append(text("backend", hx, my + 48, "mb", 18, T["text"], anchor="middle")[0])
    return svg(W, H, "".join(b), f"{D.NAME} · {D.ROLE} · {''.join(D.HOOK)}")


# ---------------------------------------------------------------- 버튼과 아이콘 (README 글 사이에 넣는 작은 그림)
def button(label, fill, h=24, size=13):
    """모서리 없는 버튼. 라이트·다크 모두 같은 그림을 쓴다."""
    w = width(label, "b", size) + 22
    body = (f'<rect width="{_fmt(w)}" height="{h}" fill="{fill}"/>'
            + text(label, 11, h / 2 + size * 0.36, "b", size, "#FFFFFF")[0])
    return svg(round(w), h, body, label)


def icon_file(slug):
    """기술 아이콘 한 개. 라이트·다크 어디서도 묻히는 색(아주 어둡거나 밝은 색)은 회색으로."""
    c = "#" + ICONS[slug]["hex"]
    if _contrast(c, "#FFFFFF") < 1.9 or _contrast(c, "#0D1117") < 1.9:
        c = "#8B949E"
    return svg(24, 24, f'<path fill="{c}" d="{ICONS[slug]["path"]}"/>', ICONS[slug]["title"])


# ---------------------------------------------------------------- README (글과 HTML)
def _pic(name, alt, w="100%", link=None):
    s = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">'
         f'<img src="./assets/{name}-light.svg" width="{w}" alt="{alt}"></picture>')
    return f'<a href="{link}">{s}</a>' if link else s


def _techs(techs):
    out = []
    for t in techs:
        slug, label = parse_tech(t)
        img = f'<img src="./assets/icons/{slug}.svg" height="14" alt=""> ' if slug else ""
        out.append(img + label)
    return "&nbsp; ".join(out)


def _buttons(p, h=20):
    out = []
    if p.get("repo"):
        out.append(f'<a href="{p["repo"]}"><img src="./assets/btn-repo.svg" height="{h}" alt="{p["name"]} 저장소"></a>')
    if p.get("demo"):
        out.append(f'<a href="{p["demo"]}"><img src="./assets/btn-demo.svg" height="{h}" alt="{p["name"]} 데모"></a>')
    return " ".join(out)


def _featured(i, p):
    """표 한 칸: 제목, 설명, 담당, 기술, 결과, 버튼."""
    pre, em, post = p["result"]
    btn = _buttons(p, 22)
    return (f'<td width="50%" valign="top">\n'
            f'<h3>{i:02d}&nbsp; {p["name"]}</h3>\n'
            f'{p["desc"]}<br><br>\n'
            f'<b>{p["role"]}</b> · {p["team"]} · {p["period"]}<br>\n'
            f'{_techs(p["tech"])}<br>\n'
            f'결과 &nbsp;{pre}<b>{em}</b>{post}'
            + (f'<br><br>\n{btn}\n' if btn else '\n')
            + '</td>')



def _featured_table():
    rows = []
    items = list(enumerate(D.FEATURED, 1))
    for k in range(0, len(items), 2):
        rows.append("<tr>\n" + "\n".join(_featured(i, p) for i, p in items[k:k + 2]) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def _more(i, p):
    return f'| {i:02d} | **{p["name"]}**&nbsp; {p["desc"]} | {_techs(p["tech"][:3])} | {_buttons(p, 22)} |'


def _h(k):
    tag, title = D.SECTIONS[k]
    return f"## {tag} <sub>{title}</sub>"


def readme():
    L = [
        "<p>" + _pic("hero", f"{D.NAME} · {D.ROLE} · {''.join(D.HOOK)}") + "</p>",
        "",
        "　".join(f'**{n}** [{t}]({u})' for n, t, u in D.LINKS),
        "",
        _h("projects"),
        "",
        _featured_table(),
        "",
        _h("more"),
        "",
        "| | 프로젝트 | 기술 | |\n|:--|:--|:--|:--|\n"
        + "\n".join(_more(i, p) for i, p in enumerate(D.MORE, len(D.FEATURED) + 1)),
        "",
        _h("stack"),
        "",
        "| | |\n|:--|:--|\n" + "\n".join(f"| **{l}** | {_techs(it)} |" for l, it in D.STACK),
        "",
        _h("activity"),
        "",
        "\n".join(f"- {pre}**{em}**" for _, pre, em in D.ACTIVITY),
        "- 자격 &nbsp;" + " · ".join(D.CERTS),
        "",
        _h("grass"),
        "",
        '<picture><source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-green.svg">'
        '<img src="./profile-3d-contrib/profile-green.svg" width="100%" alt="최근 1년 커밋 기록을 입체 막대로 그린 잔디"></picture>',
        "",
        "<!-- 이 파일은 scripts/build.py가 만든다. 내용은 scripts/data.py에서 고치고 python3 scripts/build.py를 실행한다. "
        "잔디 그림은 .github/workflows/profile-3d.yml이 매일 새로 그린다. -->",
        "",
    ]
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(L))


def main():
    import shutil
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "icons"))
    made = [save("hero", theme, hero(T, theme)) for theme, T in THEMES.items()]
    for name, label, fill in (("btn-repo", "레포 보기 ↗", "#2F8050"), ("btn-demo", "데모 ↗", "#C2672A")):
        p = os.path.join(OUT, f"{name}.svg")
        open(p, "w", encoding="utf-8").write(button(label, fill))
        made.append(p)
    slugs = {parse_tech(t)[0] for p in D.FEATURED + D.MORE for t in p["tech"]}
    slugs |= {parse_tech(t)[0] for _, it in D.STACK for t in it}
    for slug in sorted(slugs - {None}):
        p = os.path.join(OUT, "icons", f"{slug}.svg")
        open(p, "w", encoding="utf-8").write(icon_file(slug))
        made.append(p)
    readme()
    total = sum(os.path.getsize(p) for p in made)
    print(f"{len(made)} files, {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
