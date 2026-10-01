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
    _coordinate_in_basis,
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


def test_exact_coordinate_recovery_uses_full_basis_rref() -> None:
    """Independent exact coordinates remain recoverable in a wide basis."""

    space = VectorSpace("wide", ("x", "y", "z"), Eisenstein)
    first = CoordinateVector(space, (1, 0, 1))
    second = CoordinateVector(space, (0, 1, 1))
    vector = CoordinateVector(space, (2, 3, 5))
    assert _coordinate_in_basis((first, second), vector) == (
        Eisenstein(2),
        Eisenstein(3),
    )


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


def test_cochain_mapping_cone_of_identity_is_acyclic_over_eisenstein() -> None:
    degree_zero = VectorSpace("E^0", ("a",), Eisenstein)
    degree_one = VectorSpace("E^1", ("b",), Eisenstein)
    complex_ = CochainComplex(
        GradedVectorSpace("E", {0: degree_zero, 1: degree_one}),
        {0: LinearMap(degree_zero, degree_one, ((OMEGA,),))},
    )
    cone = mapping_cone(ChainMap.identity(complex_))

    assert isinstance(cone, CochainComplex)
    assert cone.differential(-1).compose(cone.differential(-2)).is_zero()
    assert cone.differential(0).compose(cone.differential(-1)).is_zero()
    assert all(cone.cohomology_dimension(degree) == 0 for degree in cone.degrees)
    assert all(
        isinstance(value, Eisenstein)
        for _, differential in cone.differentials
        for row in differential.rows
        for value in row
    )


def test_cochain_homotopy_respects_shifted_degree_and_exact_equation() -> None:
    degree_zero = VectorSpace("C^0", ("a",))
    degree_one = VectorSpace("C^1", ("b",))
    complex_ = CochainComplex(
        GradedVectorSpace("C", {0: degree_zero, 1: degree_one}),
        {0: LinearMap(degree_zero, degree_one, ((1,),))},
    )
    identity = ChainMap.identity(complex_)
    zero = ChainMap(complex_, complex_, {})
    homotopy = ChainHomotopy(
        identity, zero, {1: LinearMap(degree_one, degree_zero, ((1,),))}
    )

    assert homotopy.component(1).rows == ((Rational(1),),)
    with pytest.raises(ValueError, match="shifted codomain"):
        ChainHomotopy(identity, zero, {1: LinearMap(degree_one, degree_one, ((1,),))})


def test_complex_and_chain_map_reject_incompatible_named_bases() -> None:
    first = VectorSpace("first", ("x",))
    other = VectorSpace("other", ("x",))
    target = VectorSpace("target", ("y",))
    complex_ = ChainComplex(GradedVectorSpace("C", {1: first, 0: target}), {})

    with pytest.raises(ValueError, match="domain"):
        ChainComplex(
            complex_.spaces,
            {1: LinearMap(other, target, ((0,),))},
        )
    with pytest.raises(ValueError, match="domain"):
        ChainMap(complex_, complex_, {1: LinearMap(other, first, ((0,),))})


def test_linear_map_direct_sum_keeps_distinct_block_frames() -> None:
    """Block-diagonal maps retain each distinct domain and codomain basis."""

    left_domain = VectorSpace("left domain", ("x",))
    left_codomain = VectorSpace("left codomain", ("u",))
    right_domain = VectorSpace("right domain", ("y",))
    right_codomain = VectorSpace("right codomain", ("v",))
    summed = LinearMap.direct_sum(
        LinearMap(left_domain, left_codomain, ((2,),)),
        LinearMap(right_domain, right_codomain, ((3,),)),
    )

    assert summed.domain.dimension == 2
    assert summed.codomain.dimension == 2
    assert summed.rows == ((Rational(2), Rational(0)), (Rational(0), Rational(3)))


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


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_direct_sum_preserves_explicit_zero_edge_bases(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """Explicit terminal and incoming zeros use the assembled named spaces."""

    step = -1 if complex_type is ChainComplex else 1
    left = VectorSpace("left", ("l",), scalar_type)
    right = VectorSpace("right", ("r",), scalar_type)
    left_spaces = GradedVectorSpace("L", {0: left})
    right_spaces = GradedVectorSpace("R", {0: right})
    left_complex = complex_type(left_spaces, {
        0: LinearMap.zero(left, left_spaces.space(step)),
        -step: LinearMap.zero(left_spaces.space(-step), left),
    })
    right_complex = complex_type(right_spaces, {
        0: LinearMap.zero(right, right_spaces.space(step)),
    })
    summed = left_complex.direct_sum(right_complex)

    assert isinstance(summed, complex_type)
    assert summed.cohomology_dimension(0) == 2
    assert summed.spaces.space(0) == left.direct_sum(right)
    for degree in (-step, 0):
        differential = summed.differential(degree)
        assert differential.domain == summed.spaces.space(degree)
        assert differential.codomain == summed.spaces.space(degree + step)
        assert differential.is_zero()
    assert summed.cohomology_dimension(step) == 0
    assert summed.cohomology_dimension(-step) == 0


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
@pytest.mark.parametrize("amount", (-3, -2, 0, 1, 2, 3))
def test_shift_preserves_explicit_zero_edge_bases(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
    amount: int,
) -> None:
    """Shifting incoming and outgoing zero maps retains their exact typing."""

    step = -1 if complex_type is ChainComplex else 1
    space = VectorSpace("middle", ("m",), scalar_type)
    spaces = GradedVectorSpace("C", {0: space})
    complex_ = complex_type(spaces, {
        -step: LinearMap.zero(spaces.space(-step), space),
        0: LinearMap.zero(space, spaces.space(step)),
    })

    shifted = complex_.shift(amount)
    assert shifted.spaces.space(amount) == space
    assert shifted.cohomology_dimension(amount) == 1
    for degree in (amount - step, amount):
        differential = shifted.differential(degree)
        assert differential.domain == shifted.spaces.space(degree)
        assert differential.codomain == shifted.spaces.space(degree + step)
        assert differential.domain.scalar_type is scalar_type
        assert differential.codomain.scalar_type is scalar_type
        assert differential.is_zero()
        assert shifted.differential(degree + step).compose(differential).is_zero()


@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_shift_retains_explicitly_named_zero_components(
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """Declared zero-dimensional bases remain declared rather than canonicalized."""

    step = -1 if complex_type is ChainComplex else 1
    space = VectorSpace("middle", ("m",), Eisenstein)
    zero = VectorSpace("named zero", (), Eisenstein)
    complex_ = complex_type(
        GradedVectorSpace("C", {0: space, step: zero}),
        {0: LinearMap.zero(space, zero)},
    )
    shifted = complex_.shift(-1)

    assert shifted.spaces.space(step - 1) == zero
    assert shifted.differential(-1).codomain == zero
    assert shifted.differential(-1) == -complex_.differential(0)
    assert shifted.cohomology_dimension(-1) == 1


def _three_term_complex(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> ChainComplex | CochainComplex:
    """Give a generic exact complex with one surviving middle class."""

    step = -1 if complex_type is ChainComplex else 1
    first = VectorSpace("first", ("x",), scalar_type)
    middle = VectorSpace("middle", ("u", "v", "w"), scalar_type)
    last = VectorSpace("last", ("y",), scalar_type)
    a = scalar_type(2)
    b = Rational(3) if scalar_type is Rational else OMEGA
    return complex_type(
        GradedVectorSpace("three term", {0: first, step: middle, 2 * step: last}),
        {
            0: LinearMap(first, middle, ((a,), (b,), (0,))),
            step: LinearMap(middle, last, ((-b, a, 0),)),
        },
    )


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_representatives_are_cycles_independent_modulo_boundaries(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """The quotient basis removes an actual nonzero boundary over either field."""

    complex_ = _three_term_complex(scalar_type, complex_type)
    step = -1 if complex_type is ChainComplex else 1
    assert complex_.cohomology_dimension(0) == 0
    assert complex_.cohomology_dimension(2 * step) == 0
    assert complex_.cohomology_dimension(step) == 1
    assert len(complex_.cycles(step)) == 2
    assert len(complex_.boundaries(step)) == 1
    representatives = complex_.cohomology_representatives(step)
    assert len(representatives) == 1
    assert representatives[0].coordinates == tuple(scalar_type(x) for x in (0, 0, 1))
    assert all(complex_.differential(step)(cycle).is_zero()
               for cycle in (*complex_.boundaries(step), *representatives))
    for amount in (-3, -2, 0, 2, 3):
        shifted = complex_.shift(amount)
        assert shifted.cohomology_dimension(step + amount) == 1
        assert shifted.differential(amount).rows == complex_.differential(0).scale(
            -1 if amount % 2 else 1
        ).rows


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_identity_cone_has_an_explicit_contracting_homotopy(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """The signed cone contracts by h(y, x) = (0, y), not just a rank count."""

    complex_ = _three_term_complex(scalar_type, complex_type)
    cone = mapping_cone(ChainMap.identity(complex_))
    step = -1 if complex_type is ChainComplex else 1
    components = {}
    for degree in cone.degrees:
        domain = cone.spaces.space(degree)
        codomain = cone.spaces.space(degree - step)
        top_dimension = complex_.spaces.space(degree - step).dimension
        components[degree] = LinearMap(domain, codomain, (
            tuple(int(row - top_dimension == column) if row >= top_dimension else 0
                  for column in range(domain.dimension))
            for row in range(codomain.dimension)
        ))
    homotopy = ChainHomotopy(
        ChainMap.identity(cone), ChainMap(cone, cone, {}), components
    )

    assert homotopy.first.source == cone
    assert all(cone.cohomology_dimension(degree) == 0 for degree in cone.degrees)
    zero_cone = mapping_cone(ChainMap(complex_, complex_, {}))
    for degree in zero_cone.degrees:
        assert zero_cone.cohomology_dimension(degree) == (
            complex_.cohomology_dimension(degree)
            + complex_.cohomology_dimension(degree + step)
        )


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_negative_horizontal_degree_totalization_keeps_exact_signs(
    scalar_type: type[Rational] | type[Eisenstein],
) -> None:
    """Negative odd degrees also negate the vertical direction exactly."""

    spaces = {
        cell: VectorSpace(str(cell), ("e",), scalar_type)
        for cell in ((-1, 0), (0, 0), (-1, 1), (0, 1))
    }
    a = scalar_type(2)
    b = Rational(3) if scalar_type is Rational else OMEGA
    bicomplex = Bicomplex(
        "negative square", spaces,
        horizontal={
            (-1, q): LinearMap(spaces[-1, q], spaces[0, q], ((a,),)) for q in (0, 1)
        },
        vertical={
            (p, 0): LinearMap(spaces[p, 0], spaces[p, 1], ((b,),)) for p in (-1, 0)
        },
    )
    total = bicomplex.totalize()
    assert total.differential(-1).rows == ((-b,), (a,))
    assert total.differential(0).rows == ((a, b),)
    assert total.differential(0).compose(total.differential(-1)).is_zero()
    assert all(total.cohomology_dimension(degree) == 0 for degree in total.degrees)


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
