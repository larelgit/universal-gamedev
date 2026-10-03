#!/usr/bin/env bash
# Link skills/ into the folders each agent scans in a clone: .claude/skills, .agents/skills, .gemini/skills
# and .github/skills. Run once after cloning (the links are gitignored). On Windows, use
# tools/link-skills.ps1, which makes directory junctions (Git Bash's ln -s copies instead of linking).
set -euo pipefail
cd "$(dirname "$0")/.."
for d in .claude .agents .gemini .github; do
  mkdir -p "$d"
  if [ -e "$d/skills" ] || [ -L "$d/skills" ]; then echo "exists: $d/skills"; continue; fi
  ln -s ../skills "$d/skills" && echo "linked: $d/skills -> ../skills"
done
