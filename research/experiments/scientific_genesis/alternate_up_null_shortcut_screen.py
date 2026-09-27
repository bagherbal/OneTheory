"""Test whether null homotopies alone close a same-cone up scalar.

Owns:
    An exact countercheck of the A/F0-only contraction of one outer
    extension cup with the opposite null-channel primitive.

Depends on:
    Frozen alternate extension representatives, strict matter classes,
    certified null homotopies, and the common-cover differential.

Must not:
    Treat a nonclosed projection as a Yukawa coefficient, discard
    syzygy terms from a physical calculation, or infer rank three.

Phase 0:
    Research-only screen of a proposed shortcut to the F--F block.
"""

from __future__ import annotations

import json
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .alternate_constituent_outer_universal_cone import INVARIANTS
from .alternate_constituent_up_matter_representatives import (
    alternate_constituent_up_matter_representatives,
)
from .alternate_up_mixed_scalar_trace import _contract, _scalar_context
from .alternate_up_null_channel import OUTPUT as NULL_CHANNELS
from .alternate_up_null_channel import alternate_up_null_channels
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_null_shortcut_screen.json"


def alternate_up_null_shortcut_screen() -> dict[str, object]:
    """Falsify direct A/F0 truncation for the first outer parameter."""

    null_digest, null_record = _verified_payload(NULL_CHANNELS)
    invariant_digest, invariant_record = _verified_payload(INVARIANTS)
    if (
        null_record.get("schema") != "alternate-up-null-channel-v1"
        or null_record.get("rank_three_established") is not False
        or null_record.get("null_to_null_coefficients_computed") is not False
        or invariant_record.get("schema") != "alternate-constituent-outer-invariants-v1"
    ):
        raise ValueError("the null shortcut premises changed")

    left_null, right_null = alternate_up_null_channels()
    classes = tuple(
        item for item in alternate_constituent_up_matter_representatives().classes
        if item.character == (0, 0)
    )
    if (
        len(classes) != 2
        or tuple(item.seed_index for item in classes) != (0, 5)
        or left_null.matter_character != (0, 0)
        or right_null.matter_character != (1, 0)
    ):
        raise ValueError("the declared null matter basis changed")
    null_matter = (
        classes[1].full_cochain
        + classes[0].full_cochain.scale(-left_null.seed5_over_seed0)
    )
    extension = _representative(
        invariant_record["strict_full_cech_representatives"][0]
    )
    product = mixed_outer_cup(extension, null_matter)
    context = _MixedContraction(mixed_schoen_constituents()[0], mixed_schoen_unit())
    if product.is_zero() or not context.differential(product).is_zero():
        raise ValueError("the first extension cup is not an exact cycle")

    syzygy_count = sum(
        basis.component.left_index in (4, 5) for basis, _ in product.terms
    )
    if syzygy_count == 0:
        raise ValueError("the extension cup no longer tests syzygy truncation")
    syzygy_witness = next(
        (basis, value) for basis, value in product.terms
        if basis.component.left_index in (4, 5)
    )
    try:
        _contract(SparseOuterCechCochain((syzygy_witness,)), right_null.primitive)
    except ValueError as error:
        if str(error) != "the first matter class left its A/F0 support":
            raise
    else:
        raise ValueError("the scoped scalar contraction accepted syzygy support")

    restricted = SparseOuterCechCochain(tuple(
        (basis, value) for basis, value in product.terms
        if basis.component.left_index in (1, 2, 3)
    ))
    candidate = _contract(restricted, right_null.primitive)
    if candidate.is_zero():
        raise ValueError("the truncated candidate unexpectedly vanished")
    defect = _scalar_context().differential(candidate)
    if defect.is_zero():
        raise ValueError("the truncated candidate unexpectedly became a cycle")

    return {
        "schema": "alternate-up-null-shortcut-screen-v1",
        "outer_parameter": "a0",
        "first_null_character": [0, 0],
        "opposite_primitive_character": [1, 0],
        "null_matter_term_count": len(null_matter.terms),
        "extension_cup_term_count": len(product.terms),
        "extension_cup_digest": _cochain_digest((product,)),
        "extension_cup_exact_cycle": True,
        "syzygy_term_count": syzygy_count,
        "full_cup_rejected_by_scoped_contraction": True,
        "a_f0_restriction_term_count": len(restricted.terms),
        "truncated_scalar_term_count": len(candidate.terms),
        "truncated_scalar_digest": _cochain_digest((candidate,)),
        "truncated_scalar_differential_term_count": len(defect.terms),
        "truncated_scalar_closed": False,
        "null_to_null_coefficient_computed": False,
        "rank_three_established": False,
        "prerequisite_artifact_digests": {
            "null_channels": null_digest,
            "outer_invariants": invariant_digest,
        },
        "next_required_object": (
            "construct the full same-cone exterior Higgs chain map and its "
            "syzygy-compatible scalar contraction"
        ),
    }


def write_alternate_up_null_shortcut_screen(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the exact closure failure without assigning a coupling."""

    payload = alternate_up_null_shortcut_screen()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_null_shortcut_screen()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"truncated_scalar_closed: {record['truncated_scalar_closed']}")
