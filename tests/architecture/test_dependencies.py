"""Enforce the one-way OneTheory production dependency law.

Owns:
    AST import resolution, forbidden layer checks, production-to-research checks, and
    circular-import detection across every production module.

Depends on:
    Production source files and Python’s AST and graph-inspection libraries.

Must not:
    Import or execute scientific implementations while checking architectural edges.

Phase 0:
    Structural test only; no scientific implementation is provided yet.
"""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "src" / "onetheory"

FORBIDDEN_LAYERS = {
    "root": {"core", "math", "physics", "models", "engine", "reality", "verification", "research"},
    "core": {"math", "physics", "models", "engine", "reality", "verification", "research"},
    "math": {"physics", "models", "engine", "reality", "verification", "research"},
    "physics": {"models", "engine", "reality", "verification", "research"},
    "models": {"engine", "reality", "verification", "research"},
    "engine": {"models", "reality", "verification", "research"},
    "reality": {"verification", "research"},
    "verification": {"research"},
}


def _module_name(path: Path) -> str:
    relative = path.relative_to(PRODUCTION_ROOT).with_suffix("")
    parts = relative.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(("onetheory", *parts))


def _layer(name: str) -> str | None:
    parts = name.split(".")
    if parts == ["onetheory"]:
        return "root"
    if len(parts) < 2 or parts[0] != "onetheory":
        return None
    return parts[1]


def _resolved_imports(path: Path, tree: ast.AST) -> set[str]:
    current_parts = _module_name(path).split(".")
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = current_parts[:-node.level]
            else:
                base = []
            module_parts = node.module.split(".") if node.module else []
            imported_module = ".".join((*base, *module_parts))
            if imported_module:
                imports.add(imported_module)
            for alias in node.names:
                if node.module is None or imported_module == "onetheory":
                    imports.add(".".join((*base, alias.name)))
                elif imported_module.startswith("onetheory"):
                    imports.add(f"{imported_module}.{alias.name}")
    return imports


def _production_import_graph() -> tuple[dict[str, set[str]], list[str]]:
    graph: dict[str, set[str]] = {}
    violations: list[str] = []
    paths = sorted(PRODUCTION_ROOT.rglob("*.py"))
    known_modules = {_module_name(path) for path in paths}
    for path in paths:
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        graph[module] = set()
        source_layer = _layer(module)
        assert source_layer is not None
        for imported in _resolved_imports(path, tree):
            if imported == "research" or imported.startswith("research."):
                violations.append(f"{module} imports research via {imported}")
            if imported == "tests" or imported.startswith("tests."):
                violations.append(f"{module} imports tests via {imported}")
            imported_layer = _layer(imported)
            if imported_layer in {"research", "tests"}:
                violations.append(f"{module} imports forbidden external layer via {imported}")
            if imported_layer in FORBIDDEN_LAYERS[source_layer]:
                violations.append(
                    f"{module} imports forbidden layer {imported_layer} via {imported}"
                )
            if imported in known_modules:
                graph[module].add(imported)
    return graph, violations


def _cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    visiting: set[str] = set()
    visited: set[str] = set()
    found: list[list[str]] = []
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visiting:
            start = stack.index(node)
            found.append([*stack[start:], node])
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for child in sorted(graph[node]):
            visit(child)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return found


def test_production_imports_follow_layer_direction() -> None:
    _, violations = _production_import_graph()
    assert not violations, "\n".join(violations)


def test_production_import_graph_has_no_cycles() -> None:
    graph, violations = _production_import_graph()
    assert not violations, "\n".join(violations)
    cycles = _cycles(graph)
    assert not cycles, f"Circular production imports: {cycles}"
