"""Enumerate invariant monomial point schemes in the Tier B bound.

Owns:
    Exact coordinate-supported monomial ideals obtained by taking the orbit of
    one local monomial order ideal at the three projective coordinate points,
    including their P-invariance, irrelevant saturation, and local lengths.

Depends on:
    Exact Eisenstein polynomial ideals, monomial saturation, and the published
    three-coordinate projective action. It is independent of extension maps.

Must not:
    Treat a monomial ideal record as a Hilbert--Burch resolution, fabricate a
    Serre cocycle, identify the coordinate-supported family with all invariant
    schemes, or infer a physical carrier from its length.

Phase 0:
    The finite coordinate-supported monomial subcategory is enumerated and
    certified exactly; non-monomial orbits, Serre construction, and descent
    remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal, saturate_by_monomial

from .dp9_actions import published_coordinate_images

Monomial = tuple[int, ...]
LocalMonomial = tuple[int, int]


def _minimal_monomials(monomials: tuple[Monomial, ...]) -> tuple[Monomial, ...]:
    """Remove monomials divisible by an earlier generator."""

    unique = tuple(sorted(set(monomials)))
    return tuple(
        candidate
        for candidate in unique
        if not any(
            other != candidate
            and all(left <= right for left, right in zip(other, candidate, strict=True))
            for other in unique
        )
    )


def _local_order_ideals(length: int) -> tuple[tuple[LocalMonomial, ...], ...]:
    """Enumerate all two-variable monomial order ideals of one length."""

    exponents = tuple(product(range(length), repeat=2))
    result = []
    for selected in combinations(exponents, length):
        order_ideal = set(selected)
        if (0, 0) not in order_ideal:
            continue
        if any(
            tuple(
                value - (position == coordinate_index)
                for position, value in enumerate(monomial)
            ) not in order_ideal
            for monomial in order_ideal
            for coordinate_index, coordinate in enumerate(monomial)
            if coordinate > 0
        ):
            continue
        result.append(tuple(sorted(order_ideal)))
    return tuple(result)


def _local_generators(
    standard: tuple[LocalMonomial, ...],
) -> tuple[LocalMonomial, ...]:
    """Return the minimal generators of the local monomial ideal complement."""

    selected = set(standard)
    bound = len(standard) + 1
    candidates = tuple(
        exponent
        for exponent in product(range(bound + 1), repeat=2)
        if exponent not in selected
        and all(
            coordinate == 0
            or tuple(
                value - (position == coordinate_index)
                for position, value in enumerate(exponent)
            ) in selected
            for coordinate_index, coordinate in enumerate(exponent)
        )
    )
    return tuple(sorted(candidates))


def _cyclic(monomial: Monomial) -> Monomial:
    """Apply the coordinate cycle ``a -> b -> c -> a`` to exponents."""

    if len(monomial) != 3:
        raise ValueError("the coordinate cycle requires three exponents")
    return monomial[2], monomial[0], monomial[1]


def _intersection(
    left: tuple[Monomial, ...],
    right: tuple[Monomial, ...],
) -> tuple[Monomial, ...]:
    """Intersect two monomial ideals by exact least common multiples."""

    return _minimal_monomials(
        tuple(
            tuple(max(first, second) for first, second in zip(a, b, strict=True))
            for a in left
            for b in right
        )
    )


def _coordinate_point_orbit(standard: tuple[LocalMonomial, ...]) -> tuple[Monomial, ...]:
    """Construct the saturated ideal of the cyclic coordinate-point orbit."""

    local = _local_generators(standard)
    point_a = tuple((0, exponent[0], exponent[1]) for exponent in local)
    point_b = tuple(_cyclic(monomial) for monomial in point_a)
    point_c = tuple(_cyclic(monomial) for monomial in point_b)
    return _intersection(_intersection(point_a, point_b), point_c)


def _ideal_from_monomials(monomials: tuple[Monomial, ...]) -> PolynomialIdeal:
    """Build one normalized exact monomial ideal."""

    return PolynomialIdeal(
        tuple(Polynomial.monomial(monomial, scalar_type=Eisenstein) for monomial in monomials),
        variable_count=3,
        scalar_type=Eisenstein,
    )


def _local_standard_length(ideal: PolynomialIdeal, vertex: int) -> int:
    """Compute one affine coordinate-chart standard-monomial length."""

    other = tuple(index for index in range(3) if index != vertex)
    projected = tuple(
        tuple(monomial[index] for index in other)
        for monomial in ideal.monomials
    )
    bound = max(sum(monomial) for monomial in projected) + 1
    standard = tuple(
        exponent
        for exponent in product(range(bound + 1), repeat=2)
        if not any(
            all(left <= right for left, right in zip(generator, exponent, strict=True))
            for generator in projected
        )
    )
    if any(max(exponent) == bound for exponent in standard):
        raise ValueError("coordinate chart standard monomial window did not terminate")
    return len(standard)


def _saturated(ideal: PolynomialIdeal) -> bool:
    """Check irrelevant saturation by exact coordinate-variable saturation."""

    saturated = saturate_by_monomial(ideal, (1, 0, 0)).monomials
    for variable in (1, 2):
        current = saturate_by_monomial(
            ideal,
            tuple(1 if index == variable else 0 for index in range(3)),
        ).monomials
        saturated = _intersection(saturated, current)
    return saturated == ideal.monomials


def _invariant_under(ideal: PolynomialIdeal, name: str) -> bool:
    """Check monomial-ideal invariance under one published deck lift."""

    images = published_coordinate_images(name)
    transformed = tuple(
        sorted(
            generator.substitute_monomials(images).terms[0][0]
            for generator in ideal.generators
        )
    )
    return transformed == tuple(sorted(ideal.monomials))


@dataclass(frozen=True, slots=True)
class InvariantMonomialScheme:
    """One exact coordinate-supported invariant monomial point scheme."""

    name: str
    local_standard_monomials: tuple[LocalMonomial, ...]
    ideal: PolynomialIdeal
    local_lengths: tuple[int, int, int]
    p_invariant: bool
    t_invariant: bool
    irrelevant_saturated: bool

    @property
    def length(self) -> int:
        """Return the exact projective length from the three affine charts."""

        return sum(self.local_lengths)

    @property
    def exact(self) -> bool:
        """Return the complete monomial ideal certificate."""

        return (
            self.length == 3 * len(self.local_standard_monomials)
            and self.local_lengths == (len(self.local_standard_monomials),) * 3
            and self.p_invariant
            and self.t_invariant
            and self.irrelevant_saturated
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact ideal and finite invariant-scheme gates."""

        return {
            "name": self.name,
            "local_standard_monomials": [list(item) for item in self.local_standard_monomials],
            "length": self.length,
            "ideal": self.ideal.as_record(),
            "local_lengths": list(self.local_lengths),
            "p_invariant": self.p_invariant,
            "t_invariant": self.t_invariant,
            "irrelevant_saturated": self.irrelevant_saturated,
            "exact": self.exact,
            "status": (
                "exact coordinate-supported monomial scheme; Hilbert--Burch, "
                "Serre extension, and quotient descent remain unresolved"
            ),
        }


def _scheme(standard: tuple[LocalMonomial, ...], index: int) -> InvariantMonomialScheme:
    """Construct and certify one orbit scheme from its local order ideal."""

    monomials = _coordinate_point_orbit(standard)
    ideal = _ideal_from_monomials(monomials)
    p_invariant = _invariant_under(ideal, "P")
    t_invariant = _invariant_under(ideal, "T")
    local_lengths = tuple(_local_standard_length(ideal, vertex) for vertex in range(3))
    result = InvariantMonomialScheme(
        f"B-monomial-coordinate-orbit-{index}",
        standard,
        ideal,
        local_lengths,
        p_invariant,
        t_invariant,
        _saturated(ideal),
    )
    if not result.exact:
        raise ValueError("constructed invariant monomial scheme failed exact gates")
    return result


def tier_b_invariant_monomial_schemes(
    maximum_length: int = 9,
) -> tuple[InvariantMonomialScheme, ...]:
    """Enumerate all coordinate-supported local order ideals within the bound."""

    if isinstance(maximum_length, bool) or not isinstance(maximum_length, int):
        raise TypeError("maximum point length must be an integer")
    if maximum_length < 1:
        raise ValueError("maximum point length must be positive")
    standards = tuple(
        standard
        for length in range(1, maximum_length // 3 + 1)
        for standard in _local_order_ideals(length)
    )
    return tuple(_scheme(standard, index) for index, standard in enumerate(standards))


__all__ = ["InvariantMonomialScheme", "tier_b_invariant_monomial_schemes"]
