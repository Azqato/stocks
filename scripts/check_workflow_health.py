#!/usr/bin/env python3
"""
Reports the health of the repo's GitHub Actions workflows.

Exists because two multi-week outages (the Wikipedia constituent break in
v4.1.8 and the Vanguard endpoint break in v4.3.4) were both invisible: a
scheduled workflow that fails keeps failing silently, and the daily feeds stay
fresh enough that nothing looks wrong from the outside. This is the local half
of the fix, run by .githooks/pre-push so a broken cron is surfaced at the
terminal before anyone pushes on top of it. The other half is
alert-on-failure.yml, which opens a GitHub issue from CI.

Two independent failure modes are checked per workflow, because the first two
outages were one of each:
  - the latest run FAILED (Vanguard: it ran every week and failed every week)
  - the latest run is STALE (Wikipedia: the job stopped producing anything)

Reads the public Actions API, so it needs no token for a public repo. Prints a
report and exits 1 when something is wrong, 0 when everything is healthy.
Network problems exit 0 with a note: this must never be the reason a push is
blocked.

Usage: python scripts/check_workflow_health.py [--repo OWNER/NAME] [--quiet]
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com"

# How long each workflow may go without a run before it is called stale.
# Each is its own cadence plus generous slack for GitHub's scheduler, which
# fires hours late and getting later (see PRD, Known Technical Debt).
MAX_AGE_HOURS = {
    "constituents.yml": 24 * 9,      # weekly (Saturdays), 9 days
    "market-overview.yml": 24 * 4,   # 3x per weekday, 4 days covers a long weekend
    "screener-data.yml": 24 * 4,
    "screener-data-etfs.yml": 24 * 4,
    "screener-data-gvd.yml": 24 * 4,
    "screener-data-intl.yml": 24 * 4,
    "screener-data-sp500.yml": 24 * 4,
}
DEFAULT_MAX_AGE_HOURS = 24 * 9


def repo_from_git():
    """OWNER/NAME from origin, so this works in any clone without configuration."""
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None
    url = url.removesuffix(".git")
    for sep in ("github.com/", "github.com:"):
        if sep in url:
            return url.split(sep, 1)[1]
    return None


def get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "azqato-workflow-health",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def check(repo):
    """Return (rows, problems). A row is (name, state, detail)."""
    wfs = get(f"{API}/repos/{repo}/actions/workflows")["workflows"]
    rows, problems = [], []
    now = datetime.now(timezone.utc)
    for wf in sorted(wfs, key=lambda w: w["path"]):
        fname = wf["path"].rsplit("/", 1)[-1]
        # Looked up by id, not filename: GitHub's own pages-build-deployment
        # workflow reports a synthetic path with no real file behind it, and a
        # filename lookup 404s on it. It is worth watching, since a failed
        # Pages deploy is exactly as invisible as a failed cron.
        runs = get(f"{API}/repos/{repo}/actions/workflows/{wf['id']}/runs?per_page=1")
        runs = runs.get("workflow_runs", [])
        if not runs:
            rows.append((fname, "NO RUNS", "never run"))
            continue
        run = runs[0]
        started = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
        age = now - started
        conclusion = run["conclusion"] or run["status"]
        limit = timedelta(hours=MAX_AGE_HOURS.get(fname, DEFAULT_MAX_AGE_HOURS))
        stamp = f"{age_str(age)} ago"
        if conclusion == "failure":
            rows.append((fname, "FAILING", f"last run {stamp}: {run['html_url']}"))
            problems.append(f"{fname} last run FAILED ({stamp})")
        elif age > limit:
            rows.append((fname, "STALE", f"last run {stamp}, expected within "
                                         f"{limit.days}d"))
            problems.append(f"{fname} has not run in {age_str(age)}")
        else:
            rows.append((fname, "ok", f"{conclusion}, {stamp}"))
    return rows, problems


ALERT_WORKFLOW = ".github/workflows/alert-on-failure.yml"


def check_alert_watchlist(root):
    """Return a list of workflows alert-on-failure.yml is not watching.

    workflow_run matches on a workflow's `name:`, not its filename, so a typo
    or a renamed workflow silently watches nothing. Parsed with regex rather
    than PyYAML so the hook has no third-party dependency: this runs on every
    push and must work in a bare clone.
    """
    alert = os.path.join(root, ALERT_WORKFLOW)
    if not os.path.exists(alert):
        return ["alert-on-failure.yml is missing entirely"]
    text = open(alert, encoding="utf-8").read()
    block = re.search(r"^    workflows:\n((?:      - .*\n)+)", text, re.M)
    watched = set()
    if block:
        watched = {ln.strip()[2:].strip() for ln in block.group(1).splitlines()}
    missing = []
    for path in sorted(glob.glob(os.path.join(root, ".github/workflows/*.yml"))):
        if os.path.basename(path) == os.path.basename(ALERT_WORKFLOW):
            continue
        m = re.search(r"^name:\s*(.+?)\s*$", open(path, encoding="utf-8").read(), re.M)
        if m and m.group(1) not in watched:
            missing.append(f"{os.path.basename(path)} (name: {m.group(1)!r})")
    return missing


def age_str(d):
    h = int(d.total_seconds() // 3600)
    return f"{h}h" if h < 48 else f"{h // 24}d"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=None, help="OWNER/NAME (default: from origin)")
    ap.add_argument("--quiet", action="store_true",
                    help="print nothing when every workflow is healthy")
    args = ap.parse_args()

    repo = args.repo or repo_from_git()
    if not repo:
        print("workflow health: could not determine the GitHub repo; skipping.")
        return 0

    try:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
        unwatched = check_alert_watchlist(root)
    except Exception:
        unwatched = []

    try:
        rows, problems = check(repo)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        # Never let a network hiccup or a rate limit stand in the way of a push.
        print(f"workflow health: could not reach the GitHub API ({e}); skipping.")
        return 0

    for w in unwatched:
        problems.append(f"alert-on-failure.yml does not watch {w}")

    if problems:
        print("=" * 68)
        print(f"GITHUB ACTIONS PROBLEMS in {repo}:")
        for p in problems:
            print(f"  ! {p}")
        print("-" * 68)
    elif args.quiet:
        return 0
    else:
        print(f"GitHub Actions health, {repo}:")

    for name, state, detail in rows:
        print(f"  {state:8s} {name:26s} {detail}")
    if problems:
        print("=" * 68)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
