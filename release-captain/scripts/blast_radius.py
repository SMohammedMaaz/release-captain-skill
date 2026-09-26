#!/usr/bin/env python3
"""
blast_radius.py -- look up how many people depend on a package, as a proxy
for "blast radius" before publishing a new version.

Usage:
    python blast_radius.py <package_name> <npm|pypi>

Prints a one-line, human-readable summary the agent can drop straight into
its approval prompt. Exits with a clear message (not a crash) if the
registry can't be reached, so the agent can honestly say "couldn't check"
instead of guessing.
"""

import sys
import json
import urllib.request
import urllib.error


def npm_downloads(package_name):
    # npm's public download-counts API, no auth required
    url = f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    return data.get("downloads")


def pypi_info(package_name):
    # PyPI JSON API exposes basic package metadata (not live download counts)
    url = f"https://pypi.org/pypi/{package_name}/json"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    releases = data.get("releases", {})
    return {
        "version_count": len(releases),
        "latest_version": data.get("info", {}).get("version"),
    }


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("npm", "pypi"):
        print("Usage: python blast_radius.py <package_name> <npm|pypi>", file=sys.stderr)
        sys.exit(1)

    package_name, registry = sys.argv[1], sys.argv[2]

    try:
        if registry == "npm":
            downloads = npm_downloads(package_name)
            if downloads is None:
                print(f"Could not determine weekly downloads for '{package_name}' on npm.")
            else:
                print(
                    f"'{package_name}' had {downloads:,} downloads on npm in the last week "
                    f"-- that's the rough blast radius of this release."
                )
        else:
            info = pypi_info(package_name)
            print(
                f"'{package_name}' has {info['version_count']} published versions on PyPI "
                f"(latest: {info['latest_version']}). PyPI's public API does not expose live "
                f"download counts, so treat this as a partial signal, not a full blast-radius figure."
            )
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"'{package_name}' was not found on {registry} -- cannot assess blast radius.")
        else:
            print(f"Could not reach {registry} registry (HTTP {e.code}) -- blast radius unknown.")
    except Exception as e:
        print(f"Could not reach {registry} registry ({e}) -- blast radius unknown.")


if __name__ == "__main__":
    main()
