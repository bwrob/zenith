"""Unit tests for Spec-Driven Development tooling scripts."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_SPEC = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "sdd-spec"
    / "scripts"
)
SCRIPTS_REVIEW = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "sdd-review"
    / "scripts"
)
SCRIPTS_SDD = (
    Path(__file__).resolve().parent.parent / ".agents" / "skills" / "sdd" / "scripts"
)

sys.path.insert(0, str(SCRIPTS_SPEC))
sys.path.insert(0, str(SCRIPTS_REVIEW))
sys.path.insert(0, str(SCRIPTS_SDD))

import archive_feature
import check_spec
import check_traceability
import revert_task

# --- check_spec.py tests ---


def test_validate_spec_content_valid() -> None:
    valid_spec = (
        "# Feature Spec\n\n"
        "### In-Scope\n- Feature A\n\n"
        "### Out-of-Scope\n- Feature B\n\n"
        "### Requirement 1: REQ-001\n"
        "- **ID**: `REQ-001`\n"
        "The system must validate input.\n\n"
        "### Scenario 1: Happy Path\n"
        "- Given valid input\n"
        "- When executed\n"
        "- Then output is returned\n"
    )
    res = check_spec.validate_spec_content(valid_spec, Path("spec.md"))
    assert res.is_valid
    assert len(res.errors) == 0
    assert res.requirement_count >= 1
    assert res.scenario_count >= 1


def test_validate_spec_content_missing_boundaries() -> None:
    content = "Just some text without boundaries."
    res = check_spec.validate_spec_content(content, Path("spec.md"))
    assert not res.is_valid
    assert any("In-Scope" in err for err in res.errors)
    assert any("Out-of-Scope" in err for err in res.errors)
    assert any("No functional requirements" in err for err in res.errors)
    assert any("No complete Given/When/Then" in err for err in res.errors)


def test_validate_spec_content_code_leakage() -> None:
    content = (
        "### In-Scope\n- A\n### Out-of-Scope\n- B\nREQ-001\nGiven When Then\n"
        "```python\nclass InternalLeak:\n    pass\n```\n"
    )
    res = check_spec.validate_spec_content(content, Path("spec.md"))
    assert not res.is_valid
    assert any("Premature implementation" in err for err in res.errors)

    # Allowed when tagged with # example or <!-- allow-code -->
    content_allowed = (
        "### In-Scope\n- A\n### Out-of-Scope\n- B\nREQ-001\nGiven When Then\n"
        "```python\n# example of payload\nclass ExampleDto:\n    pass\n```\n"
    )
    res_allowed = check_spec.validate_spec_content(content_allowed, Path("spec.md"))
    assert res_allowed.is_valid


def test_validate_spec_content_placeholders() -> None:
    content = (
        "### In-Scope\n- A\n### Out-of-Scope\n- B\nREQ-001\nGiven When Then\n"
        "Problem: [Describe problem here]\n"
    )
    res = check_spec.validate_spec_content(content, Path("spec.md"))
    assert res.is_valid
    assert any("unfilled template placeholder" in w for w in res.warnings)


def test_validate_spec_file_not_found(tmp_path: Path) -> None:
    res = check_spec.validate_spec_file(tmp_path / "nonexistent.md")
    assert not res.is_valid
    assert any("not found" in err for err in res.errors)


def test_validate_spec_format_report_and_main(tmp_path: Path) -> None:
    spec_dir = tmp_path / "feat"
    spec_dir.mkdir()
    spec_file = spec_dir / "spec.md"
    spec_file.write_text(
        "### In-Scope\n- A\n### Out-of-Scope\n- B\nREQ-001\nGiven When Then\nThe system must work.\n",
        encoding="utf-8",
    )

    res = check_spec.validate_spec_file(spec_file)
    report = check_spec.format_validation_report(res)
    assert "Passed" in report

    exit_code = check_spec.main([str(spec_dir)])
    assert exit_code == 0

    exit_code_missing = check_spec.main([str(tmp_path / "missing.md")])
    assert exit_code_missing == 1


# --- check_traceability.py tests ---


def test_extract_requirements_from_spec(tmp_path: Path) -> None:
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "### Requirement 1: User Profile Retrieval\n"
        "- **ID**: `REQ-001`\n"
        "### Requirement 2: Profile Update\n"
        "- **ID**: `REQ-002`\n"
        "## 6. Acceptance Criteria\n"
        "### Scenario 1: Pass\n",
        encoding="utf-8",
    )
    reqs = check_traceability.extract_requirements_from_spec(spec_file)
    assert len(reqs) == 2
    assert reqs[0].req_id == "REQ-001"
    assert reqs[0].title == "User Profile Retrieval"
    assert reqs[1].req_id == "REQ-002"
    assert reqs[1].title == "Profile Update"


def test_extract_requirements_fallback(tmp_path: Path) -> None:
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "Text mentioning REQ-042 and REQ-099 casually.", encoding="utf-8"
    )
    reqs = check_traceability.extract_requirements_from_spec(spec_file)
    assert [r.req_id for r in reqs] == ["REQ-042", "REQ-099"]


def test_extract_requirements_missing_file(tmp_path: Path) -> None:
    assert (
        check_traceability.extract_requirements_from_spec(tmp_path / "missing.md") == []
    )


def test_scan_tests_for_requirements(tmp_path: Path) -> None:
    test_file = tmp_path / "test_feature.py"
    test_file.write_text(
        "def test_req_001_logic(): pass\n"
        "\n"
        "def test_custom():\n"
        '    """Docstring REQ-002."""\n'
        "    pass\n"
        "\n"
        '@pytest.mark.req("REQ-003")\n'
        "def test_decorated(): pass\n"
        "\n"
        '@pytest.mark.req("004")\n'
        "def test_decorated_numeric(): pass\n"
        "\n"
        "def test_freq_1_false_positive(): pass\n",
        encoding="utf-8",
    )
    mapping = check_traceability.scan_tests_for_requirements(tmp_path)
    assert "REQ-001" in mapping
    assert "REQ-002" in mapping
    assert "REQ-003" in mapping
    assert "REQ-004" in mapping
    assert not any(
        "test_freq_1_false_positive" in t for t in mapping.get("REQ-001", [])
    )


def test_analyze_traceability_and_main(tmp_path: Path) -> None:
    spec_file = tmp_path / "spec.md"
    spec_file.write_text("REQ-001\nREQ-002\n", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_a.py").write_text("def test_req_001(): pass\n", encoding="utf-8")

    res = check_traceability.analyze_traceability(spec_file, tests_dir)
    assert res.missing_tests == ["REQ-002"]

    report = check_traceability.format_traceability_report(res)
    assert "`REQ-002` lacks an automated test case" in report

    exit_code = check_traceability.main([str(spec_file), "--tests-dir", str(tests_dir)])
    assert exit_code == 1

    table_only_code = check_traceability.main(
        [str(spec_file), "--tests-dir", str(tests_dir), "--table-only"]
    )
    assert table_only_code == 1


# --- archive_feature.py tests ---


def test_archive_feature_success(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    docs_root = tmp_path / "docs" / "specs"

    feat_dir = specs_root / "my-feat"
    feat_dir.mkdir(parents=True)
    (feat_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (feat_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (feat_dir / "review.md").write_text(
        "# Review\n- **Verdict**: Approved\n", encoding="utf-8"
    )

    # Pre-create index.md without trailing newline to test clean concatenation
    docs_root.mkdir(parents=True)
    (docs_root / "index.md").write_text(
        "# Registry\n| Col |\n| :--- |\n", encoding="utf-8"
    )

    exit_code = archive_feature.archive_feature("my-feat", specs_root, docs_root)
    assert exit_code == 0
    assert (docs_root / "my-feat" / "spec.md").exists()
    assert (docs_root / "my-feat" / "plan.md").exists()
    assert (docs_root / "my-feat" / "review.md").exists()
    assert (docs_root / "index.md").exists()
    index_text = (docs_root / "index.md").read_text(encoding="utf-8")
    assert "\n| `my-feat` |" in index_text
    assert not feat_dir.exists()


def test_archive_feature_not_approved_error(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    docs_root = tmp_path / "docs" / "specs"

    feat_dir = specs_root / "my-feat"
    feat_dir.mkdir(parents=True)
    (feat_dir / "review.md").write_text(
        "Verdict: Changes Requested\n", encoding="utf-8"
    )

    exit_code = archive_feature.archive_feature("my-feat", specs_root, docs_root)
    assert exit_code == 1

    # Unedited template must also fail
    (feat_dir / "review.md").write_text(
        "- **Verdict**: Approved | Changes Requested\n", encoding="utf-8"
    )
    assert archive_feature.archive_feature("my-feat", specs_root, docs_root) == 1

    # Bypass with force
    exit_code_force = archive_feature.archive_feature(
        "my-feat", specs_root, docs_root, force=True, keep_temp=True
    )
    assert exit_code_force == 0
    assert feat_dir.exists()


def test_archive_feature_path_traversal(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    docs_root = tmp_path / "docs" / "specs"
    specs_root.mkdir(parents=True)

    # Attempt directory traversal outside specs_root
    exit_code = archive_feature.archive_feature("../../outside", specs_root, docs_root)
    assert exit_code == 1


def test_archive_feature_missing_dir(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    docs_root = tmp_path / "docs" / "specs"
    assert archive_feature.archive_feature("nonexistent", specs_root, docs_root) == 1


def test_archive_feature_main(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    docs_root = tmp_path / "docs" / "specs"
    feat_dir = specs_root / "cli-feat"
    feat_dir.mkdir(parents=True)
    (feat_dir / "review.md").write_text("Verdict: Approved\n", encoding="utf-8")

    exit_code = archive_feature.main(
        [
            "cli-feat",
            "--specs-dir",
            str(specs_root),
            "--docs-dir",
            str(docs_root),
        ]
    )
    assert exit_code == 0


# --- revert_task.py tests ---


def test_find_revertable_tasks_empty() -> None:
    plan = "# Plan\n- [ ] Task 1 (no sha)\n- [x] Task 2 without sha\n"
    targets = revert_task.find_revertable_tasks(plan)
    assert targets == []


def test_find_revertable_tasks_found() -> None:
    plan = (
        "# Plan\n"
        "- [x] **Task 1: Protocol** (a1b2c3d)\n"
        "- [ ] **Task 2: Service**\n"
        "  - [x] Subtask A (1234567890abcdef)\n"
    )
    targets = revert_task.find_revertable_tasks(plan)
    assert len(targets) == 2
    assert targets[0].task_title == "**Task 1: Protocol**"
    assert targets[0].sha == "a1b2c3d"
    assert targets[0].reset_line == "- [ ] **Task 1: Protocol**"

    assert targets[1].task_title == "Subtask A"
    assert targets[1].sha == "1234567890abcdef"
    assert targets[1].reset_line == "  - [ ] Subtask A"


def test_revert_task_security_violation(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    specs_root.mkdir(parents=True)
    assert revert_task.revert_task("../../outside", specs_root=specs_root) == 1
    assert revert_task.revert_task(".", specs_root=specs_root) == 1


def test_revert_task_path_exception() -> None:
    class BrokenSpecs:
        def resolve(self) -> Path:
            raise RuntimeError("Simulated resolve failure")

        def __truediv__(self, _other: str) -> BrokenSpecs:
            return self

    assert revert_task.revert_task("any-feat", specs_root=BrokenSpecs()) == 1  # type: ignore[arg-type]


def test_revert_task_plan_missing(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    assert revert_task.revert_task("auth", specs_root=specs_root) == 1


def test_revert_task_plan_read_error(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    plan_file = feat_dir / "plan.md"
    plan_file.write_text("- [x] Task 1 (abcdef1)\n", encoding="utf-8")
    plan_file.chmod(0o000)
    try:
        assert revert_task.revert_task("auth", specs_root=specs_root) == 1
    finally:
        plan_file.chmod(0o644)


def test_revert_task_no_revertable_tasks(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    (feat_dir / "plan.md").write_text("# Plan\n- [ ] Task 1\n", encoding="utf-8")
    assert revert_task.revert_task("auth", specs_root=specs_root) == 1


def test_revert_task_target_sha_not_found(tmp_path: Path) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    (feat_dir / "plan.md").write_text(
        "# Plan\n- [x] Task 1 (abcdef1)\n", encoding="utf-8"
    )
    assert (
        revert_task.revert_task("auth", target_sha="9999999", specs_root=specs_root)
        == 1
    )


def test_revert_task_commit_not_in_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    (feat_dir / "plan.md").write_text(
        "# Plan\n- [x] Task 1 (abcdef1)\n", encoding="utf-8"
    )

    import subprocess

    def mock_run_fail(
        cmd: list[str] | str, *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="error")

    monkeypatch.setattr(subprocess, "run", mock_run_fail)
    assert revert_task.revert_task("auth", specs_root=specs_root) == 1


def test_revert_task_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    plan_content = "# Plan\n- [x] Task 1 (abcdef1)\n"
    (feat_dir / "plan.md").write_text(plan_content, encoding="utf-8")

    import subprocess

    def mock_run(
        cmd: list[str], *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            cmd, returncode=0, stdout="abcdef1", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert revert_task.revert_task("auth", specs_root=specs_root, dry_run=True) == 0
    assert (feat_dir / "plan.md").read_text(encoding="utf-8") == plan_content


def test_revert_task_revert_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    (feat_dir / "plan.md").write_text(
        "# Plan\n- [x] Task 1 (abcdef1)\n", encoding="utf-8"
    )

    import subprocess

    def mock_run(
        cmd: list[str], *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        if "rev-parse" in cmd:
            return subprocess.CompletedProcess(
                cmd, returncode=0, stdout="abcdef1", stderr=""
            )
        if "revert" in cmd and "--no-edit" in cmd:
            return subprocess.CompletedProcess(
                cmd, returncode=1, stdout="", stderr="conflict error"
            )
        return subprocess.CompletedProcess(cmd, returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert revert_task.revert_task("auth", specs_root=specs_root) == 1


def test_revert_task_write_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "auth"
    feat_dir.mkdir(parents=True)
    plan_file = feat_dir / "plan.md"
    plan_file.write_text("# Plan\n- [x] Task 1 (abcdef1)\n", encoding="utf-8")

    import subprocess

    def mock_run_ok(
        cmd: list[str] | str, *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run_ok)

    plan_file.chmod(0o444)
    try:
        assert revert_task.revert_task("auth", specs_root=specs_root) == 1
    finally:
        plan_file.chmod(0o644)


def test_revert_task_success(tmp_path: Path) -> None:
    import subprocess

    subprocess.run(
        ["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )

    dummy_file = tmp_path / "hello.txt"
    dummy_file.write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "add", "hello.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "chore: initial"], cwd=tmp_path, check=True)

    dummy_file.write_text("task 1 change\n", encoding="utf-8")
    subprocess.run(["git", "add", "hello.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "feat: task 1"], cwd=tmp_path, check=True)
    sha1 = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=tmp_path, text=True
    ).strip()

    dummy_file.write_text("task 1 change\ntask 2 change\n", encoding="utf-8")
    subprocess.run(["git", "add", "hello.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "feat: task 2"], cwd=tmp_path, check=True)
    sha2 = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=tmp_path, text=True
    ).strip()

    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "feat-x"
    feat_dir.mkdir(parents=True)
    plan_file = feat_dir / "plan.md"
    plan_file.write_text(
        f"# Plan\n\n- [x] **Task 1: Init** ({sha1})\n- [x] **Task 2: Add** ({sha2})\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", str(plan_file)], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "docs(plan): track tasks"], cwd=tmp_path, check=True
    )

    # 1. Revert task 2 by default (last completed task)
    assert (
        revert_task.revert_task("feat-x", specs_root=specs_root, repo_root=tmp_path)
        == 0
    )
    plan_after_2 = plan_file.read_text(encoding="utf-8")
    assert "- [ ] **Task 2: Add**\n" in plan_after_2
    assert f"- [x] **Task 1: Init** ({sha1})" in plan_after_2

    # 2. Revert task 1 by explicit target_sha
    assert (
        revert_task.revert_task(
            "feat-x", target_sha=sha1, specs_root=specs_root, repo_root=tmp_path
        )
        == 0
    )
    plan_after_1 = plan_file.read_text(encoding="utf-8")
    assert "- [ ] **Task 1: Init**\n" in plan_after_1
    assert "- [ ] **Task 2: Add**\n" in plan_after_1


def test_revert_task_main_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specs_root = tmp_path / ".specs"
    feat_dir = specs_root / "feat-cli"
    feat_dir.mkdir(parents=True)
    (feat_dir / "plan.md").write_text(
        "# Plan\n- [x] Task 1 (abcdef1)\n", encoding="utf-8"
    )

    import subprocess

    def mock_run_commit(
        cmd: list[str] | str, *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="abcdef1")

    monkeypatch.setattr(subprocess, "run", mock_run_commit)

    exit_code = revert_task.main(
        [
            "feat-cli",
            "abcdef1",
            "--specs-dir",
            str(specs_root),
            "--dry-run",
        ]
    )
    assert exit_code == 0
