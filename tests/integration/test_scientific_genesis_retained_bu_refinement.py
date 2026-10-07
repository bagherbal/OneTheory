"""Check the Bu repair against an actual original native receipt.

Owns:
    Literal same-input restoration and rejection of inappropriate mixture use.

Depends on:
    The original captured population and unchanged native certificate validators.

Must not:
    Substitute fixtures for geometry, redraw or infer global accuracy.

Phase 0:
    Actual retained-input native restoration regression only.
"""

import pytest

from research.experiments.scientific_genesis import retained_bu_refinement as module
from research.experiments.scientific_genesis import retained_population_resolution as population


def test_actual_bu_receipt_restores_literally_with_native_interval_scalar_order():
    full = population.full
    request = full.read_request(expected_digest=population.curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                          path=full.INPUTS)
    saved = full._read_sample(request, inputs, 17)["history"][0]
    address = full.cloud.roots.refinement_address(full.cloud.inputs.address(inputs, 17), 16)
    frames = module.draws.declared_policy()
    policy, _ = full.cloud.roots.refinement_policy(16, first_frame=frames.first,
                                                  second_frame=frames.second)
    draw = module.restore_draw(address, policy, saved)
    assert address.choices()[0] == "Bu"
    assert module.native._roots_record(draw.configuration.partner) == saved["all_root_families"][0]
    frame = module.original.continuation.FramePolicy((0, 0, 0), (0, 2), (0, 1, 2),
                                                     128, population.curvature.Eisenstein(1), 9)
    admission = module.original.continuation.admit_frame(draw, frame)
    assert isinstance(admission, module.original.continuation.AdmittedFrame)
    assert all(saved.get(k) == value for k, value in full.cloud._history(admission, 16).items())


def test_bu_repair_rejects_another_actual_mixture_component():
    full = population.full
    inputs = full.cloud.inputs.read_inputs(
        expected_digest="cfaac611b57142a0c291a3c3336c6bf34c61c64aecfd3370af50aa0474380d6e",
        path=full.INPUTS)
    address = full.cloud.roots.refinement_address(full.cloud.inputs.address(inputs, 101), 16)
    with pytest.raises(ValueError, match="only the Bu"):
        module._configuration(address, None, None)
