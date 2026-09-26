"""Transfer a source-scoped stability bound to the alternate universal cone.

Owns:
    Exact applicability checks for the Serre-sequence stability theorem,
    rational open-chamber arithmetic, and the odd-Chern reduction gate.

Depends on:
    The certified alternate P1 cone, locally free ray presentation, published
    stability-source manifests, and reusable exact slope machinery.

Must not:
    Infer stability from Chern data alone, select a projective point, claim
    the entire Kähler stable cone, or fabricate matter/Higgs cocycles.

Phase 0:
    Research-only source-conditioned stable-locus certificate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Rational
from onetheory.models.heterotic_schoen.geometry import (
    SCHOEN_COVERING_DEGREE,
    schoen_geometry,
)
from onetheory.models.heterotic_schoen.visible import STABILITY_ROWS, visible_bundle
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.stability import StabilityPolynomial

from .alternate_constituent_outer_universal_cone import OUTPUT as CONE
from .alternate_constituent_outer_universal_cone import _graded_line_objects
from .distinct_constituent_ray_screen import OUTPUT as RAYS
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_outer_stability_locus import (
    BOUNDS_ARXIV_ID,
    BOUNDS_SOURCE_SHA256,
    STABILITY_ARXIV_ID,
    STABILITY_SOURCE_SHA256,
    MixedSchoenOuterStabilityLocus,
    _source_digest,
)
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT / "data/generated/scientific_genesis/"
    "alternate_constituent_outer_stability_locus.json"
)


def _certified_cone() -> str:
    """Require the exact alternate algebraic family before stability work."""

    record = json.loads(CONE.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if (
        digest != _canonical_digest(record)
        or record.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or record.get("ray_character_exponents") != [0, 1]
        or record.get("projective_non_split_space") != "P^1(Q(omega))"
        or record.get("constituent_graded_line_objects_match_published_selected_ray")
        is not True
        or record.get("equivariant_descent_exact") is not True
        or record.get("local_freeness_locus") != "all A^2(Q(omega))"
        or record.get("quotient_determinant_trivial_exact") is not True
        or record.get("genuine_su4_locus_computed") is not False
    ):
        raise ValueError("the alternate cone has not closed its algebraic gates")
    return cast(str, digest)


def _certified_serre_presentation() -> tuple[str, bool]:
    """Verify both local-unit rays and identical constituent K-classes."""

    record = json.loads(RAYS.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    survivors = record.get("local_unit_survivors", [])
    if (
        digest != _canonical_digest(record)
        or record.get("schema") != "distinct-constituent-ray-screen-v1"
        or not isinstance(survivors, list)
        or not all(
            any(
                isinstance(item, dict)
                and item.get("scheme") == scheme
                and item.get("character_exponents") == character
                for item in survivors
            )
            for scheme, character in (("I3", [1, 0]), ("I6", [0, 1]))
        )
    ):
        raise ValueError("the alternate Serre local-unit premise changed")
    old_first, old_second = mixed_schoen_constituents()
    action = published_constituent_deck_actions()[1]
    full = lift_joint_character_ray(action, OMEGA**0, OMEGA**1)
    new_second = _constituent(full, "I6-ray-0-1", 2, (1, -1, 0))
    same = (
        old_first.factor == 1
        and old_second.factor == new_second.factor == 2
        and _graded_line_objects(old_second) == _graded_line_objects(new_second)
    )
    if not same:
        raise ValueError("the alternate ray changed the Serre presentation type")
    return cast(str, digest), same


def alternate_constituent_outer_stability_locus() -> dict[str, object]:
    """Certify a sufficient stable SU(4) chamber for every nonzero class."""

    cone_digest = _certified_cone()
    ray_digest, same_presentation = _certified_serre_presentation()
    bundle = visible_bundle(schoen_geometry()).bundle
    inequalities = tuple(
        StabilityPolynomial(line_class, coefficients, anchor_value)
        for line_class, coefficients, anchor_value, _, _ in STABILITY_ROWS
    )
    locus = MixedSchoenOuterStabilityLocus(
        cone_digest,
        _source_digest(STABILITY_ARXIV_ID, STABILITY_SOURCE_SHA256),
        _source_digest(BOUNDS_ARXIV_ID, BOUNDS_SOURCE_SHA256),
        inequalities,
        (Rational(6), Rational(9), Rational(3)),
        Rational(1, 32),
        same_presentation,
        True,
        bundle.rank,
        bundle.c1,
        bundle.c3,
        SCHOEN_COVERING_DEGREE,
    )
    record = locus.as_record()
    record["schema"] = "alternate-constituent-outer-stability-locus-v1"
    record["ray_character_exponents"] = [0, 1]
    record["serre_ray_artifact_digest"] = ray_digest
    record["serre_quotient_ideals_unchanged"] = ["I3", "I6"]
    record["serre_line_and_ideal_presentation_type_unchanged"] = same_presentation
    record["alternate_serre_ray_nontrivial_and_locally_free"] = True
    record["common_flat_twist_preserves_slopes"] = True
    record["source_stability_bound_uses_serre_sequences_not_ray_coordinates"] = True
    record["source_bound_applicability"] = (
        "The published sub-line bounds use the Serre subline and fixed "
        "I3/I6 ideal quotients; the nontrivial-extension lower bound "
        "excludes a splitting. The alternate ray changes neither exact "
        "sequence type nor ideal support, and every nonzero P1 outer class "
        "is non-split. A common flat character twist leaves slopes unchanged."
    )
    record["source_bound_derivation"] = (
        "research/experiments/scientific_genesis/ALTERNATE_STABILITY_NOTE.md"
    )
    record.pop("source_invariant_ext_dimension")
    record.pop("lawful_invariant_ext_dimension")
    record.pop("dimension_mismatch_affects_stability_implication")
    record["alternate_invariant_ext_dimension"] = 2
    record["full_kahler_stability_chamber_computed"] = False
    record["physical_spectrum_computed"] = False
    record["first_missing_input"] = (
        "derive parameter-dependent matter and explicit Higgs cocycles "
        "from the same alternate universal cone"
    )
    record["status"] = (
        "every nonzero alternate P1 extension is stable and genuinely "
        "SU(4) throughout the certified sufficient Kahler chamber"
    )
    return record


def write_alternate_constituent_outer_stability_locus(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed alternate stability certificate."""

    payload = alternate_constituent_outer_stability_locus()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_outer_stability_locus()
    print(f"artifact_digest: {report['artifact_digest']}")
    structure_group = cast(dict[str, object], report["structure_group"])
    print(
        "genuine_su4_on_certified_locus: "
        f"{structure_group['genuine_su4_on_certified_locus']}"
    )
