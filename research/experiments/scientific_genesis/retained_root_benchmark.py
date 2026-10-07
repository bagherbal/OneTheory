"""Measure same-input root acceleration against completed native histories.

Owns:
    Two post-selected retained cases, literal coarse restoration, direct finer
    admission, and full-section curvature comparisons at the unchanged H1.

Depends on:
    Retained-root refinement, terminal native resolution packets, original input
    receipts and existing compiled full-basis curvature and frame consumers.

Must not:
    Form a global mean from these cases, replace histories, rebuild H1, run H2,
    or turn measured execution time or local agreement into an error bound.

Phase 0:
    Research certification-cost experiment, not a physical metric result.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from time import perf_counter

from . import continue_curvature_resolution as previous
from . import retained_root_refinement as fast

prior = previous.prior
LEVEL = 32
MAX_STEPS = 8
NATIVE = {
    526: "0ac036db82db3adf47aa6ecdad620a97ff15a45b1d4f30eb5e1b37beaa8ac2ea",
    1360: "e44b19d10547bbc60914e7069f42f4b49e2df6449fa7b2e2ab4d16d6d2c1a897",
}
NOTE = Path(__file__).with_name("RETAINED_ROOT_REFINEMENT_NOTE.md")


def output_path(ordinal):
    if type(ordinal) is not int or ordinal not in NATIVE:
        raise ValueError("only the retained diagnostic cases are declared")
    return prior.full.OUTPUT.with_name(f"retained_root_benchmark.sample_{ordinal:04d}.json")


def _sources(ordinal):
    result = prior._sources()
    paths = (Path(__file__), Path(fast.__file__), NOTE, previous.output_path(ordinal),
             prior.ROOT / "tests/integration/test_scientific_genesis_retained_root_refinement.py",
             prior.ROOT / "tests/integration/test_scientific_genesis_retained_root_benchmark.py")
    result.update({str(p.relative_to(prior.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in paths})
    return result


def read_native(ordinal):
    """Verify the independently executed finer packet and every pinned source."""

    record = json.loads(previous.output_path(ordinal).read_bytes())
    if (record.get("artifact_digest") != NATIVE[ordinal]
            or prior.full.cloud.inputs._digest({k: v for k, v in record.items()
                                               if k != "artifact_digest"}) != NATIVE[ordinal]
            or any(hashlib.sha256((prior.ROOT / name).read_bytes()).hexdigest() != digest
                   for name, digest in record["source_files_sha256"].items())
            or record["original_sample_digest"] != prior.SAMPLES[ordinal]
            or record["levels"] != list(previous.LEVELS)
            or record["h1_factor_digest"] != prior.nonunit.H1):
        raise ValueError("independent native resolution result or sources changed")
    return record


def compare_native_families(child, parent, saved):
    """Reprove native finer disks and match only by strict common-parent ancestry."""

    def families(draw):
        c = draw.configuration
        return (c.first, c.second) if isinstance(c, fast.native.LineBaseLineConfiguration) else (
            c.partner,)

    mappings = []
    for new, old, receipt in zip(families(child), families(parent), saved, strict=True):
        independent = fast.restore_family(new.cubic, receipt, child.policy.root)
        new_map = fast.draws._permutation(new, old)
        native_map = fast.draws._permutation(independent, old)
        for disk, root_index in zip(new.disks, new_map, strict=True):
            other = independent.disks[native_map.index(root_index)]
            # Both witnesses lie in the same original one-root disk. Their
            # actual finer cubic is identical; this is not nearest-root matching.
            if disk.parameter_pivot != other.parameter_pivot:
                other_ball = fast.native.Ball(other.witness.center, other.witness.radius,
                                             child.policy.input.bound_bits).inverse()
                center, radius = other_ball.center, other_ball.radius
            else:
                center, radius = other.witness.center, other.witness.radius
            if (disk.witness.center - center).norm() > (disk.witness.radius + radius)**2:
                raise ValueError("independently certified same-parent finer disks do not overlap")
        mappings.append({"new_to_parent": list(new_map), "native_to_parent": list(native_map)})
    return mappings


def run(ordinal, *, progress=None):
    """Measure the existing verifier, not a replacement physical calculation."""

    output = output_path(ordinal)
    if output.exists():
        raise FileExistsError("retain the executed same-input benchmark")
    sources = _sources(ordinal)
    native_record = read_native(ordinal)
    full = prior.full
    request = full.read_request(expected_digest=prior.curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=native_record["input_digest"],
                                           path=full.INPUTS)
    saved = full._read_sample(request, inputs, ordinal)
    if saved["artifact_digest"] != prior.SAMPLES[ordinal]:
        raise ValueError("the retained original sample changed")
    available, frames = full.cloud.inputs.address(inputs, ordinal), fast.draws.declared_policy()

    def policies(level):
        address = full.cloud.roots.refinement_address(available, level)
        policy, _ = full.cloud.roots.refinement_policy(level, first_frame=frames.first,
                                                     second_frame=frames.second)
        frame_policy = fast.continuation.FramePolicy((0, 0, 0), (0, 2), (0, 1, 2),
                                                     8*level, prior.curvature.Eisenstein(1), 9)
        return address, policy, frame_policy

    address, policy, frame_policy = policies(16)
    start = perf_counter()
    draw = fast.restore_draw(address, policy, saved["history"][0])
    restore_seconds = perf_counter() - start
    start = perf_counter()
    parent = fast.continuation.admit_frame(draw, frame_policy)
    if not isinstance(parent, fast.continuation.AdmittedFrame):
        raise ArithmeticError("restored original named frame remains unresolved")
    prior.check_original_geometry(full.cloud._history(parent, 16), saved["history"][0])
    coarse_frame_seconds = perf_counter() - start
    if progress:
        progress({"ordinal": ordinal, "stage": "literal coarse restoration",
                  "root_seconds": restore_seconds, "frame_seconds": coarse_frame_seconds})
    address, policy, frame_policy = policies(LEVEL)
    start = perf_counter()
    child_draw, counts = fast.refine_draw(draw, address, policy, max_steps=MAX_STEPS)
    root_seconds = perf_counter() - start
    start = perf_counter()
    child = fast.continuation.admit_frame(child_draw, frame_policy, parent=parent)
    frame_seconds = perf_counter() - start
    item = full.cloud._history(child, LEVEL)
    mappings = None
    if isinstance(child, fast.continuation.AdmittedFrame):
        native_history = native_record["history"][-1]
        mappings = compare_native_families(child_draw, draw, native_history["all_root_families"])
        if item["address"] != native_history["address"]:
            raise ValueError("the independent finer input prefixes differ")
        _, form = prior.nonunit.inverse.read_result(
            expected_request_digest=prior.nonunit.H1_REQUEST, expected_digest=prior.nonunit.H1)
        if form is None:
            raise ArithmeticError("the original H1 factor is unavailable")
        program = prior.curvature.features.compile_features()
        consumer = prior.curvature.FullSectionJets(program)
        parameters = tuple(prior.curvature.features._complex(prior.curvature.Eisenstein(
            Fraction(a), Fraction(b))) for a, b in request["policy"]["parameters"])
        item.update(prior._diagnostics(child, consumer, parameters, form))
        item["curvature_status"] = "computed_discovery"
        item["h1_relative_l1_difference_from_native_discovery"] = (
            item["h1"]["trace_free_l1"] / native_history["h1"]["trace_free_l1"] - 1)
    else:
        item["curvature_status"] = "unresolved"
    result = {"schema": "retained-root-benchmark-v1", "source_files_sha256": sources,
              **full.cloud.inputs.sample_identity(inputs, ordinal), "role": saved["role"],
              "original_sample_digest": saved["artifact_digest"],
              "original_history": saved["history"], "input_digest": inputs["artifact_digest"],
              "native_resolution_digest": native_record["artifact_digest"],
              "original_section_basis_digest": prior.curvature.features.BASIS,
              "original_section_count": 5345, "h1_factor_digest": prior.nonunit.H1,
              "coarse_level": 16, "finer_level": LEVEL, "max_newton_steps": MAX_STEPS,
              "newton_steps_by_family": counts, "finer_history": item,
              "independent_native_root_mappings": mappings,
              "timings_seconds": {"root_restoration": restore_seconds,
                  "coarse_frame": coarse_frame_seconds, "finer_roots": root_seconds,
                  "finer_frame": frame_seconds},
              "original_geometry_reproduced_exactly": True,
              "case_selection": "two post-selected diagnostics, not blind or IID",
              "new_entropy_obtained": False, "checkpoint_replaced": False,
              "subdivision_fallback_used": False, "hybrid_or_subset_mean_available": False,
              "h1_rebuilt": False, "h2_executed": False,
              "numerical_error_bound_certified": False, "controlled_global_integral": False,
              "hym_convergence_established": False, "physical_yukawas_available": False,
              "observations_used": False}
    if sources != _sources(ordinal):
        raise ValueError("benchmark sources changed during execution")
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(output, result)
    return result


if __name__ == "__main__":
    record = run(int(sys.argv[1]), progress=lambda r: print(json.dumps(r), flush=True))
    print(json.dumps({"ordinal": record["ordinal"], "artifact_digest": record["artifact_digest"],
                      "timings_seconds": record["timings_seconds"],
                      "status": record["finer_history"]["status"],
                      "h1_l1": record["finer_history"].get("h1", {}).get("trace_free_l1")}),
          flush=True)
