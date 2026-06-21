"""eval.py — fixed eval harness for the cross-link-sweep example.

DO NOT MODIFY. The agent edits workflow.py. This file is the judge.

Reads eval_set.json (22 entries, one per examples/*/program.md), fetches each via
the GitHub Contents API, and computes a binary score:

  +1 per file if the program.md's source-ref matches `expected_source_repo`
  +0 per file otherwise

Prints the score, the per-file result table, and exits 0 if score == len(eval_set),
1 otherwise.

The agent's goal: get this to print `score: 22.0000 | elapsed: X.Xs` with the
current state of `examples/*/program.md` on the live default branch.

Transport: uses `curl` via subprocess for portability (works on macOS Python 3.14
where urllib has SSL issues, on Linux without extra deps, in CI containers).
Falls back to urllib.request if curl is unavailable.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))

EVAL_SET = REPO_ROOT / "eval_set.json"
PROGRAM_MD_REPO = "Armosphera/autoresearch-sboss"
DEFAULT_REF = "main"


def get_token() -> str | None:
    return (
        os.environ.get("GH_TOKEN_ARMOSPHERA")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
    )


def _fetch_via_curl(url: str, token: str | None, timeout: int = 15) -> tuple[int, str]:
    """Use curl to fetch URL. Returns (http_status, body)."""
    cmd = ["curl", "-s", "-w", "\n%{http_code}", "-m", str(timeout)]
    if token:
        cmd += ["-H", f"Authorization: token {token}"]
    cmd += ["-H", "Accept: application/vnd.github+json", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout + 5)
        # Body + status separated by newline (last line is the status code)
        out = r.stdout.rstrip()
        if "\n" not in out:
            return 0, out
        body, status = out.rsplit("\n", 1)
        try:
            return int(status), body
        except ValueError:
            return 0, out
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 0, ""


def fetch_program_md(path: str, ref: str = DEFAULT_REF) -> str | None:
    """Fetch raw text of a file at <repo>:<ref>:<path> via GitHub Contents API."""
    import base64

    token = get_token()
    url = f"https://api.github.com/repos/{PROGRAM_MD_REPO}/contents/{path}?ref={ref}"

    if shutil.which("curl"):
        status, body = _fetch_via_curl(url, token)
        if status != 200:
            return None
        try:
            data = json.loads(body)
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except (json.JSONDecodeError, KeyError):
            return None

    # urllib fallback
    import urllib.error
    import urllib.request

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode() or "{}")
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError):
        return None


def score_file(content: str | None, expected_repo: str) -> tuple[int, str]:
    """Return (delta, reason)."""
    if not content:
        return 0, "fetch_failed"

    bad = "SamStep74" in content or "samstep74" in content

    if expected_repo == "Armosphera/A1-AI-Core":
        if bad:
            return 0, "still_has_samstep74"
        if "Armosphera/A1-AI-Core" in content or "github.com/Armosphera/A1-AI-Core" in content:
            return 1, "ok_aicore"
        return 0, "no_aicore_ref"
    else:
        if bad:
            return 0, "has_samstep74_in_localization"
        return 1, "ok_localization"


def main() -> int:
    if not EVAL_SET.exists():
        print(f"FAIL: missing {EVAL_SET}", file=sys.stderr)
        return 2

    eval_set = json.loads(EVAL_SET.read_text())
    t0 = time.time()
    total = 0
    per_file: list[tuple[str, str, int, str]] = []

    for entry in eval_set:
        path = entry["file"]
        expected_repo = entry["expected_source_repo"]
        content = fetch_program_md(path, ref=DEFAULT_REF)
        delta, reason = score_file(content, expected_repo)
        total += delta
        per_file.append((path, expected_repo, delta, reason))

    elapsed = time.time() - t0
    max_score = len(eval_set)

    print(f"\n=== Cross-link-sweep eval ===")
    print(f"score: {total} / {max_score} | elapsed: {elapsed:.2f}s")
    print()
    print(f"{'file':50} {'expected_repo':40} {'Δ':>3}  {'reason'}")
    print("-" * 100)
    for path, expected_repo, delta, reason in per_file:
        marker = "+" if delta else "·"
        print(f"{path:50} {expected_repo:40} {marker:>3}  {reason}")

    if total == max_score:
        print(f"\n✅ ALL CLEAR — every program.md points to the right source repo.")
        return 0
    print(f"\n❌ {max_score - total} files still need work.")
    return 1


if __name__ == "__main__":
    sys.exit(main())