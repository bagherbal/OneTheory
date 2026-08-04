"""Verify the required Phase 0 repository layout.

Owns:
    Assertions for required paths, production directory boundaries, directory
    READMEs, and forbidden production filename vocabulary.

Depends on:
    The repository filesystem and Python standard library only.

Must not:
    Implement scientific behavior, create production objects, or treat migration
    artifacts as part of the installable package.

Phase 0:
    Structural test only; no scientific implementation is provided yet.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "src" / "onetheory"

EXPECTED_PRODUCTION_DIRECTORIES = {
    "core",
    "math",
    "physics",
    "models",
    "models/heterotic_schoen",
    "engine",
    "verification",
}

REQUIRED_PATHS = {
    ".gitignore",
    ".editorconfig",
    "README.md",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "src/README.md",
    "src/onetheory/README.md",
    "src/onetheory/__init__.py",
    "src/onetheory/reality.py",
    "src/onetheory/core/README.md",
    "src/onetheory/core/__init__.py",
    "src/onetheory/core/units.py",
    "src/onetheory/core/precision.py",
    "src/onetheory/core/errors.py",
    "src/onetheory/math/README.md",
    "src/onetheory/math/__init__.py",
    "src/onetheory/math/numbers.py",
    "src/onetheory/math/linear.py",
    "src/onetheory/math/polynomials.py",
    "src/onetheory/math/finite.py",
    "src/onetheory/math/lattices.py",
    "src/onetheory/math/geometry.py",
    "src/onetheory/math/homological.py",
    "src/onetheory/physics/README.md",
    "src/onetheory/physics/__init__.py",
    "src/onetheory/physics/spacetime.py",
    "src/onetheory/physics/quantum.py",
    "src/onetheory/physics/fields.py",
    "src/onetheory/physics/gauge.py",
    "src/onetheory/physics/matter.py",
    "src/onetheory/physics/gravity.py",
    "src/onetheory/physics/strings.py",
    "src/onetheory/physics/vacuum.py",
    "src/onetheory/physics/observables.py",
    "src/onetheory/models/README.md",
    "src/onetheory/models/__init__.py",
    "src/onetheory/models/standard_model.py",
    "src/onetheory/models/heterotic_schoen/README.md",
    "src/onetheory/models/heterotic_schoen/__init__.py",
    "src/onetheory/models/heterotic_schoen/geometry.py",
    "src/onetheory/models/heterotic_schoen/visible.py",
    "src/onetheory/models/heterotic_schoen/flavor.py",
    "src/onetheory/models/heterotic_schoen/metrics.py",
    "src/onetheory/models/heterotic_schoen/instantons.py",
    "src/onetheory/models/heterotic_schoen/hidden.py",
    "src/onetheory/models/heterotic_schoen/consistency.py",
    "src/onetheory/models/heterotic_schoen/vacuum.py",
    "src/onetheory/engine/README.md",
    "src/onetheory/engine/__init__.py",
    "src/onetheory/engine/graph.py",
    "src/onetheory/engine/state.py",
    "src/onetheory/engine/solve.py",
    "src/onetheory/engine/simulate.py",
    "src/onetheory/verification/README.md",
    "src/onetheory/verification/__init__.py",
    "src/onetheory/verification/evidence.py",
    "src/onetheory/verification/certificates.py",
    "src/onetheory/verification/gates.py",
    "src/onetheory/verification/audit.py",
    "tests/README.md",
    "tests/architecture/README.md",
    "tests/architecture/test_layout.py",
    "tests/architecture/test_docstrings.py",
    "tests/architecture/test_dependencies.py",
    "tests/architecture/test_imports.py",
    "tests/unit/README.md",
    "tests/scientific/README.md",
    "tests/integration/README.md",
    "research/README.md",
    "research/experiments/README.md",
    "data/README.md",
    "data/published/README.md",
    "data/observations/README.md",
    "data/generated/README.md",
}

FORBIDDEN_PRODUCTION_FILENAME_PARTS = ("section", "chapter", "bridge", "draft", "hypothesis")


def _production_directories() -> set[str]:
    return {
        path.relative_to(PRODUCTION_ROOT).as_posix()
        for path in PRODUCTION_ROOT.rglob("*")
        if path.is_dir() and "__pycache__" not in path.parts
    }


def test_required_paths_exist() -> None:
    missing = [
        relative for relative in sorted(REQUIRED_PATHS) if not (PROJECT_ROOT / relative).exists()
    ]
    assert not missing, f"Missing required paths: {missing}"


def test_production_directory_set_is_exact() -> None:
    actual = _production_directories()
    assert actual == EXPECTED_PRODUCTION_DIRECTORIES


def test_every_created_directory_has_a_readme() -> None:
    ignored_directory_names = {
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
    }
    directories = [PROJECT_ROOT]
    directories.extend(
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_dir()
        and not any(
            part in ignored_directory_names or part.endswith(".egg-info")
            for part in path.relative_to(PROJECT_ROOT).parts
        )
    )
    missing = [
        str(directory) for directory in directories if not (directory / "README.md").is_file()
    ]
    assert not missing, f"Directories without README.md: {missing}"


def test_production_filenames_avoid_document_and_bridge_vocabulary() -> None:
    offending = []
    for path in PRODUCTION_ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.relative_to(PRODUCTION_ROOT).as_posix() == "math/sections.py":
            continue
        lowered = path.name.lower()
        if any(part in lowered for part in FORBIDDEN_PRODUCTION_FILENAME_PARTS):
            offending.append(path.relative_to(PRODUCTION_ROOT).as_posix())
    assert not offending, f"Forbidden production filenames: {offending}"
