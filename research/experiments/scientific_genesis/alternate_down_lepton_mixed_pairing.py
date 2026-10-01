"""Derive the actual down and charged-lepton mixed scalar blocks.

Owns:
    Original ordered E/F inputs, explicitly supplied down-Higgs evaluation,
    eight mixed scalars, literal witnesses, and fixed quotient traces.

Depends on:
    Pinned same-carrier constituent and Higgs certificates, original quotient
    index maps, and the existing signed mixed scalar and trace engines.

Must not:
    Substitute up/neutrino values, re-solve Q/L corrections, select a family
    basis or parameter point, fill F-F entries, or infer physical normalization.

Phase 0:
    Conditional heterotic research; partial scalar blocks are not full matrices.
"""

from functools import cache
from hashlib import sha256

from onetheory.math.numbers import Rational

from . import alternate_down_higgs_quotient_cone as down
from . import alternate_neutrino_mixed_pairing as neutrino
from . import alternate_remaining_flavor_matter as remaining
from . import alternate_up_mixed_quotient_pairing as engine
from .alternate_constituent_up_cone_matter_lifts import OUTPUT as UP_FIRST
from .alternate_constituent_up_cone_matter_lifts import _first_representatives_for
from .alternate_constituent_up_matter_representatives import OUTPUT as UP_MATTER
from .alternate_up_coupled_null_scalar import retarget_quotient_block
from .alternate_up_ff_entries import GENERATED, _read_witnesses, _write_witnesses
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_models,
    quotient_higgs_covector,
)
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = GENERATED / "alternate_down_lepton_mixed_pairing.json"
PROOF = down.hom.PROOF.with_name("ALTERNATE_DOWN_LEPTON_MIXED_PAIRING_NOTE.md")
SCHEMA = "alternate-down-lepton-mixed-pairing-v1"
POSITIONS = ((0, 1), (0, 2), (1, 0), (2, 0))
CHARACTERS = (((0, 0), (1, 1)), ((2, 1), (2, 0)))
PINS = (
    ("actual_down_higgs_cone", down.OUTPUT,
     "50d0a3f0f2547f5c1eb05444765b2322075dc03fd56b2b65cf7874534044274f"),
    ("actual_remaining_matter", remaining.OUTPUT,
     "363c8bc51e58fd6177943b89fdac08b760c5059bf09b1ba7e64b84414a53a8dc"),
    ("actual_L_matter", neutrino.OUTPUT,
     "1bc8020db27e9f7a3c7ee7a7abf4ab0c456903c993eab27b0038cad5e12e6049"),
    ("original_Q_first_metadata", UP_FIRST,
     "b821725103b3d341032e15d2335b2916fd82bcd211ec2611b9c0d41d2700d677"),
    ("original_Q_second_metadata", UP_MATTER,
     "f90026450eb9c2d4a0b84085bb64518ec3e9def5ebc5af65aa2aae30a7d94976"),
    ("original_Q_quotient_metadata", engine.OUTPUT,
     "6f475e7551bf00b13cfea5207293ffb517fdbd09d94e8b97264cd2edae941591"),
    ("actual_Q_constant_family1", GENERATED / "alternate_up_ff_lift_a0_side0_family1.json",
     "b2fd30e6b26c8140ff52c41604e161d7fe39e83fd5edbafd63a224e0489094ea"),
    ("actual_Q_constant_family2", GENERATED / "alternate_up_ff_lift_a0_side0_family2.json",
     "d76441a381f99bee8419ce380a06e1786c7d8eb4347543b2535b96f35df7673d"),
)
WITNESS_NAMES = (
    "actual_down_higgs_hom", "actual_down_higgs_quotient",
    *(f"first_s{sector}_{side}" for sector in (0, 1) for side in ("row", "column")),
    *(f"second_s{sector}_{side}_f{family}" for sector in (0, 1)
      for side in ("row", "column") for family in (1, 2)),
    *(f"s{sector}_r{row}_c{column}_{name}" for sector in (0, 1)
      for row, column in POSITIONS for name in ("scalar", "reverse", "exchange_primitive")),
)


def _parents():
    """Bind actual prerequisites without invoking a generator or primitive solver."""

    parents = {}
    for name, path, expected in PINS:
        digest, _ = _verified_payload(path)
        if digest != expected:
            raise ValueError("an actual down/lepton mixed prerequisite changed its trusted digest")
        parents[name] = digest
    trace_digest, trace = _verified_payload(engine.TRACE)
    if (trace.get("cover_to_quotient_trace_factor") != "1/9"
        or trace.get("volume_form_convention", {}).get("relation")
        != "pi*Omega_quotient=Omega_cover"
        or trace.get("scalar_class_descent_certified") is not True):
        raise ValueError("the actual down/lepton quotient trace convention changed")
    return {**parents, "fixed_quotient_trace": trace_digest}


@cache
def matter_inputs():
    """Reuse literal classes; reproduce only the original unarchived Q E class."""

    _parents()
    _, new = remaining.load_remaining_flavor_matter(expected_digest=PINS[1][2])
    _, old = neutrino.load_mixed_pairing(expected_digest=PINS[2][2])
    first_q = _first_representatives_for(((0, 0),))[0]
    _, metadata = _verified_payload(UP_FIRST)
    if first_q.as_record() != metadata["first_constituent_constant_classes"][0]:
        raise ValueError("the reproduced original Q first class changed its whole certificate")
    first = {(0, "row"): first_q.full_cochain, (1, "row"): old["first_side0"],
             (0, "column"): new["first_sector0"], (1, "column"): new["first_sector1"]}
    second = {(sector, "column", family): new[f"second_sector{sector}_family{family}"]
              for sector in (0, 1) for family in (1, 2)}
    second.update({(1, "row", family): old[f"second_side0_family{family}"]
                   for family in (1, 2)})
    actual_f = alternate_higgs_quotient_models()[0]
    context = _MixedContraction(actual_f, mixed_schoen_unit())
    _, metadata = _verified_payload(UP_MATTER)
    for family in (1, 2):
        record, witnesses = _read_witnesses(PINS[5 + family][1], "alternate-up-ff-matter-lift-v1",
            ("constant", "constituent_correction", "line_correction"))
        if record.get("character") != [0, 0] or record.get("seed_index") != (0, 5)[family - 1]:
            raise ValueError("the actual Q constant witness changed its original family")
        value = retarget_quotient_block(witnesses["constant"], context,
                                       {i + 1: i for i in range(len(actual_f.objects))}, dual=False)
        if _cochain_digest((value,)) != metadata["classes"][family - 1]["full_digest"]:
            raise ValueError("the recovered raw Q class differs from its original certificate")
        second[0, "row", family] = value
    return first, second


@cache
def actual_higgs():
    """Use the small literal Hom witness; do not decode irrelevant bulk primitives."""

    _parents()
    _, hom = down.hom.load_down_higgs_hom(expected_digest=down.HOM_DIGEST)
    quotient = quotient_higgs_covector(hom)
    _, packet = _verified_payload(down.OUTPUT)
    if _cochain_digest((quotient,)) != packet["witnesses"]["quotient_covector"]["cochain_digest"]:
        raise ValueError("the actual down-Higgs quotient differs from its replayed certificate")
    return hom, quotient


def write_mixed_pairing(path=OUTPUT):
    """Compute eight actual scalars; leave every uncomputed F-F entry unavailable."""

    parents = _parents()
    first, second = matter_inputs()
    hom, h = actual_higgs()
    line = MixedSchoenUnit("actual B1 quotient", 0, engine.QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 quotient", 0, engine.QUOTIENT_LINE),))
    context = _MixedContraction(line, mixed_schoen_unit())
    witnesses = {"actual_down_higgs_hom": hom, "actual_down_higgs_quotient": h,
                 **{f"first_s{s}_{side}": value for (s, side), value in first.items()},
                 **{f"second_s{s}_{side}_f{f}": value for (s, side, f), value in second.items()}}
    sectors = []
    for sector, (row_character, column_character) in enumerate(CHARACTERS):
        entries = []
        for first_side, second_side, line_first in (("row", "column", True),
                                                   ("column", "row", False)):
            quotient = engine._quotient(first[sector, first_side], context)
            if not context.differential(quotient).is_zero():
                raise ValueError("an actual down/lepton E quotient is not fully closed")
            if sector == 0 and first_side == "row":
                original = _verified_payload(engine.OUTPUT)[1]["first_matter_quotient_digests"][0]
                if _cochain_digest((quotient,)) != original["cochain_digest"]:
                    raise ValueError("the reproduced Q quotient changed its original orientation")
            for family in (1, 2):
                print(f"{('down', 'charged lepton')[sector]}: mixed {first_side} E family {family}",
                      flush=True)
                seed = ((2, 4), (0, 5))[sector][family - 1] if line_first else (
                    ((0, 5), (2, 4))[sector][family - 1]
                )
                entry = engine.evaluate_mixed_entry(
                    h, quotient, second[sector, second_side, family], line_first=line_first,
                    family=family,
                    first_character=row_character if line_first else column_character,
                    second_character=column_character if line_first else row_character,
                    second_seed_index=seed,
                )
                entries.append({**entry.as_record(),
                                "quotient_residue": str(entry.cover_residue * Rational(1, 9))})
                for name, value in (("scalar", entry.scalar), ("reverse", entry.reverse_scalar),
                                    ("exchange_primitive", entry.exchange_primitive)):
                    witnesses[f"s{sector}_r{entry.row}_c{entry.column}_{name}"] = value
                print(f"cover residue: {entry.cover_residue}", flush=True)
        sectors.append({"sector": sector, "coupling": [["Q", "d^c", "H_d"],
                        ["L", "e^c", "H_d"]][sector],
                        "native_matter_characters": [list(row_character), list(column_character)],
                        "evaluated_entries": entries})
    if _parents() != parents:
        raise ValueError("actual mixed prerequisites changed during evaluation")
    return _write_witnesses(path, {
        "schema": SCHEMA, "coefficient_field": "Q(omega)",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "source": remaining.SOURCE, "outer_parameter_basis": ["a0", "a1"],
        "native_down_higgs_hom_character": [2, 2], "sectors": sectors,
        "basis_convention": "unchanged original E/F reduced seed order and atlas frames",
        "scalar_order": "Higgs first in the fixed quotient volume frame",
        "cover_to_quotient_trace_factor": "1/9", "exterior_filtration_parameter_degree": 0,
        "first_first_entry_zero_by_B_wedge_B": True, "constant_mixed_entries_evaluated": True,
        "Q_first_class_reproduced_from_existing_generator": True,
        "Q_and_L_matter_corrections_recomputed": False, "second_second_entries_assigned": False,
        "complete_down_matrix_available": False, "complete_charged_lepton_matrix_available": False,
        "physical_yukawas_available": False, "extension_point_selected": False,
        "observational_inputs_used": False, "proof_sha256": sha256(PROOF.read_bytes()).hexdigest(),
        "prerequisite_artifact_digests": parents,
    }, witnesses)


def load_mixed_pairing(path=OUTPUT, *, expected_digest: str):
    """Consume a trusted literal packet without any generation or solver fallback."""

    digest, record = _verified_payload(path)
    if digest != expected_digest:
        raise ValueError("the actual down/lepton mixed packet changed its trusted digest")
    if (record.get("schema") != SCHEMA or record.get("coefficient_field") != "Q(omega)"
        or record.get("prerequisite_artifact_digests") != _parents()
        or record.get("source") != remaining.SOURCE
        or record.get("proof_sha256") != sha256(PROOF.read_bytes()).hexdigest()
        or record.get("carrier_status") != "conditional on the selected heterotic UV realization"
        or record.get("outer_parameter_basis") != ["a0", "a1"]
        or record.get("native_down_higgs_hom_character") != [2, 2]
        or record.get("basis_convention")
        != "unchanged original E/F reduced seed order and atlas frames"
        or record.get("scalar_order") != "Higgs first in the fixed quotient volume frame"
        or record.get("cover_to_quotient_trace_factor") != "1/9"
        or record.get("exterior_filtration_parameter_degree") != 0
        or any(record.get(flag) is not True for flag in (
            "first_first_entry_zero_by_B_wedge_B", "constant_mixed_entries_evaluated",
            "Q_first_class_reproduced_from_existing_generator",
        ))
        or any(record.get(flag) is not False for flag in (
            "Q_and_L_matter_corrections_recomputed", "second_second_entries_assigned",
            "complete_down_matrix_available", "complete_charged_lepton_matrix_available",
            "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
        ))):
        raise ValueError("the actual down/lepton mixed packet changed its scope, bases, or inputs")
    sectors = record.get("sectors", [])
    if len(sectors) != 2 or any(
        item.get("sector") != index
        or item.get("coupling") != [["Q", "d^c", "H_d"], ["L", "e^c", "H_d"]][index]
        or item.get("native_matter_characters") != [list(c) for c in CHARACTERS[index]]
        or [(entry.get("row"), entry.get("column")) for entry in item.get("evaluated_entries", [])]
        != list(POSITIONS) for index, item in enumerate(sectors)
    ):
        raise ValueError("the actual down/lepton mixed packet changed its sector or entry order")
    record, witnesses = _read_witnesses(path, SCHEMA, WITNESS_NAMES)
    for sector in sectors:
        for entry in sector["evaluated_entries"]:
            prefix = f"s{sector['sector']}_r{entry['row']}_c{entry['column']}"
            for name in ("scalar", "reverse", "exchange_primitive"):
                label = "reverse_scalar" if name == "reverse" else name
                value = witnesses[f"{prefix}_{name}"]
                if (entry.get(f"{label}_digest") != _cochain_digest((value,))
                    or entry.get(f"{label}_term_count") != len(value.terms)):
                    raise ValueError("an actual down/lepton entry changed its literal witness")
            residue = engine.direct_ordered_scalar_residue(witnesses[f"{prefix}_scalar"])
            if (entry.get("cover_residue") != str(residue)
                or entry.get("quotient_residue") != str(residue * Rational(1, 9))
                or any(entry.get(flag) is not True for flag in (
                    "full_scalar_closed_exact", "exchanged_scalar_closed_exact",
                    "exchange_difference_boundary_exact",
                ))):
                raise ValueError("an actual down/lepton entry changed its trace or identity scope")
    return {"artifact_digest": digest, **record}, witnesses


if __name__ == "__main__":
    print(write_mixed_pairing()["artifact_digest"], flush=True)
