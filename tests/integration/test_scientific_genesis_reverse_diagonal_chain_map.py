"""Test the asymmetric first-pencil comparison needed by reverse matter.

Owns:
    Exact local pencil identities, regularity, degree routing, and the
    full grouped-chain differential of each common Koszul summand.

Depends on:
    Published Schoen cubics and the research reverse diagonal map.

Must not:
    Infer a Yukawa value, identify independent fibers, or choose a vacuum.

Phase 0:
    Integration gates for the unresolved reverse matter comparison.
"""

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_diagonal import (
    full_chain_diagonal_differential,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _matter_contraction,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_diagonal_chain_map import (
    embed_compared_second_factor,
    reverse_diagonal_compare_common_matter,
    reverse_diagonal_comparison_pieces,
)


def _variable(index: int) -> Polynomial:
    """Select one exact coordinate in the x,p,q comparison ring."""

    return Polynomial.monomial(
        tuple(int(position == index) for position in range(7)),
        scalar_type=Eisenstein,
    )


def _embed_x(polynomial: Polynomial) -> Polynomial:
    """Embed one cubic on the first base factor."""

    return Polynomial(
        (((*exponents, 0, 0, 0, 0), coefficient) for exponents, coefficient in polynomial.terms),
        variable_count=7,
        scalar_type=Eisenstein,
    )


def _regular_monomial(degree: int, size: int) -> tuple[int, ...]:
    """Choose a covered Laurent monomial in an exact multidegree."""

    if degree >= 0:
        return (degree, *(0 for _ in range(size - 1)))
    return (degree + size - 1, *(-1 for _ in range(size - 1)))


def _regular_cell(monomial: tuple[int, ...]) -> tuple[int, ...]:
    """Cover all negative exponents in one standard Čech cell."""

    support = tuple(index for index, exponent in enumerate(monomial) if exponent < 0)
    return support or (0,)


def _source(summand: str, object_index: int = 0) -> SparseOuterCechCochain:
    """Build one regular common-Schoen term without physical interpretation."""

    component = _matter_contraction(2).components[(object_index, 0, summand)]
    x_monomial, u_monomial, q_monomial = (
        _regular_monomial(degree, size)
        for degree, size in zip(component.ambient_degree, (3, 3, 2), strict=True)
    )
    return SparseOuterCechCochain(
        (
            (
                OuterCechBasis(
                    component,
                    x_monomial,
                    u_monomial,
                    q_monomial,
                    (
                        _regular_cell(x_monomial),
                        _regular_cell(u_monomial),
                        _regular_cell(q_monomial),
                    ),
                ),
                Eisenstein(1),
            ),
        )
    )


def test_first_pencil_local_identities_are_exact() -> None:
    """Both p-chart lifts differ by the declared Koszul syzygy."""

    cox = schoen_geometry().cover.cox
    f, g = _embed_x(cox.cubic_f), _embed_x(cox.cubic_g)
    p0, p1, q0, q1 = (_variable(index) for index in range(3, 7))
    first = f * p0 + g * p1
    common = f * q0 + g * q1
    diagonal = p0 * q1 - p1 * q0
    zero = Polynomial.zero(7, scalar_type=Eisenstein)
    assert p0 * common - q0 * first - g * diagonal == zero
    assert p1 * common - q1 * first + f * diagonal == zero
    for summand in ("k0", "k1_x", "k1_u", "k2"):
        assert all(
            piece.regular_on_cell
            for piece in reverse_diagonal_comparison_pieces(summand)
        )


def test_reverse_comparison_preserves_every_common_degree() -> None:
    """The four Koszul summands land in lawful independent multidegrees."""

    expected_subsets = {
        "k0": {()},
        "k1_x": {(0,), (2,), (0, 2)},
        "k1_u": {(1,)},
        "k2": {(0, 1), (1, 2), (0, 1, 2)},
    }
    for summand, expected in expected_subsets.items():
        compared = reverse_diagonal_compare_common_matter(_source(summand))
        assert compared.factor == 2
        assert {basis.subset for basis, _ in compared.terms} == expected


def test_reverse_comparison_intertwines_common_differential() -> None:
    """The local map is a chain map on all four source summands."""

    contraction = _matter_contraction(2)
    for object_index in range(8):
        for summand in ("k0", "k1_x", "k1_u", "k2"):
            source = _source(summand, object_index)
            source_image = contraction.differential(source)
            compared_source = embed_compared_second_factor(
                reverse_diagonal_compare_common_matter(source)
            )
            compared_image = embed_compared_second_factor(
                reverse_diagonal_compare_common_matter(source_image)
            )
            assert (
                full_chain_diagonal_differential(compared_source)
                == compared_image
            ), (object_index, summand)
