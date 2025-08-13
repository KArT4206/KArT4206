import requests
import os

USERNAME = "KArT4206"  # Change to your GitHub username if needed
README_FILE = "README.md"

# Query the pinned repos API
url = f"https://gh-pinned-repos.egoist.dev/?username={USERNAME}"
try:
    repos = requests.get(url).json()
except Exception as e:
    print(f"API error: {e}")
    repos = []

project_lines = []
for repo in repos:
    name = repo['repo']
    description = repo.get('description', '')
    link = repo['link']
    line = f"- [{name}]({link}) — {description}"
    project_lines.append(line)

projects_md = "\n".join(project_lines)

# Read and update README.md
start_marker = "<!-- PROJECTS:START -->"
end_marker = "<!-- PROJECTS:END -->"

with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()

if start_marker not in readme or end_marker not in readme:
    print("Markers not found in README.md")
    exit(1)

before = readme.split(start_marker)[0] + start_marker + "\n"
after = "\n" + end_marker + readme.split(end_marker)[1]
new_readme = before + projects_md + after

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(new_readme)
