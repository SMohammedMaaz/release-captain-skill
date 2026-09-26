#!/usr/bin/env python3
"""
classify.py -- heuristic commit classifier + semver bump suggestion.

Usage:
    python classify.py commits.json

commits.json is a list of objects like:
    [{"sha": "abc123", "message": "fix: handle empty input", "diff": "..."}]

diff is optional -- if present, it's scanned too for stronger signals.

Prints a JSON report: each commit's classification + reasoning, and the
overall suggested semver bump (major/minor/patch).
"""

import json
import re
import sys

BREAKING_KEYWORDS = [
    r"breaking change", r"breaking:", r"!:",  # conventional-commit "feat!:"
    r"remove(d)? (public )?(function|method|endpoint|api|option|config)",
    r"rename(d)? (public )?(function|method|endpoint|api)",
    r"change(d)? (the )?(default|signature|behavior)",
    r"drop support",
    r"no longer support",
]

FEAT_PREFIXES = [r"^feat(\(.+\))?:", r"^feature(\(.+\))?:"]
FIX_PREFIXES = [r"^fix(\(.+\))?:", r"^bugfix(\(.+\))?:", r"^hotfix(\(.+\))?:"]

BREAKING_RE = re.compile("|".join(BREAKING_KEYWORDS), re.IGNORECASE)
FEAT_RE = re.compile("|".join(FEAT_PREFIXES), re.IGNORECASE)
FIX_RE = re.compile("|".join(FIX_PREFIXES), re.IGNORECASE)


def classify_commit(commit):
    message = commit.get("message", "")
    diff = commit.get("diff", "") or ""
    haystack = f"{message}\n{diff}"

    if BREAKING_RE.search(haystack):
        return {
            "sha": commit.get("sha"),
            "message": message.splitlines()[0][:120],
            "category": "breaking",
            "reason": "Matched a breaking-change signal in the message or diff "
                      "(e.g. removed/renamed public API, changed default behavior, "
                      "or an explicit 'breaking change' note).",
        }
    if ":" in message and "!" in message.split(":")[0]:
        return {
            "sha": commit.get("sha"),
            "message": message.splitlines()[0][:120],
            "category": "breaking",
            "reason": "Conventional-commit '!' marker indicates a breaking change.",
        }
    if FEAT_RE.search(message):
        return {
            "sha": commit.get("sha"),
            "message": message.splitlines()[0][:120],
            "category": "feat",
            "reason": "Message uses a feat: prefix and no breaking-change signal found.",
        }
    if FIX_RE.search(message):
        return {
            "sha": commit.get("sha"),
            "message": message.splitlines()[0][:120],
            "category": "fix",
            "reason": "Message uses a fix: prefix and no breaking-change signal found.",
        }
    return {
        "sha": commit.get("sha"),
        "message": message.splitlines()[0][:120],
        "category": "other",
        "reason": "No feat/fix/breaking signal detected -- review manually; "
                  "does not drive the version bump on its own.",
    }


def suggest_bump(classified):
    categories = {c["category"] for c in classified}
    if "breaking" in categories:
        bump = "major"
    elif "feat" in categories:
        bump = "minor"
    elif "fix" in categories:
        bump = "patch"
    else:
        bump = "patch"  # default to smallest bump when nothing decisive is found
    return bump


def main():
    if len(sys.argv) != 2:
        print("Usage: python classify.py commits.json", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        commits = json.load(f)

    classified = [classify_commit(c) for c in commits]
    bump = suggest_bump(classified)

    report = {
        "commits": classified,
        "suggested_bump": bump,
        "note": "This is a heuristic first pass. The agent should review each "
                "'other' or ambiguous commit manually before finalizing.",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
