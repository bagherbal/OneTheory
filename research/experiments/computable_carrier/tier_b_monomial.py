"""Enumerate invariant monomial point schemes in the Tier B bound.

Owns:
    Exact coordinate-supported monomial ideals obtained by taking the orbit of
    one local monomial order ideal at the three projective coordinate points,
    including their P/T-invariance, irrelevant saturation, local lengths, and
    signed monomial Hilbert--Burch certificates.

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
from onetheory.models.heterotic_schoen.visible import (
    HilbertBurchResolution,
    PointScheme,
)

from .dp9_actions import published_coordinate_images
from .resolution_actions import ResolutionActionPair, _derive_action

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


def _lcm(left: Monomial, right: Monomial) -> Monomial:
    """Return the componentwise least common multiple of two monomials."""

    return tuple(max(a, b) for a, b in zip(left, right, strict=True))


def _spanning_edges(generators: tuple[Monomial, ...]) -> tuple[tuple[int, int, Monomial], ...]:
    """Choose the lowest-degree monomial syzygy tree deterministically."""

    candidates = tuple(
        sorted(
            (
                (sum(_lcm(left, right)), left_index, right_index, _lcm(left, right))
                for left_index, left in enumerate(generators)
                for right_index, right in enumerate(generators[left_index + 1 :], left_index + 1)
            )
        )
    )
    parents = list(range(len(generators)))

    def root(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    selected: list[tuple[int, int, Monomial]] = []
    for _, left_index, right_index, least_common_multiple in candidates:
        left_root = root(left_index)
        right_root = root(right_index)
        if left_root == right_root:
            continue
        parents[left_root] = right_root
        selected.append((left_index, right_index, least_common_multiple))
    if len(selected) != len(generators) - 1:
        raise ValueError("monomial generators did not yield a syzygy tree")
    return tuple(selected)


def _monomial_resolution(
    name: str,
    ideal: PolynomialIdeal,
) -> HilbertBurchResolution:
    """Construct and verify the minimal monomial Hilbert--Burch matrix."""

    generators = ideal.monomials
    zero = Polynomial.zero(ideal.variable_count, scalar_type=Eisenstein)
    columns: list[list[Polynomial]] = []
    syzygy_degrees: list[int] = []
    for left_index, right_index, least_common_multiple in _spanning_edges(generators):
        column = [zero for _ in generators]
        left_factor = tuple(
            common - generator
            for common, generator in zip(
                least_common_multiple,
                generators[left_index],
                strict=True,
            )
        )
        right_factor = tuple(
            common - generator
            for common, generator in zip(
                least_common_multiple,
                generators[right_index],
                strict=True,
            )
        )
        column[left_index] = Polynomial.monomial(left_factor, scalar_type=Eisenstein)
        column[right_index] = -Polynomial.monomial(right_factor, scalar_type=Eisenstein)
        columns.append(column)
        syzygy_degrees.append(sum(least_common_multiple))
    matrix = tuple(
        tuple(column[row] for column in columns)
        for row in range(len(generators))
    )
    numerator = [0] * (max((*map(sum, generators), *syzygy_degrees)) + 1)
    numerator[0] = 1
    for generator in generators:
        numerator[sum(generator)] -= 1
    for degree in syzygy_degrees:
        numerator[degree] += 1
    resolution = HilbertBurchResolution(
        name,
        matrix,
        tuple(
            Polynomial.monomial(generator, scalar_type=Eisenstein)
            for generator in generators
        ),
        tuple(numerator),
    )
    if not resolution.verifies_generators():
        raise ValueError("monomial Hilbert--Burch minors failed exact verification")
    return resolution


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize one exact polynomial without hiding its coefficients."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


@dataclass(frozen=True, slots=True)
class InvariantMonomialScheme:
    """One exact coordinate-supported invariant monomial point scheme."""

    name: str
    local_standard_monomials: tuple[LocalMonomial, ...]
    ideal: PolynomialIdeal
    resolution: HilbertBurchResolution
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
            and self.resolution.verifies_generators()
            and self.resolution.scheme_length == self.length
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
            "hilbert_burch": {
                "matrix": [
                    [_polynomial_record(entry) for entry in row]
                    for row in self.resolution.matrix
                ],
                "hilbert_numerator": list(self.resolution.hilbert_numerator),
                "scheme_length": str(self.resolution.scheme_length),
                "verifies_generators": self.resolution.verifies_generators(),
            },
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


@dataclass(frozen=True, slots=True)
class MonomialResolutionActionAudit:
    """Audit one deterministic deck lift on a monomial resolution."""

    scheme: InvariantMonomialScheme
    actions: ResolutionActionPair

    @property
    def chain_equations(self) -> bool:
        """Return whether both lifted generators satisfy their chain equations."""

        return all(action.chain_equation for action in self.actions.actions)

    @property
    def invertible(self) -> bool:
        """Return whether both free-resolution lifts are invertible."""

        return all(action.invertible for action in self.actions.actions)

    @property
    def order_three(self) -> bool:
        """Return whether both free-resolution lifts have exact order three."""

        return self.actions.order_three

    @property
    def common_projective_commutator(self) -> bool:
        """Return whether the two resolution terms share one commutator scalar."""

        target = self.actions.target_commutator_scalar
        source = self.actions.source_commutator_scalar
        return target is not None and target == source

    @property
    def exact_resolution_gate(self) -> bool:
        """Return the finite resolution-level gate without claiming descent."""

        return self.chain_equations and self.invertible and self.order_three

    def as_record(self) -> dict[str, object]:
        """Serialize the exact lift and its unresolved linearization boundary."""

        return {
            "scheme": self.scheme.name,
            "chain_equations": self.chain_equations,
            "invertible": self.invertible,
            "order_three": self.order_three,
            "target_commutator_scalar": (
                None
                if self.actions.target_commutator_scalar is None
                else str(self.actions.target_commutator_scalar)
            ),
            "source_commutator_scalar": (
                None
                if self.actions.source_commutator_scalar is None
                else str(self.actions.source_commutator_scalar)
            ),
            "common_projective_commutator": self.common_projective_commutator,
            "exact_resolution_gate": self.exact_resolution_gate,
            "actions": self.actions.as_record(),
            "status": (
                "resolution-level deck lift only; common projective commutator, "
                "Serre linearization, and quotient descent remain unresolved"
            ),
        }


def _scheme(standard: tuple[LocalMonomial, ...], index: int) -> InvariantMonomialScheme:
    """Construct and certify one orbit scheme from its local order ideal."""

    monomials = _coordinate_point_orbit(standard)
    ideal = _ideal_from_monomials(monomials)
    resolution = _monomial_resolution(
        f"B-monomial-coordinate-orbit-{index}",
        ideal,
    )
    p_invariant = _invariant_under(ideal, "P")
    t_invariant = _invariant_under(ideal, "T")
    local_lengths = tuple(_local_standard_length(ideal, vertex) for vertex in range(3))
    result = InvariantMonomialScheme(
        f"B-monomial-coordinate-orbit-{index}",
        standard,
        ideal,
        resolution,
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


def tier_b_monomial_resolution_actions(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
) -> tuple[MonomialResolutionActionAudit, ...]:
    """Derive the exact P/T resolution lifts for the bounded monomial family."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    result = []
    for scheme in selected:
        point_scheme = PointScheme(
            scheme.name,
            tuple(scheme.ideal.generators),
            scheme.resolution,
        )
        pair = ResolutionActionPair(
            point_scheme,
            (_derive_action(point_scheme, "P"), _derive_action(point_scheme, "T")),
        )
        audit = MonomialResolutionActionAudit(scheme, pair)
        if not audit.exact_resolution_gate:
            raise ValueError("monomial resolution action failed its exact chain gate")
        result.append(audit)
    return tuple(result)


__all__ = [
    "InvariantMonomialScheme",
    "MonomialResolutionActionAudit",
    "tier_b_invariant_monomial_schemes",
    "tier_b_monomial_resolution_actions",
]
