import requests
import os

USERNAME = "KArT4206"
README_FILE = "README.md"

# Fetch pinned repos from GitHub API
url = f"https://gh-pinned-repos.egoist.dev/?username={USERNAME}"
repos = requests.get(url).json()

project_lines = []
for repo in repos:
    name = repo['repo']
    description = repo.get('description', '')
    link = repo['link']
    project_lines.append(f"- [{name}]({link}) — {description}")

projects_md = "\n".join(project_lines)

# Update README between markers
with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()

start = "<!-- PROJECTS:START -->"
end = "<!-- PROJECTS:END -->"

before = readme.split(start)[0] + start + "\n"
after = "\n" + end + readme.split(end)[1]

new_readme = before + projects_md + after

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(new_readme)
