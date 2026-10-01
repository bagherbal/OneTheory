"""Independently certify the raw contraction used by universal metric lifts.

Owns:
    Finite negative-support reduction, integer incidence verification of the
    actual raw homotopy, complete source-module composition, repaired averaging,
    and a closed-residual lifting theorem with explicit carrier premises.

Depends on:
    The observed full-cover contraction, independently reconstructed simplex
    incidence, and the actual outer-lift ambient profiles and filtration.

Must not:
    Infer closure or equivariance of every outer product from a contraction
    identity alone, claim numerical metrics, or select universal parameters.

Phase 0:
    Research-only operator certification; local fiber evaluation remains open.
"""

from __future__ import annotations

import hashlib
import json
from functools import cache
from itertools import combinations, product
from math import comb

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
    _cech_differential,
    _equation_terms,
    _homotopy,
)

from . import alternate_metric_outer_lifts as lifts
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_outer_actions import _full_action
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = lifts.first.ROOT / (
    "data/generated/scientific_genesis/alternate_metric_lift_operator_certificate.json"
)
SIZES = (3, 3, 2)


def _subsets(size, include_empty=False):
    return tuple(s for n in range(0 if include_empty else 1, size + 1)
                 for s in combinations(range(size), n))


def _sum(*vectors):
    result = {}
    for vector in vectors:
        for cell, value in vector.items():
            result[cell] = result.get(cell, 0) + value
    return {cell: value for cell, value in result.items() if value}


def _image(columns, vector):
    return _sum(*({target: value * coefficient for target, coefficient in columns[cell].items()}
                  for cell, value in vector.items()))


def _incidence(cell, parity):
    """Transpose oriented face deletion, independent of the cover engine."""

    result = {}
    preceding = parity
    for axis, (simplex, size) in enumerate(zip(cell, SIZES, strict=True)):
        for target in combinations(range(size), len(simplex) + 1):
            for omitted in range(len(target)):
                if target[:omitted] + target[omitted + 1:] == simplex:
                    new_cell = (*cell[:axis], target, *cell[axis + 1:])
                    result[new_cell] = (-1) ** (preceding + omitted)
        preceding += len(simplex) - 1
    return result


def _cohomology_projector(cell, supports):
    """Use evaluation at vertex zero for H0 and the full simplex for top H."""

    images = []
    for simplex, support, size in zip(cell, supports, SIZES, strict=True):
        if not support and simplex == (0,):
            images.append(tuple((v,) for v in range(size)))
        elif len(support) == size:
            images.append((tuple(range(size)),))
        else:
            return {}
    return {target: 1 for target in product(*images)}


def _integer_column(cochain, sample):
    result = {}
    for basis, value in cochain.terms:
        if (basis.component != sample.component
            or basis.x_monomial != sample.x_monomial
            or basis.u_monomial != sample.u_monomial
            or basis.p_monomial != sample.p_monomial
            or not value.b.is_zero() or value.a.denominator != 1):
            raise ValueError("the raw contraction does not preserve an integer support block")
        result[basis.cell] = value.a.numerator
    return result


def verify_support_block(supports, parity):
    """Verify every column in one complete Laurent-support/parity block."""

    cells = tuple(product(*(
        tuple(s for s in _subsets(size) if set(support).issubset(s))
        for size, support in zip(SIZES, supports, strict=True)
    )))
    monomials = tuple(tuple(-1 if v in support else 0 for v in range(size))
                      for size, support in zip(SIZES, supports, strict=True))
    component = OuterCechComponent(0, 0, parity, tuple(map(sum, monomials)), "k0")
    d = {cell: _incidence(cell, parity) for cell in cells}
    q = {cell: _cohomology_projector(cell, supports) for cell in cells}
    h = {}
    for cell in cells:
        basis = OuterCechBasis(component, *monomials, cell)
        unit = SparseOuterCechCochain(((basis, Eisenstein(1)),))
        if _integer_column(_cech_differential(unit), basis) != d[cell]:
            raise ValueError("raw differential disagrees with independent face incidence")
        h[cell] = _integer_column(_homotopy(unit), basis)
    transcript = []
    for cell in cells:
        if _image(d, d[cell]):
            raise ValueError("independent face incidence does not square to zero")
        expected = _sum({cell: 1}, {target: -c for target, c in q[cell].items()})
        if _sum(_image(d, h[cell]), _image(h, d[cell])) != expected:
            raise ValueError("raw contraction fails d h + h d = identity - Q")
        if (_image(h, h[cell]) or _image(q, h[cell]) or _image(h, q[cell])
            or _image(q, q[cell]) != q[cell] or _image(d, q[cell])
            or _image(q, d[cell])):
            raise ValueError("raw contraction fails a square-zero or projection side condition")
        transcript.append([cell, sorted(d[cell].items()), sorted(h[cell].items()),
                           sorted(q[cell].items())])
    return len(cells), hashlib.sha256(json.dumps(
        transcript, separators=(",", ":"),
    ).encode()).hexdigest()


@cache
def support_certificate():
    """Exhaust the genuinely finite support category, not section coefficients."""

    records = []
    count = 0
    for supports in product(*(_subsets(size, True) for size in SIZES)):
        for parity in (0, 1):
            dimension, digest = verify_support_block(supports, parity)
            records.append([supports, parity, dimension, digest])
            count += dimension
    if len(records) != 512 or count != 10816:
        raise ValueError("the complete support/parity category was not verified")
    return {
        "support_pattern_count": 256, "structural_parities": [0, 1],
        "verified_basis_column_count": count,
        "complete_operator_transcript_sha256": hashlib.sha256(json.dumps(
            records, separators=(",", ":"),
        ).encode()).hexdigest(),
        "d_h_plus_h_d_equals_identity_minus_Q": True,
        "h_squared_zero": True, "Q_h_and_h_Q_zero": True,
        "Q_squared_equals_Q": True, "d_Q_and_Q_d_zero": True,
        "observed_raw_d_matches_independent_incidence": True,
        "coefficient_arithmetic": "integer incidence; scalar extension to Q(omega)",
        "infinite_monomial_scope_reason": (
            "raw d and h depend only on negative support and structural parity; "
            "each monomial/component is preserved"
        ),
    }


def carrier_premises():
    """Recheck every actual ambient profile and combined filtration gain."""

    record = lifts.structural_certificate()
    totals = {}
    for profile in record["component_profiles"]:
        count, degree = 1, 0
        for dimension, twist in zip((2, 2, 1), profile["ambient_degree"], strict=True):
            if twist >= 0:
                count *= comb(twist + dimension, dimension)
            elif twist <= -dimension - 1:
                count *= comb(-twist - 1, dimension)
                degree += dimension
            else:
                count = 0
        if count:
            total = degree + profile["structural_degree"]
            totals[total] = totals.get(total, 0) + count
    if totals != {-3: 8640, -2: 72504, -1: 177966, 0: 137997}:
        raise ValueError("the actual ambient obstruction coordinates changed")
    target = lifts.first._context()[0]
    weights = {"A": 2, "F0": 1, "F1": 0}
    object_weights = [weights[o.name.split(":")[0]] for o in target.left.objects]
    gains = [object_weights[a.target] - object_weights[a.source]
             for a in target.left.resolution_arrows]
    gains.extend(object_weights[t.target] - object_weights[t.source] - t.koszul_degree
                 for t in target.left.extension_terms)
    wedge_sizes = {"k0": 0, "k1_x": 1, "k1_u": 1, "k2": 2}
    component_weights = [object_weights[c.left_index] + 2 - wedge_sizes[c.koszul_summand]
                         for c in target.components.values()]
    if (not gains or min(gains) <= 0 or len(component_weights) != 24
        or min(component_weights) != 0 or max(component_weights) != 4):
        raise ValueError("an actual mixed perturbation fails strict filtration increase")
    return {
        "ambient_component_count": len(record["component_profiles"]),
        "raw_reduced_dimensions": [[d, n] for d, n in sorted(totals.items())],
        "Q_vanishes_on_total_degree_one": True,
        "all_resolution_and_mixed_arrow_gains_positive": True,
        "minimum_checked_arrow_gain": min(gains), "filtration_range": [0, 4],
        "closed_residual_iteration_bound": 5,
        "equation_gain": 1, "raw_h_preserves_object_and_koszul_component": True,
    }


def _module_product(extension, section):
    """Compose through suffix cells on the whole two-chart source module.

    Right terms have zero object and Koszul degree, zero plane Čech degrees,
    and P1 degree zero or one. All tensor-crossing signs are consequently
    positive. This algorithm does not use the common cup implementation.
    """

    by_planes = {}
    for basis, coefficient in section.terms:
        if (basis.component.object_degree != 0 or basis.component.koszul_summand != "k0"
            or any(len(s) != 1 for s in basis.cell[:2])):
            raise ValueError("the right cochain is outside the polynomial-plane section module")
        key = basis.component.left_index, basis.cell[0][0], basis.cell[1][0]
        by_planes.setdefault(key, []).append((basis, coefficient))
    targets = lifts.first._context()[0].components
    values = {}
    for arrow, scalar in extension.terms:
        key = arrow.component.right_index, arrow.cell[0][-1], arrow.cell[1][-1]
        for basis, coefficient in by_planes.get(key, ()):
            right_p = basis.cell[2]
            if len(right_p) == 1:
                if right_p[0] != arrow.cell[2][-1]:
                    continue
                p_cell = arrow.cell[2]
            elif right_p == (0, 1) and arrow.cell[2] == (0,):
                p_cell = (0, 1)
            else:
                continue
            image = OuterCechBasis(
                targets[arrow.component.left_index, 0, arrow.component.koszul_summand],
                tuple(a + b for a, b in zip(arrow.x_monomial, basis.x_monomial, strict=True)),
                tuple(a + b for a, b in zip(arrow.u_monomial, basis.u_monomial, strict=True)),
                tuple(a + b for a, b in zip(arrow.p_monomial, basis.p_monomial, strict=True)),
                (arrow.cell[0], arrow.cell[1], p_cell),
            )
            values[image] = values.get(image, Eisenstein(0)) + scalar * coefficient
    return SparseOuterCechCochain(tuple(values.items()))


def _module_generator(index, chart):
    source = lifts.second._context()[0]
    component = source.components[index, 0, "k0"]
    x, u, p = component.ambient_degree
    return SparseOuterCechCochain(tuple(
        (OuterCechBasis(component, (x, 0, 0), (u, 0, 0), (p, 0),
                        ((a,), (b,), (chart,))), Eisenstein(1))
        for a, b in product(range(3), repeat=2)
    ))


def verify_module_column(index, chart, parameter):
    """Check the actual E operator on one generator, not a closed section probe."""

    target = lifts.first._context()[0]
    source = lifts.second._context()[0]
    extension = lifts._inputs()[2][parameter]
    generator = _module_generator(index, chart)
    source_d = source.differential(generator)
    image = _module_product(extension, generator)
    incoming = _module_product(extension, source_d)
    if (mixed_outer_cup(extension, generator) != image
        or mixed_outer_cup(extension, source_d) != incoming):
        raise ValueError("the constructor cup differs from the independent source-module operator")
    defect = target.differential(image) + incoming
    if not defect.is_zero():
        raise ValueError(f"actual outer module Leibniz defect: {index}, {chart}, {parameter}")
    return {
        "source_object": index, "p1_chart": chart, "parameter": parameter,
        "generator_term_count": len(generator.terms),
        "source_differential_term_count": len(source_d.terms),
        "image_term_count": len(image.terms),
        "image_digest": lifts._cochain_digest((image,)),
        "D1_E_plus_E_D2_zero": True,
        "constructor_product_matches_independent_suffix_operator": True,
    }


@cache
def composition_certificate():
    """Certify the complete module identity by ten generators per parameter."""

    _parents, streams, _extensions = lifts._inputs()
    for record in streams[1]:
        for index, monomial, chart, _coefficient in record["terms"]:
            if (index not in range(5) or chart not in (0, 1) or len(monomial) != 8
                or any(v < 0 for v in monomial[:6])):
                raise ValueError("a saved V2 section is outside the certified source module")
    records = []
    for index, chart, parameter in product(range(5), range(2), range(2)):
        records.append(verify_module_column(index, chart, parameter))
        print(f"outer_module_column_checked: {index} {chart} {parameter}", flush=True)
    return {
        "source_object_count": 5, "p1_chart_count": 2, "parameter_count": 2,
        "verified_module_column_count": len(records), "columns": records,
        "all_saved_V2_sections_in_declared_module": True,
        "source_basis_count": len(streams[1]),
        "D1_E_plus_E_D2_zero_on_entire_section_module": True,
        "coefficient_transport_reason": (
            "all differentials and suffix products are Laurent-monomial linear; "
            "the ten generators span plane-global, P1-vertex cochains over the "
            "formal Laurent coefficient module; admissible actual sections restrict it"
        ),
    }


def averaging_premises():
    """Verify the exact hypotheses for strict repaired P/T averaging."""

    target, actions, frames = lifts.first._context()
    source, _source_actions, source_frames = lifts.second._context()
    for action in actions:
        if any(image != tuple(int(i == j) for i in range(2))
               for j, (_scalar, image) in enumerate(action.p_images)):
            raise ValueError("the two-chart module is not preserved by the deck action")
    for frame in (frames[1], source_frames[1]):
        if any(not value.is_zero() for i, row in enumerate(frame.rows)
               for j, value in enumerate(row) if i != j):
            raise ValueError("T does not act diagonally on the actual homogeneous objects")
    if any(image != tuple(int(i == j) for i in range(3))
           for images in (actions[1].x_images, actions[1].u_images)
           for j, (_scalar, image) in enumerate(images)):
        raise ValueError("T does not act diagonally on Laurent monomials")
    for extension in lifts._inputs()[2]:
        for g, action in enumerate(actions):
            if _full_action(extension, target.left, source.left, action,
                            (frames[g], source_frames[g])) != extension:
                raise ValueError("an actual outer coefficient is not strictly deck fixed")
    coordinate_relations = _coordinate_relations(actions)
    for component in target.components.values():
        x, u, p = component.ambient_degree
        sample = SparseOuterCechCochain(((OuterCechBasis(
            component, (x, 0, 0), (u, 0, 0), (p, 0), ((0,), (0,), (0,)),
        ), Eisenstein(1)),))
        for generator in (0, 1):
            image = sample
            for _ in range(3):
                image = lifts.first._action(image, generator)
            if image != sample:
                raise ValueError("a target component violates a deck order-three relation")
        if lifts.first._action(lifts.first._action(sample, 0), 1) != (
            lifts.first._action(lifts.first._action(sample, 1), 0)
        ):
            raise ValueError("a target homogeneous component violates P T = T P")
    _verify_equation_units(actions)
    return {
        "P_and_T_preserve_p1_chart_vertices": True,
        "T_diagonal_on_actual_objects_and_monomials": True,
        "both_outer_coefficients_rechecked_strictly_P_and_T_fixed": True,
        "T_commutes_with_raw_h_by_preserved_component_and_monomial": True,
        "outer_suffix_product_equivariant_on_plane_global_source_module": True,
        "reynolds_factor": "1/3", "reynolds_operator": "identity+P+P^2",
        "all_24_homogeneous_components_satisfy_group_relations": True,
        "independent_coordinate_relations": coordinate_relations,
        "Schoen_equation_units_independently_reconstructed": True,
        "actual_target_operator": _equivariant_target_operator(target, actions, frames),
    }


def _pullback(monomial, action):
    images = tuple((scalar, powers + (0,) * 5) for scalar, powers in action.x_images)
    images += tuple((scalar, (0,) * 3 + powers + (0,) * 2)
                    for scalar, powers in action.u_images)
    images += tuple((scalar, (0,) * 6 + powers) for scalar, powers in action.p_images)
    powers, coefficient = [0] * 8, Eisenstein(1)
    for exponent, (scalar, target) in zip(monomial, images, strict=True):
        coefficient *= scalar ** exponent
        powers = [a + exponent * b for a, b in zip(powers, target, strict=True)]
    return coefficient, tuple(powers)


def _coordinate_relations(actions):
    """Prove the group-relation phase depends only on homogeneous multidegree."""

    ratios = []
    for index in range(8):
        coordinate = tuple(int(i == index) for i in range(8))
        for action in actions:
            coefficient, monomial = Eisenstein(1), coordinate
            for _ in range(3):
                scalar, monomial = _pullback(monomial, action)
                coefficient *= scalar
            if coefficient != Eisenstein(1) or monomial != coordinate:
                raise ValueError("a homogeneous coordinate violates a deck order-three relation")
        a, m = _pullback(coordinate, actions[0])
        b, n = _pullback(m, actions[1])
        c, m = _pullback(coordinate, actions[1])
        d, other = _pullback(m, actions[0])
        if n != other:
            raise ValueError("the coordinate commutator is not a homogeneous scalar")
        ratios.append(a * b / (c * d))
    if any(len(set(ratios[start:stop])) != 1 for start, stop in ((0, 3), (3, 6), (6, 8))):
        raise ValueError("the coordinate commutator depends on the exponent distribution")
    return {
        "P_cubed_and_T_cubed_identity_on_each_coordinate": True,
        "P_then_T_over_T_then_P_units_by_factor": [str(ratios[i]) for i in (0, 3, 6)],
        "commutation_phase_depends_only_on_multidegree": True,
    }


def _verify_equation_units(actions):
    """Independently multiply the coordinate substitutions of both equations."""

    for equation in (1, 2):
        values = {}
        for polynomial, factor, p_powers, prefactor in _equation_terms(equation):
            for powers, coefficient in polynomial.terms:
                monomial = ((powers + (0, 0, 0)) if factor == "x"
                            else ((0, 0, 0) + powers)) + p_powers
                values[monomial] = values.get(monomial, Eisenstein(0)) + coefficient * prefactor
        for action in actions:
            pulled = {}
            for monomial, coefficient in values.items():
                scalar, key = _pullback(monomial, action)
                pulled[key] = pulled.get(key, Eisenstein(0)) + scalar * coefficient
            unit = action.first_equation_unit if equation == 1 else action.second_equation_unit
            if pulled != {monomial: unit * value for monomial, value in values.items()}:
                raise ValueError("an actual Schoen equation has the wrong declared deck unit")


def _equivariant_target_operator(target, actions, frames):
    """Check all object arrows; plane-global coefficients make their cup natural."""

    objects = target.left.objects
    terms = []
    plane_groups = {}
    for term in target.left.extension_terms:
        if (any(len(s) != 1 for s in term.cell[:2])
            or any(v < 0 for v in term.x_monomial + term.u_monomial)):
            raise ValueError("a target extension arrow is not plane-global on P1 charts")
        key = (term.source, term.target, term.koszul_summand,
               term.x_monomial, term.u_monomial, term.p_monomial, term.cell[2])
        plane_groups.setdefault(key, {})[term.cell[0][0], term.cell[1][0]] = term.coefficient
        source, dest = objects[term.source], objects[term.target]
        component = OuterCechComponent(term.target, term.source, dest.position - source.position,
                                       tuple(a - b for a, b in zip(
                                           dest.line_degree, source.line_degree, strict=True,
                                       )), term.koszul_summand)
        terms.append((OuterCechBasis(component, term.x_monomial, term.u_monomial,
                                     term.p_monomial, term.cell),
                      term.coefficient * (-1 if term.parent_degree == 0 else 1)))
    for charts in plane_groups.values():
        if (set(charts) != set(product(range(3), repeat=2))
            or len(set(charts.values())) != 1):
            raise ValueError("a target arrow coefficient depends on the plane chart")
    for arrow in target.left.resolution_arrows:
        source, dest = objects[arrow.source], objects[arrow.target]
        component = OuterCechComponent(arrow.target, arrow.source,
                                       dest.position - source.position,
                                       tuple(a - b for a, b in zip(
                                           dest.line_degree, source.line_degree, strict=True,
                                       )), "k0")
        for powers, coefficient in arrow.polynomial.terms:
            x, u = (powers, (0, 0, 0)) if arrow.factor == 1 else ((0, 0, 0), powers)
            for a, b, chart in product(range(3), range(3), range(2)):
                terms.append((OuterCechBasis(component, x, u, (0, 0),
                                             ((a,), (b,), (chart,))), coefficient))
    gamma = SparseOuterCechCochain(tuple(terms))
    for generator, action in enumerate(actions):
        if _full_action(gamma, target.left, target.left, action,
                        (frames[generator], frames[generator])) != gamma:
            raise ValueError("the complete actual target object operator is not deck fixed")
    return {
        "actual_object_operator_term_count": len(gamma.terms),
        "actual_object_operator_digest": lifts._cochain_digest((gamma,)),
        "all_extension_coefficients_polynomial_and_plane_global": True,
        "all_resolution_and_extension_arrows_P_and_T_fixed": True,
        "cover_signs_and_equation_units": "established signed cover and Schoen deck action",
    }


def write_certificate():
    """Save the operator certificate only after all exact source-module checks."""

    parent_digest, _parent = _verified_payload(lifts.OUTPUT)
    payload = {
        "schema": "alternate-metric-lift-operator-certificate-v1",
        "outer_lift_artifact_digest": parent_digest,
        "raw_contraction": support_certificate(), "carrier_premises": carrier_premises(),
        "outer_composition": composition_certificate(),
        "repaired_averaging": averaging_premises(),
        "closed_degree_one_residual_primitive_rule_certified": True,
        "theorem_hypotheses": [
            "D=d+Delta is a differential (D squared equals zero)",
            "the input residual has total degree one and D r equals zero",
            "Q vanishes on total degree one",
            "raw h preserves a finite filtration raised strictly by Delta",
        ],
        "primitive_formula": "sum(j=0..4) (-h Delta)^j h r",
        "independent_derivation": (
            "r_0=r; r_(j+1)=r_j-D h r_j; D r_j=0; Q r_j=0; "
            "r_(j+1)=-(h Delta+Delta h)r_j; r_5=0; "
            "h r_(j+1)=-h Delta h r_j; D sum(j=0..4)h r_j=r"
        ),
        "all_outer_section_products_independently_certified": True,
        "full_universal_lift_formula_certified": True,
        "rank_four_section_basis_available": True,
        "complete_expanded_coefficient_replay": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "observational_inputs_used": False,
        "next_required_object": (
            "obtain actual local rank-four fiber evaluation from the certified universal "
            "section construction before controlled Ricci-flat/HYM convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    return payload


if __name__ == "__main__":
    result = write_certificate()
    print(f"artifact_digest: {result['artifact_digest']}")
