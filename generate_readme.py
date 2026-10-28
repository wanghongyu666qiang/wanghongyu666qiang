"""读取 config.toml，生成 README.md 与双主题 banner —— Python 3.12+ 零依赖

用法:
    python generate_readme.py            # 本地生成，不联网
    python generate_readme.py --remote   # 顺带用 GitHub API 拉真实 star / 语言
"""
from __future__ import annotations

import json
import os
import sys
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CFG_PATH = ROOT / "config.toml"
README_PATH = ROOT / "README.md"
ASSETS = ROOT / "assets"

# ── 统一色板 ───────────────────────────────────────────────
PRIMARY = "F0883E"   # 主橙
WARM = "FF9A76"      # 暖桃
ACCENT = "E25555"    # 珊瑚红
INK_L, INK_D = "2C1A11", "FFF7F1"
TEXT_L, TEXT_D = "6E5446", "C2A090"

# shields.io logo slug（simple-icons）与品牌色
STACK = {
    "C++":         ("00599C", "cplusplus", "white"),
    "Python":      ("3776AB", "python", "white"),
    "TypeScript":  ("3178C6", "typescript", "white"),
    "Rust":        ("DEA584", "rust", "black"),
    "Vue.js":      ("4FC08D", "vuedotjs", "white"),
    "Next.js":     ("000000", "nextdotjs", "white"),
    "HTML5":       ("E34F26", "html5", "white"),
    "CSS3":        ("1572B6", "css3", "white"),
    "WebAssembly": ("654FF0", "webassembly", "white"),
    "Git":         ("F05032", "git", "white"),
    "Linux":       ("FCC624", "linux", "black"),
    "Docker":      ("2496ED", "docker", "white"),
    "VSCode":      ("007ACC", "visualstudiocode", "white"),
}


def enc(s: str) -> str:
    """URL 编码，连 + . 一起编，避免 C++ 变成空格"""
    return urllib.parse.quote(str(s), safe="")


def shield(message: str, color: str, logo: str | None = None,
           logo_color: str = "white", style: str = "flat-square",
           mono: bool = False) -> str:
    if mono:                      # 纸墨单色，和整体调性一致
        color, logo_color = "D8C3AD", "54402F"
    url = f"https://img.shields.io/badge/{enc(message)}-{color}?style={style}"
    if logo:
        url += f"&logo={logo}&logoColor={logo_color}"
    return f'<img src="{url}" />'


def picture(light: str, dark: str, alt: str, width: str | None = None) -> str:
    w = f' width="{width}"' if width else ""
    return (
        "<picture>"
        '<source media="(prefers-color-scheme: dark)" '
        f'srcset="{dark}">'
        f'<img src="{light}"{w} alt="{alt}">'
        "</picture>"
    )


# ── banner ────────────────────────────────────────────────
def build_banner(cfg: dict, dark: bool) -> str:
    """文艺版：衬线大字 + 手绘细线 + 纸色底，只留必要的几笔。"""
    p = cfg["profile"]
    if dark:
        bg = ("#12100F", "#1C1614")
        ink = "#F2EBE3"
        meta_c, head_c = "#8A7466", "#C6AD9E"
    else:
        bg = ("#FCF8F2", "#F6EDE0")
        ink = "#2A211C"
        meta_c, head_c = "#9C8578", "#5C4A3F"

    meta = " — ".join(x.upper() for x in [
        p.get("school_en", ""), p.get("location_en", "")
    ] if x)

    return f'''<svg width="1200" height="320" viewBox="0 0 1200 320" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{p['name']}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="320" gradientUnits="userSpaceOnUse">
      <stop stop-color="{bg[0]}"/>
      <stop offset="1" stop-color="{bg[1]}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="320" fill="url(#bg)"/>
  <rect x="84" y="110" width="4" height="70" rx="2" fill="#{PRIMARY}"/>
  <text x="112" y="180" font-family="Georgia, 'Times New Roman', 'Songti SC', 'SimSun', serif" font-size="106" letter-spacing="-2" fill="{ink}">{p['name']}</text>
  <path d="M84 212 C 340 211, 620 213.5, 900 212 S 1060 211.4, 1144 212" fill="none" stroke="{ink}" stroke-opacity="0.26" stroke-width="1.2"/>
  <text x="84" y="266" font-family="'SF Mono', Consolas, 'Courier New', monospace" font-size="14" letter-spacing="1.8" fill="{meta_c}">{meta}</text>
  <text x="1144" y="268" text-anchor="end" font-family="'Songti SC', 'STSong', 'SimSun', 'PingFang SC', Georgia, serif" font-size="26" fill="{head_c}">{p.get('headline', '')}</text>
</svg>
'''


# ── 各区块 ────────────────────────────────────────────────
def build_tech(cfg: dict) -> str:
    t = cfg["tech"]
    mono = bool(t.get("mono", False))
    style = "for-the-badge"
    rows = [t.get("languages", []) + t.get("frameworks", []),
            t.get("web", []) + t.get("tools", [])]
    out = []
    for row in rows:
        if not row:
            continue
        imgs = []
        for name in row:
            color, logo, lc = STACK.get(name, ("888888", None, "white"))
            imgs.append("  " + shield(name, color, logo, lc, style, mono))
        out.append('<p align="center">\n' + "\n".join(imgs) + "\n</p>")
    return "\n".join(out)


def build_projects(cfg: dict, meta: dict) -> str:
    gh = cfg["profile"]["github"]
    cells = []
    for p in cfg["projects"]:
        m = meta.get(p["repo"], {})
        lang = m.get("language") or p.get("lang", "")
        stars = m.get("stars", p.get("stars", 0))
        star_badge = f" · ★ {stars}" if stars else ""
        url = f"https://github.com/{gh}/{p['repo']}"
        cells.append(
            f'<td width="50%" valign="top">\n'
            f'<h3>{p.get("emoji", "📦")} <a href="{url}">{p["name"]}</a></h3>\n'
            f'<p><code>{lang}</code>{star_badge}</p>\n'
            f'<p>{p["desc"]}</p>\n'
            f'</td>'
        )

    rows = []
    for i in range(0, len(cells), 2):
        pair = cells[i:i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%" valign="top"></td>')
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def build_stats(cfg: dict) -> str:
    gh = cfg["profile"]["github"]
    s = cfg.get("stats", {})
    blocks = []

    def one(url_l: str, url_d: str, alt: str) -> str:
        return f'<p align="center">\n  {picture(url_l, url_d, alt)}\n</p>'

    if s.get("streak", True):
        base = ("https://streak-stats.demolab.com/?user=" + gh
                + "&hide_border=true&background=00000000"
                + f"&stroke={PRIMARY}&ring={PRIMARY}&fire={PRIMARY}"
                + f"&currStreakLabel={PRIMARY}&sideNums={PRIMARY}")
        blocks.append(one(
            base + f"&currStreakNum={INK_L}&sideLabels={TEXT_L}&dates={TEXT_L}",
            base + f"&currStreakNum={INK_D}&sideLabels={TEXT_D}&dates={TEXT_D}",
            "GitHub streak",
        ))

    pair = []
    if s.get("overview", True):
        base = ("https://github-readme-stats.vercel.app/api?username=" + gh
                + "&show_icons=true&hide_border=true&bg_color=00000000"
                + f"&title_color={PRIMARY}&icon_color={PRIMARY}&ring_color={PRIMARY}")
        pair.append(picture(
            base + f"&text_color={TEXT_L}", base + f"&text_color={TEXT_D}",
            "GitHub stats", "420"))
    if s.get("langs", True):
        base = ("https://github-readme-stats.vercel.app/api/top-langs/?username=" + gh
                + "&layout=compact&langs_count=8&hide_border=true&bg_color=00000000"
                + f"&title_color={PRIMARY}")
        pair.append(picture(
            base + f"&text_color={TEXT_L}", base + f"&text_color={TEXT_D}",
            "Top languages", "330"))
    if pair:
        blocks.append('<p align="center">\n  ' + "&nbsp;&nbsp;\n  ".join(pair) + "\n</p>")

    if s.get("activity", True):
        base = ("https://github-readme-activity-graph.vercel.app/graph?username=" + gh
                + "&hide_border=true&area=true&bg_color=00000000"
                + f"&line={PRIMARY}&point={PRIMARY}&area_color={PRIMARY}40")
        blocks.append(one(base + f"&color={TEXT_L}", base + f"&color={TEXT_D}",
                          "Contribution graph"))

    if s.get("snake", True):
        raw = f"https://raw.githubusercontent.com/{gh}/{gh}/main/output"
        v = cfg["profile"].get("asset_version", "1")
        # 必须给 100%，否则 SVG 按 880px 原尺寸渲染、右侧会被容器裁掉
        blocks.append('<p align="center">\n  ' + picture(
            f"{raw}/github-contribution-grid-snake.svg?v={v}",
            f"{raw}/github-contribution-grid-snake-dark.svg?v={v}",
            "Contribution snake", "100%") + "\n</p>")

    return "\n\n".join(blocks)


def build_contact(cfg: dict) -> str:
    c = cfg.get("contact", {})
    items = []
    if c.get("email"):
        items.append('<a href="mailto:{0}"><img src="https://img.shields.io/badge/Email-{1}-{2}?style=flat-square&logo=gmail&logoColor=white" /></a>'
                     .format(c["email"], enc(c["email"]), ACCENT))
    if c.get("blog"):
        items.append('<a href="{0}"><img src="https://img.shields.io/badge/Blog-{1}-{2}?style=flat-square&logo=safari&logoColor=white" /></a>'
                     .format(c["blog"], enc(c.get("blog_name", "blog")), PRIMARY))
    for key, url in (c.get("social") or {}).items():
        if url:
            items.append(f'<a href="{url}"><img src="https://img.shields.io/badge/{enc(key)}-555555?style=flat-square&logo={key}&logoColor=white" /></a>')
    return '<p align="center">\n  ' + "\n  ".join(items) + "\n</p>" if items else ""


# ── 主流程 ────────────────────────────────────────────────
def fetch_repo_meta(cfg: dict) -> dict:
    gh = cfg["profile"]["github"]
    token = os.environ.get("GITHUB_TOKEN")
    out = {}
    for p in cfg["projects"]:
        req = urllib.request.Request(f"https://api.github.com/repos/{gh}/{p['repo']}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "readme-gen")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                d = json.load(r)
            out[p["repo"]] = {
                "stars": d.get("stargazers_count", 0),
                "language": d.get("language"),
            }
            print(f"  ✓ {p['repo']}: ★{out[p['repo']]['stars']}")
        except Exception as e:  # 网络挂了也不能让 CI 红
            print(f"  ! {p['repo']}: {e}")
            out[p["repo"]] = {}
    return out


def main() -> None:
    cfg = tomllib.loads(CFG_PATH.read_text(encoding="utf-8"))
    p = cfg["profile"]
    gh = p["github"]

    meta = fetch_repo_meta(cfg) if "--remote" in sys.argv else {}

    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "banner-light.svg").write_text(build_banner(cfg, False), encoding="utf-8")
    (ASSETS / "banner-dark.svg").write_text(build_banner(cfg, True), encoding="utf-8")

    raw = f"https://raw.githubusercontent.com/{gh}/{gh}/main/assets"
    v = p.get("asset_version", "1")
    banner = picture(f"{raw}/banner-light.svg?v={v}", f"{raw}/banner-dark.svg?v={v}",
                     p["name"], "100%")

    chips = [
        shield(p.get("school", ""), PRIMARY),
        shield(p.get("location", ""), PRIMARY),
        f'<img src="https://komarev.com/ghpvc/?username={gh}&style=flat-square&color={PRIMARY}&label=visitors" />',
    ]

    about = cfg["about"]["text"].strip()

    parts = [
        f'<p align="center">\n  {banner}\n</p>',
        '<p align="center">\n  ' + "\n  ".join(chips) + "\n</p>",
        build_contact(cfg),
        "## 关于我\n\n" + about,
        "## 技术栈\n\n" + build_tech(cfg),
        "## 项目\n\n" + build_projects(cfg, meta),
        "## 一些数字\n\n" + build_stats(cfg),
        '<p align="center">\n  <sub>海口 · 二〇二六年 —— <strong>%s</strong> 写，💕 t宝 陪着</sub>\n</p>' % p["name"],
    ]

    README_PATH.write_text("\n\n".join(x for x in parts if x.strip()) + "\n", encoding="utf-8")
    print("✅ README.md 与 banner 已根据 config.toml 生成")


if __name__ == "__main__":
    main()
