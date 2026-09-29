"""Evaluate the natural quotient product on complete actual null matter lifts.

Owns:
    Coefficientwise pushout matter and Higgs lifts, the corrected quotient
    product, full scalar closure, and explicitly ordered cover residues.

Depends on:
    The certified coupled presentation, fixed global minor quotient,
    actual matter corrections, and archived full Higgs primitives.

Must not:
    Substitute an earlier scalar screen, select an extension point, insert
    a quotient trace factor, or call a null-channel scalar a full matrix.

Phase 0:
    Research-only evaluation; determinant descent and physical normalization
    remain separate gates even when a complete cover scalar is obtained.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from .alternate_up_coupled_tensor_comparison import OUTPUT as COMPARISON
from .alternate_up_coupled_tensor_comparison import _push_f_vector, alternate_coupled_quotient
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_exterior_higgs_action import alternate_up_exterior_context
from .alternate_up_first_order_scalar import alternate_null_matter, null_matter_correction
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_covector,
    alternate_higgs_quotient_models,
)
from .alternate_up_mixed_scalar_trace import _scalar_context
from .alternate_up_pairing_exchange import OUTPUT as PRIMITIVES
from .alternate_up_pairing_exchange import (
    _cochain_record,
    direct_ordered_scalar_residue,
    load_alternate_up_pairing_cochains,
)
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup, mixed_outer_cup_coefficient
from .mixed_schoen_coupled_tensor import CoupledExteriorQuotient, coupled_quotient_vector_wedge
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload
from .mixed_schoen_rank_one_tensor import rank_one_vector_wedge

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_coupled_null_scalar.json"


def _require_zero(cochain: SparseOuterCechCochain, label: str) -> None:
    if not cochain.is_zero():
        raise ValueError(
            f"{label}: {len(cochain.terms)} terms; digest {_cochain_digest((cochain,))}"
        )


def quotient_block_indices(model: CoupledExteriorQuotient) -> tuple[dict[int, int], dict[int, int]]:
    """Return explicit old-K and exterior-F indices in the actual Q basis."""

    if (model.inner_target, model.outer_target) != (1, 0):
        raise ValueError("the actual quotient block map requires the declared B-first basis")
    exterior, _ = alternate_up_exterior_context()
    pairs = {pair: i for i, pair in enumerate(exterior.pairs)}
    ideal, full = {}, {}
    for i, (a, b) in enumerate(model.quotient.pairs):
        if a == 0:
            if b < 2:
                raise ValueError("the killed B wedge A relation reappeared in Q")
            ideal[b - 2] = i
        else:
            full[pairs[(a - 1, b - 1)]] = i
    if len(ideal) != 7 or len(full) != 31:
        raise ValueError("the actual quotient block basis changed")
    return ideal, full


def retarget_quotient_block(
    cochain: SparseOuterCechCochain, context: _MixedContraction,
    indices: dict[int, int], *, dual: bool,
) -> SparseOuterCechCochain:
    """Change only a declared resolution index, retaining line and degree."""

    terms = []
    for basis, value in cochain.terms:
        old = basis.component
        index = old.right_index if dual else old.left_index
        if (old.left_index if dual else old.right_index) != 0 or index not in indices:
            raise ValueError("a quotient block input has an incompatible declared basis")
        target = (0, indices[index]) if dual else (indices[index], 0)
        component = context.components[(*target, old.koszul_summand)]
        if (component.object_degree, component.line_degree) != (
            old.object_degree, old.line_degree,
        ):
            raise ValueError("retargeting a quotient block changed its line or internal degree")
        terms.append((replace(basis, component=component), value))
    return SparseOuterCechCochain(tuple(terms))


@dataclass(frozen=True, slots=True)
class CoupledNullScalar:
    """One formal parameter coefficient, not a selected carrier point."""

    parameter_index: int
    left_line_correction: SparseOuterCechCochain
    right_line_correction: SparseOuterCechCochain
    product_constant: SparseOuterCechCochain
    product_linear: SparseOuterCechCochain
    scalar: SparseOuterCechCochain
    cover_residue: Eisenstein
    projection_depth: int
    earlier_screen_difference: SparseOuterCechCochain

    def as_record(self) -> dict[str, object]:
        """Expose literal cochains and the still-unassigned normalization."""

        return {
            "parameter": f"a{self.parameter_index}",
            **{f"{name}_term_count": len(value.terms) for name, value in (
                ("left_line_correction", self.left_line_correction),
                ("right_line_correction", self.right_line_correction),
                ("product_constant", self.product_constant),
                ("product_linear", self.product_linear), ("scalar", self.scalar),
                ("earlier_screen_difference", self.earlier_screen_difference),
            )},
            **{f"{name}_digest": _cochain_digest((value,)) for name, value in (
                ("left_line_correction", self.left_line_correction),
                ("right_line_correction", self.right_line_correction),
                ("product_constant", self.product_constant),
                ("product_linear", self.product_linear), ("scalar", self.scalar),
                ("earlier_screen_difference", self.earlier_screen_difference),
            )},
            "full_pushout_matter_lifts_closed_coefficientwise": True,
            "full_quotient_higgs_lift_closed_coefficientwise": True,
            "full_quotient_product_closed_coefficientwise": True,
            "scalar_closed_exact": True,
            "direct_and_transferred_cover_residues_equal": True,
            "ordered_cover_residue": str(self.cover_residue),
            "projection_depth": self.projection_depth,
            "earlier_screen_literal_equal": self.earlier_screen_difference.is_zero(),
            "quotient_normalization_assigned": False,
            "physical_null_coefficient_assigned": False,
        }


def evaluate_coupled_null_scalar(parameter_index: int) -> CoupledNullScalar:
    """Compose complete lifts, with formal degree fixed by block support.

    U=b+a*r and H=h+a*kappa. R's outer row lands in B and vanishes
    on B. In the quotient all corrections involving a B input either
    vanish in B wedge B or in A wedge B. The product therefore has
    P0 in exterior F and a*P1 in K, with no quadratic term. Since h
    has only K support and kappa only F support, evaluation is exactly
    a*(h P1+kappa P0). No a=1 carrier point is selected here.
    """

    print(f"a{parameter_index}: constructing the complete pushout inputs", flush=True)
    model = alternate_coupled_quotient(parameter_index)
    unit = mixed_schoen_unit()
    source = _MixedContraction(model.source, unit)
    inside = replace(model.source, extension_terms=tuple(
        term for term in model.source.extension_terms if term.target == model.inner_target
    ))
    source_zero = _MixedContraction(inside, unit)
    out = _MixedContraction(model.quotient, unit)
    out_zero_model = replace(model.quotient, extension_terms=tuple(
        term for term in model.quotient.extension_terms
        if model.quotient.pairs[term.target][0] != 0
    ))
    out_zero = _MixedContraction(out_zero_model, unit)
    dual, dual_zero = (_MixedContraction(unit, item)
                       for item in (model.quotient, out_zero_model))
    line = MixedSchoenUnit(
        "actual B1 quotient", 0, QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),),
    )
    line_context = _MixedContraction(line, unit)
    b_left, b_right = alternate_null_matter()
    b = [_push_f_vector(v, model) for v in (b_left, b_right)]
    r = []
    extension = alternate_outer_coefficient(parameter_index)
    for constituent, character, pushed in zip(
        (b_left, b_right), ((0, 0), (1, 0)), b, strict=True,
    ):
        correction = null_matter_correction(constituent, character, extension)
        value = _quotient(correction, line_context)
        value = retarget_quotient_block(value, source, {0: 0}, dual=False)
        _require_zero(source_zero.differential(pushed), "constant matter is not a full inner cycle")
        _require_zero(source_zero.differential(value) + source.differential(pushed),
                      "the coefficientwise pushout matter identity failed")
        _require_zero(source.differential(value) + source_zero.differential(value).scale(-1),
                      "a quadratic outer matter action survived")
        r.append(value)
    print(f"a{parameter_index}: complete matter lift identities verified", flush=True)
    ideal_indices, exterior_indices = quotient_block_indices(model)
    earlier, _, kappa, _ = load_alternate_up_pairing_cochains(parameter_index)
    h = retarget_quotient_block(alternate_higgs_quotient_covector(), dual,
                               ideal_indices, dual=True)
    kappa = retarget_quotient_block(kappa, dual, exterior_indices, dual=True)
    _require_zero(dual_zero.differential(h), "the constant quotient Higgs is not closed")
    _require_zero(dual_zero.differential(kappa) + dual.differential(h),
                  "the coefficientwise quotient Higgs identity failed")
    _require_zero(dual.differential(kappa) + dual_zero.differential(kappa).scale(-1),
                  "a quadratic quotient Higgs action survived")
    print(f"a{parameter_index}: complete Higgs lift identities verified", flush=True)
    full = coupled_quotient_vector_wedge(b[0] + r[0], b[1] + r[1], model, 1, 1)
    k_indices = set(ideal_indices.values())
    constant = SparseOuterCechCochain(tuple(
        (basis, value) for basis, value in full.terms
        if basis.component.left_index not in k_indices
    ))
    linear = full + constant.scale(-1)
    exterior, _ = alternate_up_exterior_context()
    f_source = inside.objects[1:]
    if len(f_source) != 8:
        raise ValueError("the complete F input resolution changed")
    actual_f, _ = alternate_higgs_quotient_models()
    independent_constant = rank_one_vector_wedge(
        b_left, b_right, actual_f, exterior, _MixedContraction(exterior, unit), 1, 1,
    )
    if constant != retarget_quotient_block(
        independent_constant, out, exterior_indices, dual=False,
    ):
        raise ValueError("the constant product changed under a formal outer coefficient")
    print(f"a{parameter_index}: corrected product has {len(full.terms)} terms", flush=True)
    _require_zero(out_zero.differential(constant), "the constant quotient product is not closed")
    _require_zero(out_zero.differential(linear) + out.differential(constant),
                  "the coefficientwise quotient product identity failed")
    _require_zero(out.differential(linear) + out_zero.differential(linear).scale(-1),
                  "a quadratic quotient product action survived")
    scalar = mixed_outer_cup(h, linear) + mixed_outer_cup(kappa, constant)
    _require_zero(mixed_outer_cup(h, constant), "a constant scalar survived the support theorem")
    _require_zero(mixed_outer_cup(kappa, linear), "a quadratic scalar survived the support theorem")
    _require_zero(_scalar_context().differential(scalar),
                  "the complete natural null scalar is not closed")
    direct = direct_ordered_scalar_residue(scalar)
    coordinates, depth = _perturbed_projection(scalar, _scalar_context(), 3)
    if set(coordinates) - {0} or direct != coordinates.get(0, Eisenstein(0)):
        raise ValueError("the independent cover traces disagree on the natural scalar")
    print(f"a{parameter_index}: natural cover residue {direct}", flush=True)
    return CoupledNullScalar(parameter_index, r[0], r[1], constant, linear, scalar,
                             direct, depth, scalar + earlier.scale(-1))


def write_coupled_null_scalar(path: Path = OUTPUT) -> dict[str, object]:
    """Write only after both complete coefficient evaluations pass."""

    prerequisites = {
        "coupled_tensor_comparison": _verified_payload(COMPARISON)[0],
        "explicit_higgs_primitive_archive": _verified_payload(PRIMITIVES)[0],
    }
    results = [evaluate_coupled_null_scalar(i) for i in range(2)]
    full: dict[str, object] = {
        "schema": "alternate-up-coupled-null-scalar-cochains-v1",
        "prerequisite_artifact_digests": prerequisites,
        "parameter_coefficients": [{
            "parameter": f"a{result.parameter_index}",
            **{name: _cochain_record(value) for name, value in (
                ("left_line_correction", result.left_line_correction),
                ("right_line_correction", result.right_line_correction),
                ("product_constant", result.product_constant),
                ("product_linear", result.product_linear), ("scalar", result.scalar),
                ("earlier_screen_difference", result.earlier_screen_difference),
            )},
        } for result in results],
    }
    full["artifact_digest"] = _canonical_digest(full)
    archive = gzip.compress(
        json.dumps(full, sort_keys=True, separators=(",", ":")).encode(), mtime=0,
    )
    archive_path = path.with_suffix(".cochains.json.gz")
    payload: dict[str, object] = {
        "schema": "alternate-up-coupled-null-scalar-v1",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "parameter_coefficients": [result.as_record() for result in results],
        "scalar_order": "h_K cup P1 + kappa cup P0",
        "trace_convention": "ordered cover k2 top-Laurent generator has trace one",
        "full_carrier_null_pairing_evaluated": True,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "quotient_normalization_assigned": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": prerequisites,
        "full_cochain_archive_name": archive_path.name,
        "full_cochain_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "full_cochain_payload_digest": full["artifact_digest"],
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    archive_temp = archive_path.with_name(f".{archive_path.name}.tmp")
    archive_temp.write_bytes(archive)
    archive_temp.replace(archive_path)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)
    return payload


def load_coupled_null_scalar_witnesses(
    parameter_index: int, path: Path = OUTPUT,
) -> tuple[dict[str, object], dict[str, SparseOuterCechCochain]]:
    """Check saved full identities and a separate inverse residue convolution.

    The archive is an explicit input, never an automatic solver fallback.
    A fresh evaluation is required to create it. This verifier reconstructs
    the actual models and cochains rather than accepting completion flags.
    """

    if parameter_index not in (0, 1):
        raise ValueError("the actual null scalar parameter coefficient is unavailable")
    _, record = _verified_payload(path)
    prerequisites = {
        "coupled_tensor_comparison": _verified_payload(COMPARISON)[0],
        "explicit_higgs_primitive_archive": _verified_payload(PRIMITIVES)[0],
    }
    archive_path = path.with_suffix(".cochains.json.gz")
    if (
        record.get("schema") != "alternate-up-coupled-null-scalar-v1"
        or record.get("prerequisite_artifact_digests") != prerequisites
        or record.get("outer_parameter_basis") != ["a0", "a1"]
        or record.get("full_cochain_archive_name") != archive_path.name
        or record.get("full_carrier_null_pairing_evaluated") is not True
        or any(record.get(field) is not False for field in (
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected", "quotient_normalization_assigned",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the natural null scalar prerequisite or scientific scope changed")
    archive = archive_path.read_bytes()
    if hashlib.sha256(archive).hexdigest() != record.get("full_cochain_archive_sha256"):
        raise ValueError("the natural null scalar archive changed its content")
    full = json.loads(gzip.decompress(archive))
    digest = full.pop("artifact_digest", None)
    summaries = record.get("parameter_coefficients")
    if not isinstance(summaries, list) or any(not isinstance(item, dict) for item in summaries):
        raise ValueError("the natural null scalar coefficient summaries are missing")
    if (
        digest != _canonical_digest(full) or digest != record.get("full_cochain_payload_digest")
        or full.get("schema") != "alternate-up-coupled-null-scalar-cochains-v1"
        or full.get("prerequisite_artifact_digests") != prerequisites
        or [item.get("parameter") for item in full.get("parameter_coefficients", [])]
        != ["a0", "a1"]
        or [item.get("parameter") for item in summaries]
        != ["a0", "a1"]
    ):
        raise ValueError("the natural null scalar full witnesses changed their source")
    raw = full["parameter_coefficients"][parameter_index]
    summary = summaries[parameter_index]
    result = {}
    for name in (
        "left_line_correction", "right_line_correction", "product_constant",
        "product_linear", "scalar", "earlier_screen_difference",
    ):
        item = raw[name]
        value = (SparseOuterCechCochain() if item.get("term_count") == 0 and item.get("terms") == []
                 else _representative(item))
        if (
            len(value.terms) != item.get("term_count")
            or len(value.terms) != summary.get(f"{name}_term_count")
            or _cochain_digest((value,)) != item.get("cochain_digest")
            or _cochain_digest((value,)) != summary.get(f"{name}_digest")
        ):
            raise ValueError("an archived natural scalar witness changed its exact terms")
        result[name] = value
    model, unit = alternate_coupled_quotient(parameter_index), mixed_schoen_unit()
    indices, exterior_indices = quotient_block_indices(model)
    out = _MixedContraction(model.quotient, unit)
    zero_model = replace(model.quotient, extension_terms=tuple(
        t for t in model.quotient.extension_terms if model.quotient.pairs[t.target][0] != 0
    ))
    out_zero = _MixedContraction(zero_model, unit)
    p0, p1 = result["product_constant"], result["product_linear"]
    # Identity retargeting validates every saved line and internal position.
    for value, declared in ((p0, exterior_indices), (p1, indices)):
        if retarget_quotient_block(
            value, out, {i: i for i in declared.values()}, dual=False,
        ) != value:
            raise ValueError("an archived quotient product changed its declared basis")
    _require_zero(out_zero.differential(p0), "the archived constant product is not closed")
    _require_zero(out_zero.differential(p1) + out.differential(p0),
                  "the archived product failed the full coefficientwise identity")
    scalar = result["scalar"]
    direct = direct_ordered_scalar_residue(scalar)
    earlier, _, kappa, _ = load_alternate_up_pairing_cochains(parameter_index)
    if scalar + earlier.scale(-1) != result["earlier_screen_difference"]:
        raise ValueError("the new scalar changed its literal earlier-screen comparison")
    dual = _MixedContraction(unit, model.quotient)
    h = retarget_quotient_block(alternate_higgs_quotient_covector(), dual, indices, dual=True)
    kappa = retarget_quotient_block(kappa, dual, exterior_indices, dual=True)
    target = OuterCechBasis(_scalar_context().components[(0, 0, "k2")],
                            (-1, -1, -1), (-1, -1, -1), (-1, -1),
                            ((0, 1, 2), (0, 1, 2), (0, 1)))
    inverse = (mixed_outer_cup_coefficient(h, p1, target)
               + mixed_outer_cup_coefficient(kappa, p0, target))
    if str(direct) != summary.get("ordered_cover_residue") or direct != inverse:
        raise ValueError("the inverse convolution disagrees with the archived full scalar trace")
    return summary, result


if __name__ == "__main__":
    record = write_coupled_null_scalar()
    print(f"artifact_digest: {record['artifact_digest']}")
