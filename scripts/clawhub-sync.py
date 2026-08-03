#!/usr/bin/env python3
"""Publish this repo's skills to clawhub.ai, skipping anything already current.

Reads clawhub.yml, asks the registry what version it holds for each slug, and
shells out to `clawhub skill publish` only where they differ. Every skipped
skill is logged with the reason, so a run that publishes nothing still says why.

Two behaviors this exists to prevent, both read off the CLI source (v0.23.1):

  * `clawhub skill publish` ignores any version in SKILL.md frontmatter and
    patch-bumps from whatever the registry holds. Omit --version and the repo's
    version and ClawHub's diverge on the first release and never reconverge.
  * `clawhub sync` batches but cannot set categories, so everything it ships
    lands in the `other` bucket.

Usage:
    python3 scripts/clawhub-sync.py --dry-run
    python3 scripts/clawhub-sync.py
    python3 scripts/clawhub-sync.py --only recover

Stdlib only — no pip install step in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "clawhub.yml"
REGISTRY = "https://clawhub.ai"
OWNER = "conorbronsdon"
SOURCE_REPO = f"{OWNER}/agent-skills"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def parse_manifest(path: Path) -> list[dict]:
    """Minimal reader for the one shape clawhub.yml uses.

    Avoids a PyYAML dependency so CI needs no install step. Accepts exactly
    `key: scalar` and `key: [a, b]` under `- slug:` list items, and raises on
    anything it does not understand rather than silently dropping a field.
    """
    skills: list[dict] = []
    current: dict | None = None
    in_skills = False

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip() if not raw.strip().startswith("#") else ""
        if not line.strip():
            continue
        if line.rstrip() == "skills:":
            in_skills = True
            continue
        if not in_skills:
            continue

        stripped = line.strip()
        if stripped.startswith("- "):
            if current:
                skills.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if current is None:
            raise SystemExit(f"{path}:{lineno}: field outside a list item: {raw!r}")

        if ":" not in stripped:
            raise SystemExit(f"{path}:{lineno}: cannot parse: {raw!r}")
        key, value = stripped.split(":", 1)
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            current[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            current[key] = value

    if current:
        skills.append(current)
    return skills


def published_version(slug: str) -> str | None:
    """Latest version the registry holds for slug, or None if unpublished.

    Uses `clawhub skill inspect --json` rather than the search API: the search
    projection returns `native.version: null` and only an opaque
    `latestVersionId`, so it cannot answer this question. `inspect` returns
    `latestVersion` as a plain semver string.
    """
    try:
        result = subprocess.run(
            ["clawhub", "skill", "inspect", slug, "--json"],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        raise SystemExit("clawhub CLI not found on PATH — npm install -g clawhub")
    if result.returncode != 0:
        # An unpublished slug is a legitimate not-found, not an error. Anything
        # else is worth seeing rather than silently treating as "publish it".
        if "not found" in (result.stderr + result.stdout).lower():
            return None
        raise SystemExit(f"inspect failed for {slug}: {result.stderr.strip() or result.stdout.strip()}")

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"inspect returned non-JSON for {slug}: {exc}")

    if not payload.get("skill"):
        return None
    latest = payload.get("latestVersion")
    return latest if isinstance(latest, str) else None


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print commands, publish nothing")
    parser.add_argument("--only", action="append", default=[], metavar="SLUG")
    args = parser.parse_args()

    skills = parse_manifest(MANIFEST)
    if not skills:
        raise SystemExit(f"{MANIFEST}: no skills found")

    commit = git_head()
    published, skipped, failed = 0, 0, 0

    for skill in skills:
        slug = skill.get("slug")
        if not slug:
            raise SystemExit(f"{MANIFEST}: list item with no slug: {skill}")
        if args.only and slug not in args.only:
            continue

        version = skill.get("version", "")
        if not SEMVER.match(version):
            print(f"FAIL  {slug} — version {version!r} is not semver")
            failed += 1
            continue

        folder = REPO / slug
        if not (folder / "SKILL.md").is_file():
            print(f"FAIL  {slug} — no SKILL.md at {folder}")
            failed += 1
            continue

        live = published_version(slug)
        if live == version:
            print(f"skip  {slug} — {version} already published")
            skipped += 1
            continue

        cmd = [
            "clawhub", "skill", "publish", str(folder),
            "--slug", slug,
            "--name", skill.get("name", slug),
            "--version", version,
            "--categories", ",".join(skill.get("categories", [])),
            "--topics", ",".join(skill.get("topics", [])),
            "--source-repo", SOURCE_REPO,
            "--source-commit", commit,
            "--source-ref", "main",
            "--source-path", slug,
        ]

        was = live or "unpublished"
        print(f"---   {slug}  {was} -> {version}")
        print("      " + " ".join(cmd))
        if args.dry_run:
            continue

        result = subprocess.run(cmd)
        if result.returncode == 0:
            published += 1
        else:
            print(f"FAIL  {slug} — clawhub exited {result.returncode}")
            failed += 1

    print(f"\npublished={published} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
