#!/usr/bin/env bash
# Adds all changes and pushes to origin/main.
# Usage: ./git_push.sh "your commit message"

set -euo pipefail

BRANCH="main"
MSG="${1:-}"

if [[ -z $MSG ]]; then
    read -rp "Commit message: " MSG
fi

git status
git add .
git commit -m "$MSG"
git push -u origin "$BRANCH"
