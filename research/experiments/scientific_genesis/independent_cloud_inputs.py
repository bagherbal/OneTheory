"""Capture new named entropy streams for the actual auxiliary integration law.

Owns:
    Immutable public computational input receipts, complete stream bytes,
    sample identities, and exact conversion into existing prefix addresses.

Depends on:
    Linux getrandom and the established auxiliary draw-address types.

Must not:
    Certify IID from finite bytes, reseed failed samples, condition on geometry,
    generate physical coefficients, or substitute deterministic fixtures.

Phase 0:
    Research integration inputs only; the fair independent bit law is assumed.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

from . import auxiliary_cover_draws as draws

OUTPUT = draws.OUTPUT.with_name("independent_cloud_inputs.json")
CHANNELS = ("component", "first.spacing.0", "first.spacing.1", "first.phases.0",
            "first.phases.1", "second.spacing.0", "second.spacing.1", "second.phases.0",
            "second.phases.1", "base.spacing.0", "base.phases.0", "first_root", "second_root")


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _entropy(size):
    """Retain short reads from the same OS source; never substitute another RNG."""

    chunks = []
    remaining = size
    while remaining:
        chunk = os.getrandom(remaining)
        if not chunk or len(chunk) > remaining:
            raise OSError("getrandom returned an invalid computational entropy receipt")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def create_inputs(*, count, bytes_per_stream, path=OUTPUT):
    """Freeze the entire workload BEFORE any root or section outcome is known."""

    if (type(count) is not int or count < 1 or type(bytes_per_stream) is not int
        or bytes_per_stream < 1):
        raise ValueError("positive explicit sample and stream lengths required")
    if path.exists():
        raise FileExistsError("retain existing inputs; failed samples cannot trigger new entropy")
    if sys.platform != "linux" or not hasattr(os, "getrandom"):
        raise OSError("the declared Linux getrandom input source is unavailable")
    samples = []
    for index in range(count):
        samples.append({"ordinal": index,
            "streams": [{"channel": name, "hex": _entropy(bytes_per_stream).hex()}
                        for name in CHANNELS]})
    record = {"schema": "independent-cloud-inputs-v1", "sample_count": count,
        "bytes_per_stream": bytes_per_stream, "channel_order": CHANNELS,
        "entropy_source": "Linux os.getrandom with default flags; no user seed",
        "entropy_assumption_status": "ASSUMED",
        "entropy_assumption": "mutually independent fair infinite named bit streams",
        "finite_bytes_prove_independence": False,
        "geometry_outcomes_used_to_select_inputs": False,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "samples": samples}
    record["artifact_digest"] = _digest(record)
    with path.open("xb") as stream:
        stream.write(_canonical(record) + b"\n")
    return read_inputs(expected_digest=record["artifact_digest"], path=path)


def read_inputs(*, expected_digest, path=OUTPUT):
    """Validate complete retained public bytes without calling the entropy source."""

    record = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    if record.get("artifact_digest") != expected_digest or _digest(unsigned) != expected_digest:
        raise ValueError("the retained entropy inputs changed their trusted identity")
    if (record["schema"] != "independent-cloud-inputs-v1"
        or record["source_sha256"] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        or record["channel_order"] != list(CHANNELS)
        or record["entropy_source"] != "Linux os.getrandom with default flags; no user seed"
        or record["entropy_assumption_status"] != "ASSUMED"
        or record["entropy_assumption"] != "mutually independent fair infinite named bit streams"
        or record["finite_bytes_prove_independence"] is not False
        or record["geometry_outcomes_used_to_select_inputs"] is not False
        or type(record["sample_count"]) is not int or record["sample_count"] < 1
        or type(record["bytes_per_stream"]) is not int or record["bytes_per_stream"] < 1
        or len(record["samples"]) != record["sample_count"]):
        raise ValueError("the declared entropy scope or complete workload changed")
    for index, sample in enumerate(record["samples"]):
        if (type(sample["ordinal"]) is not int or sample["ordinal"] != index
            or len(sample["streams"]) != len(CHANNELS)
            or [s["channel"] for s in sample["streams"]] != list(CHANNELS)):
            raise ValueError("original ordered samples and named streams required")
        for item in sample["streams"]:
            raw = bytes.fromhex(item["hex"])
            if len(raw) != record["bytes_per_stream"] or raw.hex() != item["hex"]:
                raise ValueError("complete canonical stream bytes required")
    return record


def address(record, ordinal):
    """Decode exact binary prefixes without midpoint coordinates or root reselection."""

    if type(ordinal) is not int or not 0 <= ordinal < record["sample_count"]:
        raise ValueError("an original input sample ordinal required")
    raw = {s["channel"]: bytes.fromhex(s["hex"]) for s in record["samples"][ordinal]["streams"]}

    def prefix(name):
        return draws.BitPrefix(tuple((byte >> shift) & 1 for byte in raw[name]
                                     for shift in range(7, -1, -1)))

    def projective(name, dimension):
        return draws.ProjectiveAddress(
            tuple(prefix(f"{name}.spacing.{i}") for i in range(dimension)),
            tuple(prefix(f"{name}.phases.{i}") for i in range(dimension)),
        )

    return draws.DrawAddress(prefix("component"), projective("first", 2),
        projective("second", 2), projective("base", 1), prefix("first_root"), prefix("second_root"))


def sample_identity(record, ordinal):
    """Name the sample and each stream independently of its geometric success."""

    if type(ordinal) is not int or not 0 <= ordinal < record["sample_count"]:
        raise ValueError("an original input sample ordinal required")
    sample = record["samples"][ordinal]
    identifier = f"{record['artifact_digest']}:{ordinal}"
    return {"sample_id": identifier, "ordinal": ordinal,
            "streams": [{"stream_id": f"{identifier}:{s['channel']}",
                         "bytes_sha256": hashlib.sha256(bytes.fromhex(s["hex"])).hexdigest()}
                        for s in sample["streams"]]}


if __name__ == "__main__":
    print(create_inputs(count=16, bytes_per_stream=16)["artifact_digest"])
