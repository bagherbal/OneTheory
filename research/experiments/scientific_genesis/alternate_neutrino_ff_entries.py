"""Derive missing neutrino coefficients using the existing carrier engines.

Owns:
    Thin orchestration of actual neutrino constituent corrections, their
    quotient pushouts, and eight parameter-linear scalar checkpoints.

Depends on:
    The independently checked mixed neutrino witnesses, the frozen two-parameter
    carrier, existing full constituent solves, and the canonical up-Higgs object.

Must not:
    Reuse up-family values, copy its seed labels or null channel, choose a point
    of the extension family, silently replace missing checkpoints, or infer masses.

Phase 0:
    Conditional research coefficient execution, not physical normalization.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from onetheory.math.numbers import Rational

from . import alternate_neutrino_mixed_pairing as neutrino
from . import alternate_up_ff_entries as engine
from .alternate_constituent_up_cone_matter_lifts import _coefficient_job
from .alternate_constituent_up_matter_representatives import AlternateMatterClass
from .alternate_up_coupled_null_scalar import retarget_quotient_block, verify_pushout_matter_lift
from .alternate_up_coupled_tensor_comparison import _push_f_vector, alternate_coupled_quotient
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .mixed_constituent_schoen_arrows import MixedConstituentObject, mixed_schoen_constituents
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

MIXED_DIGEST = "1bc8020db27e9f7a3c7ee7a7abf4ab0c456903c993eab27b0038cad5e12e6049"
GENERATED = engine.GENERATED


def _inputs():
    """Read actual independently checked matter witnesses without solving again."""

    record, witnesses = neutrino.load_mixed_pairing(expected_digest=MIXED_DIGEST)
    classes = {}
    for side, character in enumerate(((2, 1), (2, 2))):
        selected = [item for item in record["second_constituent_classes"]
                    if item["constituent_character"] == list(character)]
        if len(selected) != 2:
            raise ValueError("the actual neutrino character sector is incomplete")
        for family, item in enumerate(selected, start=1):
            classes[side, family] = AlternateMatterClass(
                character, item["seed_index"],
                tuple(_parse_eisenstein_text(c) for c in item["cohomology_coordinates"]),
                witnesses[f"second_side{side}_family{family}"],
                item["inclusion_depth"], item["projection_depth"],
            )
    prerequisites = {
        **record["prerequisite_artifact_digests"], "actual_neutrino_mixed_pairing": MIXED_DIGEST,
        "coupled_product_presentation": _verified_payload(engine.COMPARISON)[0],
        "higgs_primitive_archive": _verified_payload(engine.PRIMITIVES)[0],
    }
    return classes, prerequisites


def lift_path(parameter: int, side: int, family: int, directory: Path = GENERATED) -> Path:
    """Name a declared actual neutrino lift, with no physical basis inference."""

    engine._indices(parameter, family)
    if type(side) is not int or side not in (0, 1):
        raise ValueError("a neutrino side must be 0 (L) or 1 (nu^c)")
    return directory / f"alternate_neutrino_ff_lift_a{parameter}_side{side}_family{family}.json"


def write_ff_coefficient(parameter: int, directory: Path = GENERATED, *, derive_lifts: bool):
    """Derive one block, or explicitly consume all four previously saved lifts."""

    engine._indices(parameter, 1)
    if type(derive_lifts) is not bool:
        raise TypeError("the execution must explicitly declare whether to derive lifts")
    classes, prerequisites = _inputs()
    unit, first = mixed_schoen_unit(), mixed_schoen_constituents()[0]
    extension = alternate_outer_coefficient(parameter)
    model = alternate_coupled_quotient(parameter)
    constituent_context = _MixedContraction(first, unit)
    line = MixedSchoenUnit("actual B1 quotient", 0, QUOTIENT_LINE, (
        MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),
    ))
    source_context = _MixedContraction(model.source, unit)
    line_context = _MixedContraction(line, unit)
    coefficients = {}
    if derive_lifts:
        jobs = [(side, family, parameter, matter, extension)
                for (side, family), matter in classes.items()]
        print(f"a{parameter}: deriving four actual neutrino constituent corrections", flush=True)
        with ProcessPoolExecutor(max_workers=4) as pool:
            for side, family, _, coefficient in pool.map(_coefficient_job, jobs):
                coefficients[side, family] = coefficient
    lifts = {}
    for (side, family), matter in classes.items():
        path = lift_path(parameter, side, family, directory)
        if derive_lifts:
            coefficient = coefficients[side, family]
            correction = retarget_quotient_block(
                _quotient(coefficient.correction, line_context), source_context, {0: 0}, dual=False,
            )
            constant = _push_f_vector(matter.full_cochain, model)
            verify_pushout_matter_lift(model, constant, correction)
            saved = engine._write_witnesses(path, {
                "schema": "alternate-neutrino-ff-matter-lift-v1",
                "parameter": f"a{parameter}", "side": side, "family": family,
                "character": list(matter.character), "seed_index": matter.seed_index,
                "actual_constituent_coefficient": coefficient.as_record(),
                "full_constituent_identity_exact": True, "full_pushout_identity_exact": True,
                "prerequisite_artifact_digests": prerequisites, "extension_point_selected": False,
            }, {"constant": constant, "constituent_correction": coefficient.correction,
                "line_correction": correction})
            actual_correction = coefficient.correction
        else:
            saved, witnesses = engine._read_witnesses(
                path, "alternate-neutrino-ff-matter-lift-v1",
                ("constant", "constituent_correction", "line_correction"),
            )
            saved = {**saved, "artifact_digest": _verified_payload(path)[0]}
            if (saved.get("prerequisite_artifact_digests") != prerequisites
                or saved.get("character") != list(matter.character)
                or saved.get("seed_index") != matter.seed_index
                or saved.get("parameter") != f"a{parameter}"
                or saved.get("side") != side or saved.get("family") != family
                or saved.get("extension_point_selected") is not False):
                raise ValueError("a neutrino lift checkpoint changed its actual inputs")
            constant, actual_correction, correction = (
                witnesses[name]
                for name in ("constant", "constituent_correction", "line_correction")
            )
            if constant != _push_f_vector(matter.full_cochain, model):
                raise ValueError("a neutrino lift changed the actual constant matter cochain")
            if correction != retarget_quotient_block(
                _quotient(actual_correction, line_context), source_context, {0: 0}, dual=False,
            ):
                raise ValueError("a neutrino lift changed the actual constituent pushout")
        engine._require_zero(constituent_context.differential(actual_correction)
                             + mixed_outer_cup(extension, matter.full_cochain),
                             "the actual neutrino constituent correction is not a full primitive")
        verify_pushout_matter_lift(model, constant, correction)
        lifts[side, family] = engine.FFMatterLift(
            matter, constant, actual_correction, correction, saved["artifact_digest"],
        )
        print(f"a{parameter}: saved/verified neutrino lift side {side} family {family}", flush=True)
    h, kappa, zero_model = engine._higgs(parameter)
    results = []
    for row, column in ((1, 1), (1, 2), (2, 1), (2, 2)):
        value = engine._evaluate_entry(parameter, row, column, lifts[0, row], lifts[1, column],
                                       h, kappa, zero_model)
        record = engine._write_witnesses(
            directory / f"alternate_neutrino_ff_a{parameter}_r{row}_c{column}.json", {
                "schema": "alternate-neutrino-ff-entry-v1", "parameter": f"a{parameter}",
                "row": row, "column": column,
                "row_character": list(lifts[0, row].matter.character),
                "column_character": list(lifts[1, column].matter.character),
                "row_seed_index": lifts[0, row].matter.seed_index,
                "column_seed_index": lifts[1, column].matter.seed_index,
                "actual_matter_lift_digests": [lifts[0, row].checkpoint_digest,
                                              lifts[1, column].checkpoint_digest],
                "prerequisite_artifact_digests": prerequisites,
                "scalar_order": "h_K cup P1 + kappa cup P0",
                "full_coefficientwise_product_identity_exact": True,
                "full_scalar_closed_exact": True,
                "direct_transferred_and_inverse_convolution_traces_equal": True,
                "cover_residue": str(value.cover_residue),
                "quotient_residue": str(value.cover_residue * Rational(1, 9)),
                "projection_depth": value.projection_depth,
                "exterior_filtration_parameter_degree": 1, "extension_point_selected": False,
                "physical_yukawa_matrix_available": False,
                "complete_holomorphic_neutrino_matrix_available": False,
            }, {"product_constant": value.product_constant, "product_linear": value.product_linear,
                "scalar": value.scalar})
        results.append(record)
    return tuple(results)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameter", type=int, choices=(0, 1))
    parser.add_argument("--derive-lifts", action="store_true",
                        help="derive actual corrections; otherwise require existing checkpoints")
    args = parser.parse_args()
    for result in write_ff_coefficient(args.parameter, derive_lifts=args.derive_lifts):
        print(result["artifact_digest"], result["cover_residue"], flush=True)
