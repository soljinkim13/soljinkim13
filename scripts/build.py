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


# ---------------------------------------------------------------- 표지
def hero(T):
    W, H = 900, 330
    b = [f'<defs><linearGradient id="em" x1="0" y1="0" x2="1" y2="0">'
         f'<stop offset="0" stop-color="{T["green"]}"/><stop offset="1" stop-color="{T["green2"]}"/></linearGradient></defs>']
    # 저장소 주소와 탭 (포트폴리오 머리 부분)
    t, w = text("soljinkim13", 0, 20, "m", 13, T["sub"])
    b.append(t)
    t, w2 = text("  /  ", w, 20, "m", 13, T["muted"])
    b.append(t)
    b.append(text("profile", w + w2, 20, "mb", 13, T["text"])[0])
    x = 0
    for i, tab in enumerate(["Overview", "Projects", "Skills", "Activity"]):
        s, tw = text(tab, x, 50, "b" if i == 0 else "r", 13, T["text"] if i == 0 else T["sub"])
        b.append(s)
        if i == 0:
            b.append(f'<rect x="0" y="59" width="{_fmt(tw + 10)}" height="2.5" fill="{T["green"]}"/>')
        x += tw + 44
    b.append(text("$ whoami", 0, 112, "m", 14, T["sub"])[0])
    b.append(text(D.HOOK[0], 0, 168, "b", 42, T["text"])[0])
    s, ew = text(D.HOOK[1], 0, 224, "k", 42, "url(#em)")
    b.append(s)
    b.append(text(D.HOOK[2], ew, 224, "b", 42, T["text"])[0])
    s, nw = name_tag(0, 254, D.NAME, T, 23, 26, 46)
    b.append(s)
    b.append(text(D.ROLE, nw + 22, 285, "r", 23, T["sub"])[0])
    # 오른쪽 커밋 기록
    lx, ly, step = 612, 120, 50
    n = len(D.LOG)
    b.append(f'<line x1="{lx}" y1="{ly}" x2="{lx}" y2="{ly + step * (n - 1)}" stroke="{T["line"]}" stroke-width="2"/>')
    for i, (h, msg, dot) in enumerate(D.LOG):
        y = ly + i * step
        last = i == n - 1
        if dot == "gray":
            b.append(f'<circle cx="{lx}" cy="{y}" r="6.5" fill="{T["bg"]}" stroke="{T["gray"]}" stroke-width="2"/>')
        else:
            b.append(f'<circle cx="{lx}" cy="{y}" r="7" fill="{T["orange"] if dot == "orange" else T["green"]}"/>')
        s, hw = text(h, lx + 22, y + 4.5, "m", 12, T["muted"])
        b.append(s)
        b.append(text(msg, lx + 22 + hw + 12, y + 4.5, "mb" if last else "m", 12, T["text"])[0])
    b.append(text("HEAD → main", lx + 22, ly + step * (n - 1) + 34, "mb", 11.5, T["green"])[0])
    return svg(W, H, "".join(b), f"{D.NAME} · {D.ROLE} · {''.join(D.HOOK)}")


# ---------------------------------------------------------------- 구역 제목
def section(key, T):
    tag, title = D.SECTIONS[key]
    W, H = 900, 64
    s, tw = name_tag(0, 8, tag, T, 22, 22, 44)
    b = [s, text(title, tw + 20, 38, "b", 22, T["text"])[0]]
    return svg(W, H, "".join(b), f"{tag} {title}")


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


# ---------------------------------------------------------------- 기술 스택
def stack(T):
    W = 900
    rh = 44
    H = rh * len(D.STACK)
    b = []
    for i, (label, items) in enumerate(D.STACK):
        y = i * rh + 28
        b.append(text(label, 0, y, "b", 14, T["sub"])[0])
        b.append(tech_row(110, y, items, T, size=15, isz=18, gap=30, face="b")[0])
    return svg(W, H, "".join(b), "기술 스택: " + "; ".join(
        f'{l} {", ".join(parse_tech(t)[1] for t in it)}' for l, it in D.STACK))


# ---------------------------------------------------------------- 기록과 활동
def activity(T):
    W = 900
    b = []
    for i, (ic, pre, em) in enumerate(D.ACTIVITY):
        x = (i % 2) * 450
        y = (i // 2) * 44 + 28
        b.append(feather(ic, x, y - 15, 18, T["green"]))
        b.append(highlight(x + 30, y, (pre, em, ""), T, 15))
    y = 2 * 44 + 28
    b.append(feather("award", 0, y - 15, 18, T["green"]))
    b.append(text(" · ".join(D.CERTS), 30, y, "r", 15, T["text"])[0])
    H = y + 14
    return svg(W, H, "".join(b), "기록과 활동: " + ", ".join(p + e for _, p, e in D.ACTIVITY) + ". 자격: " + ", ".join(D.CERTS))


# ---------------------------------------------------------------- README
def _pic(name, alt, w="100%", link=None):
    s = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">'
         f'<img src="./assets/{name}-light.svg" width="{w}" alt="{alt}"></picture>')
    return f'<a href="{link}">{s}</a>' if link else s


def _sec(k):
    tag, title = D.SECTIONS[k]
    return "<p>" + _pic(f"section-{k}", f"{tag} {title}") + "</p>"


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



def readme():
    L = [
        "<p>" + _pic("hero", f"{D.NAME} · {D.ROLE} · {''.join(D.HOOK)}") + "</p>",
        "",
        "　".join(f'**{n}** [{t}]({u})' for n, t, u in D.LINKS),
        "",
        _sec("projects"),
        "",
        _featured_table(),
        "",
        _sec("more"),
        "",
        "| | 프로젝트 | 기술 | |\n|:--|:--|:--|:--|\n"
        + "\n".join(_more(i, p) for i, p in enumerate(D.MORE, len(D.FEATURED) + 1)),
        "",
        _sec("stack"),
        "<p>" + _pic("stack", "기술 스택: " + "; ".join(f'{l} {", ".join(parse_tech(t)[1] for t in it)}' for l, it in D.STACK)) + "</p>",
        "",
        _sec("activity"),
        "<p>" + _pic("activity", "기록과 활동: " + ", ".join(p + e for _, p, e in D.ACTIVITY) + ". 자격: " + ", ".join(D.CERTS)) + "</p>",
        "",
        _sec("grass"),
        '<p><picture><source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-green.svg">'
        '<img src="./profile-3d-contrib/profile-green.svg" width="100%" alt="최근 1년 커밋 기록을 입체 막대로 그린 잔디"></picture></p>',
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
    made = []
    for theme, T in THEMES.items():
        made.append(save("hero", theme, hero(T)))
        for k in D.SECTIONS:
            made.append(save(f"section-{k}", theme, section(k, T)))
        made.append(save("stack", theme, stack(T)))
        made.append(save("activity", theme, activity(T)))
    for name, label, fill in (("btn-repo", "레포 보기 ↗", "#2F8050"), ("btn-demo", "데모 ↗", "#C2672A")):
        p = os.path.join(OUT, f"{name}.svg")
        open(p, "w", encoding="utf-8").write(button(label, fill))
        made.append(p)
    slugs = {parse_tech(t)[0] for p in D.FEATURED + D.MORE for t in p["tech"]} - {None}
    for slug in sorted(slugs):
        p = os.path.join(OUT, "icons", f"{slug}.svg")
        open(p, "w", encoding="utf-8").write(icon_file(slug))
        made.append(p)
    readme()
    total = sum(os.path.getsize(p) for p in made)
    print(f"{len(made)} files, {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
