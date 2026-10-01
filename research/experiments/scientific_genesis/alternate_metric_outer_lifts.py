"""Construct universal outer lifts of the actual metric-twist sections.

Owns:
    A finite full-cover lifting formula, the actual positive-degree ambient
    obstruction check, and exact parameterwise section access without an
    extension-point choice.

Depends on:
    Both certified constituent section archives, the frozen alternate outer
    cocycles, repaired deck frames, and the existing tensor-cover homotopy.

Must not:
    Replace the nonsplit bundle by a direct sum, infer metrics from a basis
    formula, conceal a failed residual, or claim complete independent replay.

Phase 0:
    Research-only universal section construction; numerical physics is open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass
from functools import cache

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_DEGREES,
    SparseOuterCechCochain,
)

from . import alternate_metric_first_serre_lifts as first
from . import alternate_metric_second_sections as second
from .alternate_constituent_outer_universal_cone import INVARIANTS
from .alternate_metric_subbundle_vanishing import _ambient_profile
from .mixed_schoen_common_dga import mixed_outer_cup, perturbed_homotopy
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload

OUTPUT = first.ROOT / "data/generated/scientific_genesis/alternate_metric_outer_lifts.json"


@cache
def _inputs():
    """Verify the saved inputs before decoding their complete section streams."""

    parents = {}
    streams = []
    for name, module, count in (("first", first, 2655), ("second", second, 2690)):
        digest, record = _verified_payload(module.OUTPUT)
        archive = (first.ROOT / record["section_archive"]).read_bytes()
        raw = gzip.decompress(archive)
        if (hashlib.sha256(archive).hexdigest() != record["section_archive_sha256"]
            or hashlib.sha256(raw).hexdigest() != record["exact_section_stream_sha256"]
            or record["section_dimension"] != count):
            raise ValueError("a complete actual constituent section archive changed")
        stream = json.loads(raw)
        if len(stream) != count:
            raise ValueError("a constituent section stream is incomplete")
        parents[name] = digest
        streams.append(stream)
    digest, invariant = _verified_payload(INVARIANTS)
    cone_digest, cone = _verified_payload(second.CONE)
    if (cone["invariant_artifact_digest"] != digest
        or cone["common_flat_character_twist"] != [1, 2]
        or cone["ray_character_exponents"] != [0, 1]
        or invariant["invariant_ext1_dimension"] != 2):
        raise ValueError("the actual alternate universal outer basis changed")
    extensions = tuple(_representative(raw)
                       for raw in invariant["strict_full_cech_representatives"])
    if len(extensions) != 2:
        raise ValueError("both universal parameter coefficients are required")
    parents.update(invariants=digest, cone=cone_digest)
    return parents, tuple(streams), extensions


def _compact(record):
    return tuple(((index, tuple(m), chart), tuple(value))
                 for index, m, chart, value in record["terms"])


@cache
def structural_certificate() -> dict[str, object]:
    """Check all ambient components and every source arrow of the finite bound."""

    contraction = first._context()[0]
    weights = tuple(2 if o.name == "A" else 1 if o.name.startswith("F0:") else 0
                    for o in contraction.left.objects)
    if weights != (2, 1, 1, 1, 0, 0) or not contraction.left.exact:
        raise ValueError("the actual first-constituent resolution changed")
    arrows = (*contraction.left.resolution_arrows, *contraction.left.extension_terms)
    if any(weights[a.target] <= weights[a.source] for a in arrows):
        raise ValueError("a first-constituent arrow does not raise the finite filtration")
    if any(weights[a.target] - weights[a.source] <= a.koszul_degree
           for a in contraction.left.extension_terms):
        raise ValueError("a mixed extension wedge does not raise the combined filtration")
    if contraction.right.extension_terms or contraction.right.resolution_arrows:
        raise ValueError("the metric section target must have the trivial right unit")
    profiles = []
    dimensions = {}
    for key, component in sorted(contraction.components.items()):
        ambient = _ambient_profile(component.ambient_degree)
        profiles.append({"component": list(key), "ambient_degree": list(component.ambient_degree),
                         "structural_degree": component.structural_degree,
                         "ambient_h0_to_h5": list(ambient)})
        for degree, count in enumerate(ambient):
            if count:
                total = degree + component.structural_degree
                dimensions[total] = dimensions.get(total, 0) + count
    if any(degree > 0 for degree in dimensions):
        raise ValueError("positive-degree ambient obstruction coordinates are present")
    if set(KOSZUL_DEGREES.values()) != {0, -1, -2}:
        raise ValueError("the two-equation Koszul filtration changed")
    return {
        "twist_cover_degree": [14, 16, 1], "component_profiles": profiles,
        "raw_reduced_dimensions": [[d, n] for d, n in sorted(dimensions.items())],
        "raw_reduced_degree_one_dimension": dimensions.get(1, 0),
        "object_filtration_weights": list(weights),
        "filtration_range": [0, 4], "h_delta_nilpotence_bound": 5,
        "resolution_arrow_count": len(contraction.left.resolution_arrows),
        "extension_term_count": len(contraction.left.extension_terms),
        "all_object_arrows_strictly_raise_weight": True,
        "formula": "h' = sum(j=0..4) (-h Delta)^j h; b_i = -Reynolds(h'(e_i cup s))",
        "cochain_contraction_sign": "d h + h d = identity - inclusion projection",
        "proof_source": "https://arxiv.org/abs/math/0403266",
    }


@dataclass(frozen=True, slots=True)
class UniversalMetricSection:
    """One actual section written in the declared universal extension blocks."""

    basis_index: int
    first_constant: SparseOuterCechCochain
    second_constant: SparseOuterCechCochain
    first_coefficients: tuple[SparseOuterCechCochain, SparseOuterCechCochain]
    homotopy_depths: tuple[int, int]


def lift_coefficient(section: SparseOuterCechCochain, parameter: int):
    """Return the checked coefficient of a0 or a1, without specializing either."""

    if type(parameter) is not int or parameter not in (0, 1):
        raise ValueError("the parameter index must name a0 or a1")
    structural_certificate()
    if (any(b.total_degree != 0 for b, _c in section.terms)
        or not second._context()[0].differential(section).is_zero()
        or any(second.full_action(section, g) != section for g in (0, 1))):
        raise ValueError("the actual V2 input is not a closed invariant degree-zero section")
    extension = _inputs()[2][parameter]
    residual = mixed_outer_cup(extension, section)
    target = first._context()[0]
    if not target.differential(residual).is_zero():
        raise ValueError("the actual outer-section residual is not closed")
    primitive, depth = perturbed_homotopy(residual, target)
    if depth > 5 or not (target.differential(primitive) + residual.scale(-1)).is_zero():
        raise ValueError("the finite outer-section primitive failed its exact identity")
    # T is diagonal on monomials and objects, so it commutes with the raw
    # contraction. Validate that premise before using the shorter P average.
    if first._action(primitive, 1) != primitive:
        raise ValueError("the primitive is not T fixed; the reduced Reynolds rule is invalid")
    p = first._action(primitive, 0)
    p2 = first._action(p, 0)
    if first._action(p2, 0) != primitive:
        raise ValueError("the primitive's actual P action does not have order three")
    correction = (primitive + p + p2).scale(Eisenstein(-1) / 3)
    if (not (target.differential(correction) + residual).is_zero()
        or any(first._action(correction, g) != correction for g in (0, 1))):
        raise ValueError("the invariant universal outer coefficient failed closure or descent")
    return correction, depth, residual


def universal_section(index: int) -> UniversalMetricSection:
    """Construct any of the 5345 basis sections as exact full-cover cochains."""

    if type(index) is not int or not 0 <= index < 5345:
        raise ValueError("a universal basis index must be an integer in range(5345)")
    _parents, streams, _extensions = _inputs()
    zero = SparseOuterCechCochain()
    if index < 2655:
        constant = first.expand_section(_compact(streams[0][index]))
        return UniversalMetricSection(index, constant, zero, (zero, zero), (0, 0))
    section = second.expand_section(_compact(streams[1][index - 2655]))
    coefficients = tuple(lift_coefficient(section, p) for p in (0, 1))
    return UniversalMetricSection(index, zero, section,
                                  (coefficients[0][0], coefficients[1][0]),
                                  (coefficients[0][1], coefficients[1][1]))


def write_outer_lifts() -> dict[str, object]:
    """Record the structural formula and actual coefficient probes, with scope."""

    parents, _streams, _extensions = _inputs()
    probes = []
    for second_index in (0, 1135):
        section = universal_section(2655 + second_index)
        probes.append({"second_basis_index": second_index,
                       "second_constant_term_count": len(section.second_constant.terms),
                       "second_constant_digest": _cochain_digest((section.second_constant,)),
                       "coefficient_term_counts": [len(c.terms)
                                                   for c in section.first_coefficients],
                       "coefficient_digests": [_cochain_digest((c,))
                                               for c in section.first_coefficients],
                       "homotopy_depths": list(section.homotopy_depths),
                       "all_coefficientwise_cone_identities_exact": True,
                       "all_corrections_strictly_invariant": True})
        print(f"universal_outer_probe_completed: {second_index}", flush=True)
    payload = {
        "schema": "alternate-metric-outer-lift-formula-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "parameter_basis": ["a0", "a1"],
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": parents,
        "structural_certificate": structural_certificate(),
        "basis_index_blocks": [[0, 2655, "V1 injection"], [2655, 5345, "universal V2 lifts"]],
        "reynolds_normalization": "1/3 times (identity+P+P^2), with T fixation checked",
        "basis_dimension": 5345,
        "universal_section_constructor_available": True,
        "complete_independent_rank_four_basis_replay": False,
        "rank_four_section_basis_available": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "actual_coefficient_probes": probes,
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    temporary.replace(OUTPUT)
    return payload


if __name__ == "__main__":
    report = write_outer_lifts()
    print(f"artifact_digest: {report['artifact_digest']}")
