"""Assemble both remaining holomorphic matrices after all actual scalar replay.

Owns:
    Full read-only matter and scalar verification, original ordered down/lepton
    matrices, exact formal rank loci, and their common four-sector rank condition.

Depends on:
    Actual same-carrier witness packets, unchanged lift and scalar validators,
    the established matrix constructor, and exact polynomial arithmetic.

Must not:
    Solve absent entries, present partial matrices, choose parameters or bases,
    infer physical normalization, or replace metrics and a common vacuum.

Phase 0:
    Conditional research assembly; unfinished prerequisites leave it unavailable.
"""

import json
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)

from . import alternate_down_lepton_ff_entries as coefficients
from . import alternate_neutrino_full_matrix as established
from .alternate_up_full_matrix import OUTPUT as UP_OUTPUT
from .alternate_up_full_matrix import _polynomial_record
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = coefficients.engine.GENERATED / "alternate_down_lepton_full_holomorphic_matrices.json"
SCHEMA = "alternate-down-lepton-full-holomorphic-matrices-v1"
PROOF = coefficients.PROOF.with_name("ALTERNATE_DOWN_LEPTON_FULL_MATRICES_NOTE.md")
BASES = (
    {"rows": ["E(0,0):seed2", "F(0,0):seed0", "F(0,0):seed5"],
     "columns": ["E(1,1):seed0", "F(1,1):seed2", "F(1,1):seed4"]},
    {"rows": ["E(2,1):seed0", "F(2,1):seed2", "F(2,1):seed4"],
     "columns": ["E(2,0):seed2", "F(2,0):seed0", "F(2,0):seed5"]},
)


def required_sources(directory=coefficients.engine.GENERATED):
    """Name every actual input before permitting the complete replay."""

    return (
        *(coefficients.entry_path(p, s, r, c, directory) for p in (0, 1)
          for s in (0, 1) for r in (1, 2) for c in (1, 2)),
        *(coefficients._lift_source(p, s, side, f)[0] for p in (0, 1)
          for s in (0, 1) for side in (0, 1) for f in (1, 2)),
        coefficients.mixed.OUTPUT, coefficients.mixed.down.OUTPUT,
    )


def _lift_job(job):
    parameter, sector, side, family = job
    print(f"complete flavor replay: a{parameter} s{sector} side{side} f{family}", flush=True)
    return (parameter, sector, side, family), coefficients.verified_lift(
        parameter, sector, side, family,
    )


def _scalar_job(job):
    parameter, sector, row, column, directory, digest, left, right = job
    print(f"complete flavor scalar replay: a{parameter} s{sector} ({row},{column})", flush=True)
    result = coefficients.replay_ff_entry(parameter, sector, row, column,
        expected_digest=digest, directory=Path(directory), verified_inputs=(left, right))
    return (parameter, sector, row, column), result.cover_residue


def _replay(directory, snapshot, workers):
    lift_jobs = [(p, s, side, f) for p in (0, 1) for s in (0, 1)
                 for side in (0, 1) for f in (1, 2)]

    def scalar_jobs(lifts):
        return [(p, s, r, c, str(directory), snapshot[
            coefficients.entry_path(p, s, r, c, directory).stem
        ]["artifact_digest"], lifts[p, s, 0, r], lifts[p, s, 1, c])
                for p in (0, 1) for s in (0, 1) for r in (1, 2) for c in (1, 2)]

    if workers == 1:
        lifts = dict(_lift_job(job) for job in lift_jobs)
        return dict(_scalar_job(job) for job in scalar_jobs(lifts))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        lifts = dict(pool.map(_lift_job, lift_jobs))
        return dict(pool.map(_scalar_job, scalar_jobs(lifts)))


def _polynomial(terms):
    return Polynomial(tuple((tuple(item["powers"]), _parse_eisenstein_text(item["coefficient"]))
                            for item in terms), variable_count=2, scalar_type=Eisenstein)


def _rank_parents():
    """Reuse the established actual up/neutrino certificates, not old branch zeros."""

    up_digest, up = _verified_payload(UP_OUTPUT)
    if (up_digest != "5dca3368f127ddf90eb8e263b403e6ca74f8857a3e505930194c51a67120884f"
        or up.get("outer_parameter_basis") != ["a0", "a1"]):
        raise ValueError("the established actual up matrix changed its trusted basis or digest")
    neutrino = established.load_full_neutrino_matrix(
        expected_digest="40e5e45b6be980d49c432dbc707c496be56728731cd9b6f9d71d4cf08d8909eb",
    )
    return {"artifact_digest": up_digest, **up}, neutrino


def _assembled_outputs(mixed, blocks, up, neutrino):
    """Reuse the established constructor; retain all original entries and formal parameters."""

    matrices, determinants = [], []
    for sector, inputs in enumerate(mixed["sectors"]):
        matrix, det, minor = established.assemble_actual_flavor_matrix(
            inputs["evaluated_entries"],
            {(p, r, c): blocks[p, sector, r, c] for p in (0, 1)
             for r in (1, 2) for c in (1, 2)},
        )
        determinants.append(det)
        matrices.append({"sector": sector, "coupling": inputs["coupling"],
            "basis_order": BASES[sector],
            "matrix_entries": [[_polynomial_record(value) for value in row] for row in matrix.rows],
            "determinant": _polynomial_record(det), "rank_two_minor": _polynomial_record(minor),
            "rank_floor": 2, "rank_three_locus_nonempty": not det.is_zero()})
    common = _polynomial(up["determinant"]) * _polynomial(neutrino["determinant"])
    for det in determinants:
        common *= det
    return matrices, common


def write_full_matrices(path=OUTPUT, *, workers=1):
    """Replay every actual prerequisite before returning either complete matrix."""

    if type(workers) is not int or workers not in (1, 2):
        raise ValueError("complete flavor replay requires exactly one or two workers")
    required = required_sources(path.parent)
    for source in required:
        if not source.is_file() or not source.with_suffix(".cochains.json.gz").is_file():
            raise FileNotFoundError(f"an actual complete flavor prerequisite is missing: {source}")
    snapshot = established._source_snapshot(required)
    mixed, _ = coefficients.mixed.load_mixed_pairing(expected_digest=coefficients.MIXED_DIGEST)
    up, neutrino = _rank_parents()
    blocks = _replay(path.parent, snapshot, workers)
    if established._source_snapshot(required) != snapshot:
        raise ValueError("actual flavor sources changed during complete scalar replay")
    matrices, common = _assembled_outputs(mixed, blocks, up, neutrino)
    record = {
        "schema": SCHEMA, "carrier_status": "conditional on the selected heterotic UV realization",
        "coefficient_field": "Q(omega)", "outer_parameter_basis": ["a0", "a1"],
        "scalar_order": "Higgs first in the fixed quotient volume frame",
        "cover_to_quotient_trace_factor": "1/9", "matrices": matrices,
        "four_sector_common_rank_three_locus_polynomial": _polynomial_record(common),
        "four_sector_common_rank_three_locus_nonempty": not common.is_zero(),
        "all_eighteen_entries_derived_from_actual_carrier": True,
        "all_sixteen_formal_coefficient_scalars_replayed": True,
        "complete_holomorphic_matrices_available": True,
        "physical_yukawa_matrices_available": False, "canonical_matter_metrics_available": False,
        "common_vacuum_stabilized": False, "extension_point_selected": False,
        "observational_inputs_used": False, "source_snapshot": snapshot,
        "proof_sha256": sha256(PROOF.read_bytes()).hexdigest(),
        "established_rank_parent_digests": [up["artifact_digest"], neutrino["artifact_digest"]],
    }
    record["artifact_digest"] = _canonical_digest(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def load_full_matrices(path=OUTPUT, *, expected_digest):
    """Read a pinned complete output, never replay an absent calculation."""

    digest, record = _verified_payload(path)
    if digest != expected_digest:
        raise ValueError("the complete down/lepton matrices changed their trusted digest")
    up, neutrino = _rank_parents()
    if (record.get("schema") != SCHEMA or record.get("coefficient_field") != "Q(omega)"
        or record.get("carrier_status") != "conditional on the selected heterotic UV realization"
        or record.get("outer_parameter_basis") != ["a0", "a1"]
        or record.get("scalar_order") != "Higgs first in the fixed quotient volume frame"
        or record.get("cover_to_quotient_trace_factor") != "1/9"
        or record.get("source_snapshot")
        != established._source_snapshot(required_sources(path.parent))
        or record.get("proof_sha256") != sha256(PROOF.read_bytes()).hexdigest()
        or record.get("established_rank_parent_digests")
        != [up["artifact_digest"], neutrino["artifact_digest"]]
        or any(record.get(flag) is not True for flag in (
            "all_eighteen_entries_derived_from_actual_carrier",
            "all_sixteen_formal_coefficient_scalars_replayed",
            "complete_holomorphic_matrices_available",
        ))
        or any(record.get(flag) is not False for flag in (
            "physical_yukawa_matrices_available", "canonical_matter_metrics_available",
            "common_vacuum_stabilized", "extension_point_selected", "observational_inputs_used",
        ))):
        raise ValueError("the complete down/lepton matrices changed their inputs, bases, or scope")
    matrices = record.get("matrices", [])
    if len(matrices) != 2 or any(
        item.get("sector") != sector or item.get("basis_order") != BASES[sector]
        or item.get("coupling") != [["Q", "d^c", "H_d"], ["L", "e^c", "H_d"]][sector]
        for sector, item in enumerate(matrices)
    ):
        raise ValueError("the complete down/lepton matrices changed their ordered family bases")
    mixed_digest, mixed = _verified_payload(coefficients.mixed.OUTPUT)
    if mixed_digest != coefficients.MIXED_DIGEST:
        raise ValueError("the actual mixed scalar prerequisite changed its trusted digest")
    blocks = {}
    for p in (0, 1):
        for s in (0, 1):
            for r in (1, 2):
                for c in (1, 2):
                    source = coefficients.entry_path(p, s, r, c, path.parent)
                    entry_digest, entry = _verified_payload(source)
                    if (entry_digest != record["source_snapshot"][source.stem]["artifact_digest"]
                        or entry.get("schema") != coefficients.SCHEMA
                        or any(type(entry.get(key)) is not int
                               for key in ("sector", "row", "column"))
                        or (entry.get("parameter"), entry.get("sector"), entry.get("row"),
                            entry.get("column")) != (f"a{p}", s, r, c)):
                        raise ValueError("a matrix coefficient changed its source position")
                    cover = _parse_eisenstein_text(entry["cover_residue"])
                    if str(cover / 9) != entry.get("quotient_residue"):
                        raise ValueError("a matrix coefficient changed quotient normalization")
                    blocks[p, s, r, c] = cover
    expected, common = _assembled_outputs(mixed, blocks, up, neutrino)
    if (matrices != expected
        or record.get("four_sector_common_rank_three_locus_polynomial")
        != _polynomial_record(common)
        or record.get("four_sector_common_rank_three_locus_nonempty")
        is not (not common.is_zero())):
        raise ValueError("the matrices changed actual entries, minors, or common rank locus")
    return {"artifact_digest": digest, **record}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, choices=(1, 2), default=1)
    result = write_full_matrices(workers=parser.parse_args().workers)
    print(result["artifact_digest"], flush=True)
