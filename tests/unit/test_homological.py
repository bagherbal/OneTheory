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


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_complex_direction_cannot_be_overridden_through_an_instance_dictionary(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """Frozen complexes must not inherit writable metadata from their mixin."""

    step = -1 if complex_type is ChainComplex else 1
    first = VectorSpace("first", ("x",), scalar_type)
    last = VectorSpace("last", ("y",), scalar_type)
    spaces = GradedVectorSpace("C", {0: first, step: last})
    complex_ = complex_type(spaces, {0: LinearMap(first, last, ((1,),))})

    with pytest.raises(TypeError, match="__dict__"):
        vars(complex_)["_direction"] = "cochain" if step == -1 else "chain"
    with pytest.raises(FrozenInstanceError):
        complex_._spaces = GradedVectorSpace("replacement", {})  # type: ignore[misc]
    assert not hasattr(complex_, "__dict__")
    assert complex_.direction == ("chain" if step == -1 else "cochain")
    assert complex_.differential(0).codomain == last
    assert all(complex_.cohomology_dimension(degree) == 0 for degree in complex_.degrees)


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
@pytest.mark.parametrize("axis", ("horizontal", "vertical"))
def test_bicomplex_rejects_nonzero_directional_squares(
    scalar_type: type[Rational] | type[Eisenstein],
    axis: str,
) -> None:
    """Commuting cross directions cannot excuse a nonzero directional square."""

    cells = tuple((degree, 0) if axis == "horizontal" else (0, degree)
                  for degree in range(3))
    spaces = {cell: VectorSpace(str(cell), ("e",), scalar_type) for cell in cells}
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    maps = {
        cells[index]: LinearMap(spaces[cells[index]], spaces[cells[index + 1]],
                                ((coefficient,),))
        for index in range(2)
    }

    assert not maps[cells[1]].compose(maps[cells[0]]).is_zero()
    with pytest.raises(ValueError, match="directional squares must vanish"):
        Bicomplex("invalid square", spaces, **{axis: maps})


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_chain_maps_reject_noncommuting_components_in_either_direction(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """Well-typed components alone do not certify a chain map."""

    step = -1 if complex_type is ChainComplex else 1
    first = VectorSpace("first", ("x",), scalar_type)
    last = VectorSpace("last", ("y",), scalar_type)
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    complex_ = complex_type(
        GradedVectorSpace("two term", {0: first, step: last}),
        {0: LinearMap(first, last, ((coefficient,),))},
    )

    with pytest.raises(ValueError, match="commute with the differentials"):
        ChainMap(complex_, complex_, {0: LinearMap.identity(first)})
    with pytest.raises(ValueError, match="commute with the differentials"):
        ChainMap(complex_, complex_, {step: LinearMap.identity(last)})


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_complex_identities_reject_arbitrarily_small_exact_defects(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """An exact differential identity has no numerical tolerance or underflow."""

    step = -1 if complex_type is ChainComplex else 1
    first = VectorSpace("first", ("a",), scalar_type)
    middle = VectorSpace("middle", ("b", "c"), scalar_type)
    last = VectorSpace("last", ("d",), scalar_type)
    spaces = GradedVectorSpace("exact cancellation", {0: first, step: middle, 2 * step: last})
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    tiny = scalar_type(Rational(1, 10**400))
    incoming = LinearMap(first, middle, ((coefficient,), (1,)))
    outgoing = LinearMap(middle, last, ((1, -coefficient),))
    complex_ = complex_type(spaces, {0: incoming, step: outgoing})

    assert outgoing.compose(incoming).is_zero()
    assert all(complex_.cohomology_dimension(degree) == 0 for degree in spaces.degrees)
    perturbed = LinearMap(middle, last, ((1, -coefficient + tiny),))
    assert perturbed.compose(incoming).rows == ((tiny,),)
    with pytest.raises(ValueError, match="squared equals zero"):
        complex_type(spaces, {0: incoming, step: perturbed})


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_maps_and_homotopies_reject_arbitrarily_small_exact_defects(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """Commutation and homotopy equations cannot silently round to zero."""

    step = -1 if complex_type is ChainComplex else 1
    first = VectorSpace("first", ("a",), scalar_type)
    last = VectorSpace("last", ("b",), scalar_type)
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    tiny = scalar_type(Rational(1, 10**400))
    complex_ = complex_type(
        GradedVectorSpace("contractible", {0: first, step: last}),
        {0: LinearMap(first, last, ((coefficient,),))},
    )
    identity = ChainMap.identity(complex_)
    zero = ChainMap(complex_, complex_, {})
    contraction = LinearMap(last, first, ((scalar_type(1) / coefficient,),))
    assert ChainHomotopy(identity, zero, {step: contraction}).component(step) == contraction

    with pytest.raises(ValueError, match="commute with the differentials"):
        ChainMap(complex_, complex_, {
            0: LinearMap.identity(first),
            step: LinearMap(last, last, ((scalar_type(1) + tiny,),)),
        })
    perturbed = contraction + LinearMap(last, first, ((tiny,),))
    with pytest.raises(ValueError, match="homotopy equation"):
        ChainHomotopy(identity, zero, {step: perturbed})


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_totalization_requires_exact_unsigned_square_commutation(
    scalar_type: type[Rational] | type[Eisenstein],
) -> None:
    """The total differential's sign cannot hide a tiny noncommuting square."""

    cells = {(p, q): VectorSpace(f"cell {p},{q}", ("e",), scalar_type)
             for p in (0, 1) for q in (0, 1)}
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    tiny = scalar_type(Rational(1, 10**400))
    horizontal = {(0, q): LinearMap(cells[0, q], cells[1, q], ((coefficient,),))
                  for q in (0, 1)}
    vertical = {(p, 0): LinearMap(cells[p, 0], cells[p, 1], ((1,),))
                for p in (0, 1)}
    total = Bicomplex("commuting square", cells, horizontal, vertical).totalize()
    assert total.differential(1).compose(total.differential(0)).is_zero()
    vertical[1, 0] = LinearMap(cells[1, 0], cells[1, 1], ((scalar_type(1) + tiny,),))
    with pytest.raises(ValueError, match="directions must commute"):
        Bicomplex("noncommuting square", cells, horizontal, vertical)


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


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
@pytest.mark.parametrize("invalid_degree", (False, True, 0.0, 1.0, 1.5, "0"))
def test_integer_gradings_reject_aliases_in_maps_and_lookups(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
    invalid_degree: object,
) -> None:
    """An invalid degree must not select an existing integer-indexed basis."""

    step = -1 if complex_type is ChainComplex else 1
    spaces = GradedVectorSpace("C", {
        degree: VectorSpace(f"C{degree}", ("e",), scalar_type) for degree in (0, 1)
    })
    complex_ = complex_type(spaces, {
        degree: LinearMap.zero(spaces.space(degree), spaces.space(degree + step))
        for degree in spaces.degrees
    })
    identity = ChainMap.identity(complex_)
    homotopy = ChainHomotopy(identity, identity, {
        degree: LinearMap.zero(spaces.space(degree), spaces.space(degree - step))
        for degree in spaces.degrees
    })

    for lookup in (
        spaces.space, complex_.differential, complex_.cycles, complex_.boundaries,
        complex_.cohomology_dimension, complex_.cohomology_representatives,
        identity.component, homotopy.component,
    ):
        with pytest.raises(TypeError, match="degrees must be integers"):
            lookup(invalid_degree)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="degrees must be integers"):
        GradedVectorSpace("invalid", [(invalid_degree, spaces.space(0))])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="degrees must be integers"):
        complex_type(spaces, [(invalid_degree, complex_.differential(0))])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="degrees must be integers"):
        ChainMap(complex_, complex_, [(invalid_degree, identity.component(0))])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="degrees must be integers"):
        ChainHomotopy(identity, identity, [(invalid_degree, homotopy.component(0))])  # type: ignore[list-item]


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("invalid_degree", (False, True, 0.0, 1.0, 1.5, "0"))
@pytest.mark.parametrize("axis", (0, 1))
def test_bicomplexes_require_integer_degrees_in_each_direction(
    scalar_type: type[Rational] | type[Eisenstein],
    invalid_degree: object,
    axis: int,
) -> None:
    """Neither cell labels nor map sources may bypass the integer grading."""

    space = VectorSpace("B00", ("e",), scalar_type)
    bicomplex = Bicomplex("B", {(0, 0): space})
    cell = (invalid_degree, 0) if axis == 0 else (0, invalid_degree)
    with pytest.raises(TypeError, match="degrees must be integers"):
        bicomplex.space(cell)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="degrees must be integers"):
        Bicomplex("invalid", [(cell, space)])  # type: ignore[list-item]
    for direction in ("horizontal", "vertical"):
        target = (1, 0) if direction == "horizontal" else (0, 1)
        map_ = LinearMap.zero(space, bicomplex.space(target))
        with pytest.raises(TypeError, match="degrees must be integers"):
            Bicomplex("B", {(0, 0): space}, **{direction: [(cell, map_)]})  # type: ignore[arg-type]


@pytest.mark.parametrize("cell", ((), (0,), (0, 1, 2), "00", [0, 0]))
def test_bicomplexes_reject_malformed_bidegrees(cell: object) -> None:
    """Each bidegree is explicitly an ordered pair, not an incidental index."""

    space = VectorSpace("B00", ("e",))
    bicomplex = Bicomplex("B", {(0, 0): space})
    with pytest.raises(ValueError, match="horizontal, vertical"):
        bicomplex.space(cell)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="horizontal, vertical"):
        Bicomplex("invalid", [(cell, space)])  # type: ignore[list-item]


@pytest.mark.parametrize("invalid_name", (None, True, 1, ["mutable"], {"mutable": 1}))
def test_based_spaces_reject_nonstring_identities(invalid_name: object) -> None:
    """Mutable or numeric names cannot become part of a typed basis identity."""

    with pytest.raises(TypeError, match="names must be strings"):
        VectorSpace(invalid_name, ("e",))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="names must be strings"):
        GradedVectorSpace(invalid_name, {})  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="names must be strings"):
        Bicomplex(invalid_name, {})  # type: ignore[arg-type]


def test_based_spaces_require_nonempty_identities() -> None:
    """Zero-dimensional spaces still require an explicit identity."""

    with pytest.raises(ValueError, match="nonempty space name"):
        VectorSpace("", ())
    with pytest.raises(ValueError, match="nonempty space name"):
        GradedVectorSpace("", {})
    with pytest.raises(ValueError, match="nonempty space name"):
        Bicomplex("", {})


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_empty_complex_constructions_preserve_the_declared_field(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """The zero complex remains over its field through each construction."""

    spaces = GradedVectorSpace("zero", {}, scalar_type=scalar_type)
    complex_ = complex_type(spaces, {})
    identity = ChainMap.identity(complex_)
    ChainHomotopy(identity, identity, {})
    constructions = (
        complex_, complex_.shift(-3), complex_.direct_sum(complex_), mapping_cone(identity),
    )
    for result in constructions:
        assert result.degrees == ()
        assert result.spaces.scalar_type is scalar_type
        assert result.spaces.space(7).scalar_type is scalar_type
        assert result.differential(7).domain.scalar_type is scalar_type
        assert result.differential(7).codomain.scalar_type is scalar_type
        assert result.cycles(7) == result.boundaries(7) == ()
        assert result.cohomology_dimension(7) == 0
        assert result.cohomology_representatives(7) == ()
    assert identity.compose(identity) == identity
    with pytest.raises(FrozenInstanceError):
        spaces._scalar_type = Rational  # type: ignore[misc]


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_empty_bicomplex_totalization_preserves_the_declared_field(
    scalar_type: type[Rational] | type[Eisenstein],
) -> None:
    """Signed totalization cannot turn an empty Eisenstein complex rational."""

    bicomplex = Bicomplex("zero", {}, scalar_type=scalar_type)
    assert bicomplex.scalar_type is scalar_type
    assert bicomplex.space((-1, 2)).scalar_type is scalar_type
    total = bicomplex.totalize()
    assert total.spaces.scalar_type is scalar_type
    assert total.degrees == ()
    assert total.differential(0).is_zero()
    assert total.differential(0).domain.scalar_type is scalar_type
    with pytest.raises(FrozenInstanceError):
        bicomplex._scalar_type = Rational  # type: ignore[misc]


@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_empty_complexes_reject_incompatible_coefficient_fields(
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """An empty tuple of maps must not bypass coefficient compatibility."""

    rational = GradedVectorSpace("Q", {}, scalar_type=Rational)
    eisenstein = GradedVectorSpace("Qomega", {}, scalar_type=Eisenstein)
    source = complex_type(rational, {})
    target = complex_type(eisenstein, {})
    with pytest.raises(TypeError, match="same scalar type"):
        rational.direct_sum(eisenstein)
    with pytest.raises(TypeError, match="same scalar type"):
        source.direct_sum(target)
    with pytest.raises(TypeError, match="same scalar type"):
        ChainMap(source, target, {})


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_empty_summands_preserve_nonempty_complex_bases_and_cohomology(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """A typed zero summand changes labels but not exact homology dimensions."""

    zero = complex_type(GradedVectorSpace("zero", {}, scalar_type=scalar_type), {})
    complex_ = _three_term_complex(scalar_type, complex_type)
    for result in (zero.direct_sum(complex_), complex_.direct_sum(zero)):
        assert result.spaces.scalar_type is scalar_type
        assert result.degrees == complex_.degrees
        for degree in result.degrees:
            assert result.spaces.space(degree).dimension == complex_.spaces.space(degree).dimension
            assert result.cohomology_dimension(degree) == complex_.cohomology_dimension(degree)


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_coefficient_declarations_agree_with_components(
    scalar_type: type[Rational] | type[Eisenstein],
) -> None:
    """Explicit fields are checked rather than coercing existing named spaces."""

    space = VectorSpace("component", ("e",), scalar_type)
    other_type = Eisenstein if scalar_type is Rational else Rational
    assert GradedVectorSpace("C", {0: space}).scalar_type is scalar_type
    assert Bicomplex("B", {(0, 0): space}).scalar_type is scalar_type
    with pytest.raises(TypeError, match="same scalar type"):
        GradedVectorSpace("C", {0: space}, scalar_type=other_type)
    with pytest.raises(TypeError, match="same scalar type"):
        Bicomplex("B", {(0, 0): space}, scalar_type=other_type)
    with pytest.raises(TypeError, match="scalar_type must be"):
        GradedVectorSpace("C", {}, scalar_type=float)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="scalar_type must be"):
        Bicomplex("B", {}, scalar_type=float)  # type: ignore[arg-type]
    assert GradedVectorSpace("default", {}).scalar_type is Rational
    assert Bicomplex("default", {}).scalar_type is Rational


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_nonidentity_cone_tracks_kernel_and_cokernel_with_exact_signs(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """A nonzero nullhomotopic map has both kernel and cokernel in its cone."""

    complex_ = _three_term_complex(scalar_type, complex_type)
    step = -1 if complex_type is ChainComplex else 1
    middle = complex_.spaces.space(step)
    projection = ChainMap(complex_, complex_, {
        0: LinearMap.identity(complex_.spaces.space(0)),
        step: LinearMap(middle, middle, ((1, 0, 0), (0, 1, 0), (0, 0, 0))),
        2 * step: LinearMap.identity(complex_.spaces.space(2 * step)),
    })
    # This contracts the exact two-term part while killing the surviving class.
    half = Rational(1, 2)
    ChainHomotopy(projection, ChainMap(complex_, complex_, {}), {
        step: LinearMap(middle, complex_.spaces.space(0), ((half, 0, 0),)),
        2 * step: LinearMap(complex_.spaces.space(2 * step), middle,
                           ((0,), (half,), (0,))),
    })
    cone = mapping_cone(projection)
    assert isinstance(cone, complex_type)
    for degree in cone.degrees:
        assert cone.cohomology_dimension(degree) == int(degree in (0, step))
        assert len(cone.cohomology_representatives(degree)) == int(degree in (0, step))
        differential = cone.differential(degree)
        assert cone.differential(degree + step).compose(differential).is_zero()
        target_rows = complex_.spaces.space(degree + step).dimension
        target_columns = complex_.spaces.space(degree).dimension
        if degree + step in cone.spaces.degrees:
            assert tuple(row[target_columns:] for row in differential.rows[target_rows:]) == (
                -complex_.differential(degree + step)
            ).rows


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_cone_exact_sequence_and_canonical_nullhomotopy(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """The cone realizes 0 -> target -> cone -> shifted source -> 0 exactly."""

    source = _three_term_complex(scalar_type, complex_type)
    target = source.direct_sum(source)
    step = -1 if complex_type is ChainComplex else 1
    map_ = ChainMap(source, target, {
        degree: LinearMap(source.spaces.space(degree), target.spaces.space(degree), (
            tuple(int(row == column) for column in range(source.spaces.space(degree).dimension))
            for row in range(target.spaces.space(degree).dimension)
        ))
        for degree in source.degrees
    })
    cone = mapping_cone(map_)
    shifted_source = source.shift(-step)
    degrees = sorted(set(cone.degrees) | set(target.degrees) | set(shifted_source.degrees))

    inclusion = ChainMap(target, cone, {
        degree: LinearMap(target.spaces.space(degree), cone.spaces.space(degree), (
            tuple(int(row == column) for column in range(target.spaces.space(degree).dimension))
            for row in range(cone.spaces.space(degree).dimension)
        ))
        for degree in degrees
    })
    projection = ChainMap(cone, shifted_source, {
        degree: LinearMap(cone.spaces.space(degree), shifted_source.spaces.space(degree), (
            tuple(int(column == target.spaces.space(degree).dimension + row)
                  for column in range(cone.spaces.space(degree).dimension))
            for row in range(shifted_source.spaces.space(degree).dimension)
        ))
        for degree in degrees
    })

    for degree in degrees:
        inject = inclusion.component(degree)
        project = projection.component(degree)
        assert inject.rank() == target.spaces.space(degree).dimension
        assert project.rank() == shifted_source.spaces.space(degree).dimension
        assert project.compose(inject).is_zero()
        assert inject.rank() + project.rank() == cone.spaces.space(degree).dimension

    # h(x) = (0, x) witnesses that the original map becomes nullhomotopic
    # after inclusion into its cone. The negative source differential is
    # essential for the lower block of d h + h d to cancel.
    nullhomotopy = ChainHomotopy(
        inclusion.compose(map_), ChainMap(source, cone, {}), {
            degree: LinearMap(source.spaces.space(degree), cone.spaces.space(degree - step), (
                tuple(int(row == target.spaces.space(degree - step).dimension + column)
                      for column in range(source.spaces.space(degree).dimension))
                for row in range(cone.spaces.space(degree - step).dimension)
            ))
            for degree in degrees
        },
    )
    assert nullhomotopy.first == inclusion.compose(map_)
    assert all(
        cone.cohomology_dimension(degree) == source.cohomology_dimension(degree)
        for degree in degrees
    )


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_homotopic_maps_have_explicitly_isomorphic_signed_cones(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """The shear (y, x) -> (y + h(x), x) intertwines the cone differentials."""

    complex_ = _three_term_complex(scalar_type, complex_type)
    step = -1 if complex_type is ChainComplex else 1
    middle = complex_.spaces.space(step)
    projection = ChainMap(complex_, complex_, {
        0: LinearMap.identity(complex_.spaces.space(0)),
        step: LinearMap(middle, middle, ((1, 0, 0), (0, 1, 0), (0, 0, 0))),
        2 * step: LinearMap.identity(complex_.spaces.space(2 * step)),
    })
    zero = ChainMap(complex_, complex_, {})
    homotopy = ChainHomotopy(projection, zero, {
        step: LinearMap(middle, complex_.spaces.space(0), ((Rational(1, 2), 0, 0),)),
        2 * step: LinearMap(complex_.spaces.space(2 * step), middle,
                           ((0,), (Rational(1, 2),), (0,))),
    })
    first = mapping_cone(projection)
    second = mapping_cone(zero)

    def shear(sign: int) -> dict[int, LinearMap]:
        components = {}
        for degree in first.degrees:
            space = first.spaces.space(degree)
            target_width = complex_.spaces.space(degree).dimension
            h = homotopy.component(degree + step).scale(sign)
            rows = tuple(
                tuple(
                    h.rows[row][column - target_width]
                    if row < target_width <= column else scalar_type(int(row == column))
                    for column in range(space.dimension)
                )
                for row in range(space.dimension)
            )
            components[degree] = LinearMap(space, second.spaces.space(degree), rows)
        return components

    forward = ChainMap(first, second, shear(1))
    inverse = ChainMap(second, first, shear(-1))
    assert inverse.compose(forward) == ChainMap.identity(first)
    assert forward.compose(inverse) == ChainMap.identity(second)
    assert all(
        first.cohomology_dimension(degree) == second.cohomology_dimension(degree)
        for degree in first.degrees
    )
    with pytest.raises(ValueError, match="commute"):
        ChainMap(first, second, shear(-1))


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_complexes_snapshot_mutable_constructor_inputs(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """External containers cannot later alter a validated differential or basis."""

    step = -1 if complex_type is ChainComplex else 1
    labels = ["x", "y"]
    first = VectorSpace("first", labels, scalar_type)
    last = VectorSpace("last", ("z",), scalar_type)
    components = {0: first, step: last}
    spaces = GradedVectorSpace("snapshot", components)
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    rows = [[coefficient, scalar_type(0)]]
    differential = LinearMap(first, last, rows)
    differentials = {0: differential}
    complex_ = complex_type(spaces, differentials)
    map_components = {degree: LinearMap.identity(spaces.space(degree))
                      for degree in spaces.degrees}
    identity = ChainMap(complex_, complex_, map_components)
    homotopy_components = {0: LinearMap.zero(first, spaces.space(-step))}
    homotopy = ChainHomotopy(identity, identity, homotopy_components)

    labels.reverse()
    rows[0][0] = scalar_type(0)
    components.clear()
    differentials.clear()
    map_components.clear()
    homotopy_components.clear()

    assert first.basis == ("x", "y")
    assert complex_.differential(0).rows == ((coefficient, scalar_type(0)),)
    assert complex_.cohomology_dimension(0) == 1
    assert complex_.cohomology_dimension(step) == 0
    assert identity == ChainMap.identity(complex_)
    assert len(homotopy.components) == 1
    assert hash(complex_) == hash(complex_type(spaces, {0: differential}))


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_reordered_basis_cannot_be_used_as_an_implicit_change_of_coordinates(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """Equal names and dimensions do not authorize a hidden basis permutation."""

    first = VectorSpace("same name", ("x", "y"), scalar_type)
    reordered = VectorSpace("same name", ("y", "x"), scalar_type)
    complex_ = complex_type(GradedVectorSpace("original", {0: first}), {})
    other = complex_type(GradedVectorSpace("reordered", {0: reordered}), {})
    identity = LinearMap.identity(first)

    with pytest.raises(ValueError, match="vector basis"):
        identity(CoordinateVector(reordered, (1, 0)))
    with pytest.raises(ValueError, match="matching named spaces"):
        identity.compose(LinearMap.identity(reordered))
    with pytest.raises(ValueError, match="codomain"):
        ChainMap(complex_, other, {0: identity})

    # A basis permutation is valid only when explicitly supplied as a typed map.
    permutation = ChainMap(complex_, other, {
        0: LinearMap(first, reordered, ((0, 1), (1, 0))),
    })
    inverse = ChainMap(other, complex_, {
        0: LinearMap(reordered, first, ((0, 1), (1, 0))),
    })
    assert inverse.compose(permutation) == ChainMap.identity(complex_)


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_nine_cell_totalization_matches_the_tensor_complex_cohomology(
    scalar_type: type[Rational] | type[Eisenstein],
) -> None:
    """Three-cell diagonals retain block order and all vertical parity signs."""

    cells = {(p, q): VectorSpace(f"cell {p},{q}", ("00", "01", "10", "11"), scalar_type)
             for p in range(3) for q in range(3)}
    a = Rational(2, 3) if scalar_type is Rational else OMEGA
    b = Rational(3, 5) if scalar_type is Rational else Eisenstein(1, 2)
    horizontal_rows = ((0, 0, a, 0), (0, 0, 0, a), (0, 0, 0, 0), (0, 0, 0, 0))
    vertical_rows = ((0, b, 0, 0), (0, 0, 0, 0), (0, 0, 0, b), (0, 0, 0, 0))
    bicomplex = Bicomplex(
        "tensor grid", cells,
        horizontal={(p, q): LinearMap(cells[p, q], cells[p + 1, q], horizontal_rows)
                    for p in range(2) for q in range(3)},
        vertical={(p, q): LinearMap(cells[p, q], cells[p, q + 1], vertical_rows)
                  for p in range(3) for q in range(2)},
    )
    total = bicomplex.totalize()

    # Independently assemble each scalar entry, without the block-map helper.
    for degree in range(5):
        sources = sorted(cell for cell in cells if sum(cell) == degree)
        targets = sorted(cell for cell in cells if sum(cell) == degree + 1)
        expected = []
        for target in targets:
            for row in range(4):
                values = []
                for p, q in sources:
                    block = horizontal_rows if target == (p + 1, q) else (
                        vertical_rows if target == (p, q + 1) else ((0,) * 4,) * 4
                    )
                    sign = -1 if target == (p, q + 1) and p % 2 else 1
                    values.extend(scalar_type(sign) * value for value in block[row])
                expected.append(tuple(values))
        assert total.differential(degree).rows == tuple(expected)
        assert total.differential(degree + 1).compose(total.differential(degree)).is_zero()

    # Each factor has one class at either endpoint and none in the middle.
    assert tuple(total.cohomology_dimension(degree) for degree in range(5)) == (1, 0, 2, 0, 1)
    assert tuple(len(total.cohomology_representatives(degree)) for degree in range(5)) == (
        1, 0, 2, 0, 1,
    )


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("empty", (False, True))
def test_graded_constructions_validate_explicit_names(
    scalar_type: type[Rational] | type[Eisenstein], empty: bool,
) -> None:
    """An explicitly invalid identity is not silently replaced by a default."""

    components = {} if empty else {0: VectorSpace("C0", ("x",), scalar_type)}
    space = GradedVectorSpace("C", components, scalar_type=scalar_type)
    for construct, argument in ((space.shift, 1), (space.direct_sum, space)):
        with pytest.raises(ValueError, match="nonempty space name"):
            construct(argument, name="")
        for name in (False, 0, [], {}):
            with pytest.raises(TypeError, match="space names must be strings"):
                construct(argument, name=name)

    assert space.shift(1).name == "C[1]"
    assert space.direct_sum(space).name == "C⊕C"
    assert space.shift(1, name="suspension").name == "suspension"
    assert space.direct_sum(space, name="sum").name == "sum"


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_nonidentity_quasi_isomorphism_has_an_acyclic_cone(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """An inclusion across unequal complexes induces an isomorphism on classes."""

    step = -1 if complex_type is ChainComplex else 1
    survivor = VectorSpace("survivor", ("h",), scalar_type)
    source = complex_type(GradedVectorSpace("source", {0: survivor}), {})
    middle = VectorSpace("target middle", ("boundary", "class"), scalar_type)
    incoming = VectorSpace("target incoming", ("primitive",), scalar_type)
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    target = complex_type(
        GradedVectorSpace("target", {-step: incoming, 0: middle}),
        {-step: LinearMap(incoming, middle, ((coefficient,), (0,)))},
    )
    inclusion = ChainMap(source, target, {
        0: LinearMap(survivor, middle, ((coefficient,), (1,))),
    })
    cone = mapping_cone(inclusion)

    assert source != target
    assert source.cohomology_dimension(0) == target.cohomology_dimension(0) == 1
    assert inclusion.component(0)(source.cycles(0)[0]) == CoordinateVector(
        middle, (coefficient, 1),
    )
    for degree in cone.degrees:
        assert cone.differential(degree + step).compose(cone.differential(degree)).is_zero()
        assert cone.cohomology_dimension(degree) == 0
        assert cone.cohomology_representatives(degree) == ()


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("complex_type", (ChainComplex, CochainComplex))
def test_explicit_basis_transport_preserves_complexes_and_quotient_classes(
    scalar_type: type[Rational] | type[Eisenstein],
    complex_type: type[ChainComplex] | type[CochainComplex],
) -> None:
    """A declared shear preserves classes without identifying distinct bases."""

    source = _three_term_complex(scalar_type, complex_type)
    step = -1 if complex_type is ChainComplex else 1
    spaces = GradedVectorSpace("transported", {
        degree: VectorSpace(f"transported {degree}", space.basis, scalar_type)
        for degree, space in source.spaces.components
    })
    coefficient = Rational(2, 3) if scalar_type is Rational else OMEGA
    forward = {
        degree: LinearMap(space, spaces.space(degree), (
            ((1, coefficient, 0), (0, 1, 1), (0, 0, 1))
            if degree == step else ((1,),)
        ))
        for degree, space in source.spaces.components
    }
    backward = {
        degree: LinearMap(spaces.space(degree), space, (
            ((1, -coefficient, coefficient), (0, 1, -1), (0, 0, 1))
            if degree == step else ((1,),)
        ))
        for degree, space in source.spaces.components
    }
    target = complex_type(spaces, {
        degree: forward[degree + step].compose(differential).compose(backward[degree])
        for degree, differential in source.differentials
    })
    change = ChainMap(source, target, forward)
    inverse = ChainMap(target, source, backward)

    assert inverse.compose(change) == ChainMap.identity(source)
    assert change.compose(inverse) == ChainMap.identity(target)
    for degree in source.degrees:
        assert target.cohomology_dimension(degree) == source.cohomology_dimension(degree)
        for cycle in source.cycles(degree):
            assert target.differential(degree)(change.component(degree)(cycle)).is_zero()
    transported_class = change.component(step)(source.cohomology_representatives(step)[0])
    assert transported_class.coordinates == tuple(scalar_type(value) for value in (0, 1, 1))
    boundaries = target.boundaries(step)
    span = LinearMap(VectorSpace("boundary columns", ("b",), scalar_type),
                     target.spaces.space(step),
                     tuple((entry,) for entry in boundaries[0].coordinates))
    enlarged = LinearMap(VectorSpace("boundary and class", ("b", "h"), scalar_type),
                         target.spaces.space(step),
                         tuple((boundary, representative) for boundary, representative in zip(
                             boundaries[0].coordinates, transported_class.coordinates, strict=True
                         )))
    assert span.rank() == 1
    assert enlarged.rank() == 2
    cone = mapping_cone(change)
    assert all(cone.cohomology_dimension(degree) == 0 for degree in cone.degrees)
    with pytest.raises(ValueError, match="vector basis"):
        target.differential(step)(source.cohomology_representatives(step)[0])


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
