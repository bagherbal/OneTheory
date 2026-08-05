"""Certify local Serre prerequisites for bounded monomial schemes.

Owns:
    Exact two-variable local monomial ideals, complete-intersection tests,
    unit Serre pushout relations, Fitting-ideal local-freeness certificates,
    and the explicit non-lci boundary of the bounded family.

Depends on:
    Exact Eisenstein polynomial arithmetic and the bounded monomial local
    order ideals. It is independent of global dP9 transition data.

Must not:
    Promote a local pushout to a global sheaf, infer a dP9 Ext class, hide a
    non-lci scheme behind a generic extension, or claim quotient descent or a
    physical rank-two constituent.

Phase 0:
    Local complete-intersection and unit-pushout gates are exact; global
    patching, dP9 comparison, linearization, and descent remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal, PolynomialMatrix

from .tier_b_monomial import InvariantMonomialScheme, tier_b_invariant_monomial_schemes

LocalMonomial = tuple[int, int]


def _local_generators(
    standard: tuple[LocalMonomial, ...],
) -> tuple[LocalMonomial, ...]:
    """Return minimal generators of the finite local monomial ideal."""

    selected = set(standard)
    bound = len(standard) + 1
    candidates = tuple(
        exponent
        for exponent in (
            (a, b)
            for a in range(bound + 1)
            for b in range(bound + 1)
        )
        if exponent not in selected
        and all(
            coordinate == 0
            or (
                exponent[0] - (coordinate_index == 0),
                exponent[1] - (coordinate_index == 1),
            )
            in selected
            for coordinate_index, coordinate in enumerate(exponent)
        )
    )
    return candidates


def _local_polynomial(exponent: LocalMonomial) -> Polynomial:
    """Create one exact local monomial over Eisenstein coefficients."""

    return Polynomial.monomial(exponent, scalar_type=Eisenstein)


def _unit_pushout(
    generators: tuple[Polynomial, Polynomial],
) -> tuple[PolynomialMatrix, PolynomialMatrix, PolynomialIdeal, bool, bool]:
    """Construct the exact unit pushout and its Fitting certificate."""

    first, second = generators
    first_monomial = first.terms[0][0]
    second_monomial = second.terms[0][0]
    lcm = tuple(
        max(left, right)
        for left, right in zip(first_monomial, second_monomial, strict=True)
    )
    first_factor = _local_polynomial(
        tuple(common - value for common, value in zip(lcm, first_monomial, strict=True))
    )
    second_factor = _local_polynomial(
        tuple(common - value for common, value in zip(lcm, second_monomial, strict=True))
    )
    syzygy = (-first_factor, second_factor)
    one = Polynomial.one(2, scalar_type=Eisenstein)
    zero = Polynomial.zero(2, scalar_type=Eisenstein)
    relation = PolynomialMatrix(((syzygy[0], syzygy[1], -one),))
    quotient = PolynomialMatrix(((first, second, zero),))
    relation_composes_to_zero = relation.compose(
        PolynomialMatrix(((first,), (second,), (zero,)))
    ).is_zero()
    fitting_ideal = PolynomialIdeal(
        (syzygy[0], syzygy[1], one),
        variable_count=2,
        scalar_type=Eisenstein,
    )
    locally_free = any(
        generator == one or generator == one.scale(-1)
        for generator in fitting_ideal.generators
    )
    return relation, quotient, fitting_ideal, relation_composes_to_zero, locally_free


@dataclass(frozen=True, slots=True)
class LocalMonomialSerreAudit:
    """One exact local complete-intersection and unit-pushout result."""

    scheme: InvariantMonomialScheme
    standard_monomials: tuple[LocalMonomial, ...]
    ideal_generators: tuple[LocalMonomial, ...]
    lci: bool
    relation: PolynomialMatrix | None
    quotient: PolynomialMatrix | None
    fitting_ideal: PolynomialIdeal | None
    relation_composes_to_zero: bool
    locally_free: bool

    @property
    def unit_extension_available(self) -> bool:
        """Return whether the local unit Serre pushout is constructible."""

        return self.lci and self.locally_free and self.relation_composes_to_zero

    def as_record(self) -> dict[str, object]:
        """Serialize local gates without claiming global construction."""

        def matrix_record(matrix: PolynomialMatrix | None) -> object:
            if matrix is None:
                return None
            return [
                [
                    [
                        {
                            "exponents": list(exponents),
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in entry.terms
                    ]
                    for entry in row
                ]
                for row in matrix.rows
            ]

        return {
            "scheme": self.scheme.name,
            "standard_monomials": [list(item) for item in self.standard_monomials],
            "ideal_generators": [list(item) for item in self.ideal_generators],
            "minimal_generator_count": len(self.ideal_generators),
            "lci": self.lci,
            "relation": matrix_record(self.relation),
            "quotient": matrix_record(self.quotient),
            "fitting_ideal": None if self.fitting_ideal is None else self.fitting_ideal.as_record(),
            "relation_composes_to_zero": self.relation_composes_to_zero,
            "locally_free": self.locally_free,
            "unit_extension_available": self.unit_extension_available,
            "status": (
                "exact local Serre gate only; global dP9 patching, linearization, "
                "and quotient descent remain unresolved"
            ),
        }


def local_monomial_serre_audit(
    scheme: InvariantMonomialScheme,
) -> LocalMonomialSerreAudit:
    """Construct the exact local gate for one monomial scheme."""

    standard = scheme.local_standard_monomials
    generators = _local_generators(standard)
    lci = len(generators) == 2
    if not lci:
        return LocalMonomialSerreAudit(
            scheme,
            standard,
            generators,
            False,
            None,
            None,
            None,
            False,
            False,
        )
    polynomials = (_local_polynomial(generators[0]), _local_polynomial(generators[1]))
    relation, quotient, fitting_ideal, relation_zero, local_free = _unit_pushout(polynomials)
    return LocalMonomialSerreAudit(
        scheme,
        standard,
        generators,
        True,
        relation,
        quotient,
        fitting_ideal,
        relation_zero,
        local_free,
    )


def tier_b_local_monomial_serre_audits(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
) -> tuple[LocalMonomialSerreAudit, ...]:
    """Audit local Serre prerequisites for the bounded monomial family."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    return tuple(local_monomial_serre_audit(scheme) for scheme in selected)


__all__ = [
    "LocalMonomialSerreAudit",
    "local_monomial_serre_audit",
    "tier_b_local_monomial_serre_audits",
]
