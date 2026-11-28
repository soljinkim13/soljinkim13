"""프로필 README의 SVG를 만든다.  python3 scripts/build.py

디자인: Field Notes. 종이색 표지 + 잔디 그리드, 녹색 단계색에 클레이색을 조금 섞는다.
라이트·다크 그림을 따로 만들고 README에서 <picture>로 고른다.

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
    "g": Font("BricolageGrotesque-Bold.ttf"),
}
FALLBACK = {"b": ["mb", "r"], "r": ["m", "b"], "mb": ["b", "m"], "m": ["r", "mb"], "k": ["b", "mb"], "g": ["k", "b"]}


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


# ---------------------------------------------------------------- 색 (Field Notes)
THEMES = {
    "light": dict(paper="#F4F2EB", ink="#17261D", mute="#6E7A71", line="#D9D9CC",
                  g0="#E6E6DA", g1="#C9D8C0", g2="#93B48F", g3="#4F7F5C", g4="#1F4A33",
                  clay="#D9825B", hl="#E3EDDC", clayHl="#F6E3D6"),
    "dark": dict(paper="#0F1612", ink="#E7ECE5", mute="#8A978E", line="#25302A",
                 g0="#1A231E", g1="#23402F", g2="#2F6A47", g3="#5FA273", g4="#A8D8A2",
                 clay="#E49A74", hl="#1C3326", clayHl="#3A2617"),
}
W = 1000
DOT = {"gray": "mute", "orange": "clay", "green": "g3"}

CSS = """
.up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{opacity:.25}}
.c{opacity:0;transform-box:fill-box;transform-origin:center;animation:grow 7s cubic-bezier(.2,.7,.2,1) infinite}
@keyframes grow{0%{opacity:0;transform:scale(.4)}8%{opacity:1;transform:scale(1)}82%{opacity:1;transform:scale(1)}92%,100%{opacity:0;transform:scale(.6)}}
.ul{animation:draw 1.2s cubic-bezier(.6,0,.2,1) .6s forwards}
@keyframes draw{to{stroke-dashoffset:0}}
@media (prefers-reduced-motion: reduce){*{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}}
"""


def svg(w, h, body, title, css=""):
    t = title.replace("&", "&amp;")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{t}"><title>{t}</title><style>{CSS}{css}</style>{body}</svg>\n')


def save(name, theme, content):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}-{theme}.svg")
    open(p, "w", encoding="utf-8").write(content)
    return p


def parse_tech(t):
    if t.startswith("="):
        return None, t[1:]
    if ":" in t:
        return tuple(t.split(":", 1))
    return t, ICONS[t]["title"]


def icon(slug, x, y, size, color):
    return (f'<path transform="translate({_fmt(x)} {_fmt(y)}) scale({size / 24:.4f})" fill="{color}" '
            f'd="{ICONS[slug]["path"]}"/>')


def up(body, delay):
    return f'<g class="up" style="animation-delay:{delay:.2f}s">{body}</g>'


def label(s, x, y, T, size=12, color=None, anchor="start"):
    """고정폭 이름표 (영문 대문자는 글자 간격을 조금 벌린다)."""
    return text(s, x, y, "m", size, color or T["mute"], anchor, ls=1.4 if s.isupper() else 0)[0]


def section_title(s, T, x=24, y=30):
    return f'<rect x="{x}" y="{y - 11}" width="11" height="11" rx="3" fill="{T["g3"]}"/>' + label(s, x + 20, y, T, 13)


def emph(x, y, parts, T, size, orange=False, face="r"):
    """(앞, 강조, 뒤): 강조는 굵은 녹색(또는 클레이) 글씨에 옅은 바탕."""
    pre, em, post = parts
    out = []
    s, w = text(pre, x, y, face, size, T["ink"])
    out.append(s)
    x += w
    ew = width(em, "b", size)
    out.append(f'<rect x="{_fmt(x - 2)}" y="{_fmt(y - size * .95)}" width="{_fmt(ew + 4)}" height="{_fmt(size * 1.3)}" rx="3" fill="{T["clayHl"] if orange else T["hl"]}"/>')
    out.append(text(em, x, y, "b", size, T["clay"] if orange else T["g3"])[0])
    x += ew
    s, w = text(post, x, y, face, size, T["ink"])
    out.append(s)
    return "".join(out), x + w


def grass(gx, gy, cols, rows, T, seed=7, cell=14, gap=5, clay=((12, 2), (6, 5))):
    import random
    random.seed(seed)
    out = []
    for c in range(cols):
        for r in range(rows):
            lv = random.choices([0, 1, 2, 3, 4], [30, 25, 20, 15, 10])[0]
            fill = T["clay"] if (c, r) in clay else T[f"g{lv}"]
            out.append(f'<rect class="c" x="{gx + c * (cell + gap)}" y="{gy + r * (cell + gap)}" width="{cell}" height="{cell}" '
                       f'rx="3.5" fill="{fill}" style="animation-delay:{c * .09 + r * .03:.2f}s"/>')
    return "".join(out)


# ---------------------------------------------------------------- 표지
def hero(T):
    nm, nw = text(D.NAME_EN, 44, 146, "g", 64, T["ink"], ls=-2)
    hook, _ = emph(48, 196, D.HOOK, T, 17)
    stack = " · ".join(D.HERO_STACK)
    body = (f'<rect width="{W}" height="280" rx="14" fill="{T["paper"]}"/>'
            + up(label(f"{D.NAME} · {D.ROLE.upper()}", 48, 62, T, 13) + nm, .1)
            + f'<path class="ul" stroke-dasharray="{nw:.0f}" stroke-dashoffset="{nw:.0f}" d="M48 164 H{48 + nw:.0f}" '
              f'stroke="{T["clay"]}" stroke-width="2.5" stroke-linecap="round" fill="none"/>'
            + up(hook
                 + f'<line x1="48" y1="222" x2="440" y2="222" stroke="{T["line"]}"/>'
                 + f'<circle class="pulse" cx="53" cy="248" r="4" fill="{T["g3"]}"/>'
                 + label(stack, 66, 252, T, 13), .35)
            + grass(653, 72, 16, 7, T)
            + label("commits, one cell at a time", 952, 252, T, 13, anchor="end"))
    return svg(W, 280, body, f"{D.NAME_EN} {D.NAME} · {D.ROLE} · {''.join(D.HOOK)}")


# ---------------------------------------------------------------- 소개 (A1)
def about(T):
    o = [section_title("ABOUT", T)]
    left = "".join(text(l, 24, 78 + i * 28, "r", 17, T["ink"])[0] for i, l in enumerate(D.ABOUT))
    o.append(up(left, .1))
    for i, (h, msg, c) in enumerate(D.LOG):
        y = 64 + i * 42
        last = i == len(D.LOG) - 1
        row = (f'<line x1="560" y1="{y - 26}" x2="976" y2="{y - 26}" stroke="{T["line"]}"/>'
               + f'<circle {"class=\"pulse\" " if last else ""}cx="566" cy="{y - 5}" r="4" fill="{T[DOT[c]]}"/>'
               + label(h, 580, y, T, 12)
               + text(msg, 660, y, "b" if last else "r", 15, T["ink"])[0])
        o.append(up(row, .2 + i * .12))
    o.append(f'<line x1="560" y1="{64 + len(D.LOG) * 42 - 26}" x2="976" y2="{64 + len(D.LOG) * 42 - 26}" stroke="{T["line"]}"/>')
    h = max(78 + len(D.ABOUT) * 28, 64 + len(D.LOG) * 42) + 4
    return svg(W, h, "".join(o), "소개 · " + " ".join(D.ABOUT))


# ---------------------------------------------------------------- 기술 스택 (S3, 흐르는 띠)
def stack(T):
    items = [t for _, it in D.STACK for t in it]
    marks = [T["g4"], T["g3"], T["g2"], T["clay"]]
    o, x = [], 0
    for rep in range(2):
        for i, t in enumerate(items):
            slug, name = parse_tech(t)
            if slug:
                o.append(icon(slug, x, 72, 18, T["ink"]))
                x += 26
            s, w = text(name, x, 87, "m", 16, T["ink"])
            o.append(s)
            x += w + 24
            o.append(f'<rect x="{x:.0f}" y="76" width="9" height="9" rx="2.5" fill="{marks[i % 4]}"/>')
            x += 33
    total = x / 2
    css = f".mq{{animation:mq {total / 28:.0f}s linear infinite}}@keyframes mq{{to{{transform:translateX(-{total:.0f}px)}}}}"
    body = (section_title("STACK", T)
            + f'<line x1="0" y1="50" x2="{W}" y2="50" stroke="{T["line"]}"/><line x1="0" y1="112" x2="{W}" y2="112" stroke="{T["line"]}"/>'
            + f'<clipPath id="cp"><rect x="0" y="51" width="{W}" height="60"/></clipPath>'
            + f'<g clip-path="url(#cp)"><g class="mq">{"".join(o)}</g></g>')
    return svg(W, 124, body, "기술 스택 · " + ", ".join(parse_tech(t)[1] for t in items), css)


# ---------------------------------------------------------------- 대표 프로젝트 카드 (P1)
CW, CH = 480, 236


def card(p, T):
    inner = CW - 56
    meta = f'{p["period"]} · {p["role"]}'
    o = [f'<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="14" fill="{T["paper"]}" stroke="{T["line"]}"/>',
         f'<circle cx="32" cy="38" r="4" fill="{T["clay"] if p.get("orange") else T["g3"]}"/>',
         label(meta, 44, 42, T, 12)]
    if p.get("repo"):
        o.append(text("↗", CW - 30, 44, "r", 18, T["mute"], "end")[0])
    nm = text(p["name"], 28, 94, "b", 26, T["ink"], ls=-.4)[0]
    desc = text(p["desc"], 28, 124, "r", 15, T["mute"])[0]
    size = 14
    while width("".join(p["result"]), "r", size) > inner and size > 11:
        size -= .5
    res, _ = emph(28, 160, p["result"], T, size, p.get("orange"))
    o.append(up(nm + desc + res, .1))
    o.append(label(p["team"], 28, 190, T, 12))
    x = 28
    for t in p["tech"]:
        slug, name = parse_tech(t)
        if slug:
            o.append(icon(slug, x, 202, 13, T["g3"]))
            x += 18
        s, w = text(name, x, 213, "m", 12, T["g3"])
        o.append(s)
        x += w + 14
    return svg(CW, CH, "".join(o), f'{p["name"]} · {p["desc"]}')


# ---------------------------------------------------------------- 그 밖의 프로젝트 (D1, 3단 요약)
def side(T):
    o = [section_title("SIDE PROJECTS", T)]
    cols, colw, rowh = 3, 328, 52
    for i, p in enumerate(D.MORE):
        c, r = i % cols, i // cols
        x, y = 24 + c * colw, 62 + r * rowh
        nm, w = text(p["name"], x + 16, y, "b", 15, T["ink"])
        row = (f'<rect x="{x}" y="{y - 10}" width="8" height="8" rx="2" fill="{T[["g4", "g3", "g2"][c]]}"/>' + nm
               + text(p["desc"], x + 16 + w + 8, y, "r", 13, T["mute"])[0]
               + text(" · ".join(parse_tech(t)[1] for t in p["tech"][:3]), x + 16, y + 20, "m", 11, T["g3"])[0])
        o.append(up(row, .08 + i * .05))
    rows = (len(D.MORE) + cols - 1) // cols
    return svg(W, 62 + (rows - 1) * rowh + 34, "".join(o), "그 밖의 프로젝트 · " + ", ".join(p["name"] for p in D.MORE))


# ---------------------------------------------------------------- 기록과 자격 (C2, 2단 목록)
def records(T):
    o = [section_title("RECORDS & CERTIFICATES", T)]
    o.append(label("기록", 24, 64, T, 12))
    o.append(label("자격", 512, 64, T, 12))
    o.append(f'<line x1="24" y1="76" x2="464" y2="76" stroke="{T["line"]}"/><line x1="512" y1="76" x2="976" y2="76" stroke="{T["line"]}"/>')
    for i, (_, pre, em) in enumerate(D.ACTIVITY):
        y = 106 + i * 34
        s, w = text(pre, 42, y, "r", 15, T["ink"])
        o.append(up(f'<rect x="24" y="{y - 10}" width="9" height="9" rx="2.5" fill="{T["g3"]}"/>' + s
                    + text(em, 42 + w, y, "b", 15, T["g3"])[0], .1 + i * .08))
    for i, (nm, issuer) in enumerate(D.CERTS):
        y = 106 + i * 34
        s, w = text(nm, 530, y, "r", 15, T["ink"])
        o.append(up(f'<rect x="512" y="{y - 10}" width="9" height="9" rx="2.5" fill="{T["clay"] if i == 0 else T["g2"]}"/>' + s
                    + label(issuer, 976, y, T, 12, anchor="end"), .1 + i * .08))
    n = max(len(D.ACTIVITY), len(D.CERTS))
    return svg(W, 106 + (n - 1) * 34 + 18, "".join(o), "기록과 자격 · " + ", ".join(c for c, _ in D.CERTS))


# ---------------------------------------------------------------- 푸터 (F1)
def footer(T):
    body = (f'<line x1="24" y1="28" x2="976" y2="28" stroke="{T["line"]}"/>'
            f'<rect x="24" y="52" width="10" height="10" rx="2.5" fill="{T["g3"]}"/>'
            + label(f"soljinkim13 · {D.NAME}", 44, 62, T, 13)
            + label("commits, one cell at a time", 976, 62, T, 13, anchor="end"))
    return svg(W, 84, body, f"soljinkim13 · {D.NAME}")


# ---------------------------------------------------------------- README
def _pic(name, alt, w="100%", link=None):
    s = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">'
         f'<img src="./assets/{name}-light.svg" width="{w}" alt="{alt}"></picture>')
    return f'<a href="{link}">{s}</a>' if link else s


SNAKE = "https://raw.githubusercontent.com/soljinkim13/soljinkim13/output/"


def readme():
    cards = []
    for i, p in enumerate(D.FEATURED):
        cards.append(_pic(f"project-{i + 1}", f'{p["name"]} · {p["desc"]}', "49%", p.get("repo")))
    demos = " · ".join(f'[{p["name"]} 데모 ↗]({p["demo"]})' for p in D.FEATURED if p.get("demo"))
    more_links = " · ".join(f'[{p["name"]}]({p["repo"]})' for p in D.MORE if p.get("repo"))
    L = [
        _pic("hero", f"{D.NAME_EN} {D.NAME} · {D.ROLE} · {''.join(D.HOOK)}"),
        "",
        "　".join(f'**{n}** [{t}]({u})' for n, t, u in D.LINKS),
        "",
        _pic("about", "소개 · " + " ".join(D.ABOUT)),
        "",
        _pic("stack", "기술 스택"),
        "",
        "<p>\n" + "\n".join(cards) + "\n</p>",
        "",
        f"<sub>{demos}</sub>" if demos else "",
        "",
        _pic("side", "그 밖의 프로젝트 · " + ", ".join(p["name"] for p in D.MORE)),
        "",
        f"<sub>저장소: {more_links}</sub>",
        "",
        _pic("records", "기록과 자격 · " + ", ".join(c for c, _ in D.CERTS)),
        "",
        f'<picture><source media="(prefers-color-scheme: dark)" srcset="{SNAKE}github-snake-dark.svg">'
        f'<img src="{SNAKE}github-snake.svg" width="100%" alt="최근 1년 커밋 잔디 위를 지나가는 뱀"></picture>',
        "",
        _pic("footer", f"soljinkim13 · {D.NAME}"),
        "",
        "<!-- 이 파일은 scripts/build.py가 만든다. 내용은 scripts/data.py에서 고치고 python3 scripts/build.py를 실행한다. "
        "잔디 뱀 그림은 .github/workflows/snake.yml이 매일 output 브랜치에 새로 그린다. -->",
        "",
    ]
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(L))


def main():
    import shutil
    shutil.rmtree(OUT, ignore_errors=True)
    made = []
    for theme, T in THEMES.items():
        made += [save("hero", theme, hero(T)), save("about", theme, about(T)), save("stack", theme, stack(T)),
                 save("side", theme, side(T)), save("records", theme, records(T)), save("footer", theme, footer(T))]
        made += [save(f"project-{i + 1}", theme, card(p, T)) for i, p in enumerate(D.FEATURED)]
    readme()
    total = sum(os.path.getsize(p) for p in made)
    print(f"{len(made)} files, {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
