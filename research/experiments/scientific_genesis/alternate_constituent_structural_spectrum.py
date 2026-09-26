"""Close the alternate carrier's observable structural-spectrum gate.

Owns:
    An exact equivariant exterior-square filtration argument, character
    transport, and fixed-Wilson multiplicities for the stable P1 component.

Depends on:
    Content-addressed alternate cone, stability, matter, Hom-action,
    determinant, and character certificates plus published Wilson weights.

Must not:
    Claim explicit Higgs cocycles, a Yukawa matrix, bundle moduli, hidden-sector
    consistency, or predictions from the selected spectrum constraints.

Phase 0:
    Research-only theorem-level spectrum; chain representatives remain open.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_observable_spectrum import (
    SPECTRUM_ARXIV_ID,
    SPECTRUM_SOURCE_SHA256,
    WILSON_HIGGS_CHARACTERS,
    _source_digest,
)
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "data/generated/scientific_genesis"
OUTPUT = GENERATED / "alternate_constituent_structural_spectrum.json"
CONE = GENERATED / "alternate_constituent_outer_universal_cone.json"
STABILITY = GENERATED / "alternate_constituent_outer_stability_locus.json"
MATTER = GENERATED / "alternate_constituent_matter_profile.json"
HOM = GENERATED / "alternate_constituent_hom_actions.json"
DETERMINANT = GENERATED / "alternate_constituent_determinant_descent.json"
SCREEN = GENERATED / "alternate_constituent_character_screen.json"
DIMENSIONS = GENERATED / "alternate_constituent_higgs_dimensions.json"
CONVENTION = GENERATED / "mixed_schoen_character_convention.json"
Character = tuple[int, int]


def _case(record: dict[str, object]) -> dict[str, object]:
    """Select the single declared ray without a fallback or point choice."""

    cases = record.get("cases")
    if not isinstance(cases, list):
        raise ValueError("ray cases are missing")
    matches = [
        case
        for case in cases
        if isinstance(case, dict) and case.get("ray_character_exponents") == [0, 1]
    ]
    if len(matches) != 1:
        raise ValueError("ray (0,1) must occur exactly once")
    return cast(dict[str, object], matches[0])


def _character(raw: object) -> Character:
    """Decode one exact Z3 x Z3 character without implicit normalization."""

    if (
        not isinstance(raw, list)
        or len(raw) != 2
        or any(type(value) is not int or value not in range(3) for value in raw)
    ):
        raise ValueError("a character must have two reduced integer exponents")
    return cast(Character, tuple(raw))


def _add(left: Character, right: Character) -> Character:
    return (left[0] + right[0]) % 3, (left[1] + right[1]) % 3


def _negative(value: Character) -> Character:
    return (-value[0]) % 3, (-value[1]) % 3


def _exact_scalar(source: str) -> Eisenstein:
    """Decode the saved exact matrix text without evaluation or floats."""

    def decode(node: ast.expr) -> Eisenstein:
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return Eisenstein(node.value)
        if isinstance(node, ast.Name) and node.id == "omega":
            return OMEGA
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -decode(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return decode(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = decode(node.left), decode(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        raise ValueError("the Hom action matrix contains non-exact scalar syntax")

    return decode(ast.parse(source, mode="eval").body)


def _fourier_characters(hom_case: dict[str, object]) -> tuple[Character, ...]:
    """Independently recover multiplicities from exact group traces."""

    def action(generator: str) -> Matrix:
        rows = cast(list[list[str]], hom_case[generator])
        if len(rows) != 4 or any(len(row) != 4 for row in rows):
            raise ValueError("the exact Hom action is not four-dimensional")
        return Matrix(
            tuple(tuple(_exact_scalar(value) for value in row) for row in rows),
            scalar_type=Eisenstein,
        )

    p, t = action("P"), action("T")
    identity = Matrix.identity(4, scalar_type=Eisenstein)
    if p**3 != identity or t**3 != identity or p @ t != t @ p:
        raise ValueError("the saved Hom matrices violate the deck group laws")
    characters: list[Character] = []
    for u in range(3):
        for v in range(3):
            projector_trace = Eisenstein(0)
            for a in range(3):
                for b in range(3):
                    product = p**a @ t**b
                    trace = sum((product[i][i] for i in range(4)), Eisenstein(0))
                    projector_trace += OMEGA ** (-u * a - v * b) * trace
            multiplicity = projector_trace / Eisenstein(9)
            if (
                not multiplicity.b.is_zero()
                or multiplicity.a.denominator != 1
                or multiplicity.a < 0
            ):
                raise ValueError("a Fourier character multiplicity is not integral")
            characters.extend(((u, v),) * int(multiplicity.a))
    if len(characters) != 4:
        raise ValueError("Fourier multiplicities do not span the Hom H1 space")
    return tuple(characters)


def alternate_constituent_structural_spectrum() -> dict[str, object]:
    """Certify the all-parameter observable charged spectrum, not cocycles."""

    cone_digest, cone = _verified_payload(CONE)
    stability_digest, stability = _verified_payload(STABILITY)
    matter_digest, matter = _verified_payload(MATTER)
    hom_digest, hom = _verified_payload(HOM)
    determinant_digest, determinant = _verified_payload(DETERMINANT)
    screen_digest, screen = _verified_payload(SCREEN)
    dimensions_digest, dimensions = _verified_payload(DIMENSIONS)
    convention_digest, convention = _verified_payload(CONVENTION)
    hom_case = _case(hom)
    determinant_case = _case(determinant)
    screen_case = _case(screen)
    dimension_case = _case(dimensions)
    screen_prerequisites = cast(dict[str, object], screen["prerequisite_artifact_digests"])
    matter_prerequisites = cast(dict[str, object], matter["prerequisite_artifact_digests"])
    if (
        cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("projective_non_split_space") != "P^1(Q(omega))"
        or cone.get("equivariant_descent_exact") is not True
        or cone.get("quotient_determinant_trivial_exact") is not True
        or cone.get("common_flat_character_twist") != [1, 2]
        or stability.get("schema") != "alternate-constituent-outer-stability-locus-v1"
        or stability.get("universal_cone_digest") != cone_digest
        or stability.get("all_nonzero_parameters_stable_in_chamber") is not True
        or cast(dict[str, object], stability["structure_group"]).get(
            "genuine_su4_on_certified_locus"
        )
        is not True
        or matter.get("schema") != "alternate-constituent-matter-profile-v1"
        or matter_prerequisites.get("alternate_cone") != cone_digest
        or matter_prerequisites.get("alternate_stability") != stability_digest
        or matter.get("visible_cover_h0_to_h3") != [0, 27, 0, 0]
        or hom.get("schema") != "alternate-constituent-hom-actions-v2"
        or hom_case.get("cohomology_group_relations") is not True
        or hom_case.get("boundary_preservation_certified") is not True
        or hom_case.get("h1_dimension") != 4
        or determinant.get("schema") != "alternate-constituent-determinant-descent-v1"
        or determinant_case.get("total_cover_line_degree") != [0, 0, 0]
        or determinant_case.get("constituent_determinant_characters") != [[0, 0], [2, 1]]
        or screen.get("schema") != "alternate-constituent-character-screen-v1"
        or screen_prerequisites.get("hom_actions") != hom_digest
        or screen_prerequisites.get("determinant") != determinant_digest
        or screen_prerequisites.get("source_convention") != convention_digest
        or screen.get("determinant_filtration_identifies_h1_if_extension_exists") is not True
        or cast(dict[str, object], screen["determinant_line_cohomology_h0_to_h3"])
        != {"det_v1": [0, 0, 0, 0], "det_v2": [0, 0, 0, 0]}
        or convention.get("character_conversion") != "source=(-forward) mod 3 factorwise"
        or dimensions.get("schema") != "alternate-constituent-higgs-dimensions-v2"
        or dimension_case.get("h1_dimension") != 4
    ):
        raise ValueError("the alternate structural-spectrum premises changed")
    dimension_spaces = dict(cast(list[list[int]], dimension_case["space_dimensions"]))
    dimension_ranks = dict(cast(list[list[int]], dimension_case["differential_ranks"]))
    if (
        dimension_spaces[0] - dimension_ranks[0] != 0
        or dimension_spaces[1] - dimension_ranks[0] - dimension_ranks[1] != 4
        or hom_case.get("incoming_rank") != dimension_ranks[0]
        or hom_case.get("outgoing_rank") != dimension_ranks[1]
    ):
        raise ValueError("the alternate Hom H0/H1 dimensions changed")
    total = _character(determinant_case["total_determinant_character"])
    twist = _character(cone["common_flat_character_twist"])
    if _add(total, _add(_add(twist, twist), _add(twist, twist))) != (0, 0):
        raise ValueError("the common twist does not trivialize det V")
    hom_characters = tuple(
        _character(item) for item in cast(list[list[int]], hom_case["cover_hom_characters"])
    )
    if len(hom_characters) != 4:
        raise ValueError("the four-dimensional Hom character basis changed")
    fourier_characters = _fourier_characters(hom_case)
    if tuple(sorted(hom_characters)) != fourier_characters:
        raise ValueError("the Hom eigenspaces disagree with independent Fourier traces")
    # Rank-two exterior contraction is natural: Hom(F det E,E) is
    # E tensor F tensor (det E det F)^-1. This is an equivariant identity,
    # not an empirical or native-to-heterotic adapter.
    tensor_characters = tuple(
        sorted(_add(_add(character, total), _add(twist, twist)) for character in hom_characters)
    )
    source_characters = tuple(sorted(_negative(character) for character in tensor_characters))
    projection = {
        label: source_characters.count(_negative(weight))
        for label, weight in WILSON_HIGGS_CHARACTERS.items()
    }
    if (
        [list(item) for item in tensor_characters]
        != screen_case.get("repaired_tensor_forward_characters")
        or [list(item) for item in source_characters]
        != screen_case.get("repaired_source_characters")
        or projection != screen_case.get("conditional_fixed_wilson_multiplicities")
        or projection
        != {
            "up_higgs_doublet": 1,
            "down_higgs_doublet": 1,
            "color_triplet": 0,
            "color_antitriplet": 0,
        }
    ):
        raise ValueError("the repaired Higgs character projection changed")
    deck = cast(dict[str, object], matter["deck_representation"])
    multiplicities = cast(list[dict[str, object]], deck["joint_character_multiplicities"])
    if (
        deck.get("regular_multiplicity") != 3
        or len(multiplicities) != 9
        or {tuple(cast(list[int], item["character_exponents"])) for item in multiplicities}
        != {(p, t) for p in range(3) for t in range(3)}
        or any(item.get("multiplicity") != 3 for item in multiplicities)
    ):
        raise ValueError("the alternate matter deck representation changed")
    source_digest = _source_digest(SPECTRUM_ARXIV_ID, SPECTRUM_SOURCE_SHA256)
    if screen.get("published_spectrum_source_sha256") != source_digest:
        raise ValueError("the Wilson-source archive changed")
    return {
        "schema": "alternate-constituent-structural-spectrum-v1",
        "coefficient_field": "Q(omega)",
        "ray_character_exponents": [0, 1],
        "prerequisite_artifact_digests": {
            "alternate_cone": cone_digest,
            "alternate_stability": stability_digest,
            "alternate_matter": matter_digest,
            "alternate_hom_actions": hom_digest,
            "alternate_determinant": determinant_digest,
            "prior_conditional_screen": screen_digest,
            "alternate_higgs_dimensions": dimensions_digest,
            "source_character_convention": convention_digest,
            "published_wilson_source": source_digest,
        },
        "parameter_locus": "P^1(Q(omega)) x K^s",
        "every_nonzero_extension_parameter": True,
        "arbitrary_extension_point_selected": False,
        "rank_two_equivariant_identity": ("Hom(F tensor det(E),E) = E tensor F tensor det(E+F)^-1"),
        "hom_characters_independently_recovered_by_fourier_traces": True,
        "hom_fourier_characters": [list(item) for item in fourier_characters],
        "exterior_square_filtration": ["det(E)", "E tensor F", "det(F)"],
        "determinant_endpoints_acyclic": True,
        "higgs_h1_equivariantly_identified_with_constituent_tensor": True,
        "common_flat_twist": list(twist),
        "cover_higgs_h0_to_h3": [0, 4, 4, 0],
        "cover_higgs_h2_h3_by_serre_duality": True,
        "higgs_forward_characters": [list(item) for item in tensor_characters],
        "higgs_source_characters": [list(item) for item in source_characters],
        "fixed_wilson_higgs_multiplicities": projection,
        "matter_cover_h0_to_h3": [0, 27, 0, 0],
        "matter_deck_regular_multiplicity": 3,
        "observable_wilson_projection": {
            "families": 3,
            "right_handed_neutrinos": 3,
            "anti_families": 0,
            "higgs_pairs": 1,
            "massless_color_triplets": 0,
            "charged_exotic_blocks_from_16_and_10": 0,
        },
        "selected_constraints_not_predictions": [
            "three families",
            "one Higgs pair",
            "fixed published Wilson embedding",
        ],
        "observable_charged_structural_spectrum_passes": True,
        "bundle_moduli_h_end_computed": False,
        "explicit_cone_matter_cocycles_computed": False,
        "explicit_cone_higgs_cocycles_computed": False,
        "holomorphic_yukawa_matrix_computed": False,
        "hidden_sector_consistency_computed": False,
        "genesis_to_heterotic_implication_derived": False,
        "next_required_object": (
            "freeze the structurally viable component without selecting a "
            "point, then generate same-cone matter/Higgs cocycles for Yukawas"
        ),
    }


def write_alternate_constituent_structural_spectrum(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write one content-addressed all-parameter spectrum certificate."""

    payload = alternate_constituent_structural_spectrum()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_structural_spectrum()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"observable_wilson_projection: {report['observable_wilson_projection']}")
