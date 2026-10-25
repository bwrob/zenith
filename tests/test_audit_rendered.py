"""Unit tests for scripts/audit_rendered.py.

All external effects (template rendering, subprocess gates, scratch cleanup)
are simulated so that the audit pipeline's branch logic is exercised without
rendering or executing tools.
"""

from __future__ import annotations

import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from scripts import audit_rendered

if TYPE_CHECKING:
    from collections.abc import Generator


@contextmanager
def redirect_render_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Generator[None, None, None]:
    """Point RENDER_ROOT at an isolated temporary directory and stub cleanup.

    Args:
        monkeypatch: Pytest patching hook.
        tmp_path: Pytest temporary directory.

    Yields:
        The redirected render root state, restored on exit.

    """
    monkeypatch.setattr(audit_rendered, "RENDER_ROOT", tmp_path / "rendered-lint")
    rmtree_stub = MagicMock()
    monkeypatch.setattr(audit_rendered.shutil, "rmtree", rmtree_stub)
    yield


def test_single_project_dir_returns_sole_dir(tmp_path: Path) -> None:
    """Verify the sole rendered project directory is selected.

    Args:
        tmp_path: Pytest temporary directory.

    """
    (tmp_path / "demo-app").mkdir()
    assert audit_rendered.single_project_dir(tmp_path) == tmp_path / "demo-app"


def test_single_project_dir_missing_project_raises(tmp_path: Path) -> None:
    """Verify an empty output directory reports a render failure.

    Args:
        tmp_path: Pytest temporary directory.

    """
    with pytest.raises(RuntimeError, match="produced no project directory"):
        audit_rendered.single_project_dir(tmp_path)


def test_find_uv_returns_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify uv resolution reports the discovered executable.

    Args:
        monkeypatch: Pytest patching hook.

    """

    def which_uv(executable: str) -> str:
        _ = executable
        return "/bin/uv"

    monkeypatch.setattr(audit_rendered.shutil, "which", which_uv)
    assert audit_rendered.find_uv() == "/bin/uv"


def test_find_uv_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a missing uv executable fails with a diagnostic.

    Args:
        monkeypatch: Pytest patching hook.

    """

    def missing_which(executable: str) -> None:
        _ = executable

    monkeypatch.setattr(audit_rendered.shutil, "which", missing_which)
    with pytest.raises(RuntimeError, match="uv executable not found"):
        audit_rendered.find_uv()


def test_run_in_dir_clean(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify clean rendered projects produce no failure diagnostics.

    Args:
        monkeypatch: Pytest patching hook.
        tmp_path: Pytest temporary directory standing in for a project root.

    """
    gate_calls: list[tuple[list[str], str]] = []

    def clean_run(
        cmd: list[str], *, cwd: Path, **kwargs: object
    ) -> subprocess.CompletedProcess[bytes]:
        _ = kwargs
        gate_calls.append((cmd, str(cwd)))
        return subprocess.CompletedProcess[bytes](
            cmd, returncode=0, stdout=b"", stderr=b""
        )

    monkeypatch.setattr(audit_rendered.subprocess, "run", clean_run)
    assert audit_rendered.run_in_dir("/bin/uv", tmp_path) == []
    assert [render_cmd for render_cmd, _ in gate_calls] == [
        ["/bin/uv", "run", "ruff", "check", "."],
        ["/bin/uv", "run", "ruff", "format", "--check", "."],
    ]
    assert all(invoked_cwd == str(tmp_path) for _, invoked_cwd in gate_calls)


def test_run_in_dir_reports_failures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify failing gates surface labeled diagnostics in order.

    Args:
        monkeypatch: Pytest patching hook.
        tmp_path: Pytest temporary directory standing in for a project root.

    """
    gate_results = iter(
        [
            subprocess.CompletedProcess[str](
                (), returncode=1, stdout="boom\n", stderr=""
            ),
            subprocess.CompletedProcess[str]((), returncode=1, stdout="", stderr="bad"),
        ]
    )

    def capture_run(
        capture_cmd: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        _ = capture_cmd, kwargs
        return next(gate_results)

    monkeypatch.setattr(audit_rendered.subprocess, "run", capture_run)
    assert audit_rendered.run_in_dir("/bin/uv", tmp_path) == [
        "check: boom",
        "format: bad",
    ]


def test_render_variants_yields_projects(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify every configured variant renders and yields its project root.

    Args:
        monkeypatch: Pytest patching hook.
        tmp_path: Pytest temporary directory.

    """
    with redirect_render_root(monkeypatch, tmp_path):
        rmtree_stub = audit_rendered.shutil.rmtree

        def fake_cookiecutter(
            report_template: str, *_: object, output_dir: str, **kwargs: object
        ) -> str:
            requested = kwargs["extra_context"]
            assert report_template == str(audit_rendered.TEMPLATE_ROOT)
            assert isinstance(requested, dict)
            project_dir = Path(output_dir) / "rendered-project"
            project_dir.mkdir()
            return str(project_dir)

        monkeypatch.setattr(audit_rendered, "cookiecutter", fake_cookiecutter)
        variant_count = len(audit_rendered.VARIANTS)
        for variant_name, _ in audit_rendered.VARIANTS:
            (audit_rendered.RENDER_ROOT / variant_name).mkdir(parents=True)

        with audit_rendered.render_variants() as project_dirs:
            assert [p.name for p in project_dirs] == [
                "rendered-project"
            ] * variant_count
            assert [p.parent.name for p in project_dirs] == [
                "cli-on",
                "cli-off",
                "long-slug",
            ]
        assert isinstance(rmtree_stub, MagicMock)
        assert rmtree_stub.called is True


def test_render_variants_missing_render_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify a render that produces nothing aborts with RuntimeError.

    Args:
        monkeypatch: Pytest patching hook.
        tmp_path: Pytest temporary directory.

    """
    with redirect_render_root(monkeypatch, tmp_path):

        def produce_nothing(*_: object, **__: object) -> str:
            return str(audit_rendered.RENDER_ROOT)

        monkeypatch.setattr(audit_rendered, "cookiecutter", produce_nothing)
        with pytest.raises(RuntimeError, match="produced no project directory"):
            audit_rendered.render_variants().__enter__()  # ruff: ignore[unnecessary-dunder-call]
            # Context manager raises on __enter__ before yielding; body is unreachable.


def test_audit_variants(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify audit_variants iterates over rendered variants and records results.

    Args:
        monkeypatch: Pytest patching hook.
        tmp_path: Pytest temporary directory.

    """
    with redirect_render_root(monkeypatch, tmp_path):
        run_in_dir_mock = MagicMock(side_effect=[[], ["check: fail"], []])
        monkeypatch.setattr(audit_rendered, "run_in_dir", run_in_dir_mock)

        def fake_cookiecutter(*_: object, output_dir: str, **__: object) -> str:
            proj = Path(output_dir) / "app"
            proj.mkdir(parents=True, exist_ok=True)
            return str(proj)

        monkeypatch.setattr(audit_rendered, "cookiecutter", fake_cookiecutter)
        results = audit_rendered.audit_variants("/bin/uv")
        assert len(results) == len(audit_rendered.VARIANTS)


def test_audit_rendered_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a fully clean audit exits with code zero.

    Args:
        monkeypatch: Pytest patching hook.

    """

    def resolved_uv() -> str:
        return "/bin/uv"

    def clean_variants(resolved: str) -> list[tuple[str, list[str]]]:
        _ = resolved
        return [("cli-on", []), ("cli-off", [])]

    monkeypatch.setattr(audit_rendered, "find_uv", resolved_uv)
    monkeypatch.setattr(audit_rendered, "audit_variants", clean_variants)
    assert audit_rendered.audit_rendered() == 0


def test_audit_rendered_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify gate failures exit with code one.

    Args:
        monkeypatch: Pytest patching hook.

    """

    def resolved_uv() -> str:
        return "/bin/uv"

    def failing_variants(resolved: str) -> list[tuple[str, list[str]]]:
        _ = resolved
        return [("cli-on", ["check: boom"]), ("cli-off", [])]

    monkeypatch.setattr(audit_rendered, "find_uv", resolved_uv)
    monkeypatch.setattr(audit_rendered, "audit_variants", failing_variants)
    assert audit_rendered.audit_rendered() == 1


def test_audit_rendered_missing_uv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a missing uv toolchain exits with code one.

    Args:
        monkeypatch: Pytest patching hook.

    """

    def raise_runtime_error() -> str:
        msg = "uv executable not found on PATH"
        raise RuntimeError(msg)

    monkeypatch.setattr(audit_rendered, "find_uv", raise_runtime_error)
    assert audit_rendered.audit_rendered() == 1


def test_audit_rendered_render_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify render failures exit with code one.

    Args:
        monkeypatch: Pytest patching hook.

    """

    def fail_render(resolved_uv: str) -> list[tuple[str, list[str]]]:
        msg = f"disk full near {resolved_uv}"
        raise OSError(msg)

    monkeypatch.setattr(audit_rendered, "find_uv", lambda: "/bin/uv")
    monkeypatch.setattr(audit_rendered, "audit_variants", fail_render)
    assert audit_rendered.audit_rendered() == 1
