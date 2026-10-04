"""Identify the proper failure locus of the original named metric fiber frame.

Owns:
    Exact local relation minors, their homogeneous failure numerator, a native
    nonvanishing witness, and the conditional full-measure chart/frame theorem.

Depends on:
    Original constituent relation cochains, the actual named quotient frame,
    exact polynomial determinants and the derived positive auxiliary law.

Must not:
    Equate a failed pivot with a singular bundle, discard finite-prefix failures,
    claim root-proposal termination, choose moduli or infer physical metrics.

Phase 0:
    Research geometric admission theorem only; numerical integration remains open.
"""

import hashlib
import json
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, determinant

from . import alternate_metric_bounded_fibers as bounded
from . import alternate_metric_symbolic_columns as symbolic

ROOT = symbolic.domains.ROOT
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_generic_frame.json"
PROOF = Path(__file__).with_name("ALTERNATE_METRIC_GENERIC_FRAME_NOTE.md")
CHART = (0, 0, 0)
FIRST_PIVOTS = (0, 2)
SECOND_PIVOTS = (0, 1, 2)


def _local_columns(context, cochains):
    """Extract the same local generators used by local_coordinates, symbolically."""

    rows = [[] for obj in context.left.objects if obj.position == 0]
    for cochain in cochains:
        terms = [[] for _ in rows]
        for basis, coefficient in cochain.terms:
            component = basis.component
            key = component.left_index, component.right_index, component.koszul_summand
            if context.components.get(key) != component:
                raise ValueError("an original local relation uses a foreign component")
            if (basis.cell != tuple((i,) for i in CHART)
                or component.koszul_summand != "k0"
                or context.left.objects[component.left_index].position != 0):
                continue
            exponents = basis.x_monomial + basis.u_monomial + basis.p_monomial
            normalized = tuple(0 if i in (0, 3, 6) else e for i, e in enumerate(exponents))
            if any(e < 0 for e in normalized):
                raise ValueError("a relation pole escaped the declared inverted chart pivots")
            terms[component.left_index].append((normalized, coefficient))
        for row, coefficients in zip(rows, terms, strict=True):
            row.append(Polynomial(coefficients, variable_count=8, scalar_type=Eisenstein))
    return tuple(tuple(row) for row in rows)


@cache
def local_relations():
    """Reuse actual differential/cup columns; no section lifting is repeated."""

    first, second, relations, outer = bounded._relation_cochains(CHART)
    b1, b2 = tuple(_local_columns(context, columns) for context, columns in zip(
        (first, second), relations, strict=True,
    ))
    extensions = tuple(_local_columns(first, columns) for columns in outer)
    if (len(b1), len(b1[0]), len(b2), len(b2[0])) != (4, 2, 5, 3):
        raise ValueError("the actual constituent relation ordering changed")
    return b1, b2, extensions


def frame_minors():
    """Return the two exact determinants in the already declared pivot order."""

    b1, b2, _ = local_relations()
    return (determinant(tuple(b1[i] for i in FIRST_PIVOTS)),
            determinant(tuple(b2[i] for i in SECOND_PIVOTS)))


def homogeneous_numerator(polynomial):
    """Homogenize a chart polynomial, recording rather than guessing its degrees."""

    if (not isinstance(polynomial, Polynomial) or polynomial.variable_count != 8
        or polynomial.scalar_type is not Eisenstein or polynomial.is_zero()
        or any(m[i] for m, _ in polynomial.terms for i in (0, 3, 6))):
        raise ValueError("a nonzero exact polynomial in the declared normalized chart required")
    degrees = tuple(max(sum(m[lo:hi]) for m, _ in polynomial.terms)
                    for lo, hi in ((0, 3), (3, 6), (6, 8)))
    terms = []
    for powers, coefficient in polynomial.terms:
        lifted = list(powers)
        for degree, lo, hi in zip(degrees, (0, 3, 6), (3, 6, 8), strict=True):
            lifted[lo] = degree - sum(powers[lo:hi])
        terms.append((tuple(lifted), coefficient))
    return Polynomial(terms, variable_count=8, scalar_type=Eisenstein), degrees


def _polynomial_record(polynomial):
    return [[list(m), [str(c.a), str(c.b)]] for m, c in polynomial.terms]


def generic_frame_record():
    """Check native nonvanishing before recording the conditional null-locus theorem."""

    before = symbolic._source_signature()
    identity = symbolic.section_basis_identity()
    if identity["artifact_digest"] != (
        "71f9c2f46c1f7a69087e8f3aab1ed98f4474cf76cf66db5bf2c902f4f372621c"
    ):
        raise ValueError("the original section and carrier source identity changed")
    law_digest, law = bounded.fiber._verified_payload(
        OUTPUT.with_name("alternate_metric_positive_measure.json"))
    if law_digest != "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e":
        raise ValueError("the actual positive auxiliary law changed")
    if law["component_probabilities"] != ["3/4", "1/8", "1/8"]:
        raise ValueError("the intersection-derived mixture probabilities changed")
    if hashlib.sha256((ROOT / law["proof"]).read_bytes()).hexdigest() != law["proof_sha256"]:
        raise ValueError("the positive auxiliary law proof changed")
    name, branch, frame = symbolic.domains.declared_frames()[0]
    if (name != "A" or branch != (0, 0) or frame.point.chart != CHART
        or frame.first_pivots != FIRST_PIVOTS or frame.second_pivots != SECOND_PIVOTS):
        raise ValueError("the original native nonvanishing witness frame changed")
    first, second = frame_minors()
    product = first * second
    numerator, degrees = homogeneous_numerator(product)
    coordinates = (*frame.point.x, *frame.point.u, *frame.point.p)
    values = tuple(symbolic._bounded_polynomial_value(p, coordinates)
                   for p in (first, second, product))
    if any(value.center.norm() <= value.radius**2 for value in values):
        raise ValueError("the actual coupled witness does not prove nonvanishing")
    if symbolic._source_signature() != before:
        raise ValueError("an original relation or witness source changed during the check")
    return {
        "schema": "alternate-metric-generic-frame-v1",
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "source_signature": before,
        "original_section_basis_digest": identity["artifact_digest"],
        "positive_auxiliary_law_digest": law_digest,
        "positive_auxiliary_law_proof_sha256": law["proof_sha256"],
        "assumptions": ["the selected cover is smooth, compact and irreducible",
                        "the derived auxiliary law is beta^3/72 with beta positive",
                        "the original constituent and universal outer relation data"],
        "variable_order": list(symbolic.VARIABLES), "chart_pivots": list(CHART),
        "first_pivot_rows": list(FIRST_PIVOTS), "second_pivot_rows": list(SECOND_PIVOTS),
        "first_relation_minor": _polynomial_record(first),
        "second_relation_minor": _polynomial_record(second),
        "homogeneous_failure_numerator": _polynomial_record(numerator),
        "homogeneous_numerator_degrees": list(degrees),
        "excluded_set": "x0*u0*p0=0 or homogeneous_failure_numerator=0 on the cover",
        "quotient_excluded_set": "image of the excluded set; pullback is the finite deck union",
        "nonvanishing_native_witness": {
            "component": name, "root_pair": list(branch),
            "role": "whole coupled geometric regression; not a chosen physical point",
            "coordinate_bounds": [[bounded.bounds._ball_record(c) for c in group]
                                  for group in (frame.point.x, frame.point.u, frame.point.p)],
            "minor_bounds_first_second_product": [bounded.bounds._ball_record(v) for v in values],
        },
        "full_five_relation_minor_is_product_for_all_parameters": True,
        "fixed_chart_and_frame_failure_is_auxiliary_null": True,
        "single_named_frame_claimed_deck_invariant": False,
        "fixed_frame_failure_is_physical_bundle_singularity": False,
        "all_cover_points_in_named_chart": False,
        "finite_prefix_failures_discardable": False,
        "native_solver_almost_sure_termination_proved": False,
        "global_numerical_input_coverage_certified": False,
        "independent_cover_cloud_available": False, "controlled_integral_available": False,
        "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False, "physical_moduli_selected": False,
        "observations_used": False,
    }


def write_generic_frame(path=OUTPUT):
    record = generic_frame_record()
    record["artifact_digest"] = hashlib.sha256(symbolic.archive._canonical(record)).hexdigest()
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_generic_frame(*, expected_digest, path=OUTPUT):
    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if digest != expected_digest or digest != hashlib.sha256(
        symbolic.archive._canonical(record)).hexdigest():
        raise ValueError("the generic frame record differs from its trusted digest")
    if symbolic.archive._canonical(record) != symbolic.archive._canonical(generic_frame_record()):
        raise ValueError("the actual generic frame theorem changed its source, witness or scope")
    return {"artifact_digest": digest, **record}


if __name__ == "__main__":
    print(write_generic_frame()["artifact_digest"])
