""" 读取 config.toml，自动生成 README.md —— Python 3.12+ 零依赖 """
import tomllib
from pathlib import Path

ROOT = Path(__file__).parent
config_path = ROOT / "config.toml"
readme_path = ROOT / "README.md"

with open(config_path, "rb") as f:
    cfg = tomllib.load(f)

p = cfg["profile"]
gh = p["github"]
# 徽章颜色表
colors = {
    "C++": "00599C",
    "Python": "3776AB",
    "JavaScript": "F7DF1E",
    "Vue.js": "4FC08D",
    "HTML5": "E34F26",
    "CSS3": "1572B6",
    "WebAssembly": "654FF0",
    "Git": "F05032",
    "Linux": "FCC624",
    "VSCode": "007ACC",
    "GitHub": "181717",
}

def badge(name, cat="default"):
    """生成 shields.io 徽章 HTML"""
    color = colors.get(name, "888")
    if name == "JavaScript":
        logo_color = "black"
    elif name == "Linux":
        logo_color = "black"
    else:
        logo_color = "white"
    logo = name.lower().replace(" ", "-")
    return f'<img src="https://img.shields.io/badge/{name.replace(" ","%20")}-{color}?style=for-the-badge&logo={logo}&logoColor={logo_color}" />'

def build_tech():
    lines = []
    for group in ["languages", "frameworks", "web"]:
        for t in cfg["tech"].get(group, []):
            lines.append(badge(t))
    lines.append("")  # 换行
    for t in cfg["tech"].get("tools", []):
        lines.append(badge(t))
    return "\n  ".join(lines)

def build_about():
    return "\n".join(f"- {item}" for item in cfg["about"]["items"])

def build_contact():
    c = cfg.get("contact", {})
    lines = []
    # Email
    email = c.get("email", "")
    if email:
        lines.append(f'  <a href="mailto:{email}"><img src="https://img.shields.io/badge/📧%20Email-{email.replace("@","%40")}-ea4335?style=flat-square&logo=gmail&logoColor=white" /></a>')
    # Blog
    blog = c.get("blog", "")
    if blog:
        name = c.get("blog_name", "Blog")
        lines.append(f'  <a href="{blog}"><img src="https://img.shields.io/badge/🌐%20{name}-ff69b4?style=flat-square&logo=safari&logoColor=white" /></a>')
    # Social platforms
    social = c.get("social", {})
    for key, url in social.items():
        if url:
            lines.append(f'  <a href="{url}"><img src="https://img.shields.io/badge/{key}-fff?style=flat-square&logo={key}&logoColor=333" /></a>')
    # Placeholder for future social
    if not social or all(not v for v in social.values()):
        lines.append('  <!-- 社交平台链接：在 config.toml 中 [contact.social] 下填写 -->')
    return "\n".join(lines)

def build_projects():
    rows = []
    for proj in cfg["projects"]:
        rows.append(f"| [{proj['name']}](https://github.com/{gh}/{proj['repo']}) | {proj['desc']} |")
    return "\n".join(rows)

# ── 模板 ──
readme = f"""<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=26&duration=3000&pause=1000&color=F0883E&center=true&vCenter=true&width=435&lines=Hi%2C+I'm+{p['name']}+%F0%9F%91%8B;%E6%B5%B7%E5%8D%97%E5%A4%A7%E5%AD%A6%E5%9C%A8%E8%AF%BB;%E7%83%AD%E7%88%B1%E6%9E%84%E5%BB%BA%E6%9C%89%E7%94%A8%E7%9A%84%E5%B0%8F%E4%B8%9C%E8%A5%BF;%E6%AC%A2%E8%BF%8E%E4%BD%A0%E7%9A%84%E5%88%B0%E6%9D%A5+" alt="Typing SVG" />
</p>

<p align="center">
  <a href="https://github.com/{gh}"><img src="https://img.shields.io/badge/GitHub-f0883e?style=for-the-badge&logo=github&logoColor=white" /></a>
  <img src="https://komarev.com/ghpvc/?username={gh}&style=for-the-badge&color=f0883e" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/🏫-{p['school']}-2dba4e?style=flat-square" />
  <img src="https://img.shields.io/badge/📍-{p['location']}-f0883e?style=flat-square" />
  <img src="https://img.shields.io/badge/💻-{p['bio']}-e25555?style=flat-square" />
</p>

---

### 📬 联系我

<p align="center">
{build_contact()}
</p>

---

### 🛠️ 技术栈

<p align="center">
  {build_tech()}
</p>

---

### 📊 GitHub 统计

<p align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user={gh}&hide_border=true&stroke=f0883e&ring=f0883e&fire=f0883e&currStreakLabel=f0883e&sideNums=f0883e&currStreakNum=718096&sideLabels=718096&dates=718096&background=00000000" />
</p>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={gh}&bg_color=00000000&color=718096&line=f0883e&point=f0883e&area=true&area_color=f0883e40&hide_border=true" />
</p>

---

### 🚀 精选项目

| 项目 | 描述 |
|------|------|
{build_projects()}

---

### 🌱 关于我

{build_about()}

---

<p align="center">
  <img src="https://raw.githubusercontent.com/{gh}/{gh}/main/output/github-contribution-grid-snake.svg" />
</p>

<p align="center">
  <sub>
    crafted with lots of ❤️ by <strong>{p['name']}</strong> & powered by <strong>💕 t宝</strong>
  </sub>
</p>
"""

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("✅ README.md 已根据 config.toml 生成！")
