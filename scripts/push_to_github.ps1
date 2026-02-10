# Helper: create a GitHub repo and push the current project using GitHub CLI (`gh`).
# Usage:
#   1. Install GitHub CLI: https://cli.github.com/
#   2. Run `gh auth login` to authenticate.
#   3. Run this script: `./scripts/push_to_github.ps1 -RepoName phaethon -Private` 

param(
  [string]$RepoName = "phaethon",
  [switch]$Private
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Error "gh CLI not found. Install from https://cli.github.com/ and run 'gh auth login' first."
  exit 1
}

$visibility = if ($Private) { 'private' } else { 'public' }

# Create the repo under the authenticated user's account
$create = gh repo create $RepoName --$visibility --confirm 2>&1
Write-Output $create

# Add remote (gh will have already added origin) and push
git remote -v
git push -u origin HEAD
