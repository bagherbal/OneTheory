"""Restrict the frozen alternate carrier to its exceptional-section curves.

Owns:
    Exact finite-algebra embeddings, free deck orbits, normal Euler sequences,
    and actual Serre-class pullbacks on all paired pencil base points.

Depends on:
    The existing pencil quotient algebra, frozen Schoen equations, full actual
    constituent cochains, certified alternate carrier, and exact matrix arithmetic.

Must not:
    Substitute these curves for missing conics, choose numerical roots or outer
    parameters, normalize a Pfaffian, construct hidden factors, or claim a vacuum.

Phase 0:
    Conditional research restrictions only; physical determinant data remain open.
"""

import json
from functools import cache
from hashlib import sha256
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.pencil import (
    QuotientPolynomial,
    _apply_polynomial,
    tier_a_pencil_model,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from .alternate_metric_quotient_generation import _second_constituent
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_section_curve_restrictions.json"
PROOF = Path(__file__).with_name("ALTERNATE_SECTION_CURVE_RESTRICTIONS_NOTE.md")
CARRIER = OUTPUT.with_name("alternate_constituent_carrier_state.json")
CONE = OUTPUT.with_name("alternate_constituent_outer_universal_cone.json")
PARENTS = {
    "carrier": "d525c9fb44764f8dee8fd54a449b3aa584c6e4b15786f6b4f2a26011a3541c08",
    "cone": "b7c4327d8c1ee197f431cf05eebb38f38746a2a4eaf21440ac4338b051ce3fca",
}


def _canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def _sources():
    """Pin the critical implementation paths without changing any source artifact."""

    paths = [
        "src/onetheory/math/numbers.py", "src/onetheory/math/linear.py",
        "src/onetheory/math/polynomials.py", "src/onetheory/models/heterotic_schoen/geometry.py",
        "research/experiments/computable_carrier/pencil.py",
        "research/experiments/computable_carrier/schoen_sparse_actions.py",
        "research/experiments/scientific_genesis/published_constituent_full_cech.py",
        "research/experiments/scientific_genesis/published_constituent_ray_alignment.py",
        "research/experiments/scientific_genesis/published_constituent_deck_actions.py",
        "research/experiments/scientific_genesis/distinct_constituent_ray_screen.py",
        "research/experiments/scientific_genesis/mixed_constituent_schoen_arrows.py",
        "research/experiments/scientific_genesis/alternate_metric_quotient_generation.py",
        str(Path(__file__).relative_to(ROOT)), str(PROOF.relative_to(ROOT)),
    ]
    return {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}


@cache
def _contexts():
    return tier_a_pencil_model(), (mixed_schoen_constituents()[0], _second_constituent())


def _qrecord(value):
    return [[m[0], [str(c.a), str(c.b)]] for m, c in value.representative.terms]


def multiplication_matrix(value):
    """Use the explicit basis (1,z,...,z^8) of the existing quotient algebra."""

    n = value.modulus.univariate_degree
    z = QuotientPolynomial(value.modulus, Polynomial.monomial((1,), scalar_type=Eisenstein))
    columns = tuple((value * z**i).representative for i in range(n))
    return Matrix(tuple(tuple(p.coefficient((row,)) for p in columns)
                        for row in range(n)), scalar_type=Eisenstein)


def unit_inverse(value):
    """Construct and check an actual inverse; a nonunit has no fallback."""

    matrix = multiplication_matrix(value)
    inverse = matrix.inverse()
    result = QuotientPolynomial(value.modulus, Polynomial.from_coefficients(
        tuple(row[0] for row in inverse.rows), scalar_type=Eisenstein))
    if value * result != QuotientPolynomial.one(value.modulus):
        raise ValueError("the exact basepoint inverse failed")
    return result


def _base_value(monomial, coordinates, inverses):
    result = QuotientPolynomial.one(coordinates[0].modulus)
    for power, coordinate, inverse in zip(monomial, coordinates, inverses, strict=True):
        result = result * (coordinate**power if power >= 0 else inverse**(-power))
    return result


def restricted_class(constituent, base, *, vertex, generator_index):
    """Pull back the actual Ext class in an explicitly named chart and quotient split."""

    if type(vertex) is not int or vertex not in (0, 1, 2):
        raise ValueError("an explicit original plane vertex is required")
    extension = constituent.full.alignment.action.derived.extension
    generators = extension.scheme.resolution.generators
    if type(generator_index) is not int or not 0 <= generator_index < len(generators):
        raise ValueError("an explicit original quotient generator index is required")
    if any(item.line_degree[2] != (-1 if index == 0 else 1)
           for index, item in enumerate(constituent.objects)):
        raise ValueError("the actual restricted Serre line degrees changed")
    if not constituent.full.full_closed:
        raise ValueError("the actual full constituent class is not closed")
    coordinates = (base.coordinate_x, base.coordinate_y, QuotientPolynomial.one(base.modulus))
    inverses = tuple(unit_inverse(c) for c in coordinates)
    g = tuple(QuotientPolynomial(base.modulus, p.substitute(tuple(
        c.representative for c in coordinates))) for p in generators)
    h = [QuotientPolynomial.zero(base.modulus) for _ in generators]
    for basis, coefficient in constituent.full.representative.terms:
        if (basis.component.parent_degree != 0 or basis.component.koszul_degree != 0
            or basis.cell != ((vertex,), (0, 1))):
            continue
        if sum(basis.fiber_monomial) != -2:
            raise ValueError("the actual O(-2) Ext coefficient grading changed")
        if basis.fiber_monomial == (-1, -1):
            i = basis.component.bundle_index
            h[i] = h[i] + _base_value(basis.base_monomial, coordinates, inverses).scale(coefficient)
    if not all(a*b == c*d for a, d in zip(h, g, strict=True)
               for c, b in zip(h, g, strict=True)):
        raise ValueError("the restricted Ext row does not factor through the actual ideal quotient")
    # Every original monomial generator must remain a unit, not only the chosen one.
    generator_inverses = tuple(unit_inverse(value) for value in g)
    delta = h[generator_index] * generator_inverses[generator_index]
    if delta.is_zero or base.modulus.gcd(delta.representative).univariate_degree != 0:
        raise ValueError("a nonunit Ext class needs a splitting-stratum calculation")
    return delta, unit_inverse(delta), g, tuple(h)


def _group_images(model):
    base = model.base_locus
    if not model.actions_commute or not all(a.order_three for a in model.actions):
        raise ValueError("the actual pencil action is not the declared order-nine action")
    images = []
    for p in range(3):
        for t in range(3):
            image = base.coordinate_x
            for action, power in zip(model.actions, (p, t), strict=True):
                for _ in range(power):
                    image = _apply_polynomial(action.image_x, image)
            image_y = _apply_polynomial(base.coordinate_y, image)
            images.append(((p, t), image, image_y))
    return tuple(images)


def free_basepoint_actions(model):
    """Test eight exact fixed-point ideals, not approximate eigenvectors or roots."""

    base = model.base_locus
    records = []
    for (p, t), image, image_y in _group_images(model):
        if (p, t) != (0, 0):
            gcd = base.modulus.gcd((image-base.coordinate_x).representative).gcd(
                (image_y-base.coordinate_y).representative)
            if gcd != Polynomial.one(1, scalar_type=Eisenstein):
                raise ValueError("a basepoint stabilizer obstructs the claimed quotient curves")
            records.append({"exponents": [p, t], "image_x": _qrecord(image),
                            "image_y": _qrecord(image_y), "fixed_point_ideal_gcd_degree": 0})
    return records


def actual_deck_identification(model):
    """Match both ACTUAL Schoen factor actions to the checked finite-algebra group."""

    base = model.base_locus
    coordinates = (base.coordinate_x, base.coordinate_y, QuotientPolynomial.one(base.modulus))
    inverses = tuple(unit_inverse(c) for c in coordinates)
    group = _group_images(model)
    records, first_pairs = [], []
    for action in schoen_sparse_deck_actions():
        factors = []
        for images in (action.x_images, action.u_images):
            homogeneous = tuple(_base_value(m, coordinates, inverses).scale(c) for c, m in images)
            pivot_inverse = unit_inverse(homogeneous[2])
            x, y = (homogeneous[i]*pivot_inverse for i in (0, 1))
            matches = [pair for pair, gx, gy in group if (x, y) == (gx, gy)]
            if len(matches) != 1:
                raise ValueError("an actual Schoen deck generator left the checked pencil group")
            factors.append({"pencil_exponents": list(matches[0]),
                            "image_x": _qrecord(x), "image_y": _qrecord(y)})
        first_pairs.append(factors[0]["pencil_exponents"])
        records.append({"actual_generator": action.name, "first_factor": factors[0],
                        "second_factor": factors[1]})
    if len(first_pairs) != 2 or (
        first_pairs[0][0]*first_pairs[1][1]-first_pairs[0][1]*first_pairs[1][0]) % 3 == 0:
        raise ValueError("the actual first-factor generators do not generate the checked group")
    return records


def restriction_record():
    """Reproduce the complete stated restriction family without a physical amplitude."""

    before = _sources()
    for name, path in (("carrier", CARRIER), ("cone", CONE)):
        digest, record = _verified_payload(path)
        if digest != PARENTS[name]:
            raise ValueError("the frozen alternate restriction parent changed")
        if name == "carrier" and record["computable_one_theory_carrier_state"][
                "component_id"] != "alternate-i6-ray-0-1-P1":
            raise ValueError("the curve calculation changed its actual carrier")
    model, constituents = _contexts()
    base = model.base_locus
    if base.degree != 9 or not base.reduced_and_transverse or not base.boundary_empty:
        raise ValueError("the actual nine-point transverse pencil algebra is unavailable")
    coordinates = (base.coordinate_x.representative, base.coordinate_y.representative,
                   Polynomial.one(1, scalar_type=Eisenstein))
    cox = schoen_geometry().cover.cox
    if cox.equations != ("p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)"):
        raise ValueError("the two actual frozen equation presentations changed")
    if any(not QuotientPolynomial(base.modulus, f.substitute(coordinates)).is_zero
           for f in (cox.cubic_f, cox.cubic_g)):
        raise ValueError("the actual exceptional-section embeddings leave the frozen pencils")
    affine = tuple(f.substitute((Polynomial.monomial((1, 0), scalar_type=Eisenstein),
                                 Polynomial.monomial((0, 1), scalar_type=Eisenstein), 1))
                   for f in (cox.cubic_f, cox.cubic_g))
    jacobian = affine[0].derivative(0)*affine[1].derivative(1) - (
        affine[0].derivative(1)*affine[1].derivative(0))
    j = QuotientPolynomial(base.modulus, jacobian.substitute(coordinates[:2]))
    jacobian_inverse = unit_inverse(j)
    records = []
    for constituent in constituents:
        delta, inverse, generators, h = restricted_class(
            constituent, base, vertex=2, generator_index=0)
        for vertex in (0, 1):
            if restricted_class(constituent, base, vertex=vertex, generator_index=0)[0] != delta:
                raise ValueError("the actual plane Čech charts disagree on the restricted class")
        determinant = multiplication_matrix(delta).determinant()
        records.append({"constituent": constituent.name, "surface_factor": constituent.factor,
            "source_character": [str(c) for c in constituent.full.alignment.source_character],
            "full_cochain_sha256": sha256(
                repr(constituent.full.representative).encode()).hexdigest(),
            "plane_vertex": 2, "quotient_generator_index": 0,
            "actual_ideal_generators": [_qrecord(g) for g in generators],
            "actual_ext_coefficient_row": [_qrecord(value) for value in h],
            "restricted_ext_class": _qrecord(delta), "restricted_ext_inverse": _qrecord(inverse),
            "multiplication_determinant": [str(determinant.a), str(determinant.b)],
            "all_three_plane_charts_agree": True, "restricted_splitting_degrees": [0, 0]})
    splitting = tuple(d for result in records for d in result["restricted_splitting_degrees"])
    spin_twist = -1
    record = {"schema": "alternate-section-curve-restrictions-v1",
        "prerequisite_artifact_digests": PARENTS, "source_sha256": before,
        "coefficient_algebra_basis": ["1", *(f"z^{i}" for i in range(1, base.degree))],
        "modulus": [
            [m[0], [str(c.a), str(c.b)]] for m, c in base.modulus.terms],
        "coordinate_x": _qrecord(base.coordinate_x), "coordinate_y": _qrecord(base.coordinate_y),
        "two_basepoint_factors_are_independent": True,
        "cover_curve_count": base.degree**2, "quotient_curve_count": base.degree**2 // 9,
        "embedding": "((X:Y:1),(U:V:1),(p0:p1)); independent basepoint factors",
        "both_frozen_equations_vanish_identically": True,
        "jacobian": _qrecord(j), "jacobian_inverse": _qrecord(jacobian_inverse),
        "normal_bundle_degrees": [-1, -1], "deck_fixed_point_checks": free_basepoint_actions(model),
        "actual_schoen_deck_identification": actual_deck_identification(model),
        "quotient_map_degree_on_each_cover_curve": 1, "constituents": records,
        "whole_frozen_outer_parameter_family": True, "outer_extension_point_selected": False,
        "visible_restricted_splitting_degrees": list(splitting),
        "visible_spin_twist_degree": spin_twist,
        "visible_spin_twisted_h0": sum(max(d+spin_twist+1, 0) for d in splitting),
        "visible_spin_twisted_h1": sum(max(-d-spin_twist-1, 0) for d in splitting),
        "missing_seed_conic_embeddings_supplied": False,
        "physical_pfaffian_amplitude_available": False,
        "hidden_restrictions_available": False, "instanton_sum_available": False,
        "quillen_normalization_available": False,
        "torsion_or_b_field_cancellation_evaluated": False,
        "common_stabilized_vacuum_available": False, "physical_yukawas_available": False,
        "genesis_to_uv_derivation_available": False, "observations_used": False,
        "conditional_on": "selected heterotic realization and frozen alternate carrier"}
    if _sources() != before:
        raise ValueError("an actual restriction source changed during computation")
    record["artifact_digest"] = sha256(_canonical(record)).hexdigest()
    return record


def write_restrictions():
    record = restriction_record()
    text = json.dumps(record, sort_keys=True, indent=2) + "\n"
    if OUTPUT.exists() and OUTPUT.read_text() != text:
        raise ValueError("refusing to overwrite different curve restriction evidence")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    return record


def read_restrictions(*, expected_digest):
    record = json.loads(OUTPUT.read_text())
    unsigned = dict(record)
    digest = unsigned.pop("artifact_digest", None)
    if digest != expected_digest or digest != sha256(_canonical(unsigned)).hexdigest():
        raise ValueError("the exact curve restrictions changed their trusted digest")
    if record != restriction_record():
        raise ValueError("the actual curve restriction sources or scientific scope changed")
    return record


if __name__ == "__main__":
    print(write_restrictions()["artifact_digest"])
