"""Test exact basis-aware complexes and homological constructions.

Owns:
    Exact tests for graded spaces, typed maps, chain and cochain calculations,
    homotopies, cones, shifts, direct sums, and signed bicomplex totalization.

Depends on:
    `onetheory.math.homological`, exact Rational and Eisenstein scalars, and
    pytest for validation and failure assertions.

Must not:
    Introduce sheaves, Čech covers, DGAs, transferred products, physical bundle
    data, numerical approximations, or assumptions about a carrier model.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from onetheory.math.homological import (
    DGA,
    Bicomplex,
    ChainComplex,
    ChainHomotopy,
    ChainMap,
    CochainComplex,
    Contraction,
    CoordinateVector,
    CyclicPairing,
    FiniteComplexAction,
    GradedElement,
    GradedMap,
    GradedProduct,
    GradedVectorSpace,
    HPLTransfer,
    InvariantSubcomplex,
    LinearMap,
    VectorSpace,
    graded_commutator,
    induced_action_on_cohomology,
    mapping_cone,
    tensor_product_space,
)
from onetheory.math.numbers import OMEGA, Eisenstein, Rational


def test_spaces_and_maps_preserve_named_bases_and_are_immutable() -> None:
    domain = VectorSpace("domain", ("x", "y"))
    codomain = VectorSpace("codomain", ("u",))
    map_ = LinearMap(domain, codomain, ((1, 2),))

    assert domain.dimension == 2
    assert map_(CoordinateVector(domain, (3, 4))).coordinates == (Rational(11),)
    assert map_.rank() == 1
    assert map_.kernel_basis()[0].coordinates == (Rational(-2), Rational(1))

    with pytest.raises(FrozenInstanceError):
        domain.name = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError):
        map_(CoordinateVector(VectorSpace("other", ("x", "y")), (3, 4)))
    with pytest.raises(ValueError):
        LinearMap(domain, codomain, ((1,),))


def test_chain_exactness_cycles_boundaries_and_nontrivial_homology() -> None:
    c0 = VectorSpace("C0", ("e0",))
    c1 = VectorSpace("C1", ("e1a", "e1b"))
    c2 = VectorSpace("C2", ("e2",))
    spaces = GradedVectorSpace("C", {0: c0, 1: c1, 2: c2})
    d1 = LinearMap(c1, c0, ((1, 0),))
    d2 = LinearMap(c2, c1, ((0,), (0,)))
    complex_ = ChainComplex(spaces, {1: d1, 2: d2})

    assert complex_.cycles(1)[0].coordinates == (Rational(0), Rational(1))
    assert complex_.boundaries(1) == ()
    assert complex_.cohomology_dimension(1) == 1
    assert complex_.cohomology_representatives(1)[0].coordinates == (
        Rational(0), Rational(1)
    )
    assert complex_.cohomology_dimension(0) == 0

    bad_d2 = LinearMap(c2, c1, ((1,), (0,)))
    with pytest.raises(ValueError, match="squared"):
        ChainComplex(spaces, {1: d1, 2: bad_d2})


def test_cochain_complex_uses_the_opposite_degree_direction() -> None:
    c0 = VectorSpace("C^0", ("e0",))
    c1 = VectorSpace("C^1", ("e1a", "e1b"))
    c2 = VectorSpace("C^2", ("e2",))
    spaces = GradedVectorSpace("C^", {0: c0, 1: c1, 2: c2})
    d0 = LinearMap(c0, c1, ((1,), (0,)))
    d1 = LinearMap(c1, c2, ((0, 1),))
    complex_ = CochainComplex(spaces, {0: d0, 1: d1})

    assert complex_.cycles(1)[0].coordinates == (Rational(1), Rational(0))
    assert complex_.boundaries(1)[0].coordinates == (Rational(1), Rational(0))
    assert complex_.cohomology_dimension(1) == 0


def test_chain_map_and_chain_homotopy_equation() -> None:
    c0 = VectorSpace("C0", ("e0",))
    c1 = VectorSpace("C1", ("e1",))
    complex_ = ChainComplex(
        GradedVectorSpace("C", {0: c0, 1: c1}),
        {1: LinearMap(c1, c0, ((1,),))},
    )
    identity = ChainMap.identity(complex_)
    zero = ChainMap(complex_, complex_, {
        0: LinearMap.zero(c0, c0),
        1: LinearMap.zero(c1, c1),
    })
    homotopy = ChainHomotopy(
        identity,
        zero,
        {0: LinearMap(c0, c1, ((1,),))},
    )

    assert homotopy.component(0).rows == ((Rational(1),),)
    assert identity.compose(identity) == identity
    assert identity.compose(zero) == zero

    with pytest.raises(ValueError, match="homotopy"):
        ChainHomotopy(identity, zero, {})


def test_shift_direct_sum_and_mapping_cone_preserve_exactness() -> None:
    c0 = VectorSpace("C0", ("e0",))
    c1 = VectorSpace("C1", ("e1",))
    complex_ = ChainComplex(
        GradedVectorSpace("C", {0: c0, 1: c1}),
        {1: LinearMap(c1, c0, ((1,),))},
    )
    shifted = complex_.shift(1)
    summed = complex_.direct_sum(complex_)
    cone = mapping_cone(ChainMap.identity(complex_))

    assert shifted.spaces.space(2) == c1
    assert shifted.differential(2).rows == ((Rational(-1),),)
    assert summed.spaces.space(1).dimension == 2
    assert cone.cohomology_dimension(0) == 0
    assert cone.cohomology_dimension(1) == 0


def test_eisenstein_complexes_use_exact_coefficients() -> None:
    e0 = VectorSpace("E0", ("e0",), Eisenstein)
    e1 = VectorSpace("E1", ("e1",), Eisenstein)
    spaces = GradedVectorSpace("E", {0: e0, 1: e1})
    differential = LinearMap(e1, e0, ((OMEGA,),))
    complex_ = ChainComplex(spaces, {1: differential})

    assert complex_.differential(1).rows == ((OMEGA,),)
    assert complex_.cohomology_dimension(0) == 0
    assert complex_.cohomology_dimension(1) == 0


def test_bicomplex_totalization_applies_the_vertical_sign() -> None:
    a = VectorSpace("A", ("a",))
    b = VectorSpace("B", ("b",))
    c = VectorSpace("C", ("c",))
    d = VectorSpace("D", ("d",))
    def one(source: VectorSpace, target: VectorSpace) -> LinearMap:
        return LinearMap(source, target, ((1,),))
    bicomplex = Bicomplex(
        "B",
        {(0, 0): a, (1, 0): b, (0, 1): c, (1, 1): d},
        horizontal={(0, 0): one(a, b), (0, 1): one(c, d)},
        vertical={(0, 0): one(a, c), (1, 0): one(b, d)},
    )
    total = bicomplex.totalize()

    assert total.spaces.space(1).dimension == 2
    assert total.differential(0).rows == ((Rational(1),), (Rational(1),))
    assert total.differential(1).rows == ((Rational(1), Rational(-1)),)
    assert total.differential(1).compose(total.differential(0)).is_zero()


def test_bicomplex_rejects_noncommuting_unsigned_directions() -> None:
    a = VectorSpace("A", ("a",))
    b = VectorSpace("B", ("b",))
    c = VectorSpace("C", ("c",))
    d = VectorSpace("D", ("d",))

    with pytest.raises(ValueError, match="commute"):
        Bicomplex(
            "bad",
            {(0, 0): a, (1, 0): b, (0, 1): c, (1, 1): d},
            horizontal={(0, 0): LinearMap(a, b, ((1,),)),
                        (0, 1): LinearMap(c, d, ((-1,),))},
            vertical={(0, 0): LinearMap(a, c, ((1,),)),
                      (1, 0): LinearMap(b, d, ((1,),))},
        )


def test_dga_leibniz_commutator_pairing_and_maurer_cartan() -> None:
    degree_zero = VectorSpace("A0", ("1",))
    graded = GradedVectorSpace("A", {0: degree_zero})
    differential = GradedMap.zero(graded, graded, 1)
    tensor = tensor_product_space(degree_zero, degree_zero)
    multiplication = GradedProduct(
        graded,
        {(0, 0): LinearMap(tensor, degree_zero, ((1,),))},
    )
    dga = DGA(graded, differential, multiplication)
    one = GradedElement(0, CoordinateVector(degree_zero, (1,)))

    assert dga.multiply(one, one) == one
    assert graded_commutator(multiplication, one, one).vector.is_zero()
    pairing = CyclicPairing(dga, {0: (1,)}, normalized=True)
    assert pairing.is_cyclic()
    assert pairing.is_nondegenerate()
    assert pairing.pair(one, one) == Rational(1)
    assert dga.is_maurer_cartan({0: CoordinateVector(degree_zero, (0,))})


def test_identity_contraction_and_suspended_hpl_are_exact_and_memoized() -> None:
    space = VectorSpace("C0", ("e",))
    graded = GradedVectorSpace("C", {0: space})
    complex_ = CochainComplex(graded, {})
    identity = ChainMap.identity(complex_)
    homotopy = ChainHomotopy(identity, identity, {})
    contraction = Contraction(complex_, complex_, identity, identity, homotopy)
    tensor = tensor_product_space(space, space)
    product = GradedProduct(
        graded,
        {(0, 0): LinearMap(tensor, space, ((1,),))},
    )
    transfer = HPLTransfer(contraction, product)
    element = GradedElement(0, CoordinateVector(space, (1,)))
    result = transfer.evaluate((element, element))

    assert result.result == element
    assert result.f_word_count == 2
    assert result.b_word_count == 1


def test_finite_complex_action_projector_preserves_the_exact_complex() -> None:
    space = VectorSpace("C0", ("e",))
    graded = GradedVectorSpace("C", {0: space})
    complex_ = CochainComplex(graded, {})
    identity = ChainMap.identity(complex_)
    action = FiniteComplexAction(complex_, "1", {"1": identity}, {("1", "1"): "1"})
    invariant = action.character_projector({"1": 1})

    assert invariant.component(0) == LinearMap.identity(space)
    restricted = InvariantSubcomplex(action, {"1": 1})
    assert restricted.complex.spaces.space(0).dimension == 1
    assert len(restricted.cohomology_representatives(0)) == 1
    assert induced_action_on_cohomology(action).matrix("1", 0).rows == ((Rational(1),),)
