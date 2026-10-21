"""Rebuild the auto-generated parts of the profile README from the GitHub API.

Fills three marked blocks in README.md:
  <!-- LATEST:START --> ... <!-- LATEST:END -->      the newest public projects as cards
  <!-- PROJECTS:START --> ... <!-- PROJECTS:END -->  every public project, grouped by area
  <!-- STATS:START --> ... <!-- STATS:END -->        counts and the last refresh time

Run by .github/workflows/update-readme.yml on a schedule, so a new public repository shows
up without editing the README by hand. Uses only the standard library.
"""

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = os.environ.get("GH_USER", "KArT4206")
README = Path(__file__).resolve().parents[1] / "README.md"
SKIP = {USER.lower()}

# Area is chosen from the repo's topics, name and description, first match wins.
AREAS = [
    ("Medical imaging & health AI", ["oct", "retina", "medical", "dna", "genom", "heart", "disease", "erm", "csc", "rppg"]),
    ("Cybersecurity", ["phish", "security", "keystroke", "biometric", "auth", "tls", "whois"]),
    ("AI & machine learning", ["ai", "ml", "machine-learning", "deep-learning", "summar", "gemini", "random forest", "crop", "classifier", "voice"]),
    ("Embedded & systems", ["esp32", "iot", "fog", "edge", "arduino", "bash", "monitor", "traffic", "scheduling", "firmware"]),
    ("Web & full-stack", ["web", "next", "react", "portfolio", "blog", "chat", "cms", "firebase"]),
]
DOC_SUFFIX = re.compile(r"\s*[-–—]\s*(documentation|docs)[^.]*$", re.I)


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json",
                                                                           "User-Agent": f"{USER}-readme"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def repos():
    out, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        out += batch
        if len(batch) < 100:
            return [r for r in out if not r["fork"] and not r["archived"] and not r["private"] and r["name"].lower() not in SKIP]
        page += 1


def area(r):
    text = " ".join([r["name"], r.get("description") or "", " ".join(r.get("topics") or [])]).lower().replace("_", " ")
    for title, keys in AREAS:
        if any(re.search(rf"(?<![a-z]){re.escape(k)}", text) for k in keys):
            return title
    return "Other projects"


def pretty(name):
    return re.sub(r"[-_]+", " ", name).strip()


def desc(r):
    d = DOC_SUFFIX.sub("", (r.get("description") or "").strip()).rstrip(" .")
    return (d[:140].rsplit(" ", 1)[0] + "…") if len(d) > 140 else (d or "No description yet")


def links(r):
    parts = [f"[Repo]({r['html_url']})"]
    if r.get("homepage"):
        parts.append(f"[Live / docs]({r['homepage']})")
    return " · ".join(parts)


def latest_block(rs):
    cards = []
    for r in sorted(rs, key=lambda r: r["created_at"], reverse=True)[:4]:
        topics = " ".join(f"`{t}`" for t in (r.get("topics") or [])[:4])
        cards.append(f"<td width=\"50%\" valign=\"top\">\n\n**[{pretty(r['name'])}]({r['html_url']})**<br>\n"
                     f"<sub>{desc(r)}</sub>\n\n{topics}\n\n</td>")
    rows = ["<tr>\n" + "\n".join(cards[i:i + 2]) + "\n</tr>" for i in range(0, len(cards), 2)]
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def projects_block(rs):
    groups = {}
    for r in rs:
        groups.setdefault(area(r), []).append(r)
    order = [a for a, _ in AREAS] + ["Other projects"]
    out = []
    for a in order:
        if a not in groups:
            continue
        out.append(f"<details open>\n<summary><b>{a}</b> · {len(groups[a])}</summary>\n\n| Project | What it does | Updated | |\n|---|---|---|---|")
        for r in sorted(groups[a], key=lambda r: r["pushed_at"], reverse=True):
            when = r["pushed_at"][:10]
            out.append(f"| [{pretty(r['name'])}]({r['html_url']}) | {desc(r)} | {when} | {links(r)} |")
        out.append("\n</details>\n")
    return "\n".join(out)


def stats_block(rs, user):
    now = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    stars = sum(r["stargazers_count"] for r in rs)
    return (f"<p align=\"center\">\n"
            f"<img src=\"https://img.shields.io/badge/public%20projects-{len(rs)}-0f172a?style=for-the-badge&labelColor=1d4ed8\" alt=\"public projects\">\n"
            f"<img src=\"https://img.shields.io/badge/stars-{stars}-0f172a?style=for-the-badge&labelColor=b45309\" alt=\"stars\">\n"
            f"<img src=\"https://img.shields.io/badge/followers-{user['followers']}-0f172a?style=for-the-badge&labelColor=047857\" alt=\"followers\">\n"
            f"<img src=\"https://img.shields.io/badge/on%20GitHub%20since-{user['created_at'][:4]}-0f172a?style=for-the-badge&labelColor=7c3aed\" alt=\"since\">\n"
            f"</p>\n\n<p align=\"center\"><sub>Project list refreshed automatically · last run {now}</sub></p>")


def replace(text, tag, body):
    return re.sub(rf"(<!-- {tag}:START -->).*?(<!-- {tag}:END -->)", lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text, flags=re.S)


def main():
    rs, user = repos(), api(f"/users/{USER}")
    text = README.read_text()
    text = replace(text, "LATEST", latest_block(rs))
    text = replace(text, "PROJECTS", projects_block(rs))
    text = replace(text, "STATS", stats_block(rs, user))
    README.write_text(text)
    print(f"{len(rs)} public projects written")


if __name__ == "__main__":
    main()
