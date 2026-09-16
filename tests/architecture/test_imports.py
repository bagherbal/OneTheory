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
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "src" / "onetheory"
IMPLEMENTED_PRODUCTION_MODULES = {
    "math/numbers.py",
    "math/linear.py",
    "math/polynomials.py",
    "math/cech.py",
    "math/sheaves.py",
    "math/finite.py",
    "math/lattices.py",
    "math/geometry.py",
    "math/homological.py",
    "math/sections.py",
    "core/errors.py",
    "core/precision.py",
    "core/units.py",
    "physics/spacetime.py",
    "physics/fields.py",
    "physics/gauge.py",
    "physics/matter.py",
    "physics/quantum.py",
    "physics/gravity.py",
    "physics/strings.py",
    "physics/compactification.py",
    "physics/vacuum.py",
    "physics/observables.py",
    "models/standard_model.py",
    "models/heterotic_schoen/geometry.py",
    "models/heterotic_schoen/visible.py",
    "models/heterotic_schoen/flavor.py",
    "models/heterotic_schoen/consistency.py",
    "models/heterotic_schoen/instantons.py",
    "models/heterotic_schoen/hidden.py",
    "models/heterotic_schoen/metrics.py",
    "models/heterotic_schoen/effective.py",
    "models/heterotic_schoen/vacuum.py",
    "engine/graph.py",
    "engine/solve.py",
    "engine/state.py",
    "engine/simulate.py",
    "reality.py",
    "verification/evidence.py",
    "verification/certificates.py",
    "verification/gates.py",
    "verification/audit.py",
}


def _module_name(path: Path) -> str:
    relative = path.relative_to(PRODUCTION_ROOT).with_suffix("")
    parts = relative.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(("onetheory", *parts))


def _production_modules() -> list[str]:
    return sorted(_module_name(path) for path in PRODUCTION_ROOT.rglob("*.py"))


def test_package_and_subpackages_import_successfully_and_quietly() -> None:
    existing = {
        name: module
        for name, module in sys.modules.items()
        if name == "onetheory" or name.startswith("onetheory.")
    }
    script = (
        "import importlib\n"
        f"modules = {_production_modules()!r}\n"
        "for module_name in modules:\n"
        "    importlib.import_module(module_name)\n"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == ""
    assert completed.stderr == ""
    assert all(sys.modules.get(name) is module for name, module in existing.items())


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
