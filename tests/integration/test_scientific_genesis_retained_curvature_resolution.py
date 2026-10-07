"""Guard literal original-input replay for the curvature resolution experiment.

Owns:
    Actual saved-frame comparisons, missing or altered geometry rejection,
    diagnostic-case naming, and separation from original cloud checkpoints.

Depends on:
    The retained research sample receipts and same-input resolution consumer.

Must not:
    Fabricate physical coordinates, claim a subset is an integral, or interpret
    mutation fixtures as a scientific result or controlled curvature bound.

Phase 0:
    Research input-identity checks only; physical metric gates remain closed.
"""

import gzip
import json
from copy import deepcopy
from functools import cache

import pytest

from research.experiments.scientific_genesis import retained_curvature_resolution as module


@cache
def _original():
    path = module.full._sample_path(1360)
    record = json.loads(gzip.decompress(path.read_bytes()))
    assert record["artifact_digest"] == module.SAMPLES[1360]
    assert module.full.cloud.inputs._digest({k: v for k, v in record.items()
                                           if k != "artifact_digest"}) == module.SAMPLES[1360]
    saved = record["history"][0]
    kernel_keys = {"kernel_status", "kernel_rows", "kernel_diagnostics",
                   "weight_midpoint_without_pi_cubed", "complete_original_sections_consumed",
                   "floating_mantissa_bits"}
    return saved, {k: v for k, v in saved.items() if k not in kernel_keys}


def test_actual_geometric_replay_compares_all_original_fields():
    saved, geometry = _original()
    module.check_original_geometry(geometry, saved)
    assert module.LEVELS == (16, 20, 24)
    assert module.output_path(1360) != module.full._sample_path(1360)
    assert module.output_path(526) != module.full._sample_path(526)


@pytest.mark.parametrize("field", (
    "coordinate_bounds", "all_root_families", "selected_branch", "address",
    "frame_policy", "draw_policy", "fiber_basis_labels", "relation_minor",
    "quotient_weight_without_pi_cubed", "root_parent_retained",
    "frame_parent_retained", "level", "component",
))
@pytest.mark.parametrize("mutation", ("remove", "alter"))
def test_no_original_geometric_field_can_be_removed_or_changed(field, mutation):
    saved, geometry = _original()
    changed = deepcopy(geometry)
    if mutation == "remove":
        changed.pop(field)
    else:
        changed[field] = "changed-original-geometry"
    with pytest.raises(ValueError, match="did not reproduce exactly"):
        module.check_original_geometry(changed, saved)


@pytest.mark.parametrize("ordinal", (True, False, -1, 0, 526.0, "1360", 2048))
def test_no_implicit_case_reselection_or_numeric_alias_is_allowed(ordinal):
    with pytest.raises(ValueError, match="declared post-selected"):
        module.output_path(ordinal)
