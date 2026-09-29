"""Derive the four missing F-F entries from complete actual carrier lifts.

Owns:
    Explicit constituent corrections for each fixed matter seed, their
    pushout images, complete quotient products, coefficientwise scalar
    identities, and content-addressed per-entry checkpoints.

Depends on:
    The frozen alternate carrier, established constituent lift solver,
    canonical coupled product, actual Higgs primitive archive, and fixed trace.

Must not:
    Replace constituent lifts with arbitrary line primitives, fill missing
    entries, select extension parameters, or call holomorphic traces masses.

Phase 0:
    Research-only evaluation on the conditional heterotic carrier; a complete
    matrix is unavailable until both coefficient blocks are explicitly derived.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from typing import Any, cast

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from .alternate_constituent_up_cone_matter_lifts import OUTPUT as CONE_LIFTS
from .alternate_constituent_up_cone_matter_lifts import _coefficient
from .alternate_constituent_up_matter_representatives import (
    CARRIER,
    AlternateMatterClass,
    alternate_constituent_up_matter_representatives,
)
from .alternate_constituent_up_matter_representatives import OUTPUT as MATTER
from .alternate_up_coupled_null_scalar import OUTPUT as NULL_SCALAR
from .alternate_up_coupled_null_scalar import (
    _require_zero,
    quotient_block_indices,
    retarget_quotient_block,
    verify_pushout_matter_lift,
)
from .alternate_up_coupled_tensor_comparison import OUTPUT as COMPARISON
from .alternate_up_coupled_tensor_comparison import _push_f_vector, alternate_coupled_quotient
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_exterior_higgs_action import alternate_up_exterior_context
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_covector,
    alternate_higgs_quotient_models,
)
from .alternate_up_mixed_quotient_pairing import OUTPUT as MIXED
from .alternate_up_mixed_scalar_trace import _scalar_context
from .alternate_up_pairing_exchange import OUTPUT as PRIMITIVES
from .alternate_up_pairing_exchange import (
    _cochain_record,
    direct_ordered_scalar_residue,
    load_alternate_up_pairing_cochains,
)
from .alternate_up_quotient_trace import OUTPUT as TRACE
from .mixed_constituent_schoen_arrows import MixedConstituentObject, mixed_schoen_constituents
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_common_dga import mixed_outer_cup, mixed_outer_cup_coefficient
from .mixed_schoen_coupled_tensor import coupled_quotient_vector_wedge
from .mixed_schoen_exterior_square import MixedExteriorSquare
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload
from .mixed_schoen_rank_one_tensor import rank_one_vector_wedge

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "data/generated/scientific_genesis"


def _indices(parameter: int, row: int, column: int | None = None) -> None:
    """Reject undeclared indices before constructing any actual carrier object."""

    if type(parameter) is not int or parameter not in (0, 1):
        raise ValueError("an F-F coefficient requires the declared a0 or a1 basis")
    if type(row) is not int or row not in (1, 2):
        raise ValueError("an F-F family index must be 1 or 2 in the fixed seed basis")
    if column is not None and (type(column) is not int or column not in (1, 2)):
        raise ValueError("an F-F column must be 1 or 2 in the fixed seed basis")


def ff_entry_path(parameter: int, row: int, column: int, directory: Path = GENERATED) -> Path:
    """Name one explicitly computed coefficient, not an implicit matrix cell."""

    _indices(parameter, row, column)
    return directory / f"alternate_up_ff_a{parameter}_r{row}_c{column}.json"


def _prerequisites() -> dict[str, str]:
    """Bind each entry to the exact actual inputs and established trace frame."""

    trace = cast(dict[str, Any], _verified_payload(TRACE)[1])
    if (
        trace.get("cover_to_quotient_trace_factor") != "1/9"
        or trace.get("volume_form_convention", {}).get("relation")
        != "pi*Omega_quotient=Omega_cover"
        or trace.get("scalar_class_descent_certified") is not True
    ):
        raise ValueError("the F-F block lacks its declared quotient trace convention")
    return {name: _verified_payload(path)[0] for name, path in (
        ("frozen_carrier", CARRIER), ("actual_matter", MATTER),
        ("constituent_lift_certificate", CONE_LIFTS),
        ("coupled_product_presentation", COMPARISON), ("higgs_primitive_archive", PRIMITIVES),
        ("scalar_trace_frame", TRACE), ("constant_mixed_entries", MIXED),
        ("complete_null_contraction", NULL_SCALAR),
    )}


def _write_witnesses(
    path: Path, record: dict[str, object], cochains: dict[str, SparseOuterCechCochain],
) -> dict[str, object]:
    """Save computed witnesses atomically, keeping each exact term inspectable."""

    if "artifact_digest" in record:
        raise ValueError("a new witness checkpoint must not supply its own content digest")
    full: dict[str, object] = {
        "schema": f"{record['schema']}-cochains",
        "cochains": {name: _cochain_record(value) for name, value in cochains.items()},
    }
    full["artifact_digest"] = _canonical_digest(full)
    archive = gzip.compress(
        json.dumps(full, sort_keys=True, separators=(",", ":")).encode(), mtime=0,
    )
    archive_path = path.with_suffix(".cochains.json.gz")
    result = {
        **record,
        "witnesses": {name: {
            "term_count": len(value.terms), "cochain_digest": _cochain_digest((value,)),
        } for name, value in cochains.items()},
        "full_cochain_archive_name": archive_path.name,
        "full_cochain_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "full_cochain_payload_digest": full["artifact_digest"],
    }
    result["artifact_digest"] = _canonical_digest(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    for target, content in ((archive_path, archive), (path, (
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    ).encode())):
        temp = target.with_name(f".{target.name}.tmp")
        temp.write_bytes(content)
        temp.replace(target)
    return result


def _read_witnesses(
    path: Path, schema: str, names: tuple[str, ...],
) -> tuple[dict[str, object], dict[str, SparseOuterCechCochain]]:
    """Read an explicit checkpoint or fail; never invoke a solver as fallback."""

    record = cast(dict[str, Any], _verified_payload(path)[1])
    archive_path = path.with_suffix(".cochains.json.gz")
    if (record.get("schema") != schema
            or record.get("full_cochain_archive_name") != archive_path.name):
        raise ValueError("the F-F witness checkpoint changed its schema or archive name")
    archive = archive_path.read_bytes()
    if hashlib.sha256(archive).hexdigest() != record.get("full_cochain_archive_sha256"):
        raise ValueError("the F-F witness archive changed its exact content")
    full = json.loads(gzip.decompress(archive))
    digest = full.pop("artifact_digest", None)
    if (
        digest != _canonical_digest(full) or digest != record.get("full_cochain_payload_digest")
        or full.get("schema") != f"{schema}-cochains"
        or set(full.get("cochains", {})) != set(names)
        or set(record.get("witnesses", {})) != set(names)
    ):
        raise ValueError("the F-F checkpoint lacks its declared full witnesses")
    values = {}
    for name in names:
        item = full["cochains"][name]
        value = (SparseOuterCechCochain() if item.get("terms") == []
                 and item.get("term_count") == 0 else _representative(item))
        summary = record["witnesses"][name]
        if (
            len(value.terms) != item.get("term_count")
            or len(value.terms) != summary.get("term_count")
            or _cochain_digest((value,)) != item.get("cochain_digest")
            or _cochain_digest((value,)) != summary.get("cochain_digest")
        ):
            raise ValueError("an F-F witness changed its literal coefficients or basis")
        values[name] = value
    return record, values


def _matter_classes() -> dict[tuple[int, int], AlternateMatterClass]:
    """Retain the exact row and column seeds, without a new family basis."""

    actual = alternate_constituent_up_matter_representatives()
    if actual.as_record() != _verified_payload(MATTER)[1]:
        raise ValueError("the F-F matter classes differ from the frozen input")
    classes = {}
    for side, character in enumerate(((0, 0), (1, 0))):
        selected = [item for item in actual.classes if item.character == character]
        if [item.seed_index for item in selected] != [0, 5]:
            raise ValueError("the F-F block changed the actual matter seed order")
        classes.update({(side, family): item for family, item in enumerate(selected, start=1)})
    return classes


@dataclass(frozen=True, slots=True)
class FFMatterLift:
    """An actual V lift with its full E correction and declared pushout image."""

    matter: AlternateMatterClass
    constant: SparseOuterCechCochain
    constituent_correction: SparseOuterCechCochain
    line_correction: SparseOuterCechCochain
    checkpoint_digest: str


def _derive_lift(
    parameter: int, side: int, family: int, matter: AlternateMatterClass, directory: Path,
    prerequisites: dict[str, str],
) -> FFMatterLift:
    """Reuse the established constituent solve, then verify its actual pushout."""

    _indices(parameter, family)
    first, unit = mixed_schoen_constituents()[0], mixed_schoen_unit()
    print(f"a{parameter}: deriving actual E correction side {side} seed {matter.seed_index}",
          flush=True)
    coefficient = _coefficient(
        f"a{parameter}", matter, alternate_outer_coefficient(parameter),
        _MixedContraction(first, unit), mixed_transferred_outer_hom(first, unit),
    )
    old = cast(dict[str, Any], _verified_payload(CONE_LIFTS)[1])
    matches = [item for item in old["second_constituent_parameter_linear_lifts"]
               if item["character"] == list(matter.character)
               and item["seed_index"] == matter.seed_index]
    if (len(matches) != 1
            or coefficient.as_record() != matches[0]["parameter_coefficients"][parameter]):
        raise ValueError("the regenerated actual constituent correction changed its certificate")
    model = alternate_coupled_quotient(parameter)
    line = MixedSchoenUnit(
        "actual B1 quotient", 0, QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),),
    )
    correction = retarget_quotient_block(
        _quotient(coefficient.correction, _MixedContraction(line, unit)),
        _MixedContraction(model.source, unit), {0: 0}, dual=False,
    )
    constant = _push_f_vector(matter.full_cochain, model)
    verify_pushout_matter_lift(model, constant, correction)
    path = directory / f"alternate_up_ff_lift_a{parameter}_side{side}_family{family}.json"
    record = _write_witnesses(path, {
        "schema": "alternate-up-ff-matter-lift-v1",
        "parameter": f"a{parameter}", "side": side, "family": family,
        "character": list(matter.character), "seed_index": matter.seed_index,
        "actual_constituent_coefficient": coefficient.as_record(),
        "full_constituent_identity_exact": True,
        "full_pushout_identity_exact": True,
        "prerequisite_artifact_digests": prerequisites,
        "extension_point_selected": False,
    }, {
        "constant": constant, "constituent_correction": coefficient.correction,
        "line_correction": correction,
    })
    print(f"a{parameter}: saved actual lift side {side} family {family}", flush=True)
    return FFMatterLift(matter, constant, coefficient.correction, correction,
                        str(record["artifact_digest"]))


@cache
def _higgs(parameter: int) -> tuple[
    SparseOuterCechCochain, SparseOuterCechCochain, MixedExteriorSquare,
]:
    """Use the already archived actual Higgs primitive with unchanged sign."""

    model = alternate_coupled_quotient(parameter)
    unit = mixed_schoen_unit()
    indices, exterior_indices = quotient_block_indices(model)
    zero_model = replace(model.quotient, extension_terms=tuple(
        term for term in model.quotient.extension_terms if model.quotient.pairs[term.target][0] != 0
    ))
    dual = _MixedContraction(unit, model.quotient)
    dual_zero = _MixedContraction(unit, zero_model)
    _, _, kappa, _ = load_alternate_up_pairing_cochains(parameter)
    h = retarget_quotient_block(alternate_higgs_quotient_covector(), dual, indices, dual=True)
    kappa = retarget_quotient_block(kappa, dual, exterior_indices, dual=True)
    _require_zero(dual_zero.differential(h), "the actual constant Higgs is not closed")
    _require_zero(dual_zero.differential(kappa) + dual.differential(h),
                  "the complete formal Higgs identity failed")
    _require_zero(dual.differential(kappa) + dual_zero.differential(kappa).scale(-1),
                  "a quadratic Higgs action survived")
    return h, kappa, zero_model


@dataclass(frozen=True, slots=True)
class FFEntry:
    """One derived formal coefficient, including its full closed scalar."""

    row: int
    column: int
    product_constant: SparseOuterCechCochain
    product_linear: SparseOuterCechCochain
    scalar: SparseOuterCechCochain
    cover_residue: Eisenstein
    projection_depth: int


def _evaluate_entry(
    parameter: int, row: int, column: int, left: FFMatterLift, right: FFMatterLift,
    h: SparseOuterCechCochain, kappa: SparseOuterCechCochain, zero_model: MixedExteriorSquare,
) -> FFEntry:
    """Evaluate the exact linear coefficient, never an a=1 carrier point."""

    _indices(parameter, row, column)
    model, unit = alternate_coupled_quotient(parameter), mixed_schoen_unit()
    indices, exterior_indices = quotient_block_indices(model)
    out, out_zero = _MixedContraction(model.quotient, unit), _MixedContraction(zero_model, unit)
    for lift in (left, right):
        verify_pushout_matter_lift(model, lift.constant, lift.line_correction)
    print(f"a{parameter}: evaluating complete F-F entry ({row},{column})", flush=True)
    full = coupled_quotient_vector_wedge(
        left.constant + left.line_correction, right.constant + right.line_correction,
        model, 1, 1,
    )
    k_indices = set(indices.values())
    constant = SparseOuterCechCochain(tuple(
        (basis, value) for basis, value in full.terms if basis.component.left_index not in k_indices
    ))
    linear = full + constant.scale(-1)
    exterior, _ = alternate_up_exterior_context()
    actual_f, _ = alternate_higgs_quotient_models()
    independent = rank_one_vector_wedge(
        left.matter.full_cochain, right.matter.full_cochain,
        actual_f, exterior, _MixedContraction(exterior, unit), 1, 1,
    )
    if constant != retarget_quotient_block(independent, out, exterior_indices, dual=False):
        raise ValueError("the F-F constant product disagrees with the independent exterior wedge")
    _require_zero(out_zero.differential(constant), "the F-F constant product is not closed")
    _require_zero(out_zero.differential(linear) + out.differential(constant),
                  "the F-F coefficientwise product identity failed")
    _require_zero(out.differential(linear) + out_zero.differential(linear).scale(-1),
                  "a quadratic F-F quotient action survived")
    scalar = mixed_outer_cup(h, linear) + mixed_outer_cup(kappa, constant)
    _require_zero(mixed_outer_cup(h, constant), "a constant F-F scalar survived")
    _require_zero(mixed_outer_cup(kappa, linear), "a quadratic F-F scalar survived")
    direct = direct_ordered_scalar_residue(scalar)
    coordinates, depth = _perturbed_projection(scalar, _scalar_context(), 3)
    target = OuterCechBasis(
        _scalar_context().components[(0, 0, "k2")],
        (-1, -1, -1), (-1, -1, -1), (-1, -1), ((0, 1, 2), (0, 1, 2), (0, 1)),
    )
    inverse = mixed_outer_cup_coefficient(h, linear, target) + mixed_outer_cup_coefficient(
        kappa, constant, target,
    )
    if set(coordinates) - {0} or direct != coordinates.get(0, Eisenstein(0)) or direct != inverse:
        raise ValueError("independent F-F cover traces disagree")
    print(f"a{parameter}: F-F entry ({row},{column}) cover residue {direct}", flush=True)
    return FFEntry(row, column, constant, linear, scalar, direct, depth)


def _check_null_combination(parameter: int, entries: list[FFEntry]) -> dict[str, object]:
    """Check the complete block against the separately derived actual null cochain."""

    mixed = cast(dict[str, Any], _verified_payload(MIXED)[1])
    row = {item["column"]: _parse_eisenstein_text(item["cover_residue"])
           for item in mixed["evaluated_entries"] if item["row"] == 0}
    column = {item["row"]: _parse_eisenstein_text(item["cover_residue"])
              for item in mixed["evaluated_entries"] if item["column"] == 0}
    left_ratio, right_ratio = column[2] / column[1], row[2] / row[1]
    block = {(entry.row, entry.column): entry.scalar for entry in entries}
    if set(block) != {(1, 1), (1, 2), (2, 1), (2, 2)}:
        raise ValueError("the F-F null check requires all four actual entries")
    combined = (block[2, 2] + block[1, 2].scale(-left_ratio)
                + block[2, 1].scale(-right_ratio)
                + block[1, 1].scale(left_ratio * right_ratio))
    null = cast(dict[str, Any], _verified_payload(NULL_SCALAR)[1])
    archive = NULL_SCALAR.with_suffix(".cochains.json.gz").read_bytes()
    if hashlib.sha256(archive).hexdigest() != null.get("full_cochain_archive_sha256"):
        raise ValueError("the independently verified null archive changed its content")
    full = json.loads(gzip.decompress(archive))
    digest = full.pop("artifact_digest", None)
    if digest != _canonical_digest(full) or digest != null.get("full_cochain_payload_digest"):
        raise ValueError("the independently verified null witnesses changed their digest")
    scalar = _representative(full["parameter_coefficients"][parameter]["scalar"])
    if combined != scalar:
        raise ValueError("the complete F-F block fails the literal natural-null cochain identity")
    return {
        "left_null_ratio": str(left_ratio), "right_null_ratio": str(right_ratio),
        "complete_null_scalar_literal_equal": True,
        "complete_null_scalar_digest": _cochain_digest((combined,)),
        "complete_null_cover_residue": str(direct_ordered_scalar_residue(combined)),
    }


def write_ff_coefficient(parameter: int, directory: Path = GENERATED) -> dict[str, object]:
    """Derive and checkpoint one whole block with no implicit missing-input recovery."""

    _indices(parameter, 1)
    prerequisites, classes = _prerequisites(), _matter_classes()
    lifts = {key: _derive_lift(parameter, *key, matter, directory, prerequisites)
             for key, matter in classes.items()}
    h, kappa, zero_model = _higgs(parameter)
    results, records = [], []
    for row, column in ((1, 1), (1, 2), (2, 1), (2, 2)):
        result = _evaluate_entry(
            parameter, row, column, lifts[0, row], lifts[1, column], h, kappa, zero_model,
        )
        results.append(result)
        record = _write_witnesses(ff_entry_path(parameter, row, column, directory), {
            "schema": "alternate-up-ff-entry-v1", "parameter": f"a{parameter}",
            "row": row, "column": column,
            "row_seed_index": lifts[0, row].matter.seed_index,
            "column_seed_index": lifts[1, column].matter.seed_index,
            "actual_matter_lift_digests": [
                lifts[0, row].checkpoint_digest, lifts[1, column].checkpoint_digest,
            ],
            "prerequisite_artifact_digests": prerequisites,
            "scalar_order": "h_K cup P1 + kappa cup P0",
            "full_coefficientwise_product_identity_exact": True,
            "full_scalar_closed_exact": True,
            "direct_transferred_and_inverse_convolution_traces_equal": True,
            "cover_residue": str(result.cover_residue),
            "quotient_residue": str(result.cover_residue * Rational(1, 9)),
            "projection_depth": result.projection_depth,
            "exterior_filtration_parameter_degree": 1,
            "extension_point_selected": False,
            "physical_yukawa_matrix_available": False,
            "complete_holomorphic_up_matrix_available": False,
        }, {
            "product_constant": result.product_constant, "product_linear": result.product_linear,
            "scalar": result.scalar,
        })
        records.append(record)
    null_check = _check_null_combination(parameter, results)
    payload = {
        "schema": "alternate-up-ff-coefficient-v1", "parameter": f"a{parameter}",
        "prerequisite_artifact_digests": prerequisites,
        "entry_artifact_digests": [record["artifact_digest"] for record in records],
        "cover_block": [[str(next(result.cover_residue for result in results
                                  if (result.row, result.column) == (row, column)))
                         for column in (1, 2)] for row in (1, 2)],
        **null_check,
        "all_four_entries_evaluated": True,
        "physical_yukawa_matrix_available": False,
        "complete_holomorphic_up_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path = directory / f"alternate_up_ff_coefficient_a{parameter}.json"
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)
    return payload


if __name__ == "__main__":
    for parameter in (0, 1):
        record = write_ff_coefficient(parameter)
        print(f"a{parameter}: F-F block digest {record['artifact_digest']}", flush=True)
