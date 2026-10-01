"""Assemble a neutrino matrix only after all actual coefficients pass replay.

Owns:
    Read-only validation of actual constituent and quotient corrections,
    complete scalar replay, and formal two-parameter holomorphic matrix assembly.

Depends on:
    The sector-specific full witnesses, original canonical product engines,
    both actual atlas actions, and exact polynomial arithmetic.

Must not:
    Solve missing checkpoints, reuse the up null channel or its values,
    select parameters, equate a holomorphic matrix with physical masses,
    or infer a Majorana mechanism, metrics, or a stabilized common vacuum.

Phase 0:
    Conditional research assembly; absent or invalid entries keep it unavailable.
"""

from __future__ import annotations

import json
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, PolynomialMatrix, determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from . import alternate_neutrino_ff_entries as coefficients
from . import alternate_neutrino_mixed_pairing as mixed
from . import alternate_up_ff_entries as engine
from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_up_matter_representatives import _strict
from .alternate_up_coupled_null_scalar import retarget_quotient_block, verify_pushout_matter_lift
from .alternate_up_coupled_tensor_comparison import _push_f_vector, alternate_coupled_quotient
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_full_matrix import _polynomial_record
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .mixed_constituent_schoen_arrows import MixedConstituentObject, mixed_schoen_constituents
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = coefficients.GENERATED / "alternate_neutrino_full_holomorphic_matrix.json"


def _verified_lift(parameter: int, side: int, family: int, directory: Path):
    """Replay full equations, literal pushouts, and strict characters; never solve."""

    path = coefficients.lift_path(parameter, side, family, directory)
    record, witnesses = engine._read_witnesses(path, "alternate-neutrino-ff-matter-lift-v1", (
        "constant", "constituent_correction", "line_correction",
    ))
    classes, prerequisites = coefficients._inputs()
    matter = classes[side, family]
    if (record.get("prerequisite_artifact_digests") != prerequisites
        or record.get("parameter") != f"a{parameter}"
        or record.get("side") != side or record.get("family") != family
        or record.get("character") != list(matter.character)
        or record.get("seed_index") != matter.seed_index
        or record.get("extension_point_selected") is not False
        or any(record.get(flag) is not True for flag in (
            "full_constituent_identity_exact", "full_pushout_identity_exact",
        ))):
        raise ValueError("the actual neutrino lift changed its declared source or scope")
    correction = witnesses["constituent_correction"]
    if record.get("actual_constituent_coefficient", {}).get("correction_digest") != (
        _cochain_digest((correction,))
    ):
        raise ValueError("the neutrino constituent correction changed its certificate")
    first, unit = mixed_schoen_constituents()[0], mixed_schoen_unit()
    context = _MixedContraction(first, unit)
    product = mixed_outer_cup(alternate_outer_coefficient(parameter), matter.full_cochain)
    engine._require_zero(context.differential(correction) + product,
                         "the archived neutrino correction fails its full constituent identity")
    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    frames = {name: (_common_frame(first, action), Matrix.identity(1, scalar_type=Eisenstein))
              for name, action in actions.items()}
    if not _strict(correction, matter.character, context, actions, frames):
        raise ValueError("the actual neutrino correction lost its strict atlas character")
    model = alternate_coupled_quotient(parameter)
    line = MixedSchoenUnit("actual B1 quotient", 0, QUOTIENT_LINE, (
        MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),
    ))
    constant = _push_f_vector(matter.full_cochain, model)
    line_correction = retarget_quotient_block(
        _quotient(correction, _MixedContraction(line, unit)),
        _MixedContraction(model.source, unit), {0: 0}, dual=False,
    )
    if constant != witnesses["constant"] or line_correction != witnesses["line_correction"]:
        raise ValueError("the actual neutrino matter lift changed its literal quotient pushout")
    verify_pushout_matter_lift(model, constant, line_correction)
    return engine.FFMatterLift(matter, constant, correction, line_correction,
                               _verified_payload(path)[0])


def _verified_entry(parameter: int, row: int, column: int, directory: Path, *, lifts=None):
    """Compare a fresh complete evaluation to all three literal scalar witnesses."""

    engine._indices(parameter, row, column)
    path = directory / f"alternate_neutrino_ff_a{parameter}_r{row}_c{column}.json"
    record, witnesses = engine._read_witnesses(path, "alternate-neutrino-ff-entry-v1", (
        "product_constant", "product_linear", "scalar",
    ))
    if lifts is None:
        left = _verified_lift(parameter, 0, row, directory)
        right = _verified_lift(parameter, 1, column, directory)
    else:
        left, right = lifts[parameter, 0, row], lifts[parameter, 1, column]
    if (record.get("parameter") != f"a{parameter}"
        or (record.get("row"), record.get("column")) != (row, column)
        or record.get("row_character") != list(left.matter.character)
        or record.get("column_character") != list(right.matter.character)
        or record.get("row_seed_index") != left.matter.seed_index
        or record.get("column_seed_index") != right.matter.seed_index
        or record.get("actual_matter_lift_digests")
        != [left.checkpoint_digest, right.checkpoint_digest]
        or record.get("prerequisite_artifact_digests") != coefficients._inputs()[1]
        or record.get("scalar_order") != "h_K cup P1 + kappa cup P0"
        or record.get("exterior_filtration_parameter_degree") != 1
        or any(record.get(flag) is not True for flag in (
            "full_coefficientwise_product_identity_exact", "full_scalar_closed_exact",
            "direct_transferred_and_inverse_convolution_traces_equal",
        ))
        or any(record.get(flag) is not False for flag in (
            "complete_holomorphic_neutrino_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected",
        ))):
        raise ValueError("the actual neutrino entry changed its fixed inputs or scope")
    result = engine._evaluate_entry(parameter, row, column, left, right, *engine._higgs(parameter))
    if (result.product_constant != witnesses["product_constant"]
        or result.product_linear != witnesses["product_linear"]
        or result.scalar != witnesses["scalar"]
        or record.get("cover_residue") != str(result.cover_residue)
        or record.get("quotient_residue") != str(result.cover_residue * Rational(1, 9))
        or record.get("projection_depth") != result.projection_depth):
        raise ValueError("the actual neutrino entry differs from fresh complete scalar replay")
    return result


def write_full_neutrino_matrix(path: Path = OUTPUT):
    """Require all sixteen source files before assembling any physical-model matrix."""

    directory = path.parent
    required = [coefficients.lift_path(parameter, side, family, directory)
                for parameter in (0, 1) for side in (0, 1) for family in (1, 2)]
    required.extend(directory / f"alternate_neutrino_ff_a{parameter}_r{row}_c{column}.json"
                    for parameter in (0, 1) for row in (1, 2) for column in (1, 2))
    for source in required:
        if not source.is_file():
            raise FileNotFoundError(
                f"actual neutrino coefficient prerequisite is missing: {source}",
            )
    # Memoization is scoped to one assembly; another call rereads changed artifacts.
    lifts = {(parameter, side, family): _verified_lift(parameter, side, family, directory)
             for parameter in (0, 1) for side in (0, 1) for family in (1, 2)}
    blocks = {(parameter, row, column): _verified_entry(
        parameter, row, column, directory, lifts=lifts,
    )
              for parameter in (0, 1) for row in (1, 2) for column in (1, 2)}
    packet, _ = mixed.load_mixed_pairing(expected_digest=coefficients.MIXED_DIGEST)
    entries = {(0, 0): Polynomial.zero(2, scalar_type=Eisenstein)}
    for item in packet["evaluated_entries"]:
        entries[item["row"], item["column"]] = Polynomial.constant(
            _parse_eisenstein_text(item["quotient_residue"]), 2, scalar_type=Eisenstein,
        )
    for row in (1, 2):
        for column in (1, 2):
            entries[row, column] = Polynomial(
                tuple((tuple(int(i == parameter) for i in (0, 1)),
                       blocks[parameter, row, column].cover_residue * Rational(1, 9))
                      for parameter in (0, 1)), variable_count=2, scalar_type=Eisenstein,
            )
    matrix = PolynomialMatrix(tuple(tuple(entries[row, column] for column in range(3))
                                    for row in range(3)))
    det = determinant(matrix.rows)
    independent = (-entries[0, 1] * (entries[1, 0] * entries[2, 2]
                                     - entries[1, 2] * entries[2, 0])
                   + entries[0, 2] * (entries[1, 0] * entries[2, 1]
                                     - entries[1, 1] * entries[2, 0]))
    if det != independent or any(sum(powers) != 1 for powers, _ in det.terms):
        raise ValueError(
            "the complete neutrino determinant fails its exact linear support identity",
        )
    minor = -entries[0, 1] * entries[1, 0]
    if minor.is_zero():
        raise ValueError("the established neutrino mixed rank-two minor vanished")
    record = {
        "schema": "alternate-neutrino-full-holomorphic-matrix-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "coefficient_field": "Q(omega)", "outer_parameter_basis": ["a0", "a1"],
        "basis_order": {"rows": ["E(2,1):seed0", "F(2,1):seed2", "F(2,1):seed4"],
                        "columns": ["E(2,2):seed1", "F(2,2):seed1", "F(2,2):seed3"]},
        "scalar_order": "Higgs first in the fixed quotient volume frame",
        "cover_to_quotient_trace_factor": "1/9",
        "matrix_entries": [[_polynomial_record(value) for value in row] for row in matrix.rows],
        "determinant": _polynomial_record(det), "rank_two_minor": _polynomial_record(minor),
        "rank_three_locus_nonempty": not det.is_zero(),
        "all_nine_entries_derived_from_actual_carrier": True,
        "all_eight_formal_coefficient_scalars_replayed": True, "holomorphic_matrix_available": True,
        "physical_yukawa_matrix_available": False, "canonical_matter_metrics_available": False,
        "majorana_mechanism_derived": False, "common_vacuum_stabilized": False,
        "extension_point_selected": False, "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "constant_mixed_pairing": coefficients.MIXED_DIGEST,
            **{source.stem: _verified_payload(source)[0] for source in required},
        },
    }
    record["artifact_digest"] = _canonical_digest(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


if __name__ == "__main__":
    result = write_full_neutrino_matrix()
    print(result["artifact_digest"], result["determinant"], flush=True)
