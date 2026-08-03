"""Contract tests for the ssot-check skill.

Asserts the rules CONTRIBUTING.md says reviewers reject on: the 60-character
description limit, tool-reference naming, platform declaration, and section
order. A doc-only skill has no runtime, so its contract is the test surface.

The constants below are transcribed from CONTRIBUTING.md, deliberately, so this
file grades the skill against the spec rather than against itself. Changing a
heading in SKILL.md must break this test, not be absorbed by it.

Self-contained on purpose: each skill ships in its own PR, so a test may not
import a shared helper that would not travel with it.

stdlib + pytest + PyYAML (as used by tests/skills/test_grounded_citations_skill.py).
No network, no API keys.
"""

import re
from pathlib import Path

import pytest
import yaml

SLUG = "ssot-check"
CATEGORY = "software-development"

# CONTRIBUTING §5, verbatim and in order.
REQUIRED_SECTIONS = (
    "When to Use",
    "Prerequisites",
    "How to Run",
    "Quick Reference",
    "Procedure",
    "Pitfalls",
    "Verification",
)

# CONTRIBUTING's don't-name-the-wrapper table, complete. Matched only in their
# backticked form: bare-word matching is unsound here because `find`, `patch`
# and `ls` are ordinary English, and a regex over prose cannot tell a shell
# utility from a verb. Backticks are how an author actually writes a tool name,
# so this catches the real failure mode without the false positives.
WRAPPED_UTILITIES = (
    "grep", "rg", "cat", "head", "tail", "sed", "awk", "curl", "echo", "find", "ls",
)
NATIVE_TOOLS = (
    "terminal", "web_extract", "read_file", "write_file", "search_files", "patch",
    "vision_analyze", "browser_navigate", "delegate_task", "cronjob", "memory",
)
MARKETING = ("powerful", "comprehensive", "seamless", "robust", "effortless", "cutting-edge")
FOREIGN_PLATFORMS = ("claude", "copilot", "cursor", "anthropic", "openai", "codex")


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "optional-skills").is_dir():
            return parent
    raise AssertionError("could not locate optional-skills/ above this test")


@pytest.fixture(scope="module")
def skill_dir() -> Path:
    path = _repo_root() / "optional-skills" / CATEGORY / SLUG
    assert path.is_dir(), f"missing skill directory {path}"
    return path


@pytest.fixture(scope="module")
def skill_text(skill_dir: Path) -> str:
    path = skill_dir / "SKILL.md"
    assert path.is_file(), f"missing {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def meta(skill_text: str) -> dict:
    match = re.match(r"---\n(.*?)\n---\n", skill_text, re.S)
    assert match, "SKILL.md must open with a YAML frontmatter block"
    loaded = yaml.safe_load(match.group(1))
    assert isinstance(loaded, dict), "frontmatter must parse to a mapping"
    return loaded


@pytest.fixture(scope="module")
def body(skill_text: str) -> str:
    return re.sub(r"\A---\n.*?\n---\n", "", skill_text, flags=re.S)


@pytest.mark.parametrize(
    "key", ["name", "description", "version", "author", "license", "platforms"]
)
def test_required_frontmatter_present(meta: dict, key: str) -> None:
    assert meta.get(key), f"frontmatter missing required field: {key}"


def test_name_matches_directory(meta: dict) -> None:
    assert meta["name"] == SLUG


def test_description_within_sixty_chars(meta: dict) -> None:
    description = meta["description"]
    assert len(description) <= 60, (
        f"description is {len(description)} chars; the limit is 60 and reviewers "
        f"reject over it without exception: {description!r}"
    )


def test_description_is_one_sentence_ending_in_a_period(meta: dict) -> None:
    description = meta["description"]
    assert description.endswith("."), "description must end with a period"
    assert description.count(".") == 1, "description must be a single sentence"


def test_description_has_no_marketing_language(meta: dict) -> None:
    lowered = meta["description"].lower()
    assert not [word for word in MARKETING if word in lowered]


def test_description_does_not_repeat_the_skill_name(meta: dict) -> None:
    # CONTRIBUTING §1: "Don't repeat skill name".
    lowered = meta["description"].lower()
    for token in SLUG.split("-"):
        assert token not in lowered, f"description repeats a name token: {token!r}"


def test_version_is_semver(meta: dict) -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", str(meta["version"]))


def test_license_is_mit(meta: dict) -> None:
    # CONTRIBUTING: "contributions will be licensed under the MIT License".
    assert meta["license"] == "MIT"


def test_author_credits_the_human_first(meta: dict) -> None:
    # CONTRIBUTING §4: contributor first, "Hermes Agent" secondary.
    author = meta["author"]
    assert not author.startswith("Hermes Agent")
    assert re.match(r"^[^(]+\(([^)]+)\)\s*$", author), (
        f'author must read "Name (github-login)": {author!r}'
    )


def test_hermes_metadata_block(meta: dict) -> None:
    hermes = (meta.get("metadata") or {}).get("hermes")
    assert isinstance(hermes, dict), "metadata.hermes must be a mapping"
    assert hermes.get("tags"), "metadata.hermes.tags required"
    assert hermes.get("category") == CATEGORY, (
        f"metadata.hermes.category must be {CATEGORY!r}, got {hermes.get('category')!r}"
    )


def test_platforms_are_exact_identifiers(meta: dict) -> None:
    # A substring check would pass "linuxbsd". Compare list members exactly.
    platforms = meta["platforms"]
    assert isinstance(platforms, list), "platforms must be a YAML list"
    assert set(platforms) <= {"linux", "macos", "windows"}, f"unknown platform in {platforms}"
    assert platforms, "platforms must not be empty"


def test_no_wrapped_shell_utilities_named_as_tools(body: str) -> None:
    found = sorted({
        match for match in re.findall(r"`([a-z]+)`", body) if match in WRAPPED_UTILITIES
    })
    assert not found, (
        f"name the native Hermes tool, not the utility it wraps: {found}. "
        f"See CONTRIBUTING's mapping table."
    )


def test_every_backticked_tool_reference_is_native(body: str) -> None:
    # Tool-shaped identifiers (snake_case words) must be real Hermes tools.
    candidates = {m for m in re.findall(r"`([a-z][a-z0-9]*_[a-z0-9_]+)`", body)}
    unknown = sorted(c for c in candidates if c not in NATIVE_TOOLS)
    assert not unknown, f"not native Hermes tools: {unknown}"


def test_no_foreign_platform_references(body: str) -> None:
    found = sorted({p for p in FOREIGN_PLATFORMS if re.search(rf"\b{p}\b", body, re.I)})
    assert not found, f"references another agent platform: {found}"


@pytest.mark.parametrize("heading", REQUIRED_SECTIONS)
def test_required_section_present(body: str, heading: str) -> None:
    assert re.search(rf"^##\s+{re.escape(heading)}\s*$", body, re.M), (
        f"missing required section: ## {heading}"
    )


def test_sections_appear_in_the_prescribed_order(body: str) -> None:
    positions = []
    for heading in REQUIRED_SECTIONS:
        match = re.search(rf"^##\s+{re.escape(heading)}\s*$", body, re.M)
        assert match, f"missing required section: ## {heading}"
        positions.append(match.start())
    assert positions == sorted(positions), (
        "sections are out of the order CONTRIBUTING §5 prescribes"
    )


def test_referenced_support_files_exist(skill_dir: Path, body: str) -> None:
    # A brief or template the skill points at but does not ship makes it
    # unexecutable. This is what shipped eval-integrity without its briefs.
    for target in re.findall(r"\]\((references/[^)]+|scripts/[^)]+|templates/[^)]+)\)", body):
        assert (skill_dir / target).exists(), f"referenced but not shipped: {target}"
