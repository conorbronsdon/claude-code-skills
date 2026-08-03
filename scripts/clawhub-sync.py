#!/usr/bin/env python3
"""Publish this repo's skills to clawhub.ai, skipping anything already current.

Reads clawhub.yml, asks the registry what it already holds for each slug, and
shells out to `clawhub skill publish` only where the repo and the registry
disagree. Every skipped skill is logged with its reason, so a run that publishes
nothing still says why.

Idempotency is the whole point: a push that changes nothing must publish
nothing. Two CLI behaviors, both read off v0.23.1 and confirmed against the live
registry on 2026-08-03, decide how that is done.

  * `clawhub skill publish` ignores any version in SKILL.md frontmatter and
    patch-bumps from whatever the registry holds. Omit --version and the repo's
    version and ClawHub's diverge on the first release and never reconverge.
    So the publish call always passes --version from the manifest.

  * `clawhub skill publish --dry-run --json` reports `latestVersion` as a plain
    semver string and a `status` of "unchanged" when the folder's content
    fingerprint already matches a published version. That probe is the gate.
    It returns before the CLI requires a token and before it POSTs anything
    (dist/cli/commands/publish.js: the --dry-run branch returns at the
    "would-publish" result, above `requireAuthToken()` and the form upload).

The probe deliberately omits --version, --categories, and --topics. The CLI
only reports "unchanged" when neither an explicit version nor explicit catalog
metadata was passed (`hasExplicitCatalogMetadata` in publish.js); passing them
suppresses the fingerprint check and makes every probe read "would-publish".

Both the probe and the publish pass --owner explicitly. Slugs are not unique
across the registry: `skill-creator` currently resolves to four owners
(chindden, gasgangrene, paudyyin, conorbronsdon), and a gate that read a
stranger's version would either publish backwards or refuse to publish at all.

Owner scoping is not automatic. publish.js resolves it as

    ownerHandle = explicitOwnerHandle
                  || (optionalToken ? await getDefaultOwnerHandle(...) : undefined)

and resolveSkillVersion only sends `ownerHandle` when that value is truthy — so
with no --owner and no stored token the lookup is GLOBAL and silently reads
whichever same-slug skill the registry returns. In CI the login step runs first,
so the token path would cover it; run the script on a box that has never logged
in and it would not. Passing --owner removes the dependency entirely, costs one
flag, and skips a whoami round-trip per skill. On the publish call it is also a
safety rail: a token belonging to some other handle now fails server-side
instead of quietly publishing under that handle.

`clawhub inspect` is not used. Its `--json` returns `latestVersion` as an object
(`{"version": "1.0.0", ...}`), not a string, and reading it as a string silently
yields None for every published skill — which reads as "unpublished" and
republishes all nine on every run. Different endpoint, different projection; the
probe above is the same code path that performs the publish, so the version it
reports is the one the publish will actually be compared against.

The --source-* flags are passed because they are free, not because they work.
Verified 2026-08-03: `links.source` is null for every natively published skill
on the registry (0 of 390 sampled) and stays null after a publish that passes
all four. Never gate this script, or a verification step, on them.

Usage:
    python3 scripts/clawhub-sync.py --check      # manifest + secret scan only, no network
    python3 scripts/clawhub-sync.py --dry-run    # probe the registry, publish nothing
    python3 scripts/clawhub-sync.py              # publish what differs
    python3 scripts/clawhub-sync.py --only recover

Stdlib only — no pip install step in CI.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "clawhub.yml"
OWNER = "conorbronsdon"
SOURCE_REPO = f"{OWNER}/agent-skills"

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# Deliberately wider than what can actually reach the registry today. Two CLI
# filters already block most of this: dot-leading path segments are dropped, and
# so is any extension outside the client's text allowlist. Measured against
# v0.23.1 with dry-run publishes (fileCount and content fingerprint, baseline vs
# planted):
#
#   .env.local        not uploaded        credentials.json  UPLOADED
#   server.key        not uploaded        secrets.yaml      UPLOADED
#   id.pem            not uploaded        notes.txt         UPLOADED
#
# So `.env*`, `*.key` and `*.pem` catch nothing right now; they stay as a hedge
# against that filtering changing. `credentials*` and `*secret*` are the two that
# match something publishable.
#
# The real gap is that this matches on NAME. A credential pasted inside
# SKILL.md, config.json or settings.yml has an innocuous name and an allowlisted
# extension, and nothing here stops it. Treat this as a tripwire for obvious
# mistakes, not as the thing that makes publishing safe.
#
# Publishing is not undoable by a delete — a soft delete cannot un-download what
# was public in the meantime.
RISKY_GLOBS = (".env*", "*.key", "*.pem", "credentials*", "*secret*")


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


def find_risky_files(folder: Path) -> list[Path]:
    """Publishable files whose name looks like a credential.

    Scans the whole folder, which is a superset of what actually uploads —
    erring wide is the right direction for a guard that gates a public,
    irreversible publish.
    """
    hits = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if any(fnmatch.fnmatch(path.name.lower(), glob) for glob in RISKY_GLOBS):
            hits.append(path)
    return hits


def clawhub_bin() -> str:
    """Absolute path to the CLI.

    `shutil.which` resolves the PATHEXT shim on Windows (`clawhub.CMD`), which a
    bare `subprocess.run(["clawhub", ...])` does not find. On Linux CI it
    resolves the normal symlink.
    """
    found = shutil.which("clawhub")
    if not found:
        raise SystemExit("clawhub CLI not found on PATH — npm install -g clawhub")
    return found


def probe(folder: Path, slug: str, name: str) -> dict:
    """Ask the registry what it holds for slug, via a publish dry-run.

    Publishes nothing. See the module docstring for why this rather than
    `clawhub inspect`, and why --version/--categories/--topics are omitted here
    but passed on the real publish.
    """
    result = subprocess.run(
        [clawhub_bin(), "skill", "publish", str(folder),
         "--slug", slug, "--name", name, "--owner", OWNER, "--dry-run", "--json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"probe failed for {slug}: {detail}")
    try:
        state = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"probe returned non-JSON for {slug}: {exc}")
    # Assert the one field the whole gate rests on. `latestVersion` is a plain
    # string here because publish.js unwraps it (`resolved.latestVersion?.version
    # ?? null`) — but `clawhub inspect --json` returns it as an OBJECT, and an
    # earlier version of this script read that shape, got None for every
    # published skill, and would have republished all nine on every run. If a
    # future CLI renames, drops, or nulls this key, the same silent failure
    # returns: `latest is None` reads as "never published". Refuse instead.
    if "latestVersion" not in state or not isinstance(
        state["latestVersion"], (str, type(None))
    ):
        raise SystemExit(
            f"probe for {slug}: unexpected JSON shape — 'latestVersion' is "
            f"{state.get('latestVersion')!r}, expected a string or null. The CLI "
            f"contract changed; refusing to publish rather than treating this as "
            f"unpublished."
        )
    return state


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def semver_tuple(value: str) -> tuple[int, int, int] | None:
    """(major, minor, patch) as ints, or None if not plain semver.

    Ints, not the regex's string groups: comparing those lexically puts 1.10.0
    below 1.9.0 and would call a correct manifest "behind the registry".
    """
    match = SEMVER.match(value or "")
    return tuple(int(part) for part in match.groups()) if match else None


def notice(level: str, message: str) -> None:
    """Print, and surface it in the Actions UI when running there."""
    print(f"{level.upper()}  {message}")
    if os.environ.get("GITHUB_ACTIONS") == "true" and level in ("warning", "error"):
        print(f"::{level}::{message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish skills to clawhub.ai")
    parser.add_argument("--dry-run", action="store_true",
                        help="probe the registry and print decisions, publish nothing")
    parser.add_argument("--check", action="store_true",
                        help="validate the manifest and run the secret scan only; no network")
    parser.add_argument("--only", action="append", default=[], metavar="SLUG")
    args = parser.parse_args()

    skills = parse_manifest(MANIFEST)
    if not skills:
        raise SystemExit(f"{MANIFEST}: no skills found")

    targets = []
    for skill in skills:
        slug = skill.get("slug")
        if not slug:
            raise SystemExit(f"{MANIFEST}: list item with no slug: {skill}")
        if args.only and slug not in args.only:
            continue
        targets.append(skill)

    if args.only:
        missing = set(args.only) - {s["slug"] for s in targets}
        if missing:
            raise SystemExit(f"--only named slugs not in the manifest: {', '.join(sorted(missing))}")

    # Validate every target before touching the network, so a broken manifest
    # fails the run rather than publishing the subset that happened to parse.
    problems = 0
    for skill in targets:
        slug = skill["slug"]
        version = skill.get("version", "")
        if not SEMVER.match(version):
            notice("error", f"{slug} — version {version!r} is not semver")
            problems += 1
        folder = REPO / slug
        if not (folder / "SKILL.md").is_file():
            notice("error", f"{slug} — no SKILL.md at {folder}")
            problems += 1

    # The secret sweep, before any publish and across every target. A publish is
    # public and irreversible, so this fails the whole run rather than skipping
    # the one skill: nothing ships from a tree that holds a credential-shaped
    # file. `--preflight` in the shell driver is advisory and skippable, which is
    # why the guard lives on the publish path here rather than beside it.
    for skill in targets:
        for hit in find_risky_files(REPO / skill["slug"]):
            notice("error", f"{skill['slug']} — refusing to publish, credential-shaped file "
                            f"would upload: {hit.relative_to(REPO)}")
            problems += 1

    if problems:
        print(f"\n{problems} problem(s) — nothing published")
        return 1

    if args.check:
        print(f"check OK — {len(targets)} skill(s), manifest parses, no credential-shaped files")
        return 0

    commit = git_head()
    published = skipped = failed = stale = 0

    for skill in targets:
        slug = skill["slug"]
        version = skill["version"]
        folder = REPO / slug
        name = skill.get("name", slug)

        state = probe(folder, slug, name)
        latest = state.get("latestVersion")
        # On an "unchanged" result this is the version whose fingerprint matched,
        # which is not necessarily the latest — a revert to older content matches
        # an older version. Comparing the two separates "current" from "reverted".
        matched = state.get("version") if state.get("status") == "unchanged" else None
        content_is_latest = matched is not None and matched == latest

        if latest is None:
            reason = "unpublished"
        elif version == latest:
            if content_is_latest:
                print(f"skip  {slug} — {version} already published, content identical")
            else:
                notice("warning",
                       f"{slug} — content differs from published {latest} but clawhub.yml still "
                       f"says {version}. Bump the manifest version to ship it.")
                stale += 1
            skipped += 1
            continue
        else:
            live = semver_tuple(latest)
            # A registry version this cannot parse (a prerelease, say) is not
            # something to guess about — publish forward and let the CLI reject
            # it rather than silently deciding which one is newer.
            if live is not None and semver_tuple(version) < live:
                notice("error", f"{slug} — clawhub.yml says {version}, registry already holds "
                                f"{latest}. The manifest is behind; fix it rather than "
                                f"publishing backwards.")
                failed += 1
                continue
            reason = f"{latest} -> {version}"

        cmd = [
            clawhub_bin(), "skill", "publish", str(folder),
            "--slug", slug,
            "--name", name,
            "--owner", OWNER,
            "--version", version,
        ]
        # Only when non-empty. publish.js sends the key just for being present
        # (`options.categories !== undefined ? { categories } : {}`), and
        # parseCsv("") is [] — so `--categories ""` would overwrite the skill's
        # catalog metadata with an empty list. Omitting the flag leaves whatever
        # the registry already holds.
        for flag, values in (("--categories", skill.get("categories", [])),
                             ("--topics", skill.get("topics", []))):
            if values:
                cmd += [flag, ",".join(values)]
        cmd += [
            "--source-repo", SOURCE_REPO,
            "--source-commit", commit,
            "--source-ref", "main",
            "--source-path", slug,
        ]

        print(f"---   {slug}  {reason}")
        print("      " + " ".join(cmd[1:]))
        if args.dry_run:
            continue

        if subprocess.run(cmd).returncode == 0:
            published += 1
        else:
            notice("error", f"{slug} — clawhub publish failed")
            failed += 1

    # A publish is not readable back immediately: the version stays absent from
    # --versions and the detail API for 30-60s while moderation runs
    # (docs/clawhub-publishing.md §8). Nothing here reads it back, which is
    # deliberate — a verify step would report a false failure, and a retry loop
    # would republish over a good publish.
    print(f"\npublished={published} skipped={skipped} stale={stale} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
