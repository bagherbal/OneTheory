"""Test the frozen reverse computable OneTheory carrier component.

Owns:
    Reverse certificate binding, component-level freeze criteria, source-ledger
    separation, forward no-go preservation, and unresolved DGA boundaries.

Depends on:
    The reverse carrier-state constructor and its content-addressed artifact.

Must not:
    Select a P5 point, identify source P3 with reverse P5, erase the lawful
    forward carrier, or claim generated Yukawa representatives.

Phase 0:
    Reverse carrier-component freeze regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.computable_one_theory_reverse_carrier_state import (
    OUTPUT,
    computable_one_theory_reverse_carrier_state,
)


def test_reverse_reference_and_computable_states_remain_distinct() -> None:
    """The source P3 ledger is not identified with the lawful reverse P5."""

    reference, computable = computable_one_theory_reverse_carrier_state()

    assert reference.epistemic_status == "SELECTED"
    assert computable.epistemic_status == "COMPUTED"
    assert computable.component_id == "lawful-mixed-schoen-reverse-P5"
    assert computable.parameter_component == "P^5(Q(omega))"
    assert reference.source_parameter_ledger != computable.parameter_component


def test_reverse_freeze_advances_the_component_without_a_point() -> None:
    """The entire reverse physical component advances into the DGA stage."""

    _reference, computable = computable_one_theory_reverse_carrier_state()
    record = computable.as_record()

    assert computable.frozen
    assert not computable.representative_selected
    assert computable.kahler_chamber == "K_reverse^s"
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


def test_reverse_carrier_artifact_preserves_forward_scope() -> None:
    """The replacement freeze does not rewrite the lawful forward result."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    reference, computable = computable_one_theory_reverse_carrier_state()

    assert digest == _canonical_digest(stored)
    assert stored["published_reference_carrier_state"] == reference.as_record()
    assert stored["computable_one_theory_carrier_state"] == computable.as_record()
    assert stored["states_are_distinct"] is True
    assert stored["source_p3_to_lawful_reverse_p5_equivalence_claimed"] is False
    assert stored["forward_p1_remains_lawful"] is True
    assert stored["forward_p1_flavor_scope_exhausted"] is True
