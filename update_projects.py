import requests

USERNAME = "KArT4206"  # Your GitHub username
README_FILE = "README.md"

start_marker = "<!-- PROJECTS:START -->"
end_marker = "<!-- PROJECTS:END -->"

# Step 1: Fetch pinned repos from the API
url = f"https://gh-pinned-repos.egoist.dev/?username={USERNAME}"
try:
    repos = requests.get(url, timeout=10).json()
    print("Fetched repos from API:", repos)  # DEBUG: Log what was fetched
except Exception as e:
    print(f"❌ API error: {e}")
    repos = []

# Step 2: Build markdown list from fetched repos
project_lines = []
for repo in repos:
    name = repo.get('repo')
    description = repo.get('description', '')
    link = repo.get('link')
    line = f"- [{name}]({link}) — {description}"
    project_lines.append(line)

projects_md = "\n".join(project_lines) if project_lines else "_No pinned projects found_"

# Step 3: Read README.md
with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()

if start_marker not in readme or end_marker not in readme:
    print("❌ Markers not found in README.md")
    exit(1)

# Step 4: Replace content between markers
before = readme.split(start_marker)[0] + start_marker + "\n"
after = "\n" + end_marker + readme.split(end_marker)[1]
new_readme = before + projects_md + after

# Step 5: Save updated README.md
with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(new_readme)

print("✅ README.md updated successfully.")
