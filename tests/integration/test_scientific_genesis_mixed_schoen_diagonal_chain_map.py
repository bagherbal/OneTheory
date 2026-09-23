"""Test the Cech-local common-to-diagonal Koszul chain map.

Owns:
    Regression gates for local multiplier regularity, Koszul wedge targets,
    overlap-homotopy signs, and exact total-degree preservation.

Depends on:
    The certified local pencil comparison and sparse common-Schoen cochains.

Must not:
    Interpret a basis fixture as a physical cocycle, infer a deformation
    residue, omit chart overlap data, or identify fibers by substitution.

Phase 0:
    Integration tests for the first lawful deformation chain-map machinery.
"""

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_diagonal import (
    full_chain_diagonal_differential,
)
from research.experiments.scientific_genesis.mixed_schoen_diagonal_chain_map import (
    diagonal_chain_map_certificate,
    diagonal_compare_common_matter,
    diagonal_comparison_pieces,
    embed_compared_first_factor,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _matter_contraction,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_tensor import (
    IndependentMatterBasis,
    IndependentMatterCochain,
    external_lifted_matter_tensor,
)


def _regular_monomial(degree: int, size: int) -> tuple[int, ...]:
    """Choose one deterministic Laurent monomial of the requested degree."""

    if degree >= 0:
        return (degree, *(0 for _index in range(size - 1)))
    return (degree + size - 1, *(-1 for _index in range(size - 1)))


def _regular_cell(monomial: tuple[int, ...]) -> tuple[int, ...]:
    """Choose the smallest standard-cover cell supporting a Laurent monomial."""

    support = tuple(index for index, exponent in enumerate(monomial) if exponent < 0)
    return support or (0,)


def test_local_koszul_rules_include_the_required_overlap_homotopies() -> None:
    """Both u-containing source wedges receive local maps and signed homotopies."""

    generator = diagonal_comparison_pieces("k1_u")
    top = diagonal_comparison_pieces("k2")
    assert {piece.target_subset for piece in generator} == {(1,), (2,), (1, 2)}
    assert {piece.target_subset for piece in top} == {
        (0, 1),
        (0, 2),
        (0, 1, 2),
    }
    assert (
        next(piece for piece in generator if piece.q_cell == (0, 1)).coefficient
        == Eisenstein(-1)
    )
    assert (
        next(piece for piece in top if piece.q_cell == (0, 1)).coefficient
        == Eisenstein(-1)
    )
    assert diagonal_chain_map_certificate().exact


def test_common_cochain_comparison_preserves_total_degree_and_covers_poles() -> None:
    """A typed u-Koszul basis term maps to regular local diagonal terms."""

    component = OuterCechComponent(0, 0, 0, (0, 3, 1), "k1_u")
    basis = OuterCechBasis(
        component,
        (0, 0, 0),
        (0, 0, 0),
        (0, 0),
        ((0,), (0,), (0,)),
    )
    source = SparseOuterCechCochain(((basis, Eisenstein(1)),))
    result = diagonal_compare_common_matter(source)
    second_factor = diagonal_compare_common_matter(source, 2)
    assert result.total_degree == -1
    assert result.terms
    assert second_factor.factor == 2
    assert tuple(
        (mapped.object_index, mapped.subset, mapped.object_degree,
         mapped.monomials, mapped.cell, coefficient)
        for mapped, coefficient in second_factor.terms
    ) == tuple(
        (mapped.object_index, mapped.subset, mapped.object_degree,
         mapped.monomials, mapped.cell, coefficient)
        for mapped, coefficient in result.terms
    )
    assert all(
        exponent >= 0 or index in mapped.cell[3]
        for mapped, _coefficient in result.terms
        for index, exponent in enumerate(mapped.monomials[3])
    )
    assert {mapped.subset for mapped, _coefficient in result.terms} == {
        (1,),
        (2,),
        (1, 2),
    }
    embedded = embed_compared_first_factor(result)
    assert embedded.terms
    assert all(basis.total_degree == -1 for basis, _coefficient in embedded.terms)


def test_comparison_intertwines_every_common_koszul_summand() -> None:
    """The signed local comparison commutes with the complete raw differential."""

    contraction = _matter_contraction(1)
    for summand in ("k0", "k1_x", "k1_u", "k2"):
        component = contraction.components[(0, 0, summand)]
        x_monomial, u_monomial, p_monomial = (
            _regular_monomial(degree, size)
            for degree, size in zip(
                component.ambient_degree,
                (3, 3, 2),
                strict=True,
            )
        )
        basis = OuterCechBasis(
            component,
            x_monomial,
            u_monomial,
            p_monomial,
            (
                _regular_cell(x_monomial),
                _regular_cell(u_monomial),
                _regular_cell(p_monomial),
            ),
        )
        source = SparseOuterCechCochain(((basis, Eisenstein(1)),))
        source_image = contraction.differential(source)
        compared_source = embed_compared_first_factor(
            diagonal_compare_common_matter(source)
        )
        compared_image = embed_compared_first_factor(
            diagonal_compare_common_matter(source_image)
        )
        assert full_chain_diagonal_differential(compared_source) == compared_image


def test_lifted_tensor_annihilates_repeated_koszul_generators() -> None:
    """Exterior multiplication drops terms sharing the independent equation."""

    component = OuterCechComponent(0, 0, 0, (0, 3, 1), "k1_u")
    common = SparseOuterCechCochain(
        (
            (
                OuterCechBasis(
                    component,
                    (0, 0, 0),
                    (0, 0, 0),
                    (0, 0),
                    ((0,), (0,), (0,)),
                ),
                Eisenstein(1),
            ),
        )
    )
    left = diagonal_compare_common_matter(common)
    right = IndependentMatterCochain(
        2,
        0,
        (
            (
                IndependentMatterBasis(
                    2,
                    0,
                    (1,),
                    0,
                    ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0)),
                    ((0,), (0,), (0,), (0, 1)),
                ),
                Eisenstein(1),
            ),
        ),
    )
    product = external_lifted_matter_tensor(left, right)
    assert product.terms
    assert {
        basis.component.subset for basis, _coefficient in product.terms
    } == {(1, 2)}
