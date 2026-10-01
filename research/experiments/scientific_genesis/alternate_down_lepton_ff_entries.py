"""Compute the remaining actual down and charged-lepton F-F scalars.

Owns:
    Read-only reuse of Q/L and actual d/e lifts, explicitly supplied down-Higgs
    coefficients, and sixteen full scalar checkpoints in the original bases.

Depends on:
    Pinned same-carrier inputs and the existing full lift, coupled-Higgs,
    canonical wedge, exact scalar, trace, and deterministic archive engines.

Must not:
    Solve a missing correction, reuse up-Higgs primitives, choose parameters,
    fill partial matrices, or infer masses, matter metrics, or a common vacuum.

Phase 0:
    Conditional heterotic research coefficients; complete matrix replay is separate.
"""

from concurrent.futures import ProcessPoolExecutor
from functools import cache
from hashlib import sha256
from pathlib import Path

from onetheory.math.numbers import Rational

from . import alternate_down_lepton_mixed_pairing as mixed
from . import alternate_remaining_flavor_matter_lifts as columns
from . import alternate_up_ff_entries as engine
from .alternate_constituent_up_matter_representatives import AlternateMatterClass
from .alternate_neutrino_full_matrix import _source_snapshot
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_universal_cone import _verified_payload

MIXED_DIGEST = "ae7f62edaf3621af9b8dc8142f597218cd5426b8b922fd9b6b1e8ae2cb1ed1b1"
SCHEMA = "alternate-down-lepton-ff-entry-v1"
PROOF = mixed.PROOF.with_name("ALTERNATE_DOWN_LEPTON_FF_NOTE.md")
ROW_DIGESTS = (
    (("b2fd30e6b26c8140ff52c41604e161d7fe39e83fd5edbafd63a224e0489094ea",
      "d76441a381f99bee8419ce380a06e1786c7d8eb4347543b2535b96f35df7673d"),
     ("ffc2ff3bdab420bfc9b16ffd1892aa4b84c2896808f976a09ffbca604d6a1379",
      "7da302ec452f693ced8a436b29bed9402257428ce85576e2f36c9b0e3cbeab62")),
    (("77f04729847dc58ec78314fc1c6fb92017c5a999475dd7047e6f50ee2b837526",
      "b32e6cc80c8492e01ffd896c2d77edb5e74a0967a4c962daf0263e64a84c5d03"),
     ("d20d9d68689a66e769a4c637efc8abb365fcb4021990dc021126302e8824004d",
      "4002b844a63e4a3de0d909f6b232bc4ad645ce7c835fdf4cbb733ef665ee8245")),
)
COLUMN_DIGESTS = (
    (("1d4a931761d341544ee256e0d1550be434bde41ac3d0a51588b02540d02b6d29",
      "3b508c5e6b9c24d5eb433b9cf187d06c767fe13d5ec7d5afd977a9b8d4afb1c4"),
     ("8b7644c50e4ea0e2d4ff89ba35c111d0c5611599f63e289fac506c58b76202a7",
      "1683484cb1a51168f7c3506adf38a831fad65e87485906fa2873501544e3c631")),
    (("eb3f71dec8372883e3b132fc877e2870c271a5d58628f2941c59b059e2a983da",
      "09aaa371e465124fd344fb3a4fc421d51d1164fbf7e8330a45fcbffd31df9b52"),
     ("572637f5986124caece4159531611e592e6177f9166b1d2806f048ed65e91c86",
      "064e7fd324f2ba23dff2a51dddd7969397b083de6061ba338dc2301218c5ad44")),
)


def entry_path(parameter, sector, row, column, directory=engine.GENERATED):
    engine._indices(parameter, row, column)
    if type(sector) is not int or sector not in (0, 1):
        raise ValueError("an actual flavor sector must be 0 (down) or 1 (charged lepton)")
    return directory / f"alternate_down_lepton_ff_a{parameter}_s{sector}_r{row}_c{column}.json"


def _lift_source(parameter, sector, side, family):
    entry_path(parameter, sector, family, 1)
    if type(side) is not int or side not in (0, 1):
        raise ValueError("an actual matter side must be row or column")
    if side == 1:
        return (columns.lift_path(parameter, sector, family),
                COLUMN_DIGESTS[parameter][sector][family-1])
    prefix = ("up", "neutrino")[sector]
    return (engine.GENERATED / f"alternate_{prefix}_ff_lift_a{parameter}_side0_family{family}.json",
            ROW_DIGESTS[parameter][sector][family-1])


@cache
def _row_classes():
    packet, witnesses = mixed.load_mixed_pairing(expected_digest=MIXED_DIGEST)
    _, up = _verified_payload(mixed.UP_MATTER)
    _, neutrino = _verified_payload(mixed.neutrino.OUTPUT)
    result = {}
    for sector, metadata in enumerate((up["classes"][:2],
                                      neutrino["second_constituent_classes"][:2])):
        for family, item in enumerate(metadata, 1):
            full = witnesses[f"second_s{sector}_row_f{family}"]
            if _cochain_digest((full,)) != item["full_digest"]:
                raise ValueError("an actual flavor row changed its original raw class")
            result[sector, family] = AlternateMatterClass(
                mixed.CHARACTERS[sector][0], item["seed_index"],
                tuple(_parse_eisenstein_text(value) for value in item["cohomology_coordinates"]),
                full, item["inclusion_depth"], item["projection_depth"],
            )
    return result, packet["prerequisite_artifact_digests"]


def verified_lift(parameter, sector, side, family):
    """Replay pinned original matter equations; never call a primitive solver."""

    path, expected = _lift_source(parameter, sector, side, family)
    if _verified_payload(path)[0] != expected:
        raise ValueError("an actual flavor lift changed its trusted digest")
    if side == 1:
        return columns.replay_matter_lift(parameter, sector, family, expected_digest=expected)
    matter = _row_classes()[0][sector, family]
    _, witnesses = engine._read_witnesses(
        path, f"alternate-{('up', 'neutrino')[sector]}-ff-matter-lift-v1",
        ("constant", "constituent_correction", "line_correction"),
    )
    return engine.checked_quotient_matter_lift(
        parameter, matter, witnesses["constant"], witnesses["constituent_correction"],
        witnesses["line_correction"], checkpoint_digest=expected,
    )


@cache
def actual_higgs(parameter):
    """Supply the real down-Higgs witnesses, not the hard-coded up wrapper."""

    engine._indices(parameter, 1)
    _, witnesses = mixed.down.load_down_higgs_quotient_cone(expected_digest=mixed.PINS[0][2])
    return engine.checked_coupled_higgs(parameter, witnesses["quotient_covector"],
                                        witnesses[f"correction_a{parameter}"])


def _snapshot(parameter):
    required = [mixed.OUTPUT, mixed.down.OUTPUT]
    for sector in (0, 1):
        for side in (0, 1):
            for family in (1, 2):
                path, digest = _lift_source(parameter, sector, side, family)
                if _verified_payload(path)[0] != digest:
                    raise ValueError("an actual flavor coefficient prerequisite changed")
                required.append(path)
    if _verified_payload(mixed.OUTPUT)[0] != MIXED_DIGEST:
        raise ValueError("the actual mixed input changed its trusted digest")
    return _source_snapshot(required)


def _lift_job(job):
    parameter, sector, side, family = job
    print(f"actual flavor replay: a{parameter} sector{sector} side{side} family{family}",
          flush=True)
    return (sector, side, family), verified_lift(parameter, sector, side, family)


def _entry_job(job):
    parameter, sector, row, column, left, right, snapshot, directory = job
    result = engine._evaluate_entry(parameter, row, column, left, right, *actual_higgs(parameter))
    if _snapshot(parameter) != snapshot:
        raise ValueError("actual flavor sources changed during complete scalar evaluation")
    return engine._write_witnesses(entry_path(parameter, sector, row, column, Path(directory)), {
        "schema": SCHEMA, "coefficient_field": "Q(omega)",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "parameter": f"a{parameter}", "sector": sector, "row": row, "column": column,
        "row_character": list(left.matter.character),
        "column_character": list(right.matter.character),
        "row_seed_index": left.matter.seed_index, "column_seed_index": right.matter.seed_index,
        "actual_matter_lift_digests": [left.checkpoint_digest, right.checkpoint_digest],
        "source_snapshot": snapshot, "proof_sha256": sha256(PROOF.read_bytes()).hexdigest(),
        "scalar_order": "h_down cup P1 + kappa_down cup P0",
        "full_coefficientwise_product_identity_exact": True, "full_scalar_closed_exact": True,
        "direct_transferred_and_inverse_convolution_traces_equal": True,
        "cover_residue": str(result.cover_residue),
        "quotient_residue": str(result.cover_residue * Rational(1, 9)),
        "projection_depth": result.projection_depth, "exterior_filtration_parameter_degree": 1,
        "complete_down_matrix_available": False, "complete_charged_lepton_matrix_available": False,
        "Q_and_L_matter_corrections_recomputed": False, "up_Higgs_primitives_used": False,
        "physical_yukawas_available": False, "extension_point_selected": False,
        "observational_inputs_used": False,
    }, {"product_constant": result.product_constant, "product_linear": result.product_linear,
        "scalar": result.scalar})


def write_ff_coefficient(parameter, directory=engine.GENERATED, *, workers=1):
    """Evaluate one complete formal coefficient of both sectors, saving each entry."""

    engine._indices(parameter, 1)
    if type(workers) is not int or workers not in (1, 2):
        raise ValueError("actual flavor execution requires exactly one or two workers")
    snapshot = _snapshot(parameter)
    jobs = [(parameter, sector, side, family) for sector in (0, 1)
            for side in (0, 1) for family in (1, 2)]

    def entry_jobs(lifts):
        return [(parameter, sector, row, column, lifts[sector, 0, row], lifts[sector, 1, column],
                 snapshot, str(directory)) for sector in (0, 1)
                for row in (1, 2) for column in (1, 2)]

    if workers == 1:
        lifts = dict(_lift_job(job) for job in jobs)
        return tuple(_entry_job(job) for job in entry_jobs(lifts))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        lifts = dict(pool.map(_lift_job, jobs))
        return tuple(pool.map(_entry_job, entry_jobs(lifts)))


def load_ff_entry(parameter, sector, row, column, *, expected_digest,
                  directory=engine.GENERATED):
    """Read a trusted actual result without deriving a lift or scalar."""

    path = entry_path(parameter, sector, row, column, directory)
    digest, record = _verified_payload(path)
    if digest != expected_digest:
        raise ValueError("the actual down/lepton F-F entry changed its trusted digest")
    if (record.get("schema") != SCHEMA or record.get("coefficient_field") != "Q(omega)"
        or record.get("carrier_status") != "conditional on the selected heterotic UV realization"
        or record.get("proof_sha256")
        != sha256(PROOF.read_bytes()).hexdigest()
        or (record.get("parameter"), record.get("sector"), record.get("row"), record.get("column"))
        != (f"a{parameter}", sector, row, column)
        or record.get("source_snapshot") != _snapshot(parameter)
        or record.get("actual_matter_lift_digests") != [
            _lift_source(parameter, sector, side, family)[1]
            for side, family in ((0, row), (1, column))
        ]
        or record.get("scalar_order") != "h_down cup P1 + kappa_down cup P0"
        or record.get("row_character") != list(mixed.CHARACTERS[sector][0])
        or record.get("column_character") != list(mixed.CHARACTERS[sector][1])
        or record.get("row_seed_index") != ((0, 5), (2, 4))[sector][row-1]
        or record.get("column_seed_index") != ((2, 4), (0, 5))[sector][column-1]
        or record.get("exterior_filtration_parameter_degree") != 1
        or any(record.get(flag) is not True for flag in (
            "full_coefficientwise_product_identity_exact", "full_scalar_closed_exact",
            "direct_transferred_and_inverse_convolution_traces_equal",
        ))
        or any(record.get(flag) is not False for flag in (
            "complete_down_matrix_available", "complete_charged_lepton_matrix_available",
            "Q_and_L_matter_corrections_recomputed", "up_Higgs_primitives_used",
            "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
        ))):
        raise ValueError("the actual down/lepton F-F entry changed its source or scope")
    record, witnesses = engine._read_witnesses(path, SCHEMA,
        ("product_constant", "product_linear", "scalar"))
    direct = engine.direct_ordered_scalar_residue(witnesses["scalar"])
    if (record.get("cover_residue") != str(direct)
        or record.get("quotient_residue") != str(direct * Rational(1, 9))):
        raise ValueError("an actual down/lepton F-F trace changed its quotient normalization")
    return {"artifact_digest": digest, **record}, witnesses


def replay_ff_entry(parameter, sector, row, column, *, expected_digest,
                    directory=engine.GENERATED):
    """Check all three actual scalar witnesses literally without any solver."""

    record, witnesses = load_ff_entry(parameter, sector, row, column,
                                      expected_digest=expected_digest, directory=directory)
    left, right = (verified_lift(parameter, sector, side, family)
                   for side, family in ((0, row), (1, column)))
    result = engine._evaluate_entry(parameter, row, column, left, right, *actual_higgs(parameter))
    if (any(getattr(result, name) != witnesses[name]
            for name in ("product_constant", "product_linear", "scalar"))
        or record["cover_residue"] != str(result.cover_residue)
        or record["projection_depth"] != result.projection_depth):
        raise ValueError("the actual down/lepton F-F entry differs from full scalar replay")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameter", type=int, choices=(0, 1))
    parser.add_argument("--workers", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    for record in write_ff_coefficient(args.parameter, workers=args.workers):
        print(record["artifact_digest"], record["cover_residue"], flush=True)
