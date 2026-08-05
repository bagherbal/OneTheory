"""Enumerate all locally free presentation-level Serre eigenrays.

Owns:
    Exact I3 and I6 eigenclass enumeration in the derived finite
    Hilbert--Burch presentations, support-local Fitting filtering, and the
    scoped monomial resolution-lift compatibility audit for every surviving
    ray.

Depends on:
    The exact point schemes, derived resolution actions, polynomial pushout
    relations, and the finite presentation-action search. It does not import
    observations or the published carrier’s cocycle data.

Must not:
    Call a finite dual eigenline a sheaf Ext representative, infer global
    dP9 descent, claim completeness beyond the declared presentation family,
    or select a ray using phenomenological data.

Phase 0:
    Every locally free ray in the declared finite presentation diagnostic is
    serialized; full sheaf comparison and quotient promotion remain open.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes

from .dual_cokernels import (
    _target_action,
    dual_resolution_cokernel,
)
from .pushout_linearization import _alternative_variant_counts
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions
from .serre_pushout import (
    CHARACTERS,
    SerrePushoutCandidate,
    _constant,
    _full_dual_vector,
    _local_fitting_data,
    _polynomial_from_basis,
    _relation_matrix,
    _row_vector,
    _stacked_equations,
    tier_a_serre_pushouts,
)


def _polynomial_record(polynomial: Polynomial) -> dict[str, object]:
    """Serialize one exact eigenclass component."""

    return {
        "terms": [
            {
                "exponents": list(exponents),
                "coefficient": str(coefficient),
            }
            for exponents, coefficient in polynomial.terms
        ]
    }


@dataclass(frozen=True, slots=True)
class SerreEigenclassVariant:
    """One locally free eigenray and its finite action compatibility result."""

    scheme: str
    character_pair: tuple[Eisenstein, Eisenstein]
    extension_map: tuple[Polynomial, ...]
    local_fitting: tuple[tuple[str, bool, tuple[int, ...]], ...]
    compatible_variant_counts: tuple[int, int]
    complete_variant_pair_count: int

    @property
    def locally_free_at_support(self) -> bool:
        """Return whether every declared support point has a unit minor."""

        return all(unit for _, unit, _ in self.local_fitting)

    def as_record(self) -> dict[str, object]:
        """Serialize the ray without assigning it a sheaf-level meaning."""

        return {
            "scheme": self.scheme,
            "character_pair": [str(value) for value in self.character_pair],
            "extension_map": [
                _polynomial_record(polynomial)
                for polynomial in self.extension_map
            ],
            "local_fitting": [
                {
                    "point": point,
                    "unit_minor_exists": unit,
                    "unit_minor_indices": list(indices),
                }
                for point, unit, indices in self.local_fitting
            ],
            "locally_free_at_support": self.locally_free_at_support,
            "compatible_variant_counts": list(self.compatible_variant_counts),
            "complete_variant_pair_count": self.complete_variant_pair_count,
            "status": (
                "finite presentation eigenray; sheaf Ext comparison and "
                "quotient descent remain unresolved"
            ),
        }


def _i3_variants(
    scheme: PointScheme,
    pair: ResolutionActionPair,
) -> tuple[tuple[tuple[Polynomial, ...], tuple[Eisenstein, Eisenstein]], ...]:
    """Enumerate all constant I3 eigenclasses passing support freeness."""

    actions = tuple(action.source_action.transpose() for action in pair.actions)
    variants = []
    for p_value in CHARACTERS:
        for t_value in CHARACTERS:
            equations = _stacked_equations(actions[0], actions[1], p_value, t_value)
            for vector in equations.nullspace():
                extension_map = tuple(_constant(value) for value in vector.values)
                relation = _relation_matrix(scheme, extension_map)
                if all(item[1] for item in _local_fitting_data(relation)):
                    variants.append((extension_map, (p_value, t_value)))
    return tuple(variants)


def _i6_variants(
    scheme: PointScheme,
    pair: ResolutionActionPair,
) -> tuple[tuple[tuple[Polynomial, ...], tuple[Eisenstein, Eisenstein]], ...]:
    """Enumerate all I6 quotient eigenclasses passing full checks."""

    cokernel = dual_resolution_cokernel(scheme, pair.actions)
    full_actions = tuple(
        _target_action(cokernel.target_basis, action)
        for action in pair.actions
    )
    variants = []
    for p_value in CHARACTERS:
        for t_value in CHARACTERS:
            equations = _stacked_equations(
                cokernel.action("P").matrix,
                cokernel.action("T").matrix,
                p_value,
                t_value,
            )
            for vector in equations.nullspace():
                values = _full_dual_vector(cokernel, vector.values)
                row = _row_vector(values)
                if not all(
                    action @ row == row.scale(character)
                    for action, character in zip(
                        full_actions,
                        (p_value, t_value),
                        strict=True,
                    )
                ):
                    continue
                extension_map = tuple(
                    _polynomial_from_basis(cokernel.target_basis, values, column)
                    for column in range(3)
                )
                relation = _relation_matrix(scheme, extension_map)
                if all(item[1] for item in _local_fitting_data(relation)):
                    variants.append((extension_map, (p_value, t_value)))
    return tuple(variants)


def _one_scheme_variants(
    candidate: SerrePushoutCandidate,
    pair: ResolutionActionPair,
) -> tuple[SerreEigenclassVariant, ...]:
    """Build the exact finite audit records for one point scheme."""

    raw = (
        _i3_variants(candidate.scheme, pair)
        if candidate.scheme.name == "I3"
        else _i6_variants(candidate.scheme, pair)
    )
    records = []
    for extension_map, character_pair in raw:
        relation = _relation_matrix(candidate.scheme, extension_map)
        altered = replace(
            candidate,
            extension_map=extension_map,
            character_pair=character_pair,
            relation=relation,
        )
        local_fitting = _local_fitting_data(relation)
        _, _, compatible, complete = _alternative_variant_counts(altered)
        records.append(
            SerreEigenclassVariant(
                candidate.scheme.name,
                character_pair,
                extension_map,
                local_fitting,
                compatible,
                complete,
            )
        )
    return tuple(records)


def tier_a_serre_eigenclass_variants(
    candidates: tuple[SerrePushoutCandidate, ...] | None = None,
    actions: tuple[ResolutionActionPair, ...] | None = None,
) -> tuple[SerreEigenclassVariant, ...]:
    """Enumerate all locally free I3/I6 finite presentation eigenrays."""

    selected = tier_a_serre_pushouts() if candidates is None else candidates
    resolution_actions = tier_a_resolution_actions() if actions is None else actions
    schemes = tuple(candidate.scheme for candidate in selected)
    if schemes != point_schemes():
        raise ValueError("Tier A eigenray audits require I3 and I6 in order")
    return tuple(
        variant
        for candidate, pair in zip(selected, resolution_actions, strict=True)
        for variant in _one_scheme_variants(candidate, pair)
    )


__all__ = [
    "SerreEigenclassVariant",
    "tier_a_serre_eigenclass_variants",
]
