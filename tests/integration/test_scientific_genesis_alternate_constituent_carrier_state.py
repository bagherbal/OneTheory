"""Guard the alternate computable-carrier component freeze.

Owns:
    Exact certificate binding, reference/computable separation, and the
    prohibition on selecting a projective extension coordinate.

Depends on:
    The alternate carrier-state constructor and its content-addressed record.

Must not:
    Equate this P1 with the published P3, claim Higgs cocycles, or treat
    selected spectrum constraints as Genesis predictions.

Phase 0:
    Research-only regression before same-cone DGA construction.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_carrier_state import (
    OUTPUT,
    alternate_constituent_carrier_state,
)


def test_alternate_carrier_freeze_uses_hom_evidence_not_pushdowns() -> None:
    """The frozen component must retain its exact evidence and open gates."""

    saved = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = saved.pop("artifact_digest")
    reference, computable = alternate_constituent_carrier_state()
    assert digest == _canonical_digest(saved)
    assert saved["published_reference_carrier_state"] == reference.as_record()
    assert saved["computable_one_theory_carrier_state"] == computable.as_record()
    assert reference.epistemic_status == "SELECTED"
    assert computable.epistemic_status == "COMPUTED"
    assert computable.component_id == "alternate-i6-ray-0-1-P1"
    assert computable.frozen is True
    assert computable.representative_selected is False
    assert computable.pushdown_artifact_digest == ""
    assert computable.hom_action_artifact_digest
    certificates = computable.as_record()["certificate_digests"]
    assert "relative_pushdowns" not in certificates
    assert certificates["higgs_hom_actions"] == computable.hom_action_artifact_digest
    assert saved["source_p3_to_alternate_p1_equivalence_claimed"] is False
    assert saved["physical_yukawas_available"] is False
    assert saved["full_vacuum_consistency_established"] is False
