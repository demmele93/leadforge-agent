#!/usr/bin/env bash
# LeadForge GitHub publish.
# Usage: GH_TOKEN=ghp_xxx ./publish.sh [repo-name] [visibility]
# Requires a GitHub PAT with 'repo' scope (NEVER commit the token).
set -e
REPO="${1:-leadforge-agent}"
VIS="${2:-public}"
TOKEN="${GH_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  echo "ERROR: set GH_TOKEN=your_pat first. Example:" >&2
  echo '  GH_TOKEN=ghp_xxx ./publish.sh leadforge-agent public' >&2
  exit 1
fi
# install gh if missing (macOS)
if ! command -v gh >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then brew install gh; else
    echo "gh not found and brew unavailable. Install gh manually." >&2; exit 1
  fi
fi
echo "$TOKEN" | gh auth login --with-token
# create the repo (ignores if exists)
gh repo create "$REPO" --${VIS} --description "LeadForge — portable lead-enrichment + dashboard agent for Hermes" || true
git init -q 2>/dev/null || true
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
git add -A
git commit -q -m "LeadForge v0.1 — grill-me lead enrichment + brand dashboard" || true
git branch -M main
git remote add origin "https://github.com/$(gh api user --jq .login)/$REPO.git" 2>/dev/null || true
git push -u origin main
echo "Published to https://github.com/$(gh api user --jq .login)/$REPO"
