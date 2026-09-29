"""Check the exact Hom evaluation used after the quotient tensor comparison.

Owns:
    Full signed evaluation identities with mixed rows, syzygies and every
    Koszul pair, plus explicit refusal of incompatible retargetings.

Depends on:
    Existing Hom composition, mixed differentials and declared block indices.

Must not:
    Interpret generic gauge fixtures as carrier scalars or physical evidence.

Phase 0:
    Mathematical evaluation checks preceding actual null-channel evaluation.
"""

from dataclasses import replace
from functools import cache
from itertools import product

import pytest

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.alternate_up_coupled_null_scalar import (
    retarget_quotient_block,
    verify_pushout_matter_lift,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedExtensionTerm,
    MixedResolutionArrow,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup as cup
from research.experiments.scientific_genesis.mixed_schoen_coupled_tensor import (
    coupled_exterior_quotient,
    coupled_quotient_vector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
)


def _entry(context, indices, subset, cell):
    component = context.components[(*indices, subset)]
    x, u, p = component.ambient_degree
    return SparseOuterCechCochain(((OuterCechBasis(
        component,
        tuple(x if i == cell[0][0] else 0 for i in range(3)),
        tuple(u if i == cell[1][0] else 0 for i in range(3)),
        tuple(p if i == cell[2][0] else 0 for i in range(2)), cell,
    ), Eisenstein(2, 1)),))


@cache
def _complex():
    unit = mixed_schoen_unit()
    scalar = _MixedContraction(unit, unit)
    eta = _entry(scalar, (0, 0), "k0", ((0,), (1,), (1,)))
    terms = []
    for source, parent, value in (
        (1, 0, scalar.differential(eta)), (2, 1, eta.scale(-1)),
    ):
        for b, c in value.terms:
            terms.append(MixedExtensionTerm(
                source, 0, parent, None, b.x_monomial, b.u_monomial,
                b.p_monomial, b.cell, c * (1 if parent else -1),
            ))
    return MixedSchoenUnit(
        "mathematical exact Hom evaluation fixture", 2, (0, 0, 0),
        tuple(MixedConstituentObject(name, degree, (0, 0, 0))
              for name, degree in (("A", 0), ("C", 0), ("s", -1))),
        (MixedResolutionArrow(2, 1, Polynomial.constant(1, 3, scalar_type=Eisenstein), 2),),
        tuple(terms),
    )


@pytest.mark.parametrize("subsets", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=2)))
@pytest.mark.parametrize("indices", ((0, 1), (1, 2), (2, 2), (1, 1)))
def test_full_evaluation_leibniz_with_mixed_rows_and_syzygies(subsets, indices) -> None:
    model, unit = _complex(), mixed_schoen_unit()
    dual, vector = _MixedContraction(unit, model), _MixedContraction(model, unit)
    scalar = _MixedContraction(unit, unit)
    h = _entry(dual, (0, indices[0]), subsets[0], ((0,), (0, 1), (0,)))
    z = _entry(vector, (indices[1], 0), subsets[1], ((0,), (1,), (0, 1)))
    degree = h.terms[0][0].total_degree
    assert dual.differential(dual.differential(h)).is_zero()
    assert vector.differential(vector.differential(z)).is_zero()
    assert scalar.differential(cup(h, z)) == (
        cup(dual.differential(h), z)
        + cup(h, vector.differential(z)).scale(-1 if degree % 2 else 1)
    )


def test_retargeting_keeps_the_declared_line_and_internal_degree() -> None:
    model, unit = _complex(), mixed_schoen_unit()
    context = _MixedContraction(model, unit)
    cochain = _entry(context, (1, 0), "k0", ((0,), (0,), (0,)))
    assert retarget_quotient_block(cochain, context, {1: 0}, dual=False).terms[0][
        0
    ].component.left_index == 0
    with pytest.raises(ValueError, match="incompatible declared basis"):
        retarget_quotient_block(cochain, context, {0: 0}, dual=False)
    with pytest.raises(ValueError, match="internal degree"):
        retarget_quotient_block(cochain, context, {1: 2}, dual=False)
    changed = replace(model, objects=(replace(model.objects[0], line_degree=(1, 0, 0)),
                                     *model.objects[1:]))
    with pytest.raises(ValueError, match="line or internal degree"):
        retarget_quotient_block(cochain, _MixedContraction(changed, unit), {1: 0}, dual=False)


@cache
def _coupled_complex():
    """Add one exact triangular gauge row, without physical input."""

    old, unit = _complex(), mixed_schoen_unit()
    scalar = _MixedContraction(unit, unit)
    gamma = _entry(scalar, (0, 0), "k0", ((1,), (1,), (0,)))
    terms = [replace(t, source=t.source + 1, target=t.target + 1)
             for t in old.extension_terms]
    coefficients = [(1, 0, scalar.differential(gamma))]
    for t in old.extension_terms:
        alpha = SparseOuterCechCochain(((OuterCechBasis(
            scalar.components[(0, 0, "k0")], t.x_monomial, t.u_monomial,
            t.p_monomial, t.cell,
        ), t.coefficient * (1 if t.parent_degree else -1)),))
        coefficients.append((t.source + 1, t.parent_degree, cup(gamma, alpha).scale(-1)))
    for source, parent, value in coefficients:
        for basis, coefficient in value.terms:
            terms.append(MixedExtensionTerm(
                source, 0, parent, None, basis.x_monomial, basis.u_monomial,
                basis.p_monomial, basis.cell, coefficient * (1 if parent else -1),
            ))
    return replace(
        old, name="mathematical formal-degree fixture",
        objects=(MixedConstituentObject("B", 0, (0, 0, 0)), *old.objects),
        resolution_arrows=tuple(replace(a, source=a.source + 1, target=a.target + 1)
                                for a in old.resolution_arrows),
        extension_terms=tuple(terms),
    )


@pytest.mark.parametrize("indices", ((2, 2), (2, 3), (3, 2), (3, 3)))
def test_outer_parameter_degree_is_linear_for_B_supported_corrections(indices) -> None:
    """Attack the support theorem over an exact nonrational field element.

    Finite test values are regressions, not the proof of formal degree.
    The proof is that every possible quadratic output is B wedge B or
    the killed A wedge B relation; no extension point is inferred.
    """

    source, unit = _coupled_complex(), mixed_schoen_unit()
    context = _MixedContraction(source, unit)

    def matter(index):
        cell = ((0,), (0, 1), (0,)) if source.objects[index].position == 0 else (
            (0, 1), (0,), (0, 1)
        )
        return _entry(context, (index, 0), "k0", cell)

    left, right = (matter(i) for i in indices)
    r = _entry(context, (0, 0), "k0", ((0,), (1,), (0, 1)))

    def at(value):
        coefficient = Eisenstein.coerce(value)
        model = coupled_exterior_quotient(replace(source, extension_terms=tuple(
            replace(t, coefficient=t.coefficient * coefficient) if t.target == 0 else t
            for t in source.extension_terms
        )), 1, 0)
        return coupled_quotient_vector_wedge(
            left + r.scale(coefficient), right + r.scale(coefficient * Eisenstein(1, 1)),
            model, 1, 1,
        )

    constant, at_one = at(0), at(1)
    value = Eisenstein(2, 1)
    assert at(value) == constant + (at_one + constant.scale(-1)).scale(value)


def _exact_pushout_lift():
    """Use a boundary of a typed noncycle as a mathematical lift fixture."""

    source, unit = _coupled_complex(), mixed_schoen_unit()
    model = coupled_exterior_quotient(source, 1, 0)
    context = _MixedContraction(source, unit)
    primitive = _entry(context, (1, 0), "k0", ((1,), (1,), (0,)))
    full = context.differential(primitive)
    assert not full.is_zero()
    constant = SparseOuterCechCochain(tuple(
        (basis, value) for basis, value in full.terms if basis.component.left_index != 0
    ))
    correction = full + constant.scale(-1)
    assert not constant.is_zero() and not correction.is_zero()
    return model, constant, correction


def test_complete_pushout_archive_lift_is_checked_as_cochains() -> None:
    model, constant, correction = _exact_pushout_lift()
    verify_pushout_matter_lift(model, constant, correction)


@pytest.mark.parametrize("corruption", ("sign", "missing", "block", "degree"))
def test_pushout_archive_lift_refuses_invalid_corrections(corruption) -> None:
    """A content digest cannot replace a typed, closed complete lift."""

    model, constant, correction = _exact_pushout_lift()
    if corruption == "sign":
        bad = correction.scale(-1)
        message = "coefficientwise pushout matter identity failed"
    elif corruption == "missing":
        bad = SparseOuterCechCochain()
        message = "coefficientwise pushout matter identity failed"
    elif corruption == "block":
        bad = constant
        message = "incompatible declared basis"
    else:
        context = _MixedContraction(model.source, mixed_schoen_unit())
        bad = _entry(context, (0, 0), "k0", ((0,), (0,), (0,)))
        message = "total degree one"
    with pytest.raises(ValueError, match=message):
        verify_pushout_matter_lift(model, constant, bad)
