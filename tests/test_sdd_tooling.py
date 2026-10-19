"""Unit tests for Spec-Driven Development tooling scripts."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_SPEC = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "workflow-sdd-spec"
    / "scripts"
)
SCRIPTS_REVIEW = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "workflow-sdd-review"
    / "scripts"
)
SCRIPTS_SDD = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "workflow-sdd"
    / "scripts"
)

sys.path.insert(0, str(SCRIPTS_SPEC))
sys.path.insert(0, str(SCRIPTS_REVIEW))
sys.path.insert(0, str(SCRIPTS_SDD))

import archive_feature
import check_spec
import check_traceability

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
        "### Requirement 1: REQ-001\n"
        "- **ID**: `REQ-001`\n"
        "### Scenario 1: Pass\n"
        "### Requirement 2: REQ-002\n"
        "- **ID**: `REQ-002`\n",
        encoding="utf-8",
    )
    reqs = check_traceability.extract_requirements_from_spec(spec_file)
    assert len(reqs) == 2
    assert reqs[0].req_id == "REQ-001"
    assert reqs[1].req_id == "REQ-002"


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
        'def test_req_001_logic(): pass\n\ndef test_custom():\n    """Docstring REQ-002."""\n    pass\n',
        encoding="utf-8",
    )
    mapping = check_traceability.scan_tests_for_requirements(tmp_path)
    assert "REQ-001" in mapping
    assert "REQ-002" in mapping


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
        "# Review\nVerdict: Approved\n", encoding="utf-8"
    )

    exit_code = archive_feature.archive_feature("my-feat", specs_root, docs_root)
    assert exit_code == 0
    assert (docs_root / "my-feat" / "spec.md").exists()
    assert (docs_root / "my-feat" / "plan.md").exists()
    assert (docs_root / "my-feat" / "review.md").exists()
    assert (docs_root / "index.md").exists()
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

    # Bypass with force
    exit_code_force = archive_feature.archive_feature(
        "my-feat", specs_root, docs_root, force=True, keep_temp=True
    )
    assert exit_code_force == 0
    assert feat_dir.exists()


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
