"""Generate the source-routed down-Higgs Hom class in the frozen carrier.

Owns:
    Exact character routing and a full strict Hom witness needed by down-quark
    and charged-lepton couplings, in the original deterministic reduced basis.

Depends on:
    Published Wilson provenance, the frozen determinant repair, certified
    source/forward inversion, and the existing exact Hom-character engine.

Must not:
    Copy an up-Higgs class, infer a full exterior Higgs from a Hom witness,
    choose extension parameters, fill Yukawa entries, or infer physical masses.

Phase 0:
    Conditional heterotic research input; the remaining flavor matrices are open.
"""

from __future__ import annotations

from hashlib import sha256

from .alternate_constituent_structural_spectrum import CONVENTION
from .alternate_constituent_up_matter_representatives import (
    CARRIER,
    SPECTRUM,
    SPECTRUM_ARXIV_ID,
    SPECTRUM_SOURCE_SHA256,
    _add,
    _negative,
    _source_digest,
)
from .alternate_up_ff_entries import _read_witnesses, _write_witnesses
from .alternate_up_higgs_hom_representative import (
    CONE,
    HOM_ACTIONS,
    ROOT,
    _strict_hom_representative,
)
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_down_higgs_hom_representative.json"
PROOF = ROOT / "research/experiments/scientific_genesis/ALTERNATE_DOWN_HIGGS_HOM_NOTE.md"
SOURCE = {
    "arxiv_id": SPECTRUM_ARXIV_ID, "version": "v3", "locator": "equation (28)",
    "url": "https://arxiv.org/html/hep-th/0512177v3",
}


def route():
    """Determine the native character from fixed frames and published Hd weight."""

    carrier_digest, carrier = _verified_payload(CARRIER)
    spectrum_digest, spectrum = _verified_payload(SPECTRUM)
    cone_digest, cone = _verified_payload(CONE)
    convention_digest, convention = _verified_payload(CONVENTION)
    state = carrier.get("computable_one_theory_carrier_state", {})
    twist, total, weight = (1, 2), (2, 1), (0, 1)
    native = _add(_add(weight, _negative(total)), _negative(_add(twist, twist)))
    if (carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or spectrum.get("schema") != "alternate-constituent-structural-spectrum-v1"
        or cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or state.get("frozen") is not True
        or state.get("certificate_digests", {}).get("observable_spectrum") != spectrum_digest
        or state.get("certificate_digests", {}).get("universal_cone") != cone_digest
        or spectrum.get("common_flat_twist") != list(twist)
        or cone.get("determinant_character_before_common_twist") != list(total)
        or cone.get("determinant_character_after_common_twist") != [0, 0]
        or convention.get("character_conversion") != "source=(-forward) mod 3 factorwise"
        or spectrum.get("prerequisite_artifact_digests", {}).get("source_character_convention")
        != convention_digest
        or list(weight) not in spectrum.get("higgs_forward_characters", [])
        or native != (2, 2) or list(native) not in spectrum.get("hom_fourier_characters", [])
        or _add(native, _negative(_add(twist, twist))) != weight):
        raise ValueError("the actual down-Higgs routing or frozen determinant repair changed")
    return native, {
        "frozen_carrier": carrier_digest, "structural_spectrum": spectrum_digest,
        "universal_cone": cone_digest, "source_character_convention": convention_digest,
        "alternate_hom_actions": _verified_payload(HOM_ACTIONS)[0],
        "published_wilson_source": _source_digest(SPECTRUM_ARXIV_ID, SPECTRUM_SOURCE_SHA256),
    }


def write_down_higgs_hom(path=OUTPUT):
    """Save one actual Hom class, not a substitute Higgs or guessed coupling."""

    native, prerequisites = route()
    full, seed, coordinates, inclusion, projection = _strict_hom_representative(native)
    return _write_witnesses(path, {
        "schema": "alternate-down-higgs-hom-class-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "coefficient_field": "Q(omega)", "native_hom_character": list(native),
        "repaired_higgs_forward_character": [0, 1], "repaired_higgs_source_character": [0, 2],
        "common_flat_twist": [1, 2], "covector_common_twist_weight": -2,
        "source": SOURCE, "proof_sha256": sha256(PROOF.read_bytes()).hexdigest(),
        "hom_orientation": "Hom(V2 tensor det(V1), V1)",
        "reduced_basis_identity": "alternate:up-higgs:Hom (unchanged original identity)",
        "seed_index": seed, "cohomology_coordinates": [str(c) for c in coordinates],
        "inclusion_depth": inclusion, "projection_depth": projection,
        "full_cycle_exact": True, "strict_native_character_exact": True, "nonboundary_exact": True,
        "higgs_exterior_cocycle_constructed": False, "constant_mixed_couplings_evaluated": False,
        "complete_down_matrix_available": False, "complete_charged_lepton_matrix_available": False,
        "physical_yukawas_available": False, "extension_point_selected": False,
        "observational_inputs_used": False, "prerequisite_artifact_digests": prerequisites,
        "next_required_object": (
            "realize the actual down-Higgs quotient covector, then derive all down and "
            "charged-lepton matter products on this same carrier"
        ),
    }, {"strict_native_hom": full})


def load_down_higgs_hom(path=OUTPUT, *, expected_digest: str):
    """Read a pinned full class without solving or silently constructing a Higgs."""

    digest, _ = _verified_payload(path)
    if digest != expected_digest:
        raise ValueError("the down-Higgs Hom input changed its expected content digest")
    record, witnesses = _read_witnesses(
        path, "alternate-down-higgs-hom-class-v1", ("strict_native_hom",),
    )
    native, parents = route()
    if (record.get("prerequisite_artifact_digests") != parents
        or record.get("native_hom_character") != list(native)
        or record.get("repaired_higgs_forward_character") != [0, 1]
        or record.get("repaired_higgs_source_character") != [0, 2]
        or record.get("common_flat_twist") != [1, 2]
        or record.get("covector_common_twist_weight") != -2
        or record.get("coefficient_field") != "Q(omega)"
        or record.get("seed_index") != 1
        or record.get("cohomology_coordinates")
        != ["0", "1/3-1/3*omega", "0", "2/3+1/3*omega"]
        or record.get("inclusion_depth") != 2 or record.get("projection_depth") != 1
        or record.get("source") != SOURCE
        or record.get("proof_sha256") != sha256(PROOF.read_bytes()).hexdigest()
        or record.get("hom_orientation") != "Hom(V2 tensor det(V1), V1)"
        or record.get("reduced_basis_identity")
        != "alternate:up-higgs:Hom (unchanged original identity)"
        or any(record.get(flag) is not True for flag in (
            "full_cycle_exact", "strict_native_character_exact", "nonboundary_exact",
        ))
        or any(record.get(flag) is not False for flag in (
            "higgs_exterior_cocycle_constructed", "constant_mixed_couplings_evaluated",
            "complete_down_matrix_available", "complete_charged_lepton_matrix_available",
            "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
        ))):
        raise ValueError("the down-Higgs Hom input changed its source, frames, proof, or scope")
    full = witnesses["strict_native_hom"]
    if (len(full.terms) != 351
        or any(basis.total_degree != 1 for basis, _ in full.terms)):
        raise ValueError("the down-Higgs Hom witness is not a nonzero degree-one cochain")
    return {"artifact_digest": digest, **record}, full


if __name__ == "__main__":
    record = write_down_higgs_hom()
    print(record["artifact_digest"], record["seed_index"], record["witnesses"], flush=True)
