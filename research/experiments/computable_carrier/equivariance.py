"""Check deck-coordinate equivariance of generated local transition data.

Owns:
    Exact Laurent substitution by Schoen coordinate generators, chart
    permutation, transition invariance checks, and explicit failure records
    when no honest local gauge lift has been constructed.

Depends on:
    Exact Tier A transition candidates, Eisenstein arithmetic, and the
    production Heisenberg coordinate convention.

Must not:
    Insert a guessed gauge transformation, equate kernel-ray actions with
    bundle linearizations, or report descent from a dimension count.

Phase 0:
    The equivariance checker is executable; generated formal transitions remain
    unpromoted until every generator passes with explicit lifts.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import OMEGA, OMEGA2
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .constituents import SerreConstituentCandidate, tier_a_constituents


@dataclass(frozen=True, slots=True)
class GeneratorEquivarianceCheck:
    """One exact coordinate-generator transition check."""

    name: str
    chart_permutation: tuple[int, int, int]
    failed_pairs: tuple[tuple[int, int], ...]
    gauge_lift_constructed: bool

    @property
    def invariant(self) -> bool:
        """Return whether every ordered transition is invariant as written."""

        return not self.failed_pairs

    @property
    def honest(self) -> bool:
        """Return whether invariance has an explicit gauge-lift witness."""

        return self.invariant and self.gauge_lift_constructed


@dataclass(frozen=True, slots=True)
class EquivarianceReport:
    """The complete Tier A coordinate-equivariance boundary report."""

    checks: tuple[GeneratorEquivarianceCheck, ...]
    group_relations_verified: bool
    failed_group_relations: tuple[str, ...]
    status: str

    @property
    def honest(self) -> bool:
        """Return whether every generator has an honest transition lift."""

        return self.group_relations_verified and all(check.honest for check in self.checks)

    def as_record(self) -> dict[str, object]:
        """Return exact failure pairs and the promotion status."""

        return {
            "checks": [
                {
                    "name": check.name,
                    "chart_permutation": list(check.chart_permutation),
                    "failed_pairs": [list(pair) for pair in check.failed_pairs],
                    "invariant": check.invariant,
                    "gauge_lift_constructed": check.gauge_lift_constructed,
                    "honest": check.honest,
                }
                for check in self.checks
            ],
            "group_relations_verified": self.group_relations_verified,
            "failed_group_relations": list(self.failed_group_relations),
            "honest": self.honest,
            "status": self.status,
        }


def _substitute_matrix(
    matrix: LaurentMatrix,
    images: tuple[tuple[object, tuple[int, ...]], ...],
) -> LaurentMatrix:
    """Apply one exact coordinate substitution entrywise."""

    return LaurentMatrix(
        tuple(
            tuple(entry.substitute_monomials(images) for entry in row)
            for row in matrix.rows
        )
    )


def _unipotent(potential):
    """Build the exact local gauge ``I + potential E12``."""

    zero = potential.scale(0)
    one = LaurentPolynomial.one(
        potential.variable_count,
        scalar_type=potential.scalar_type,
    )
    return LaurentMatrix(((one, potential), (zero, one)))


def _unipotent_inverse(potential):
    """Build the exact inverse ``I - potential E12``."""

    zero = potential.scale(0)
    one = LaurentPolynomial.one(
        potential.variable_count,
        scalar_type=potential.scalar_type,
    )
    return LaurentMatrix(((one, -potential), (zero, one)))


def _derived_gauge_lift(
    candidate: SerreConstituentCandidate,
    chart: int,
    images: tuple[tuple[object, tuple[int, ...]], ...],
    permutation: tuple[int, int, int],
) -> LaurentMatrix:
    """Derive the gauge lift forced by the split local potentials."""

    transformed = _substitute_matrix(
        _unipotent(candidate.local_potentials[chart]),
        images,
    )
    target_inverse = _unipotent_inverse(candidate.local_potentials[permutation[chart]])
    return transformed.compose(target_inverse)


def _check_split_generator(
    candidate: SerreConstituentCandidate,
    name: str,
    images: tuple[tuple[object, tuple[int, ...]], ...],
    permutation: tuple[int, int, int],
) -> GeneratorEquivarianceCheck:
    """Check the exact split-derived lift on every transition pair."""

    lifts = tuple(
        _derived_gauge_lift(candidate, chart, images, permutation)
        for chart in range(3)
    )
    lift_inverses = tuple(
        _unipotent(candidate.local_potentials[permutation[chart]]).compose(
            _unipotent_inverse(
                _substitute_matrix(
                    _unipotent(candidate.local_potentials[chart]),
                    images,
                ).rows[0][1]
            )
        )
        for chart in range(3)
    )
    failed = tuple(
        (left, right)
        for left in range(3)
        for right in range(3)
        if left != right
        if _substitute_matrix(candidate._transition(left, right), images)
        != lifts[left].compose(
            candidate._transition(permutation[left], permutation[right])
        ).compose(lift_inverses[right])
    )
    return GeneratorEquivarianceCheck(name, permutation, failed, True)


def _split_group_relation_failures(
    candidate: SerreConstituentCandidate,
    p_images: tuple[tuple[object, tuple[int, ...]], ...],
    t_images: tuple[tuple[object, tuple[int, ...]], ...],
) -> tuple[str, ...]:
    """Check exact P, T, and projective-commutator lift relations."""

    p_permutation = (1, 2, 0)
    t_permutation = (0, 1, 2)
    p_lifts = tuple(
        _derived_gauge_lift(candidate, chart, p_images, p_permutation)
        for chart in range(3)
    )
    t_lifts = tuple(
        _derived_gauge_lift(candidate, chart, t_images, t_permutation)
        for chart in range(3)
    )
    failures: list[str] = []
    p_power = p_lifts
    t_power = t_lifts
    for _ in range(2):
        p_power = tuple(
            _substitute_matrix(p_power[chart], p_images).compose(
                p_lifts[p_permutation[chart]]
            )
            for chart in range(3)
        )
        t_power = tuple(
            _substitute_matrix(t_power[chart], t_images).compose(
                t_lifts[t_permutation[chart]]
            )
            for chart in range(3)
        )
    if not all(matrix.is_identity() for matrix in p_power):
        failures.append("P^3 != identity")
    if not all(matrix.is_identity() for matrix in t_power):
        failures.append("T^3 != identity")
    p_then_t = tuple(
        _substitute_matrix(p_lifts[chart], t_images).compose(
            t_lifts[p_permutation[chart]]
        )
        for chart in range(3)
    )
    t_then_p = tuple(
        _substitute_matrix(t_lifts[chart], p_images).compose(
            p_lifts[t_permutation[chart]]
        )
        for chart in range(3)
    )
    if p_then_t != t_then_p:
        failures.append("PT != TP")
    return tuple(failures)


def _check_generator(
    candidate: SerreConstituentCandidate,
    name: str,
    images: tuple[tuple[object, tuple[int, ...]], ...],
    permutation: tuple[int, int, int],
) -> GeneratorEquivarianceCheck:
    """Check transition invariance without supplying a gauge fallback."""

    failed = tuple(
        (left, right)
        for left in range(3)
        for right in range(3)
        if left != right
        if _substitute_matrix(candidate._transition(left, right), images)
        != candidate._transition(permutation[left], permutation[right])
    )
    return GeneratorEquivarianceCheck(name, permutation, failed, False)


def tier_a_equivariance() -> EquivarianceReport:
    """Run exact P and T checks on both generated Tier A constituents."""

    candidates = tier_a_constituents()
    p_images = ((OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)), (1, (1, 0, 0)))
    t_images = ((1, (1, 0, 0)), (OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)))
    checks = tuple(
        check
        for candidate in candidates
        for check in (
            _check_generator(candidate, f"{candidate.scheme.name}:P", p_images, (1, 2, 0)),
            _check_generator(candidate, f"{candidate.scheme.name}:T", t_images, (0, 1, 2)),
        )
    )
    return EquivarianceReport(
        checks,
        True,
        (),
        "coordinate equivariance checked; no honest gauge lifts constructed",
    )


def tier_a_split_equivariance() -> EquivarianceReport:
    """Check gauge lifts derived from the explicitly split local potentials."""

    candidates = tier_a_constituents()
    p_images = ((OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)), (1, (1, 0, 0)))
    t_images = ((1, (1, 0, 0)), (OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)))
    checks = tuple(
        check
        for candidate in candidates
        for check in (
            _check_split_generator(candidate, f"{candidate.scheme.name}:P", p_images, (1, 2, 0)),
            _check_split_generator(candidate, f"{candidate.scheme.name}:T", t_images, (0, 1, 2)),
        )
    )
    failures = tuple(
        f"{candidate.scheme.name}:{relation}"
        for candidate in candidates
        for relation in _split_group_relation_failures(candidate, p_images, t_images)
    )
    return EquivarianceReport(
        checks,
        not failures,
        failures,
        "split-derived gauge lifts checked; exact group relations remain unresolved",
    )


__all__ = [
    "EquivarianceReport",
    "GeneratorEquivarianceCheck",
    "tier_a_equivariance",
    "tier_a_split_equivariance",
]
