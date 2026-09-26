---
name: release-captain
description: Prepares a software release safely - reads commits since the last tag, runs tests in a sandbox, classifies changes and proposes a semver bump, checks blast radius, drafts release notes, and pauses for human approval before tagging or publishing. Use this skill whenever asked to "prepare a release", "cut a release", "ship a new version", or similar for a given repository.
---

# Release Captain

## When to use this skill
Use whenever the human asks you to prepare, cut, or ship a release for a
specific GitHub repository.

## Step-by-step workflow

1. **Find the last tag.** Use the GitHub tool to get the most recent tag on
   the target repo. If there is no tag yet, treat the first commit as the
   starting point and say so.

2. **List commits since that tag.** Pull commit messages, authors, and
   (where available) diffs.

3. **Clone and test in the sandbox.** Use the sandbox to clone the repo and
   run its test command (check package.json "scripts.test", or a
   pytest/go test/etc. convention depending on the language). Capture the
   real pass/fail output -- do not summarize from memory.

4. **Gate on test results.**
   - Any failure -> stop. Report exactly which tests failed and why. Do not
     continue to notes, versioning, or approval. This refusal IS the
     deliverable for this path -- make it clear and specific, not vague.
   - All pass -> continue.

5. **Classify commits and propose a semver bump.** Run `scripts/classify.py`
   (bundled with this skill) in the sandbox against the commit list to get a
   structured first pass (feat/fix/breaking per commit + a suggested bump).
   Then review its output yourself and adjust if the commit messages or diffs
   suggest the script's heuristic missed something -- state clearly when you
   overrode the script and why.

6. **Check blast radius.** Run `scripts/blast_radius.py <package_name>
   <registry>` (npm or pypi) to fetch weekly download counts as a proxy for
   how many people/projects depend on this package. If the script can't reach
   the registry, say so honestly rather than inventing a number.

7. **Draft release notes.** Group into Breaking Changes / Features / Fixes,
   in plain language, referencing the real commits.

8. **Present and pause for approval.** Show: proposed version, reasoning,
   blast-radius line, and the release notes. Ask explicitly: "Approve
   publishing v<X.Y.Z>? (yes/no)". Do not tag or publish until you get an
   explicit yes.

## Files in this skill
- `scripts/classify.py` -- heuristic commit classifier + semver suggestion
- `scripts/blast_radius.py` -- registry download-count lookup

## Guardrails
- Never fabricate test results, commit data, or download numbers.
- Never tag, push a tag, or publish to a registry without an explicit human
  "yes" after step 8.
- Never print or log API keys/tokens.
