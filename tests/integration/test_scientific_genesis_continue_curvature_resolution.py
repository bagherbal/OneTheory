"""Guard immutable predecessors and same-ancestry finer curvature continuation.

Owns:
    Actual prior-packet digest/source checks, self-resealed mutation rejection,
    exact geometric-history comparisons and captured-prefix scope checks.

Depends on:
    The two executed retained-point sensitivity packets and follow-up reader.

Must not:
    Substitute synthetic carrier coordinates, obtain new entropy, turn local
    diagnostics into an integral, or claim a plateau supplies an error bound.

Phase 0:
    Research predecessor checks only; physical metric gates remain unresolved.
"""

import json
from copy import deepcopy

import pytest

from research.experiments.scientific_genesis import continue_curvature_resolution as module


@pytest.mark.parametrize("ordinal", tuple(module.DIGESTS))
def test_finer_schedule_is_separate_from_unchanged_actual_predecessors(ordinal):
    parent = module.read_prior(ordinal)
    assert parent["artifact_digest"] == module.DIGESTS[ordinal]
    assert module.output_path(ordinal) != module.prior.output_path(ordinal)
    assert module.output_path(ordinal) != module.prior.full._sample_path(ordinal)
    assert module.LEVELS == (16, 20, 24, 28, 32)
    assert 4 * module.LEVELS[-1] < 256
    for saved in parent["history"]:
        geometry = {key: value for key, value in saved.items() if key in (
            "level", "address", "draw_policy", "frame_policy", "root_parent_retained",
            "frame_parent_retained", "component", "selected_branch", "all_root_families",
            "status", "fiber_basis_labels", "relation_minor", "coordinate_bounds",
            "quotient_weight_without_pi_cubed",
        )}
        module.check_prior_geometry(geometry, saved)
        changed = deepcopy(geometry)
        changed["coordinate_bounds"] = []
        with pytest.raises(ValueError, match="did not replay exactly"):
            module.check_prior_geometry(changed, saved)


@pytest.mark.parametrize("ordinal", tuple(module.DIGESTS))
def test_self_resealed_new_values_cannot_replace_the_actual_predecessor(ordinal, tmp_path):
    parent = module.read_prior(ordinal)
    parent["history"][-1]["h1"]["trace_free_l1"] = 0
    parent["artifact_digest"] = module.prior.full.cloud.inputs._digest({
        key: value for key, value in parent.items() if key != "artifact_digest"
    })
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(ValueError, match="predecessor"):
        module.read_prior(ordinal, path=path)
