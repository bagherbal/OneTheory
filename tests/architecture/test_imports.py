"""Verify quiet imports for every Phase 0 production package and module.

Owns:
    Import success, quiet-import, artifact-read, and no-runtime-body checks for the
    empty production scaffold.

Depends on:
    The production source tree, Python import machinery, and standard-library AST
    inspection.

Must not:
    Execute scientific calculations, add import-time registries, or require open
    physical components to exist.

Phase 0:
    Structural test only; no scientific implementation is provided yet.
"""

import ast
import importlib
import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "src" / "onetheory"
IMPLEMENTED_PRODUCTION_MODULES = {"math/numbers.py", "math/linear.py"}


def _module_name(path: Path) -> str:
    relative = path.relative_to(PRODUCTION_ROOT).with_suffix("")
    parts = relative.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(("onetheory", *parts))


def _production_modules() -> list[str]:
    return sorted(_module_name(path) for path in PRODUCTION_ROOT.rglob("*.py"))


def _clear_production_modules() -> None:
    for name in list(sys.modules):
        if name == "onetheory" or name.startswith("onetheory."):
            del sys.modules[name]


def test_package_and_subpackages_import_successfully_and_quietly() -> None:
    _clear_production_modules()
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        for module_name in _production_modules():
            importlib.import_module(module_name)
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""


def test_unimplemented_production_modules_have_no_runtime_definitions() -> None:
    failures: list[str] = []
    for path in sorted(PRODUCTION_ROOT.rglob("*.py")):
        if path.relative_to(PRODUCTION_ROOT).as_posix() in IMPLEMENTED_PRODUCTION_MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
            failures.append(str(path))
    assert not failures, f"Production imports have executable module bodies: {failures}"


def test_production_sources_do_not_read_project_artifacts_at_import_time() -> None:
    forbidden_calls = {"open", "read", "read_bytes", "read_text", "read_texts"}
    failures: list[str] = []
    for path in sorted(PRODUCTION_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id in forbidden_calls:
                failures.append(f"{path}: {node.func.id}")
            if isinstance(node.func, ast.Attribute) and node.func.attr in forbidden_calls:
                failures.append(f"{path}: {node.func.attr}")
    assert not failures, "Import-time artifact reads are forbidden: " + ", ".join(failures)
