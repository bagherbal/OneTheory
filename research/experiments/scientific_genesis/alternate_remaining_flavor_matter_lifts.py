"""Derive the missing down and charged-lepton matter coefficients in one carrier.

Owns:
    Actual d^c/e^c outer corrections, explicit quotient pushouts, full witness
    archives, and read-only replay in the unchanged atlas and original bases.

Depends on:
    Pinned constituent inputs, the frozen universal outer class, and the
    established exact constituent and quotient-matter engines.

Must not:
    Recompute Q/L sectors, select an extension point, borrow neutrino or up
    correction values, solve absent read-only inputs, or assign Yukawa entries.

Phase 0:
    Conditional heterotic research inputs; Higgs and complete scalar traces
    remain separate prerequisites for holomorphic flavor matrices.
"""

from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from pathlib import Path

from . import alternate_remaining_flavor_matter as constituents
from . import alternate_up_ff_entries as engine
from .alternate_constituent_up_cone_matter_lifts import CONE, INVARIANTS, _coefficient_job
from .alternate_constituent_up_matter_representatives import AlternateMatterClass
from .alternate_up_coupled_null_scalar import retarget_quotient_block, verify_pushout_matter_lift
from .alternate_up_coupled_tensor_comparison import _push_f_vector, alternate_coupled_quotient
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

MATTER_DIGEST = "363c8bc51e58fd6177943b89fdac08b760c5059bf09b1ba7e64b84414a53a8dc"
SCHEMA = "alternate-remaining-flavor-matter-lift-v1"
PROOF = constituents.PROOF.with_name("ALTERNATE_REMAINING_FLAVOR_MATTER_LIFTS_NOTE.md")


def _inputs():
    """Read the four actual archived F classes; do not choose or solve new bases."""

    record, witnesses = constituents.load_remaining_flavor_matter(expected_digest=MATTER_DIGEST)
    classes = {}
    for sector, character in enumerate(((1, 1), (2, 0))):
        selected = [item for item in record["second_constituent_classes"]
                    if item["constituent_character"] == list(character)]
        for family, item in enumerate(selected, 1):
            classes[sector, family] = AlternateMatterClass(
                character, item["seed_index"],
                tuple(_parse_eisenstein_text(value) for value in item["cohomology_coordinates"]),
                witnesses[f"second_sector{sector}_family{family}"],
                item["inclusion_depth"], item["projection_depth"],
            )
    return classes, {
        **record["prerequisite_artifact_digests"], "actual_remaining_matter": MATTER_DIGEST,
        "universal_cone": _verified_payload(CONE)[0],
        "invariant_outer_basis": _verified_payload(INVARIANTS)[0],
        "coupled_product_presentation": _verified_payload(engine.COMPARISON)[0],
    }


def lift_path(parameter: int, sector: int, family: int, directory: Path = engine.GENERATED):
    """Name only the declared original parameter, sector, and family indices."""

    engine._indices(parameter, family)
    if type(sector) is not int or sector not in (0, 1):
        raise ValueError("remaining matter sector must be 0 (d^c) or 1 (e^c)")
    return directory / (
        f"alternate_remaining_flavor_lift_a{parameter}_sector{sector}_family{family}.json"
    )


def write_matter_lifts(parameter: int, directory: Path = engine.GENERATED, *, workers: int = 1):
    """Explicitly derive four new coefficients, archiving each completed identity."""

    engine._indices(parameter, 1)
    if type(workers) is not int or workers not in (1, 2):
        raise ValueError("remaining matter execution requires exactly one or two workers")
    classes, parents = _inputs()
    model, unit = alternate_coupled_quotient(parameter), mixed_schoen_unit()
    line = MixedSchoenUnit("actual B1 quotient", 0, QUOTIENT_LINE, (
        MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),
    ))
    source_context = _MixedContraction(model.source, unit)
    line_context = _MixedContraction(line, unit)
    extension = alternate_outer_coefficient(parameter)
    jobs = [(sector, family, parameter, matter, extension)
            for (sector, family), matter in classes.items()]

    def save(completed):
        sector, family, _, coefficient = completed
        matter = classes[sector, family]
        constant = _push_f_vector(matter.full_cochain, model)
        correction = retarget_quotient_block(
            _quotient(coefficient.correction, line_context), source_context, {0: 0}, dual=False,
        )
        verify_pushout_matter_lift(model, constant, correction)
        result = engine._write_witnesses(lift_path(parameter, sector, family, directory), {
            "schema": SCHEMA, "coefficient_field": "Q(omega)",
            "carrier_status": "conditional on the selected heterotic UV realization",
            "parameter": f"a{parameter}", "outer_parameter_basis": ["a0", "a1"],
            "sector": sector, "sector_label": ("d^c", "e^c")[sector], "family": family,
            "character": list(matter.character), "seed_index": matter.seed_index,
            "actual_constituent_coefficient": coefficient.as_record(),
            "full_constituent_identity_exact": True, "full_pushout_identity_exact": True,
            "prerequisite_artifact_digests": parents,
            "proof_sha256": sha256(PROOF.read_bytes()).hexdigest(),
            "existing_Q_and_L_recomputed": False, "extension_point_selected": False,
            "yukawa_entries_assigned": False, "physical_yukawas_available": False,
            "observational_inputs_used": False,
        }, {"constant": constant, "constituent_correction": coefficient.correction,
            "line_correction": correction})
        print(f"a{parameter}: saved actual {( 'd^c', 'e^c')[sector]} family {family} correction",
              flush=True)
        return result

    print(f"a{parameter}: deriving the four missing d^c/e^c corrections", flush=True)
    if workers == 1:
        return tuple(save(_coefficient_job(job)) for job in jobs)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return tuple(save(completed) for completed in pool.map(_coefficient_job, jobs))


def load_matter_lift(parameter: int, sector: int, family: int, *, expected_digest: str,
                     directory: Path = engine.GENERATED):
    """Read one pinned complete witness with no missing-input solver fallback."""

    path = lift_path(parameter, sector, family, directory)
    digest, record = _verified_payload(path)
    if digest != expected_digest:
        raise ValueError("the remaining matter lift changed its trusted content digest")
    classes, parents = _inputs()
    matter = classes[sector, family]
    if (record.get("schema") != SCHEMA or record.get("coefficient_field") != "Q(omega)"
        or record.get("carrier_status") != "conditional on the selected heterotic UV realization"
        or record.get("prerequisite_artifact_digests") != parents
        or record.get("proof_sha256") != sha256(PROOF.read_bytes()).hexdigest()
        or record.get("outer_parameter_basis") != ["a0", "a1"]
        or record.get("parameter") != f"a{parameter}"
        or (record.get("sector"), record.get("family")) != (sector, family)
        or record.get("sector_label") != ("d^c", "e^c")[sector]
        or record.get("character") != list(matter.character)
        or record.get("seed_index") != matter.seed_index
        or any(record.get(flag) is not True for flag in (
            "full_constituent_identity_exact", "full_pushout_identity_exact",
        ))
        or any(record.get(flag) is not False for flag in (
            "existing_Q_and_L_recomputed", "extension_point_selected", "yukawa_entries_assigned",
            "physical_yukawas_available", "observational_inputs_used",
        ))):
        raise ValueError("the remaining matter lift changed its actual input, basis, or scope")
    record, witnesses = engine._read_witnesses(path, SCHEMA, (
        "constant", "constituent_correction", "line_correction",
    ))
    coefficient = record.get("actual_constituent_coefficient", {})
    if (coefficient.get("parameter") != f"a{parameter}"
        or coefficient.get("correction_digest")
        != _cochain_digest((witnesses["constituent_correction"],))
        or coefficient.get("correction_term_count")
        != len(witnesses["constituent_correction"].terms)
        or any(coefficient.get(flag) is not True for flag in (
            "product_cycle_exact", "coefficientwise_cone_identity_exact",
            "strict_alternate_character_exact",
        ))):
        raise ValueError("the remaining matter lift changed its constituent identity")
    return {"artifact_digest": digest, **record}, witnesses, matter


def replay_matter_lift(parameter: int, sector: int, family: int, *, expected_digest: str,
                       directory: Path = engine.GENERATED):
    """Verify actual full equations and deck maps without rerunning the solver."""

    record, witnesses, matter = load_matter_lift(
        parameter, sector, family, expected_digest=expected_digest, directory=directory,
    )
    return engine.checked_quotient_matter_lift(
        parameter, matter, witnesses["constant"], witnesses["constituent_correction"],
        witnesses["line_correction"], checkpoint_digest=record["artifact_digest"],
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameter", type=int, choices=(0, 1))
    parser.add_argument("--workers", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    for record in write_matter_lifts(args.parameter, workers=args.workers):
        print(record["artifact_digest"], flush=True)
