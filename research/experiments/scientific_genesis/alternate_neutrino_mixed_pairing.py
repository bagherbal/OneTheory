"""Derive actual constant neutrino couplings in the frozen alternate carrier.

Owns:
    Source-pinned L and nu^c character routing, strict constituent cycles, four
    canonical mixed scalars, complete witnesses, and explicit quotient traces.

Depends on:
    The frozen carrier and determinant repair, reusable strict-character
    projectors, the existing up-Higgs quotient, and the original scalar engine.

Must not:
    Copy up-sector coupling values, identify different family bases, fill an
    uncomputed F-F block, select parameters, infer Majorana masses or metrics.

Phase 0:
    Conditional research holomorphic pairings; the full neutrino matrix is open.
"""

from __future__ import annotations

import hashlib
from functools import cache

from onetheory.math.numbers import Rational

from . import alternate_up_mixed_quotient_pairing as pairing
from .alternate_constituent_structural_spectrum import CONVENTION
from .alternate_constituent_up_cone_matter_lifts import _first_representatives_for
from .alternate_constituent_up_matter_representatives import (
    CARRIER,
    SPECTRUM,
    SPECTRUM_ARXIV_ID,
    SPECTRUM_SOURCE_SHA256,
    _add,
    _negative,
    _source_digest,
    _strict_i6_representatives,
)
from .alternate_up_ff_entries import _read_witnesses, _write_witnesses
from .alternate_up_mixed_quotient_pairing import (
    MixedQuotientEntry,
    quotient_mixed_product,
)
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = pairing.OUTPUT.with_name("alternate_neutrino_mixed_pairing.json")
PROOF = "research/experiments/scientific_genesis/ALTERNATE_NEUTRINO_MIXED_PAIRING_NOTE.md"
SCHEMA = "alternate-neutrino-mixed-pairing-v1"
POSITIONS = ((0, 1), (0, 2), (1, 0), (2, 0))
WITNESS_NAMES = (
    *(f"first_side{side}" for side in (0, 1)),
    *(f"second_side{side}_family{family}" for side in (0, 1) for family in (1, 2)),
    *(f"r{row}_c{column}_{name}" for row, column in POSITIONS
      for name in ("scalar", "reverse", "exchange_primitive")),
)


def route():
    """Convert published Wilson weights using the already certified source convention."""

    carrier_digest, carrier = _verified_payload(CARRIER)
    spectrum_digest, spectrum = _verified_payload(SPECTRUM)
    convention_digest, convention = _verified_payload(CONVENTION)
    state = carrier.get("computable_one_theory_carrier_state", {})
    if (carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or spectrum.get("schema") != "alternate-constituent-structural-spectrum-v1"
        or state.get("frozen") is not True
        or state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or state.get("certificate_digests", {}).get("observable_spectrum") != spectrum_digest
        or spectrum.get("matter_cover_h0_to_h3") != [0, 27, 0, 0]
        or spectrum.get("cover_higgs_h0_to_h3") != [0, 4, 4, 0]
        or spectrum.get("common_flat_twist") != [1, 2]
        or convention.get("character_conversion") != "source=(-forward) mod 3 factorwise"
        or spectrum.get("prerequisite_artifact_digests", {}).get("source_character_convention")
        != convention_digest):
        raise ValueError("the actual carrier or source/forward character convention changed")
    source_digest = _source_digest(SPECTRUM_ARXIV_ID, SPECTRUM_SOURCE_SHA256)
    weights, higgs = ((0, 0), (0, 1)), (0, 2)
    twist = tuple(spectrum["common_flat_twist"])
    characters = tuple(_add(weight, _negative(twist)) for weight in weights)
    if (characters != ((2, 1), (2, 2))
        or _add(_add(*weights), higgs) != (0, 0)
        or list(higgs) not in spectrum.get("higgs_forward_characters", [])
        or _add(*characters) != (1, 0)):
        raise ValueError("the source-pinned Dirac-neutrino routing is incompatible")
    return characters, {
        "frozen_carrier": carrier_digest, "structural_spectrum": spectrum_digest,
        "source_character_convention": convention_digest, "published_wilson_source": source_digest,
        "canonical_up_pairing": _verified_payload(pairing.OUTPUT)[0],
        "shared_up_higgs": _verified_payload(pairing.HIGGS_CONE)[0],
        "quotient_trace": _verified_payload(pairing.TRACE)[0],
    }


@cache
def matter_classes():
    """Return actual ordered E/F constituent classes, never uncorrected V classes."""

    characters, _ = route()
    first = _first_representatives_for(characters)
    second, dimension, boundaries = _strict_i6_representatives(characters)
    if (len(first) != 2 or len(second) != 4 or dimension != 18 or boundaries != 189
        or [item.character for item in first] != list(characters)
        or [item.character for item in second] != [characters[0]]*2 + [characters[1]]*2):
        raise ValueError("the actual neutrino constituent character bases are incomplete")
    return first, second


@cache
def mixed_entries():
    """Compute all four mixed scalars, with exact exchange and independent trace checks."""

    first, second = matter_classes()
    line = MixedSchoenUnit("actual B1 quotient", 0, pairing.QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 quotient", 0, pairing.QUOTIENT_LINE),))
    line_context = _MixedContraction(line, mixed_schoen_unit())
    h = pairing.alternate_higgs_quotient_covector()
    results = []
    for left, character, line_first in (
        (first[0], first[1].character, True), (first[1], first[0].character, False),
    ):
        quotient = pairing._quotient(left.full_cochain, line_context)
        if not line_context.differential(quotient).is_zero():
            raise ValueError("a neutrino E class lost its full quotient closure")
        selected = tuple(item for item in second if item.character == character)
        if len(selected) != 2:
            raise ValueError("each actual neutrino F character needs two independent classes")
        for family, matter in enumerate(selected, start=1):
            scalar = pairing.mixed_outer_cup(h, quotient_mixed_product(
                quotient, matter.full_cochain, line_first=line_first,
            ))
            reverse = pairing.mixed_outer_cup(h, quotient_mixed_product(
                quotient, matter.full_cochain, line_first=not line_first,
            ))
            if not pairing._scalar_context().differential(scalar).is_zero():
                raise ValueError("a canonical neutrino scalar is not fully closed")
            direct = pairing.direct_ordered_scalar_residue(scalar)
            reduced, _depth = _perturbed_projection(scalar, pairing._scalar_context(), 3)
            if (set(reduced) - {0} or reduced.get(0, 0) != direct
                or pairing.direct_ordered_scalar_residue(reverse) != direct):
                raise ValueError("the independent canonical neutrino traces disagree")
            difference = reverse + scalar.scale(-1)
            primitive, _ = pairing.perturbed_homotopy(difference, pairing._scalar_context())
            if pairing._scalar_context().differential(primitive) != difference:
                raise ValueError("the neutrino exchange lacks its full exact boundary identity")
            results.append(MixedQuotientEntry(
                0 if line_first else family, family if line_first else 0,
                left.character, matter.character, matter.seed_index,
                scalar, reverse, primitive, direct,
            ))
    return tuple(results)


def write_mixed_pairing(path=OUTPUT):
    """Archive only derived entries and actual witnesses; do not return a guessed matrix."""

    characters, prerequisites = route()
    _, trace = _verified_payload(pairing.TRACE)
    if (trace.get("cover_to_quotient_trace_factor") != "1/9"
        or trace.get("volume_form_convention", {}).get("relation")
        != "pi*Omega_quotient=Omega_cover"
        or trace.get("scalar_class_descent_certified") is not True):
        raise ValueError("the shared quotient trace normalization is not certified")
    first, second = matter_classes()
    entries, witnesses = mixed_entries(), {}
    for side, item in enumerate(first):
        witnesses[f"first_side{side}"] = item.full_cochain
    for side, character in enumerate(characters):
        for family, item in enumerate((i for i in second if i.character == character), start=1):
            witnesses[f"second_side{side}_family{family}"] = item.full_cochain
    for item in entries:
        for name, value in (("scalar", item.scalar), ("reverse", item.reverse_scalar),
                            ("exchange_primitive", item.exchange_primitive)):
            witnesses[f"r{item.row}_c{item.column}_{name}"] = value
    known = {(item.row, item.column): item.cover_residue / 9 for item in entries}
    minors = {f"rows_0_{i}_columns_0_{j}": str(-known[0, j] * known[i, 0])
              for i in (1, 2) for j in (1, 2)}
    return _write_witnesses(path, {
        "schema": SCHEMA,
        "carrier_status": "conditional on the selected heterotic UV realization",
        "coupling": ["L", "nu^c", "H_u"],
        "source": {"arxiv_id": SPECTRUM_ARXIV_ID, "version": "v3", "locator": "eq:burt4"},
        "wilson_weights": [[0, 0], [0, 1], [0, 2]], "common_flat_twist": [1, 2],
        "pre_twist_matter_characters": [list(c) for c in characters],
        "parameter_basis": ["a0", "a1"],
        "basis_convention": "unchanged reduced seed order; rows L, columns nu^c",
        "first_constituent_classes": [item.as_record() for item in first],
        "second_constituent_classes": [item.as_record((1, 2)) for item in second],
        "shared_higgs_covector_digest": _cochain_digest((
            pairing.alternate_higgs_quotient_covector(),
        )),
        "proof": PROOF,
        "proof_sha256": hashlib.sha256((pairing.ROOT / PROOF).read_bytes()).hexdigest(),
        "scalar_order": "Higgs first in the fixed quotient volume frame",
        "cover_to_quotient_trace_factor": "1/9",
        "evaluated_entries": [{**item.as_record(),
            "quotient_residue": str(item.cover_residue * Rational(1, 9))} for item in entries],
        "exact_known_two_by_two_minors": minors,
        "constant_mixed_entries_evaluated": True,
        "constituent_classes_are_uncorrected_cone_classes": False,
        "first_first_entry_zero_by_B_wedge_B": True,
        "second_second_entries_assigned": False,
        "complete_holomorphic_neutrino_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "canonical_matter_metrics_available": False,
        "majorana_mechanism_derived": False,
        "common_vacuum_stabilized": False,
        "extension_point_selected": False, "observational_inputs_used": False,
        "prerequisite_artifact_digests": prerequisites,
        "next_required_object": (
            "actual neutrino constituent corrections and full F-F coefficient blocks"
        ),
    }, witnesses)


def load_mixed_pairing(path=OUTPUT, *, expected_digest: str):
    """Consume actual full witnesses with a trusted digest; never call a solver."""

    record, witnesses = _read_witnesses(path, SCHEMA, WITNESS_NAMES)
    record = {**record, "artifact_digest": _verified_payload(path)[0]}
    characters, prerequisites = route()
    if (record.get("artifact_digest") != expected_digest
        or record.get("prerequisite_artifact_digests") != prerequisites
        or record.get("proof") != PROOF
        or record.get("proof_sha256")
        != hashlib.sha256((pairing.ROOT / PROOF).read_bytes()).hexdigest()
        or record.get("coupling") != ["L", "nu^c", "H_u"]
        or record.get("wilson_weights") != [[0, 0], [0, 1], [0, 2]]
        or record.get("common_flat_twist") != [1, 2]
        or record.get("pre_twist_matter_characters") != [list(c) for c in characters]
        or record.get("parameter_basis") != ["a0", "a1"]
        or record.get("source") != {
            "arxiv_id": SPECTRUM_ARXIV_ID, "version": "v3", "locator": "eq:burt4",
        }
        or record.get("scalar_order") != "Higgs first in the fixed quotient volume frame"
        or record.get("cover_to_quotient_trace_factor") != "1/9"
        or [(item.get("row"), item.get("column"))
            for item in record.get("evaluated_entries", [])] != list(POSITIONS)
        or any(record.get(flag) is not True for flag in (
            "constant_mixed_entries_evaluated", "first_first_entry_zero_by_B_wedge_B",
        ))
        or any(record.get(flag) is not False for flag in (
            "constituent_classes_are_uncorrected_cone_classes", "second_second_entries_assigned",
            "complete_holomorphic_neutrino_matrix_available", "physical_yukawa_matrix_available",
            "canonical_matter_metrics_available", "majorana_mechanism_derived",
            "common_vacuum_stabilized", "extension_point_selected", "observational_inputs_used",
        ))):
        raise ValueError("the actual neutrino witnesses changed their trusted scope or inputs")
    return record, witnesses


if __name__ == "__main__":
    result = write_mixed_pairing()
    print(result["artifact_digest"], flush=True)
    print([p["cover_residue"] for p in result["evaluated_entries"]], flush=True)
