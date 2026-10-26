"""Repository-wide lint-contract tests.

Encoding hard-won policy invariants as tests: suppression directives must use
the Ruff ignore form (never noqa), and the root and template Ruff ignore
lists must never drift apart. The manual-only skill list in AGENTS.md must
match the skills that set ``disable-model-invocation: true``.
"""

from __future__ import annotations

import re
import tomllib
from itertools import takewhile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "{{cookiecutter.project_slug}}"


def _python_files() -> list[Path]:
    """Collect every Python file subject to the repo lint contract.

    Returns:
        All tracked-ish ``.py`` files under the repo root, the hooks and
        scripts trees, and the Jinja template tree (excluding virtualenvs,
        caches, and the rendered-project sandbox directories).

    """
    scan_roots = (
        REPO_ROOT,
        REPO_ROOT / "hooks",
        REPO_ROOT / "scripts",
        REPO_ROOT / "tests",
        REPO_ROOT / "{{cookiecutter.project_slug}}",
    )
    skip_parts = {".venv", ".temp", ".ruff_cache", "__pycache__", "site", "dist"}
    files: list[Path] = []
    for root in scan_roots:
        for path in root.rglob("*.py"):
            if not skip_parts.isdisjoint(path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def test_no_noqa_directives_anywhere() -> None:
    """Reach every Python file with a ruff ignore directive, never a noqa.

    The replacement directive was introduced after the noqa ban; this scan
    prevents any regressions to the legacy comment style.
    """
    offenders: list[str] = []
    this_file = Path(__file__).resolve()
    for path in _python_files():
        if not path.is_file() or path.resolve() == this_file:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if "# noqa" in line:
                offenders.append(f"{path}:{number}")
    assert not offenders


def test_no_noqa_directives_detects_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that legacy noqa comments are detected and reported."""
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("x = 1  # noqa: E501\n", encoding="utf-8")
    monkeypatch.setattr("tests.test_repo_conventions._python_files", lambda: [bad_file])
    with pytest.raises(AssertionError):
        test_no_noqa_directives_anywhere()


def test_no_noqa_skips_non_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that non-file paths in scan roots are safely skipped."""
    non_file = tmp_path / "dir.py"
    non_file.mkdir()
    monkeypatch.setattr("tests.test_repo_conventions._python_files", lambda: [non_file])
    test_no_noqa_directives_anywhere()


def _ignore_list(config_path: Path) -> list[str]:
    """Read the Ruff global ignore list from a ruff.toml configuration file.

    Args:
        config_path: Path of the ruff.toml to parse.

    Returns:
        The configured ``lint.ignore`` list.

    """
    text = config_path.read_text(encoding="utf-8")
    config = tomllib.loads(text)
    return config["lint"]["ignore"]


def test_root_and_template_ignore_lists_match() -> None:
    """Hold root and template global Ruff ignore lists to exact parity.

    The rule lists were unified after surviving two divergent policies; this
    census fails on the first rule that flips on only one side, so drift is
    visible in tests instead of in surprise render-lint failures.
    """
    assert _ignore_list(REPO_ROOT / "ruff.toml") == _ignore_list(
        TEMPLATE_ROOT / "ruff.toml"
    )


_MANUAL_FLAG = re.compile(r"^disable-model-invocation:\s*true\s*$", re.MULTILINE)
_SKILL_NAME = re.compile(r"`((?:workflow|tool|guide|sdd|domain)-[a-z0-9-]+|sdd)`")


def _manual_only_skills(skills_dir: Path) -> set[str]:
    """Collect skills whose frontmatter disables model invocation.

    Args:
        skills_dir: Directory that holds one subdirectory per skill.

    Returns:
        The names of the skills marked ``disable-model-invocation: true``.

    """
    names: set[str] = set()
    for skill_file in skills_dir.glob("*/SKILL.md"):
        frontmatter = skill_file.read_text(encoding="utf-8").split("---", 2)[1]
        if _MANUAL_FLAG.search(frontmatter):
            names.add(skill_file.parent.name)
    return names


def _agents_md_manual_only(agents_md: Path) -> set[str]:
    """Collect the skill names listed in the AGENTS.md "Manual Only" bullet.

    Args:
        agents_md: Path of the AGENTS.md file to parse.

    Returns:
        The skill names named in backticks inside the bullet.

    """
    lines = agents_md.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if "**Manual Only**" in line)
    continuation = takewhile(
        lambda line: bool(line.strip()) and not line.lstrip().startswith("- "),
        lines[start + 1 :],
    )
    return set(_SKILL_NAME.findall(" ".join([lines[start], *continuation])))


@pytest.mark.parametrize(
    ("skills_dir", "agents_md"),
    [
        (REPO_ROOT / ".agents" / "skills", REPO_ROOT / "AGENTS.md"),
        (TEMPLATE_ROOT / ".agents" / "skills", TEMPLATE_ROOT / "AGENTS.md"),
    ],
    ids=["root", "template"],
)
def test_manual_only_skills_match_agents_md(skills_dir: Path, agents_md: Path) -> None:
    """Hold the AGENTS.md manual-only list to parity with skill frontmatter.

    Agents that skip skill frontmatter still read AGENTS.md, so the two
    sources must name the same manual-only skills.
    """
    manual = _manual_only_skills(skills_dir)
    assert manual
    assert manual == _agents_md_manual_only(agents_md)


def test_template_skills_omit_repo_only_references() -> None:
    """Keep template-repository and Cookiecutter machinery out of template .agents.

    Skills and subagents shipped inside ``{{cookiecutter.project_slug}}/.agents/``
    must have zero awareness of the template repository they were generated from,
    Cookiecutter/Jinja syntax, maintainer-only tasks/scripts/tests, or Zenith's
    own documentation tree.
    """
    repo_only = {
        path.name
        for path in (REPO_ROOT / ".agents" / "skills").iterdir()
        if not path.is_symlink()
    }
    forbidden = (
        *repo_only,
        "zenith",
        "cookiecutter",
        "{{",
        "{%",
        "lint-rendered",
        "sync-skills-check",
        "sync_skills",
        "audit_rendered",
        "test_template",
        "test_repo_conventions",
        "post_gen_project",
        "pre_gen_project",
        "include_cli",
        "include_ci",
        "include_agent_skills",
        "docs/first-steps.md",
        "docs/philosophy.md",
        "docs/tools/",
        "docs/skills/",
        "docs/ci-actions.md",
    )
    agent_files = [
        path
        for path in (TEMPLATE_ROOT / ".agents").rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".toml"}
    ]
    offenders = [
        f"{path.relative_to(TEMPLATE_ROOT)}: {term}"
        for path in sorted(agent_files)
        for term in forbidden
        if term in path.read_text(encoding="utf-8").lower()
    ]
    assert not offenders
