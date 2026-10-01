"""Extract the two missing flavor constituent sectors in the frozen carrier.

Owns:
    Source-routed d^c and e^c characters, exact strict constituent classes in
    the original bases, and complete content-addressed witness archives.

Depends on:
    Pinned Wilson provenance, the fixed determinant repair, original strict
    I3/I6 engines, and the independently checked down-Higgs character input.

Must not:
    Recompute the archived Q/L sectors, invent family bases, substitute up
    coupling values, omit carrier corrections, or infer complete flavor matrices.

Phase 0:
    Conditional heterotic constituent research, not physical matter normalization.
"""

from hashlib import sha256

from . import alternate_down_higgs_hom_representative as down
from .alternate_constituent_up_cone_matter_lifts import _first_representatives_for
from .alternate_constituent_up_matter_representatives import (
    _add,
    _negative,
    _strict_i6_representatives,
)
from .alternate_up_ff_entries import _read_witnesses, _write_witnesses
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = down.ROOT / "data/generated/scientific_genesis/alternate_remaining_flavor_matter.json"
PROOF = down.ROOT / (
    "research/experiments/scientific_genesis/ALTERNATE_REMAINING_FLAVOR_MATTER_NOTE.md"
)
HOM_DIGEST = "476e48e981ab66382b43d2510d7a271b2fa3f82468f885b7050edb9af3cd9276"
SOURCE = {
    "arxiv_id": "hep-th/0512177", "version": "v3", "matter_locator": "equation (24)",
    "higgs_locator": "equation (28)", "url": "https://arxiv.org/html/hep-th/0512177v3",
}


def route():
    """Require both published Wilson triples in the same existing repaired frame."""

    h, parents = down.route()
    twist, weights = (1, 2), ((2, 0), (0, 2))
    characters = tuple(_add(weight, _negative(twist)) for weight in weights)
    known_weights, known_characters = ((1, 2), (0, 0)), ((0, 0), (2, 1))
    if (h != (2, 2) or characters != ((1, 1), (2, 0))
        or any(_add(_add(left, right), (0, 1)) != (0, 0)
               for left, right in zip(known_weights, weights, strict=True))
        or any(_add(_add(left, right), h) != (0, 0)
               for left, right in zip(known_characters, characters, strict=True))):
        raise ValueError("the remaining flavor sectors changed their published character routing")
    record, _ = down.load_down_higgs_hom(expected_digest=HOM_DIGEST)
    if record["prerequisite_artifact_digests"] != parents:
        raise ValueError("the remaining flavor inputs changed their fixed carrier premises")
    return characters, {**parents, "actual_down_higgs_hom": HOM_DIGEST}


def write_remaining_flavor_matter(path=OUTPUT):
    """Derive only the missing classes, without filling any Yukawa block."""

    characters, parents = route()
    print("remaining flavor: deriving actual I3 classes (1,1) and (2,0)", flush=True)
    first = _first_representatives_for(characters)
    print("remaining flavor: deriving actual I6 classes (1,1) and (2,0)", flush=True)
    second, dimension, boundaries = _strict_i6_representatives(characters)
    if (len(first) != 2 or len(second) != 4 or dimension != 18 or boundaries != 189
        or [item.character for item in first] != list(characters)
        or [item.character for item in second] != [characters[0]]*2 + [characters[1]]*2):
        raise ValueError("the actual remaining constituent character bases are incomplete")
    witnesses = {f"first_sector{side}": item.full_cochain for side, item in enumerate(first)}
    for side, character in enumerate(characters):
        for family, item in enumerate((item for item in second if item.character == character), 1):
            witnesses[f"second_sector{side}_family{family}"] = item.full_cochain
    return _write_witnesses(path, {
        "schema": "alternate-remaining-flavor-matter-v1", "coefficient_field": "Q(omega)",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "source": SOURCE,
        "missing_sector_labels": ["d^c", "e^c"], "wilson_weights": [[2, 0], [0, 2]],
        "common_flat_twist": [1, 2], "native_matter_characters": [list(c) for c in characters],
        "native_down_higgs_hom_character": [2, 2], "matter_pair_native_character": [1, 1],
        "first_constituent_classes": [item.as_record() for item in first],
        "second_constituent_classes": [item.as_record((1, 2)) for item in second],
        "second_reduced_h1_dimension": dimension, "second_boundary_dimension": boundaries,
        "basis_convention": "unchanged original reduced seed order and atlas frames",
        "existing_Q_and_L_recomputed": False, "actual_constituent_inputs_computed": True,
        "full_cone_matter_corrections_computed": False, "yukawa_entries_assigned": False,
        "complete_down_matrix_available": False, "complete_charged_lepton_matrix_available": False,
        "physical_yukawas_available": False, "extension_point_selected": False,
        "observational_inputs_used": False, "prerequisite_artifact_digests": parents,
        "proof_sha256": sha256(PROOF.read_bytes()).hexdigest(),
        "next_required_object": (
            "independently verify actual full constituent witnesses, then derive "
            "the remaining same-carrier matter lifts and complete scalar products"
        ),
    }, witnesses)


def load_remaining_flavor_matter(path=OUTPUT, *, expected_digest: str):
    """Consume a pinned literal packet, never solve an absent constituent input."""

    digest, _ = _verified_payload(path)
    if digest != expected_digest:
        raise ValueError("the remaining flavor input changed its expected content digest")
    names = ("first_sector0", "first_sector1", "second_sector0_family1",
             "second_sector0_family2", "second_sector1_family1", "second_sector1_family2")
    record, witnesses = _read_witnesses(path, "alternate-remaining-flavor-matter-v1", names)
    characters, parents = route()
    if (record.get("prerequisite_artifact_digests") != parents
        or record.get("source") != SOURCE or record.get("coefficient_field") != "Q(omega)"
        or record.get("proof_sha256") != sha256(PROOF.read_bytes()).hexdigest()
        or record.get("native_matter_characters") != [list(c) for c in characters]
        or record.get("native_down_higgs_hom_character") != [2, 2]
        or record.get("matter_pair_native_character") != [1, 1]
        or record.get("missing_sector_labels") != ["d^c", "e^c"]
        or record.get("wilson_weights") != [[2, 0], [0, 2]]
        or record.get("common_flat_twist") != [1, 2]
        or record.get("basis_convention")
        != "unchanged original reduced seed order and atlas frames"
        or record.get("second_reduced_h1_dimension") != 18
        or record.get("second_boundary_dimension") != 189
        or record.get("actual_constituent_inputs_computed") is not True
        or any(record.get(flag) is not False for flag in (
            "existing_Q_and_L_recomputed", "full_cone_matter_corrections_computed",
            "yukawa_entries_assigned", "complete_down_matrix_available",
            "complete_charged_lepton_matrix_available", "physical_yukawas_available",
            "extension_point_selected", "observational_inputs_used",
        ))):
        raise ValueError("the remaining flavor input changed its routing, basis, proof, or scope")
    first, second = record.get("first_constituent_classes", []), record.get(
        "second_constituent_classes", [],
    )
    if (len(first) != 2 or len(second) != 4
        or [item.get("character") for item in first] != [list(c) for c in characters]
        or [item.get("constituent_character") for item in second]
        != [list(characters[0])]*2 + [list(characters[1])]*2
        or [item.get("seed_index") for item in first] != [0, 2]
        or [item.get("seed_index") for item in second] != [2, 4, 0, 5]):
        raise ValueError("the remaining flavor input changed its original seed order")
    for side, item in enumerate(first):
        full = witnesses[f"first_sector{side}"]
        if (item.get("full_digest") != _cochain_digest((full,))
            or item.get("full_term_count") != len(full.terms)
            or len(item.get("cohomology_coordinates", [])) != 9
            or item.get("full_cycle_exact") is not True
            or item.get("strict_alternate_character_exact") is not True):
            raise ValueError("an actual remaining E class changed its full witness or coordinates")
    for index, item in enumerate(second):
        full = witnesses[f"second_sector{index // 2}_family{1 + index % 2}"]
        if (item.get("full_digest") != _cochain_digest((full,))
            or item.get("full_term_count") != len(full.terms)
            or len(item.get("cohomology_coordinates", [])) != 18
            or item.get("repaired_carrier_character") != [[2, 0], [0, 2]][index // 2]
            or item.get("full_cycle_exact") is not True
            or item.get("strict_alternate_character_exact") is not True):
            raise ValueError("an actual remaining F class changed its full witness or coordinates")
    return {"artifact_digest": digest, **record}, witnesses


if __name__ == "__main__":
    record = write_remaining_flavor_matter()
    print(record["artifact_digest"], record["witnesses"], flush=True)
