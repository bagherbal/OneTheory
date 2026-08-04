"""Test exact multigraded Cox section spaces and finite section actions.

Owns:
    Multidegree arithmetic, monomial enumeration, homogeneous ideal quotient
    normal forms, pullbacks, multiplication, basis serialization, and exact
    finite actions over Rational and Eisenstein coefficients.

Depends on:
    `onetheory.math.sections`, exact polynomial machinery, and pytest.

Must not:
    Insert Schoen degrees, infer global generation, fabricate extension classes,
    use random sections, or construct numerical carrier metrics.

Phase 0:
    Generic exact section tests only; carrier section bases remain unresolved.
"""

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.sections import (
    CoxMap,
    CoxRing,
    CoxVariable,
    HomogeneousIdeal,
    MultiDegree,
    SectionGroupAction,
    SectionSpace,
    polynomial_terms_to_vector,
)


def _ring(scalar_type=Rational) -> CoxRing:
    return CoxRing(
        (CoxVariable("x", MultiDegree((1,))), CoxVariable("y", MultiDegree((1,)))),
        scalar_type=scalar_type,
    )


def test_exact_homogeneous_quotient_has_deterministic_normal_forms() -> None:
    ring = _ring()
    ideal = HomogeneousIdeal(ring, (ring.monomial((1, 1)),))
    space = SectionSpace(ring, MultiDegree((2,)), ideal)
    relation = polynomial_terms_to_vector(ring.monomial((1, 1)), space.ambient_basis)

    assert space.ambient_dimension == 3
    assert space.dimension == 2
    assert space.from_ambient(relation).is_zero()
    assert len(space.basis_serialization()) == 2
    assert space.basis_serialization()[0] != space.basis_serialization()[1]


def test_exact_section_products_and_polynomial_pullbacks() -> None:
    source = _ring()
    ideal = HomogeneousIdeal(source, (source.monomial((1, 1)),))
    degree_one = SectionSpace(source, MultiDegree((1,)), ideal)
    degree_two = SectionSpace(source, MultiDegree((2,)), ideal)
    x = degree_one.from_ambient(
        polynomial_terms_to_vector(source.monomial((1, 0)), degree_one.ambient_basis)
    )
    y = degree_one.from_ambient(
        polynomial_terms_to_vector(source.monomial((0, 1)), degree_one.ambient_basis)
    )

    assert degree_one.multiply(x, y, degree_two).is_zero()

    target = _ring()
    map_ = CoxMap(source, target, (target.monomial((1, 0)), target.polynomial(
        (((1, 0), 1), ((0, 1), 1))
    )))
    pulled = degree_one.pullback(x, map_, SectionSpace(target, MultiDegree((1,))))

    assert pulled.space.polynomial(pulled) == target.monomial((1, 0))


def test_section_actions_validate_the_group_law_exactly() -> None:
    ring = _ring()
    space = SectionSpace(ring, MultiDegree((2,)), HomogeneousIdeal(ring, (ring.monomial((1, 1)),)))
    swap = Matrix(((0, 1), (1, 0)), scalar_type=Rational)
    action = SectionGroupAction(
        space,
        "e",
        {"e": Matrix.identity(2), "s": swap},
        {("e", "e"): "e", ("e", "s"): "s", ("s", "e"): "s", ("s", "s"): "e"},
    )
    first = space.basis()[0]

    assert action.apply("s", first).is_zero() is False
    assert action.matrix("s").matmul(action.matrix("s")) == Matrix.identity(2)


def test_eisenstein_section_coefficients_remain_exact() -> None:
    ring = _ring(Eisenstein)
    space = SectionSpace(ring, MultiDegree((1,)))
    section = space.from_quotient_coordinates((OMEGA, 0))

    assert section.space.polynomial(section).coefficient((0, 1)) == OMEGA
