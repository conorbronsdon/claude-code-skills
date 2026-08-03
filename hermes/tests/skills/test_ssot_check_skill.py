"""Contract tests for the ssot-check skill.

Stdlib + pytest only. No network, no API keys — safe under hermetic CI.

These assert the rules CONTRIBUTING.md says reviewers enforce without exception:
the 60-character description limit, tool-reference naming, and platform gating.
A doc-only skill has no runtime to test, so its contract *is* the test surface.
"""

import re
from pathlib import Path

import pytest

SLUG = "ssot-check"
CATEGORY = "software-development"

# Native Hermes tools. CONTRIBUTING forbids naming the shell utilities these wrap.
WRAPPED_UTILITIES = ("grep", "cat", "sed", "curl", "rg")
MARKETING = ("powerful", "comprehensive", "seamless", "robust", "effortless")
REQUIRED_SECTIONS = (
    "When to use this skill",
    "Prerequisites",
    "How to run",
    "Quick reference",
    "Procedure",
    "Pitfalls",
    "Verification",
)


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "optional-skills").is_dir():
            return parent
    raise AssertionError("could not locate optional-skills/ above this test")


@pytest.fixture(scope="module")
def skill_text() -> str:
    path = _repo_root() / "optional-skills" / CATEGORY / SLUG / "SKILL.md"
    assert path.is_file(), f"missing {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def frontmatter(skill_text: str) -> str:
    match = re.match(r"---\n(.*?)\n---\n", skill_text, re.S)
    assert match, "SKILL.md must open with a YAML frontmatter block"
    return match.group(1)


def _field(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(.+)$", frontmatter, re.M)
    assert match, f"frontmatter missing required field: {key}"
    return match.group(1).strip().strip('"')


@pytest.mark.parametrize(
    "key", ["name", "description", "version", "author", "license", "platforms"]
)
def test_required_frontmatter_present(frontmatter: str, key: str) -> None:
    assert _field(frontmatter, key)


def test_name_matches_directory(frontmatter: str) -> None:
    assert _field(frontmatter, "name") == SLUG


def test_description_within_sixty_chars(frontmatter: str) -> None:
    description = _field(frontmatter, "description")
    assert len(description) <= 60, (
        f"description is {len(description)} chars; the limit is 60 and reviewers "
        f"reject over it without exception: {description!r}"
    )


def test_description_is_one_sentence_ending_in_a_period(frontmatter: str) -> None:
    description = _field(frontmatter, "description")
    assert description.endswith("."), "description must end with a period"
    assert description.count(".") == 1, "description must be a single sentence"


def test_description_has_no_marketing_language(frontmatter: str) -> None:
    description = _field(frontmatter, "description").lower()
    assert not [word for word in MARKETING if word in description]


def test_version_is_semver(frontmatter: str) -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", _field(frontmatter, "version"))


def test_author_credits_the_human_first(frontmatter: str) -> None:
    # CONTRIBUTING: external contributions put the contributor first, not the tool.
    assert not _field(frontmatter, "author").startswith("Hermes Agent")


def test_declares_hermes_tags(frontmatter: str) -> None:
    assert re.search(r"^\s+hermes:", frontmatter, re.M), "metadata.hermes block required"
    assert re.search(r"^\s+tags:\s*\[.+\]", frontmatter, re.M), "metadata.hermes.tags required"


def test_declares_platforms(frontmatter: str) -> None:
    # Nothing here uses POSIX-only calls, so all three platforms are declared
    # rather than gated. If that changes, this test should change with it.
    platforms = _field(frontmatter, "platforms")
    for platform in ("linux", "macos", "windows"):
        assert platform in platforms


def test_no_wrapped_shell_utilities_named_in_prose(skill_text: str) -> None:
    prose = re.sub(r"```.*?```", "", skill_text, flags=re.S)
    prose = re.sub(r"`[^`]*`", "", prose)
    found = sorted({m for m in re.findall(r"\b(" + "|".join(WRAPPED_UTILITIES) + r")\b", prose)})
    assert not found, (
        f"name the native Hermes tool, not the utility it wraps: {found} "
        "(search_files, read_file, patch, web_extract)"
    )


@pytest.mark.parametrize("heading", REQUIRED_SECTIONS)
def test_follows_contributing_section_order(skill_text: str, heading: str) -> None:
    assert re.search(rf"^##\s+{re.escape(heading)}\s*$", skill_text, re.M), (
        f"missing required section: {heading}"
    )


def test_sections_appear_in_the_prescribed_order(skill_text: str) -> None:
    positions = [skill_text.index(f"## {h}") for h in REQUIRED_SECTIONS]
    assert positions == sorted(positions), "sections are out of CONTRIBUTING order"
