"""Freeze the lawful reverse Schoen carrier component for vertical work.

Owns:
    An immutable reverse P5 carrier state bound to exact algebraic, stability,
    and spectrum certificates while retaining the source-reference separation.

Depends on:
    The reverse observable-spectrum artifact and the established generic
    carrier-state record used by the earlier forward component.

Must not:
    Select a P5 point, erase the forward carrier's scoped flavor no-go, identify
    P5 with the source P3 ledger, or claim common-DGA representatives exist.

Phase 0:
    Research-only reverse carrier-component freeze before DGA construction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .computable_one_theory_carrier_state import (
    ComputableOneTheoryCarrierState,
    PublishedReferenceCarrierState,
    _verified_spectrum_artifact,
    published_reference_carrier_state,
)
from .mixed_schoen_reverse_observable_spectrum import OUTPUT as SPECTRUM_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "computable_one_theory_reverse_carrier_state.json"
)


def computable_one_theory_reverse_carrier_state() -> tuple[
    PublishedReferenceCarrierState,
    ComputableOneTheoryCarrierState,
]:
    """Freeze the lawful reverse P5 component without selecting a point."""

    spectrum_digest, spectrum = _verified_spectrum_artifact(
        SPECTRUM_ARTIFACT,
        "mixed-schoen-reverse-observable-spectrum-v1",
        "P^5(Q(omega)) x K_reverse^s",
    )
    source = cast(dict[str, object], spectrum["source"])
    prerequisites = cast(
        dict[str, str],
        spectrum["prerequisite_artifact_digests"],
    )
    reference = published_reference_carrier_state(
        cast(str, source["source_archive_sha256"])
    )
    computable = ComputableOneTheoryCarrierState(
        "lawful-mixed-schoen-reverse-P5",
        "P^5(Q(omega))",
        "K_reverse^s",
        "Q(omega)",
        spectrum_digest,
        prerequisites["universal_cone"],
        prerequisites["stable_su4_locus"],
        prerequisites["relative_pushdowns"],
        4,
        "trivial",
        -54,
        -6,
        "SU(4)",
        (
            "the smallest exact unretired replacement after the forward "
            "all-sector flavor no-go; no phenomenological ranking among P5 points"
        ),
        True,
        False,
        "COMPUTED",
    )
    return reference, computable


def write_computable_one_theory_reverse_carrier_state(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed reverse carrier-component state."""

    reference, computable = computable_one_theory_reverse_carrier_state()
    payload: dict[str, object] = {
        "schema": "computable-one-theory-reverse-carrier-state-v1",
        "published_reference_carrier_state": reference.as_record(),
        "computable_one_theory_carrier_state": computable.as_record(),
        "states_are_distinct": True,
        "source_p3_to_lawful_reverse_p5_equivalence_claimed": False,
        "forward_p1_remains_lawful": True,
        "forward_p1_flavor_scope_exhausted": True,
        "status": (
            "lawful reverse physical carrier component frozen for vertical "
            "common-DGA computation"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the frozen reverse carrier-component artifact."""

    payload = write_computable_one_theory_reverse_carrier_state()
    state = cast(dict[str, object], payload["computable_one_theory_carrier_state"])
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"component_id: {state['component_id']}")
    print(f"next_required_object: {state['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "computable_one_theory_reverse_carrier_state",
    "write_computable_one_theory_reverse_carrier_state",
]
