"""Assemble one exact holomorphic up matrix only from verified actual entries.

Owns:
    Fresh replay of explicit F-F witnesses, the fixed mixed pairing, the
    natural null check, and the formal exact matrix on the alternate carrier.

Depends on:
    Actual carrier matter and Higgs lifts, canonical quotient wedge and trace,
    content-addressed coefficient archives, and exact polynomial arithmetic.

Must not:
    Infer a missing entry, replace a constituent lift with a quotient-line
    guess, select moduli or geometry from observations, or claim a physical
    Yukawa matrix without canonical metrics and a stabilized vacuum.

Phase 0:
    Research-only assembly; missing coefficients leave this calculation
    unavailable rather than returning a partial or synthetic matrix.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any, cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, PolynomialMatrix, determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_up_cone_matter_lifts import OUTPUT as CONE_LIFTS
from .alternate_constituent_up_matter_representatives import _strict
from .alternate_up_coupled_null_scalar import (
    _require_zero,
    retarget_quotient_block,
    verify_pushout_matter_lift,
)
from .alternate_up_coupled_tensor_comparison import _push_f_vector, alternate_coupled_quotient
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_ff_entries import (
    GENERATED,
    FFEntry,
    FFMatterLift,
    _check_null_combination,
    _evaluate_entry,
    _higgs,
    _indices,
    _matter_classes,
    _prerequisites,
    _read_witnesses,
    ff_entry_path,
)
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .alternate_up_mixed_quotient_pairing import OUTPUT as MIXED
from .alternate_up_mixed_quotient_pairing import mixed_quotient_entries
from .mixed_constituent_schoen_arrows import MixedConstituentObject, mixed_schoen_constituents
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = GENERATED / "alternate_up_full_holomorphic_matrix.json"


def _lift_path(parameter: int, side: int, family: int, directory: Path) -> Path:
    _indices(parameter, family)
    if type(side) is not int or side not in (0, 1):
        raise ValueError("the actual F-F source side must be row or column")
    return directory / f"alternate_up_ff_lift_a{parameter}_side{side}_family{family}.json"


@cache
def _verified_lift(parameter: int, side: int, family: int, directory: Path) -> FFMatterLift:
    """Recheck a saved constituent lift without invoking its original solver."""

    _indices(parameter, family)
    path = _lift_path(parameter, side, family, directory)
    record, witnesses = _read_witnesses(path, "alternate-up-ff-matter-lift-v1", (
        "constant", "constituent_correction", "line_correction",
    ))
    matter = _matter_classes()[side, family]
    if (
        record.get("parameter") != f"a{parameter}"
        or record.get("side") != side or record.get("family") != family
        or record.get("character") != list(matter.character)
        or record.get("seed_index") != matter.seed_index
        or record.get("prerequisite_artifact_digests") != _prerequisites()
        or record.get("extension_point_selected") is not False
        or record.get("full_constituent_identity_exact") is not True
        or record.get("full_pushout_identity_exact") is not True
        or any(record.get(flag, False) is not False for flag in (
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the archived F-F matter lift changed its actual source or scope")
    old = cast(dict[str, Any], _verified_payload(CONE_LIFTS)[1])
    selected = [item for item in old["second_constituent_parameter_linear_lifts"]
                if item["character"] == list(matter.character)
                and item["seed_index"] == matter.seed_index]
    expected = selected[0]["parameter_coefficients"][parameter] if len(selected) == 1 else None
    if (expected is None or record.get("actual_constituent_coefficient") != expected
            or expected["correction_digest"] != _cochain_digest((
                witnesses["constituent_correction"],
            ))):
        raise ValueError("the saved correction is not the certified actual E constituent lift")
    first, unit = mixed_schoen_constituents()[0], mixed_schoen_unit()
    context = _MixedContraction(first, unit)
    correction = witnesses["constituent_correction"]
    product = mixed_outer_cup(alternate_outer_coefficient(parameter), matter.full_cochain)
    _require_zero(context.differential(product), "the archived E matter product is not closed")
    _require_zero(context.differential(correction) + product,
                  "the archived E correction fails its complete differential equation")
    # The original solver checked strictness; replay both actual atlas actions
    # on the saved exact correction instead of trusting that success flag.
    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    frames = {name: (_common_frame(first, action), Matrix.identity(
        1, scalar_type=Eisenstein,
    )) for name, action in actions.items()}
    if not _strict(correction, matter.character, context, actions, frames):
        raise ValueError("the archived E correction lost its actual atlas character")
    model = alternate_coupled_quotient(parameter)
    line = MixedSchoenUnit(
        "actual B1 quotient", 0, QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),),
    )
    constant = _push_f_vector(matter.full_cochain, model)
    line_correction = retarget_quotient_block(
        _quotient(correction, _MixedContraction(line, unit)),
        _MixedContraction(model.source, unit), {0: 0}, dual=False,
    )
    if constant != witnesses["constant"] or line_correction != witnesses["line_correction"]:
        raise ValueError("the saved F-F pushout lift changed its global quotient map")
    verify_pushout_matter_lift(model, constant, line_correction)
    return FFMatterLift(matter, constant, correction, line_correction,
                        _canonical_digest(record))


def _verified_entry(parameter: int, row: int, column: int, directory: Path) -> FFEntry:
    """Replay an actual entry and compare all literal cochains and traces."""

    _indices(parameter, row, column)
    path = ff_entry_path(parameter, row, column, directory)
    record, witnesses = _read_witnesses(path, "alternate-up-ff-entry-v1", (
        "product_constant", "product_linear", "scalar",
    ))
    expected_digests = [
        _verified_payload(_lift_path(parameter, side, family, directory))[0]
        for side, family in ((0, row), (1, column))
    ]
    if (
        record.get("parameter") != f"a{parameter}"
        or (record.get("row"), record.get("column")) != (row, column)
        or (record.get("row_seed_index"), record.get("column_seed_index"))
        != (0 if row == 1 else 5, 0 if column == 1 else 5)
        or record.get("actual_matter_lift_digests") != expected_digests
        or record.get("prerequisite_artifact_digests") != _prerequisites()
        or record.get("scalar_order") != "h_K cup P1 + kappa cup P0"
        or record.get("exterior_filtration_parameter_degree") != 1
        or any(record.get(flag) is not True for flag in (
            "full_coefficientwise_product_identity_exact", "full_scalar_closed_exact",
            "direct_transferred_and_inverse_convolution_traces_equal",
        ))
        or any(record.get(flag) is not False for flag in (
            "extension_point_selected", "physical_yukawa_matrix_available",
            "complete_holomorphic_up_matrix_available",
        ))
    ):
        raise ValueError("the saved F-F entry changed its actual bases, inputs, or scope")
    left = _verified_lift(parameter, 0, row, directory)
    right = _verified_lift(parameter, 1, column, directory)
    h, kappa, zero_model = _higgs(parameter)
    result = _evaluate_entry(parameter, row, column, left, right, h, kappa, zero_model)
    if (
        result.product_constant != witnesses["product_constant"]
        or result.product_linear != witnesses["product_linear"]
        or result.scalar != witnesses["scalar"]
        or record.get("cover_residue") != str(result.cover_residue)
        or record.get("quotient_residue") != str(result.cover_residue * Rational(1, 9))
        or record.get("projection_depth") != result.projection_depth
    ):
        raise ValueError("the saved F-F entry differs from fresh complete evaluation")
    return result


def verify_ff_coefficient(parameter: int, directory: Path = GENERATED) -> tuple[FFEntry, ...]:
    """Require the entire explicit block, including the independent null check."""

    _indices(parameter, 1)
    path = directory / f"alternate_up_ff_coefficient_a{parameter}.json"
    _, record = _verified_payload(path)
    if (
        record.get("schema") != "alternate-up-ff-coefficient-v1"
        or record.get("parameter") != f"a{parameter}"
        or record.get("prerequisite_artifact_digests") != _prerequisites()
        or record.get("all_four_entries_evaluated") is not True
        or any(record.get(flag) is not False for flag in (
            "extension_point_selected", "physical_yukawa_matrix_available",
            "complete_holomorphic_up_matrix_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the F-F block lacks its four exact entries or changes their scope")
    results = tuple(
        _verified_entry(parameter, row, column, directory)
        for row, column in ((1, 1), (1, 2), (2, 1), (2, 2))
    )
    records = [_verified_payload(ff_entry_path(parameter, item.row, item.column, directory))[0]
               for item in results]
    null_check = _check_null_combination(parameter, list(results))
    if (
        record.get("entry_artifact_digests") != records
        or record.get("cover_block") != [
            [str(next(item.cover_residue for item in results
                      if (item.row, item.column) == (row, column)))
             for column in (1, 2)] for row in (1, 2)
        ]
        or any(record.get(key) != value for key, value in null_check.items())
    ):
        raise ValueError("the F-F block fails its archived full-null contraction")
    return results


def _polynomial_record(value: Polynomial) -> list[dict[str, object]]:
    return [{"powers": list(powers), "coefficient": str(coefficient)}
            for powers, coefficient in value.terms]


def write_full_up_matrix(path: Path = OUTPUT) -> dict[str, object]:
    """Return no matrix until both complete blocks pass fresh replay."""

    directory = path.parent
    for parameter in (0, 1):
        required = directory / f"alternate_up_ff_coefficient_a{parameter}.json"
        if not required.is_file():
            raise FileNotFoundError(f"complete F-F coefficient a{parameter} is missing: {required}")
    blocks = [verify_ff_coefficient(parameter, directory) for parameter in (0, 1)]
    mixed = cast(dict[str, Any], _verified_payload(MIXED)[1])
    if (
        mixed.get("schema") != "alternate-up-mixed-quotient-pairing-v1"
        or mixed.get("basis_order") != {
            "rows": ["E(0,0)", "F(0,0):seed0", "F(0,0):seed5"],
            "columns": ["E(1,0)", "F(1,0):seed0", "F(1,0):seed5"],
        }
        or mixed.get("scalar_order") != "h_K cup projected ordered B-F exterior product"
        or mixed.get("first_first_entry_zero_by_B_wedge_B") is not True
        or mixed.get("second_second_entries_assigned") is not False
    ):
        raise ValueError("the fixed constant mixed pairings changed their physical scope")
    actual_mixed = {(item.row, item.column): item for item in mixed_quotient_entries()}
    records = mixed["evaluated_entries"]
    if len(records) != 4 or {(item["row"], item["column"]) for item in records} != set(
        actual_mixed
    ):
        raise ValueError("the four constant mixed entries lack their exact fixed bases")
    for item in records:
        actual = actual_mixed[item["row"], item["column"]]
        if (
            {key: item[key] for key in actual.as_record()} != actual.as_record()
            or _parse_eisenstein_text(item["quotient_residue"])
            != actual.cover_residue * Rational(1, 9)
        ):
            raise ValueError("a saved mixed scalar changed from its actual Higgs-first trace")
    zero = Polynomial.zero(2, scalar_type=Eisenstein)
    entries: dict[tuple[int, int], Polynomial] = {(0, 0): zero}
    for item in actual_mixed.values():
        entries[item.row, item.column] = Polynomial.constant(
            item.cover_residue * Rational(1, 9), 2, scalar_type=Eisenstein,
        )
    for row in (1, 2):
        for column in (1, 2):
            values = [next(result.cover_residue for result in block
                           if (result.row, result.column) == (row, column))
                      for block in blocks]
            entries[row, column] = Polynomial(
                (((1, 0), values[0] * Rational(1, 9)),
                 ((0, 1), values[1] * Rational(1, 9))),
                variable_count=2, scalar_type=Eisenstein,
            )
    matrix = PolynomialMatrix(tuple(tuple(entries[row, column] for column in range(3))
                                    for row in range(3)))
    det = determinant(matrix.rows)
    row0, col0 = entries[0, 1], entries[1, 0]
    if row0.is_zero() or col0.is_zero():
        raise ValueError("the exact rank-two mixed minor vanished")
    null_values = []
    for parameter in (0, 1):
        null_check = _check_null_combination(parameter, list(blocks[parameter]))
        cover_text = null_check["complete_null_cover_residue"]
        if not isinstance(cover_text, str):
            raise ValueError("the complete natural-null cover residue lost its exact scalar")
        null_values.append(_parse_eisenstein_text(cover_text) * Rational(1, 9))
    expected_null = Polynomial(
        (((1, 0), null_values[0]), ((0, 1), null_values[1])),
        variable_count=2, scalar_type=Eisenstein,
    )
    if det != -(row0 * col0 * expected_null):
        raise ValueError("the full matrix determinant disagrees with its exact null contraction")
    if det.is_zero():
        raise ValueError("the complete formal matrix has no rank-three locus")
    source_inputs = {f"ff_coefficient_a{parameter}": _verified_payload(
        directory / f"alternate_up_ff_coefficient_a{parameter}.json"
    )[0] for parameter in (0, 1)}
    source_inputs["mixed_pairing"] = _verified_payload(MIXED)[0]
    payload: dict[str, object] = {
        "schema": "alternate-up-full-holomorphic-matrix-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "basis_order": mixed["basis_order"],
        "scalar_order": "Higgs first in the fixed quotient volume frame",
        "cover_to_quotient_trace_factor": "1/9",
        "matrix_entries": [[_polynomial_record(matrix.rows[row][column])
                            for column in range(3)] for row in range(3)],
        "determinant": _polynomial_record(det),
        "rank_two_minor": _polynomial_record(-(row0 * col0)),
        "null_contraction": _polynomial_record(expected_null),
        "all_nine_entries_derived_from_actual_carrier": True,
        "holomorphic_matrix_available": True,
        "physical_yukawa_matrix_available": False,
        "canonical_matter_metrics_available": False,
        "common_vacuum_stabilized": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": source_inputs,
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_full_up_matrix()
    print(f"full up matrix digest: {result['artifact_digest']}")
