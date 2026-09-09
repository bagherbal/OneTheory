"""Solve exact boundaries in diagonal-Schoen line complexes.

Owns:
    Full-to-reduced HPL projection, strict inclusion, and deterministic exact
    primitives for line-valued Cech--Koszul cocycles.

Depends on:
    The certified diagonal line presentation, its exact Cech contraction, and
    sparse linear preimages over the Eisenstein field.

Must not:
    Assign a bundle determinant map, infer a Higgs lift, choose carrier
    parameters, normalize a trace, or import observational data.

Phase 0:
    Research-only contraction needed by the exterior-square flavor frontier.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein

from .diagonal_schoen_lines import (
    LineDegree4,
    _FullCochain,
    _homotopy,
    _include,
    _perturbation,
    _projection_index,
    _reduced_entries,
    _subtract_degrees,
    diagonal_schoen_line_bundle,
)
from .mixed_schoen_common_dga import _sparse_preimage
from .mixed_schoen_yukawa_trace import scalar_full_differential


def _add(left: _FullCochain, right: _FullCochain) -> _FullCochain:
    """Add two normalized line-valued full cochains exactly."""

    return _FullCochain(left.terms + right.terms)


def _validate_degree(
    cochain: _FullCochain,
    ambient_degrees: LineDegree4,
    total_degree: int,
) -> None:
    """Reject terms outside the declared line and total cochain degree."""

    for basis, _coefficient in cochain.terms:
        if basis.ambient_degrees != _subtract_degrees(
            ambient_degrees,
            basis.subset,
        ):
            raise ValueError("a full cochain occupies the wrong diagonal line")
        cech_degree = sum(len(simplex) - 1 for simplex in basis.cell)
        if cech_degree - len(basis.subset) != total_degree:
            raise ValueError("a full cochain occupies the wrong total degree")


def projected_line_coordinates(
    cochain: _FullCochain,
    ambient_degrees: LineDegree4,
    total_degree: int,
) -> tuple[tuple[tuple[int, Eisenstein], ...], int]:
    """Apply the finite full-to-reduced HPL projection for one line degree."""

    _validate_degree(cochain, ambient_degrees, total_degree)
    entries = _reduced_entries(ambient_degrees, total_degree)
    indices = {(entry.subset, entry.monomials): entry.index for entry in entries}
    values: dict[int, Eisenstein] = {}
    current = cochain
    depth = 0
    while not current.is_zero():
        for basis, coefficient in current.terms:
            index = _projection_index(basis, indices)
            if index is not None:
                values[index] = values.get(index, Eisenstein(0)) + coefficient
        current = _perturbation(_homotopy(current)).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("the diagonal line projection did not terminate")
    return (
        tuple(
            (index, coefficient)
            for index, coefficient in sorted(values.items())
            if not coefficient.is_zero()
        ),
        depth,
    )


def strict_line_inclusion(
    ambient_degrees: LineDegree4,
    total_degree: int,
    coordinates: tuple[tuple[int, Eisenstein], ...],
) -> tuple[_FullCochain, int]:
    """Lift reduced line coordinates through the finite perturbed inclusion."""

    entries = _reduced_entries(ambient_degrees, total_degree)
    current = _FullCochain(
        tuple(
            (basis, coefficient * scalar)
            for index, scalar in coordinates
            for basis, coefficient in _include(entries[index]).terms
        )
    )
    result = _FullCochain()
    depth = 0
    while not current.is_zero():
        result = _add(result, current)
        current = _homotopy(_perturbation(current)).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("the diagonal line inclusion did not terminate")
    return result, depth


def _perturbed_line_homotopy(cochain: _FullCochain) -> tuple[_FullCochain, int]:
    """Apply the finite perturbed Cech homotopy to one full line cochain."""

    result = _FullCochain()
    current = _homotopy(cochain)
    depth = 0
    while not current.is_zero():
        result = _add(result, current)
        current = _homotopy(_perturbation(current)).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("the diagonal line homotopy did not terminate")
    return result, depth


@dataclass(frozen=True, slots=True)
class ExactDiagonalLinePrimitive:
    """One deterministic primitive with exact reconstruction evidence."""

    schoen_degrees: tuple[int, int, int]
    total_degree: int
    cocycle: _FullCochain
    primitive: _FullCochain
    projection_depth: int
    inclusion_depth: int
    homotopy_depth: int
    exact: bool


def exact_diagonal_line_primitive(
    cocycle: _FullCochain,
    schoen_degrees: tuple[int, int, int],
    total_degree: int,
) -> ExactDiagonalLinePrimitive:
    """Solve one exact boundary through the diagonal line contraction."""

    line = diagonal_schoen_line_bundle(*schoen_degrees)
    ambient_degrees = line.ambient_degrees
    _validate_degree(cocycle, ambient_degrees, total_degree)
    if not scalar_full_differential(cocycle).is_zero():
        raise ValueError("a diagonal line primitive requires a cocycle")
    projected, projection_depth = projected_line_coordinates(
        cocycle,
        ambient_degrees,
        total_degree,
    )
    source_coordinates = _sparse_preimage(
        line.differential(total_degree - 1),
        dict(projected),
    )
    lifted, inclusion_depth = strict_line_inclusion(
        ambient_degrees,
        total_degree - 1,
        tuple(sorted(source_coordinates.items())),
    )
    residual = _add(
        cocycle,
        scalar_full_differential(lifted).scale(-1),
    )
    correction, homotopy_depth = _perturbed_line_homotopy(residual)
    primitive = _add(lifted, correction)
    exact = scalar_full_differential(primitive) == cocycle
    if not exact:
        raise ValueError("the diagonal line contraction failed exact reconstruction")
    return ExactDiagonalLinePrimitive(
        schoen_degrees,
        total_degree,
        cocycle,
        primitive,
        projection_depth,
        inclusion_depth,
        homotopy_depth,
        exact,
    )


__all__ = [
    "ExactDiagonalLinePrimitive",
    "exact_diagonal_line_primitive",
    "projected_line_coordinates",
    "strict_line_inclusion",
]
