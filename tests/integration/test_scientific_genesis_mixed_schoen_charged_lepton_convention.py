"""Test the convention-corrected charged-lepton matrix certificate.

Owns:
    Regression gates for inverse-pullback relabeling, prerequisite provenance,
    all-orders rank, and the exhausted current-carrier flavor frontier.

Depends on:
    The content-addressed character convention and exact forward-sector matrix.

Must not:
    Recompute dense cochains, retain the withdrawn Dirac-neutrino assignment,
    select a carrier point, or call holomorphic data physically normalized.

Phase 0:
    Integration tests for the exact charged-lepton reinterpretation only.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_charged_lepton_convention import (
    OUTPUT,
    build_charged_lepton_convention,
)

EXPECTED_ARTIFACT_DIGEST = (
    "7a0cd06656863704feaea9d2694df4868203ac46c37d8da9c80b030e7c913d80"
)
EXPECTED_PREREQUISITES = {
    "character_convention": (
        "0fea398b94ab48da7fc0e2172b6b13fced369c62ee035f0014735cccef1fe241"
    ),
    "forward_matter_lifts": (
        "31917dd6c0e5abd9f7fae1f981be51df3e9ff5a5f2f335fc46211d67393fecd6"
    ),
    "forward_tree_matrix": (
        "5db6d9e1df7fd0e3840c565a64b3ca8b27e15991bb5924ece62b519f91f185ab"
    ),
    "forward_universal_matrix": (
        "08a3750a8a914d835113d7f2507c360aa87a549110ae7099e031dcd84337d89c"
    ),
}


def _payload() -> dict[str, object]:
    """Load the frozen certificate and verify its content address."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_ARTIFACT_DIGEST
    assert digest == _canonical_digest(payload)
    return payload


def test_charged_lepton_labels_are_exact_inverse_pullbacks() -> None:
    """The old forward labels correspond to physical charged leptons."""

    payload = _payload()
    assert payload["source_action_is_inverse_forward_pullback"] is True
    assert payload["physical_slice"] == {
        "matrix": "charged-lepton holomorphic Yukawa",
        "source_matter_character_exponents": [[0, 0], [0, 1]],
        "forward_matter_character_exponents": [[0, 0], [0, 2]],
        "source_higgs_character_exponents": [0, 2],
        "forward_higgs_character_exponents": [0, 1],
    }
    assert payload["prior_dirac_neutrino_physical_assignment_valid"] is False
    assert payload["physical_charged_lepton_assignment_exact"] is True


def test_charged_lepton_relabel_preserves_exact_provenance() -> None:
    """The certificate references every immutable chain-level prerequisite."""

    payload = _payload()
    assert payload["prerequisite_artifact_digests"] == EXPECTED_PREREQUISITES
    assert build_charged_lepton_convention() == payload


def test_charged_lepton_matrix_is_an_all_orders_scoped_no_go() -> None:
    """Filtration closure turns the exact zero into a scoped no-go."""

    payload = _payload()
    zero = [["0", "0", "0"]] * 3
    assert payload["tree_matrix_rank"] == 0
    assert payload["complete_first_order_coefficient_count"] == 8
    assert payload["coefficient_matrices"] == {"a0": zero, "a1": zero}
    assert payload["maximum_exterior_allowed_parameter_order"] == 1
    assert payload["higher_orders_structurally_zero"] is True
    assert payload[
        "complete_universal_holomorphic_charged_lepton_matrix_available"
    ] is True
    assert payload["generic_rank"] == 0
    assert payload["classification"] == (
        "SCOPED_ALL_ORDERS_CHARGED_LEPTON_NO_GO"
    )
    assert payload["physical_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["exact"] is True
    assert payload["next_required_object"] == (
        "an exact replacement constituent or carrier realization with a "
        "nontrivial holomorphic Yukawa matrix"
    )
