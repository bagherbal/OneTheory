"""Extend unresolved retained curvature diagnostics with captured finer prefixes.

Owns:
    Exact replay of the executed level-16/20/24 geometric histories followed by
    level-28/32 continuation and unchanged full-basis H0/H1 curvature evaluation.

Depends on:
    The immutable prior diagnostic cases, original native continuation, frozen
    section jets and actual H1 factor; no new input or numerical law is introduced.

Must not:
    Change prior packets, replace a failed branch, rebuild H1, execute H2, form a
    partial global mean, or mistake a local plateau for certified convergence.

Phase 0:
    Further research discovery sensitivity only; physical metric gates stay closed.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import retained_curvature_resolution as prior

LEVELS = (*prior.LEVELS, 28, 32)
DIGESTS = {
    526: "8ef99ba30b04be60b9820f6a75ecaed3767bcb4a22e4491aa78d742b21071604",
    1360: "d8017c86955b985a5e5793374811e07f63873e638bfefbf4242d1ae7df553c07",
}
NOTE = Path(__file__).with_name("CONTINUE_CURVATURE_RESOLUTION_NOTE.md")


def read_prior(ordinal, *, path=None):
    """Require the externally observed terminal case and its unchanged sources."""

    original_path = prior.output_path(ordinal)
    record = json.loads((original_path if path is None else path).read_bytes())
    if (record.get("artifact_digest") != DIGESTS[ordinal]
            or prior.full.cloud.inputs._digest({k: v for k, v in record.items()
                                               if k != "artifact_digest"}) != DIGESTS[ordinal]
            or any(hashlib.sha256((prior.ROOT / name).read_bytes()).hexdigest() != digest
                   for name, digest in record["source_files_sha256"].items())
            or record["original_sample_digest"] != prior.SAMPLES[ordinal]
            or record["h1_factor_digest"] != prior.nonunit.H1
            or record["levels"] != list(prior.LEVELS)):
        raise ValueError("the executed same-input predecessor or its sources changed")
    return record


def output_path(ordinal):
    """Keep the finer result separate from both prior cases and cloud receipts."""

    prior.output_path(ordinal)
    return prior.full.OUTPUT.with_name(f"continued_curvature_resolution.sample_{ordinal:04d}.json")


def check_prior_geometry(geometry, saved):
    """A finer experiment must replay every already executed geometric field."""

    if (geometry.get("status") != "admitted"
            or saved.get("curvature_status") != "computed_discovery"
            or geometry.get("level") not in prior.LEVELS
            or any(saved.get(key) != value for key, value in geometry.items())
            or any(key not in geometry for key in (
                "coordinate_bounds", "all_root_families", "selected_branch", "address",
                "frame_policy", "draw_policy", "fiber_basis_labels", "relation_minor",
                "quotient_weight_without_pi_cubed", "root_parent_retained",
                "frame_parent_retained", "level", "component"))):
        raise ValueError("the previously executed geometric ancestry did not replay exactly")


def _sources(ordinal):
    result = prior._sources()
    paths = (Path(__file__), NOTE, prior.output_path(ordinal), prior.ROOT /
             "tests/integration/test_scientific_genesis_continue_curvature_resolution.py")
    result.update({str(path.relative_to(prior.ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in paths})
    return result


def run(ordinal, *, progress=None):
    """Reuse the known geometry, then refine the SAME roots at levels 28 and 32."""

    output = output_path(ordinal)
    if output.exists():
        raise FileExistsError("preserve the original finer-resolution result")
    parent = read_prior(ordinal)
    sources = _sources(ordinal)
    full = prior.full
    request = full.read_request(expected_digest=prior.curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=parent["input_digest"], path=full.INPUTS)
    saved = full._read_sample(request, inputs, ordinal)
    if saved["artifact_digest"] != parent["original_sample_digest"]:
        raise ValueError("the original cloud sample changed")
    _, form = prior.nonunit.inverse.read_result(expected_request_digest=prior.nonunit.H1_REQUEST,
                                               expected_digest=prior.nonunit.H1)
    if form is None:
        raise ArithmeticError("the unchanged full-basis H1 factor is unavailable")
    program = prior.curvature.features.compile_features()
    consumer = prior.curvature.FullSectionJets(program)
    parameters = tuple(prior.curvature.features._complex(prior.curvature.Eisenstein(
        Fraction(a), Fraction(b))) for a, b in request["policy"]["parameters"])
    available = full.cloud.inputs.address(inputs, ordinal)
    geometry = full.cloud.draws.declared_policy()
    previous, history = None, []
    for level in LEVELS:
        address = full.cloud.roots.refinement_address(available, level)
        policy, work = full.cloud.roots.refinement_policy(
            level, first_frame=geometry.first, second_frame=geometry.second,
        )
        work["max_cells"] = request["policy"]["max_cells"]
        frame_policy = full.cloud.continuation.FramePolicy(
            (0, 0, 0), (0, 2), (0, 1, 2), 8 * level, prior.curvature.Eisenstein(1), 9,
        )
        if previous is None:
            admission = full.cloud.continuation.admit_frame(
                full.cloud.roots.attempt_subdivision_draw(address, policy, **work), frame_policy,
            )
        else:
            admission = full.cloud.continuation.refine_frame(
                previous, address, policy, frame_policy, **work,
            )
        previous = admission
        item = full.cloud._history(admission, level)
        if level in prior.LEVELS:
            saved_step = parent["history"][prior.LEVELS.index(level)]
            check_prior_geometry(item, saved_step)
            item = saved_step.copy()
        else:
            item["curvature_status"] = "unresolved"
            if isinstance(admission, full.cloud.continuation.AdmittedFrame):
                try:
                    item.update(prior._diagnostics(admission, consumer, parameters, form))
                    item["curvature_status"] = "computed_discovery"
                except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
                    item["curvature_reason"] = str(error)
            else:
                item["curvature_reason"] = admission.reason
        history.append(item)
        if progress:
            progress({"ordinal": ordinal, "level": level, "frame_status": item["status"],
                      "curvature_status": item["curvature_status"],
                      "prior_geometry_replayed": level in prior.LEVELS,
                      "h1_l1": item.get("h1", {}).get("trace_free_l1")})
    record = {key: value for key, value in parent.items() if key not in (
        "artifact_digest", "source_files_sha256", "history", "levels", "schema",
    )}
    record.update({"schema": "continued-curvature-resolution-v1", "source_files_sha256": sources,
                   "prior_resolution_digest": parent["artifact_digest"], "levels": list(LEVELS),
                   "history": history, "all_prior_geometric_histories_replayed_exactly": True,
                   "finer_schedule_role": "predeclared sensitivity after non-plateau at point 526",
                   "input_prefix_bits_at_last_level": 4 * LEVELS[-1],
                   "captured_bits_per_stream": 8 * inputs["bytes_per_stream"],
                   "h1_rebuilt": False, "local_resolution_error_bound_certified": False})
    if sources != _sources(ordinal):
        raise ValueError("the finer same-input experiment changed during execution")
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(output, record)
    return record


if __name__ == "__main__":
    result = run(int(sys.argv[1]), progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({"ordinal": result["ordinal"], "artifact_digest": result["artifact_digest"]}),
          flush=True)
