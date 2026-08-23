"""Tests for the first frozen computable OneTheory carrier component.

Owns:
    Reference/computable separation, component-level freeze criteria, exact
    certificate binding, epistemic status, and unresolved DGA boundaries.

Depends on:
    The carrier-state constructor and its content-addressed generated artifact.

Must not:
    Select an extension point, identify source P3 with lawful P1, or claim
    generated Yukawa representatives or physical observables.

Phase 0:
    Carrier-component freeze tests only; common-DGA construction is next.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.computable_one_theory_carrier_state import (
    OUTPUT,
    computable_one_theory_carrier_state,
)


def test_reference_and_computable_carrier_states_remain_distinct() -> None:
    """The source P3 ledger is not silently identified with the lawful P1."""

    reference, computable = computable_one_theory_carrier_state()

    assert reference.epistemic_status == "SELECTED"
    assert reference.source_parameter_ledger == (
        "generic nonzero invariant Ext in source P^3 ledger"
    )
    assert computable.epistemic_status == "COMPUTED"
    assert computable.parameter_component == "P^1(Q(omega))"
    assert reference.source_parameter_ledger != computable.parameter_component


def test_freeze_selects_the_component_without_selecting_a_point() -> None:
    """The whole connected physical family advances into the DGA stage."""

    _reference, computable = computable_one_theory_carrier_state()
    record = computable.as_record()

    assert computable.frozen
    assert not computable.representative_selected
    assert computable.rank == 4
    assert computable.determinant == "trivial"
    assert computable.structure_group == "SU(4)"
    assert record["structural_spectrum"] == {
        "families": 3,
        "right_handed_neutrinos": 3,
        "higgs_pairs": 1,
        "anti_families": 0,
        "massless_color_triplets": 0,
        "exotic_massless_blocks": 0,
    }
    assert record["full_common_dga_representatives_available"] is False


def test_computable_carrier_artifact_is_current_and_content_addressed() -> None:
    """The frozen state remains exactly bound to its spectrum certificates."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    reference, computable = computable_one_theory_carrier_state()

    assert digest == _canonical_digest(stored)
    assert stored["published_reference_carrier_state"] == reference.as_record()
    assert stored["computable_one_theory_carrier_state"] == computable.as_record()
    assert stored["states_are_distinct"] is True
    assert stored["source_p3_to_lawful_p1_equivalence_claimed"] is False
