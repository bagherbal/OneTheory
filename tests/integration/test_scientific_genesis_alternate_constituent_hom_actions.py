"""Guard the scoped alternate determinant-twisted Hom action experiment.

Owns:
    Candidate matrix integrity, fail-closed cohomology boundaries, and the
    default-frame regression of the reusable full Čech action.

Depends on:
    The content-addressed research artifact and selected mixed action engine.

Must not:
    Interpret chosen-cycle characters as physical Higgs or Wilson states.

Phase 0:
    Research-only regression checks for an incomplete equivariant edge.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    _include,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import (
    OUTPUT,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _constituent_frame,
    _full_action,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    _skeleton,
)


def test_candidate_hom_matrices_stay_outside_physical_spectrum() -> None:
    """The exact candidate matrices retain their unresolved descent gates."""

    report = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = report.pop("artifact_digest")
    assert digest == _canonical_digest(report)
    assert report["schema"] == "alternate-constituent-hom-actions-v1"
    assert report["scope"] == "atlas-derived cover H1 of Hom(V2 tensor det(V1), V1)"
    assert [case["ray_character_exponents"] for case in report["cases"]] == [
        [0, 1], [1, 1]
    ]
    assert [case["chosen_cycle_character_candidates"] for case in report["cases"]] == [
        [[0, 0], [1, 2], [2, 0], [2, 2]],
        [[0, 0], [0, 2], [1, 2], [2, 0]],
    ]
    for case in report["cases"]:
        assert case["h1_dimension"] == 4
        assert (case["incoming_rank"], case["outgoing_rank"]) == (129, 331)
        assert case["chosen_cycle_group_relations"] is True
        assert case["chosen_cycle_images_closed"] is True
        assert case["boundary_preservation_certified"] is False
    assert report["cohomology_action_certified"] is False
    assert report["equivariant_tensor_identification_available"] is False
    assert report["wilson_projection_performed"] is False


def test_explicit_frames_preserve_selected_default_action() -> None:
    """The frame override leaves the existing selected action unchanged."""

    first, second = mixed_schoen_constituents()
    action = next(item for item in schoen_sparse_deck_actions() if item.name == "P")
    entry = _reduced_basis(_skeleton(first), _skeleton(second), 1)[0]
    cochain = _include(entry)
    frames = (
        _constituent_frame(first.factor, action.name),
        _constituent_frame(second.factor, action.name),
    )
    assert _full_action(cochain, first, second, action) == _full_action(
        cochain, first, second, action, frames
    )
