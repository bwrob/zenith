"""Unit tests for check_public_api.py in workflow-sdd-review."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "workflow-sdd-review"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIR))

import check_public_api


def test_detect_package_name_from_src(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    pkg_dir = src_dir / "my_pkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    assert check_public_api.detect_package_name(tmp_path) == "my_pkg"


def test_detect_package_name_from_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo-lib"\n', encoding="utf-8")

    assert check_public_api.detect_package_name(tmp_path) == "demo_lib"


def test_detect_package_name_none(tmp_path: Path) -> None:
    assert check_public_api.detect_package_name(tmp_path) is None


def test_get_default_base_ref_success() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert check_public_api.get_default_base_ref() == "origin/main"


def test_get_default_base_ref_fallback() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)
        assert check_public_api.get_default_base_ref() == "HEAD"


def test_run_griffe_check_file_not_found() -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError):
        ok, breaking = check_public_api.run_griffe_check("pkg", "main")
        assert not ok
        assert "uv executable not found" in breaking[0]


def test_run_griffe_check_not_installed() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=127, stdout="", stderr="command not found"
        )
        ok, breaking = check_public_api.run_griffe_check("pkg", "main")
        assert not ok
        assert breaking == []


def test_run_griffe_check_breaking_changes() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="INFO: starting\nParameter 'x' was removed\nINFO: done",
            stderr="",
        )
        ok, breaking = check_public_api.run_griffe_check("pkg", "main")
        assert ok
        assert breaking == ["Parameter 'x' was removed"]


def test_run_griffe_check_success() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        ok, breaking = check_public_api.run_griffe_check("pkg", "main")
        assert ok
        assert breaking == []


def test_extract_public_symbols_syntax_error() -> None:
    assert check_public_api.extract_public_symbols_from_ast("def invalid(") == []


def test_extract_public_symbols_explicit_all() -> None:
    code = '__all__ = ["Alpha", "Beta"]\nGamma = 1\n'
    symbols = check_public_api.extract_public_symbols_from_ast(code)
    assert symbols == ["Alpha", "Beta"]


def test_extract_public_symbols_fallback() -> None:
    code = (
        "class PublicClass:\n"
        "    pass\n"
        "class _PrivateClass:\n"
        "    pass\n"
        "def public_func():\n"
        "    pass\n"
        "async def async_func():\n"
        "    pass\n"
        "def _private_func():\n"
        "    pass\n"
    )
    symbols = check_public_api.extract_public_symbols_from_ast(code)
    assert symbols == ["PublicClass", "async_func", "public_func"]


def test_get_package_public_symbols(tmp_path: Path) -> None:
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text('__all__ = ["InitSymbol"]\n', encoding="utf-8")
    symbols = check_public_api.get_package_public_symbols(pkg_dir)
    assert symbols == ["InitSymbol"]


def test_get_package_public_symbols_fallback_modules(tmp_path: Path) -> None:
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    (pkg_dir / "mod.py").write_text("def module_func(): pass\n", encoding="utf-8")
    (pkg_dir / "_private.py").write_text("def ignored(): pass\n", encoding="utf-8")
    symbols = check_public_api.get_package_public_symbols(pkg_dir)
    assert symbols == ["module_func"]


def test_get_git_file_content() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="content")
        assert check_public_api.get_git_file_content("main", "file.py") == "content"

        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert check_public_api.get_git_file_content("main", "file.py") is None


def test_get_base_public_symbols_from_init() -> None:
    with patch("check_public_api.get_git_file_content") as mock_get:
        mock_get.return_value = '__all__ = ["BaseSymbol"]\n'
        symbols = check_public_api.get_base_public_symbols("main", "pkg")
        assert symbols == ["BaseSymbol"]


def test_get_base_public_symbols_from_tree() -> None:
    with (
        patch("check_public_api.get_git_file_content") as mock_get,
        patch("subprocess.run") as mock_run,
    ):
        mock_get.side_effect = [None, "def tree_func(): pass\n"]
        mock_run.return_value = MagicMock(returncode=0, stdout="src/pkg/tree.py\n")
        symbols = check_public_api.get_base_public_symbols("main", "pkg")
        assert symbols == ["tree_func"]


def test_get_base_public_symbols_ls_tree_failed() -> None:
    with (
        patch("check_public_api.get_git_file_content", return_value=None),
        patch("subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=1)
        assert check_public_api.get_base_public_symbols("main", "pkg") == []


def test_extract_planned_symbols(tmp_path: Path) -> None:
    assert check_public_api.extract_planned_symbols(tmp_path / "nonexistent.md") == []

    plan_file = tmp_path / "plan.md"
    plan_file.write_text(
        "# Plan\n"
        "```python\n"
        "class PlannedClass:\n"
        "    pass\n"
        "class _IgnoredClass:\n"
        "    pass\n"
        "def planned_func():\n"
        "    pass\n"
        "```\n",
        encoding="utf-8",
    )
    symbols = check_public_api.extract_planned_symbols(plan_file)
    assert symbols == ["PlannedClass", "planned_func"]


def test_analyze_public_api(tmp_path: Path) -> None:
    src_dir = tmp_path / "src" / "demo"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text(
        '__all__ = ["SymbolA", "SymbolB"]\n', encoding="utf-8"
    )

    plan_path = tmp_path / "plan.md"
    plan_path.write_text(
        "class SymbolA:\n    pass\nclass SymbolC:\n    pass\n", encoding="utf-8"
    )

    with (
        patch("check_public_api.get_base_public_symbols", return_value=["SymbolA"]),
        patch("check_public_api.run_griffe_check", return_value=(True, [])),
    ):
        result = check_public_api.analyze_public_api(
            tmp_path, "demo", "main", plan_path=plan_path
        )

        assert result.package_name == "demo"
        assert result.added_symbols == ["SymbolB"]
        assert result.unplanned_symbols == ["SymbolB"]
        assert result.missing_planned_symbols == ["SymbolC"]


def test_format_report_and_main(tmp_path: Path) -> None:
    res = check_public_api.ApiDiffResult(
        package_name="demo",
        base_ref="origin/main",
        griffe_available=True,
        breaking_changes=["Breaking signature change"],
        current_public_symbols=["A", "B"],
        base_public_symbols=["A", "C"],
        added_symbols=["B"],
        removed_symbols=["C"],
        planned_symbols=["A"],
        unplanned_symbols=["B"],
        missing_planned_symbols=[],
    )
    report = check_public_api.format_report(res)
    assert "Breaking signature change" in report
    assert "Unplanned Public Symbols" in report
    assert "Removed Public Symbols" in report

    out_file = tmp_path / "report.md"
    with patch("check_public_api.analyze_public_api", return_value=res):
        exit_code = check_public_api.main(
            ["--package", "demo", "--output", str(out_file)]
        )
        assert exit_code == 1
        assert out_file.exists()


def test_main_package_not_detected(tmp_path: Path) -> None:
    with patch("check_public_api.detect_package_name", return_value=None):
        exit_code = check_public_api.main(["--package", ""])
        assert exit_code == 1


def test_main_clean_exit() -> None:
    res = check_public_api.ApiDiffResult(
        package_name="demo",
        base_ref="main",
        griffe_available=True,
        breaking_changes=[],
        current_public_symbols=["A"],
        base_public_symbols=["A"],
        added_symbols=[],
        removed_symbols=[],
        planned_symbols=["A"],
        unplanned_symbols=[],
        missing_planned_symbols=[],
    )
    with patch("check_public_api.analyze_public_api", return_value=res):
        exit_code = check_public_api.main(["--package", "demo"])
        assert exit_code == 0
