"""Test the frozen independent-algebra certificate for carrier research.

Owns:
    Lightweight manifest, digest, output, and independence checks for the
    pinned SageMath reproduction of the current computable-carrier frontier.

Depends on:
    The generated carrier artifact and the standalone external Sage script.

Must not:
    Replace the external container run, import carrier research calculations
    into the Sage path, or promote conditional descent to physical selection.

Phase 0:
    Frozen external results are audited; later scientific gates remain open.
"""

import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "data"
    / "generated"
    / "computable_carrier"
    / "computable_carrier_artifact.json"
)
SCRIPT = (
    ROOT
    / "research"
    / "experiments"
    / "computable_carrier"
    / "external"
    / "verify.sage"
)


def test_external_manifest_matches_frozen_sage_result() -> None:
    """The recorded Sage output and script digest identify the exact run."""

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    external = artifact["external_algebra"]

    assert external["status"] == "passed"
    assert external["runtime"] == "sagemath/sagemath:10.6"
    assert external["script_sha256"] == sha256(SCRIPT.read_bytes()).hexdigest()
    assert external["verified_scopes"]["curvilinear_rank_two_descent_inputs"] == (
        "passed"
    )
    assert external["verified_scopes"]["curvilinear_rank_four_topology"] == (
        "excluded"
    )
    assert external["output"][-1] == (
        "curvilinear_rank_four_topology: excluded_index_zero"
    )
    assert external["conditional_inputs"] == [
        {
            "input": "published free order-nine Schoen quotient",
            "recomputed_by_external_script": False,
            "source": "src/onetheory/models/heterotic_schoen/geometry.py",
        }
    ]


def test_external_sage_path_does_not_import_onetheory() -> None:
    """The independent verifier contains no import of the Python engine."""

    source = SCRIPT.read_text(encoding="utf-8")

    assert "import onetheory" not in source.lower()
    assert "from onetheory" not in source.lower()
