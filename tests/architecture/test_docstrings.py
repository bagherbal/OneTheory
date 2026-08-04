"""Verify the Phase 0 production-module docstring and body contract.

Owns:
    AST checks for customized scope docstrings and the prohibition on implementation
    definitions or placeholder statements in production modules.

Depends on:
    Production source files and Python’s AST and filesystem libraries.

Must not:
    Test scientific correctness or require future APIs that Phase 0 deliberately does
    not expose.

Phase 0:
    Structural test only; no scientific implementation is provided yet.
"""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "src" / "onetheory"
IMPLEMENTED_PRODUCTION_MODULES = {
    "math/numbers.py",
    "math/linear.py",
    "math/polynomials.py",
    "math/finite.py",
    "math/lattices.py",
    "math/geometry.py",
    "math/homological.py",
    "core/errors.py",
    "core/precision.py",
    "physics/gauge.py",
    "physics/matter.py",
    "physics/strings.py",
    "models/standard_model.py",
    "models/heterotic_schoen/geometry.py",
    "models/heterotic_schoen/visible.py",
}


def _production_python_files() -> list[Path]:
    return sorted(PRODUCTION_ROOT.rglob("*.py"))


def test_production_modules_have_scope_docstrings() -> None:
    failures: list[str] = []
    for path in _production_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        docstring = ast.get_docstring(tree, clean=False)
        if not docstring:
            failures.append(f"{path}: missing module docstring")
            continue
        for marker in ("Owns:", "Depends on:", "Must not:", "Phase 0:"):
            if marker not in docstring:
                failures.append(f"{path}: missing {marker}")
    assert not failures, "\n".join(failures)


def test_unimplemented_production_modules_define_no_functions_or_classes() -> None:
    failures: list[str] = []
    for path in _production_python_files():
        if path.relative_to(PRODUCTION_ROOT).as_posix() in IMPLEMENTED_PRODUCTION_MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        definitions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef, ast.Lambda))
        ]
        if definitions:
            failures.append(f"{path}: definitions are not allowed in Phase 0")
    assert not failures, "\n".join(failures)


def test_production_modules_have_no_placeholder_constructs() -> None:
    failures: list[str] = []
    for path in _production_python_files():
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        if any(marker in source for marker in ("TODO", "FIXME", "NotImplementedError")):
            failures.append(f"{path}: forbidden placeholder marker")
        is_implemented = (
            path.relative_to(PRODUCTION_ROOT).as_posix() in IMPLEMENTED_PRODUCTION_MODULES
        )
        if not is_implemented and "..." in source:
            failures.append(f"{path}: ellipsis token")
        if any(isinstance(node, ast.Pass) for node in ast.walk(tree)):
            failures.append(f"{path}: pass statement")
        if not is_implemented and any(
            isinstance(node, ast.Constant) and node.value is Ellipsis for node in ast.walk(tree)
        ):
            failures.append(f"{path}: ellipsis expression")
    assert not failures, "\n".join(failures)
