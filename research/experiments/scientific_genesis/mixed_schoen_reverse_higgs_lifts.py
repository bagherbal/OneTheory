"""Lift the physical down-Higgs cocycle over the reverse extension family.

Owns:
    Exact determinant-two corrections to the strict middle tensor Higgs class
    for every reverse outer-extension parameter and their canonical fiber frame.

Depends on:
    The certified reverse basis, synchronized strict Higgs cocycle, independent
    second-factor lift, Hilbert--Burch pairing, and exact diagonal line homotopy.

Must not:
    Select an extension point, infer a Yukawa coefficient, replace the derived
    determinant frame, or use observational inputs.

Phase 0:
    Research-only common-chain reverse universal Higgs lift.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .diagonal_schoen_line_actions import (
    constituent_determinant_character,
    line_has_character,
    project_line_character,
)
from .diagonal_schoen_line_contraction import exact_diagonal_ambient_line_primitive
from .diagonal_schoen_line_isomorphism import canonicalize_q_minus_p_twist
from .diagonal_schoen_lines import (
    LineDegree4,
    Monomial,
    _FullBasis,
    _FullCochain,
    _subtract_degrees,
)
from .mixed_schoen_chain_actions import load_certified_higgs_representative
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalCochain,
    chain_diagonal_objects,
)
from .mixed_schoen_character_convention import (
    OUTPUT as CONVENTION_ARTIFACT,
)
from .mixed_schoen_matter_comparison import _cochain_digest
from .mixed_schoen_matter_tensor import _cell_cup, lift_matter_cochain
from .mixed_schoen_outer_universal_cone import _load_orientation_basis
from .mixed_schoen_reverse_down_matter_lifts import FORWARD_DOWN_HIGGS_CHARACTER
from .mixed_schoen_reverse_outer_universal_cone import (
    OUTPUT as REVERSE_UNIVERSAL_ARTIFACT,
)
from .mixed_schoen_universal_matter_lifts import _verified_digest
from .mixed_schoen_yukawa_trace import (
    _complementary_minor_polynomials,
    _full_cochain_digest,
    scalar_full_differential,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_reverse_higgs_lifts.json"
)
DET_V2_RAW_DEGREES: LineDegree4 = (2, -1, -2, 1)
DET_V2_CANONICAL_DEGREES: LineDegree4 = (2, 0, -2, 0)


def _source_zero_component(
    extension: SparseOuterCechCochain,
) -> SparseOuterCechCochain:
    """Retain the reverse arrow composable with the strict A1 Higgs leg."""

    result = SparseOuterCechCochain(
        tuple(
            (basis, coefficient)
            for basis, coefficient in extension.terms
            if basis.component.right_index == 0
        )
    )
    if result.is_zero():
        raise ValueError("the reverse extension has no A1-composable terms")
    return result


def _sum_monomials(*values: Monomial) -> Monomial:
    """Add Laurent exponents in one named ambient factor."""

    return tuple(sum(entries) for entries in zip(*values, strict=True))


def reverse_extension_higgs_action(
    extension: SparseOuterCechCochain,
    higgs: ChainDiagonalCochain,
) -> _FullCochain:
    """Apply a reverse arrow to A1 and pair its V2 output with A2."""

    independent = lift_matter_cochain(_source_zero_component(extension), 2)
    minors = _complementary_minor_polynomials(2)
    objects = chain_diagonal_objects()
    zero3: Monomial = (0, 0, 0)
    zero2: Monomial = (0, 0)
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    for extension_basis, extension_coefficient in independent.terms:
        if extension_basis.object_index == 0:
            continue
        if extension_basis.object_index > len(minors):
            continue
        minor = minors[extension_basis.object_index - 1]
        for higgs_basis, higgs_coefficient in higgs.terms:
            higgs_object = objects[higgs_basis.component.object_index]
            if (higgs_object.first_index, higgs_object.second_index) != (0, 0):
                raise ValueError("the reverse action requires the strict A1-A2 Higgs")
            cell_product = _cell_cup(extension_basis.cell, higgs_basis.cell)
            if cell_product is None:
                continue
            cell_sign, cell = cell_product
            raw_subset = (
                *extension_basis.subset,
                *higgs_basis.component.subset,
            )
            if len(set(raw_subset)) != len(raw_subset):
                continue
            inversions = sum(
                raw_subset[first] > raw_subset[second]
                for first in range(len(raw_subset))
                for second in range(first + 1, len(raw_subset))
            )
            subset = tuple(sorted(raw_subset))
            crossing = (
                len(extension_basis.subset) * higgs_object.position
                + extension_basis.cech_degree
                * higgs_basis.component.structural_degree
            )
            sign = cell_sign * (-1 if (inversions + crossing) % 2 else 1)
            ambient_degrees = _subtract_degrees(DET_V2_RAW_DEGREES, subset)
            for exponents, minor_coefficient in minor.terms:
                monomials = cast(
                    tuple[Monomial, Monomial, Monomial, Monomial],
                    tuple(
                        _sum_monomials(source, higgs_value, polynomial)
                        for source, higgs_value, polynomial in zip(
                            extension_basis.monomials,
                            higgs_basis.monomials,
                            (zero3, zero2, cast(Monomial, exponents), zero2),
                            strict=True,
                        )
                    ),
                )
                if tuple(sum(monomial) for monomial in monomials) != ambient_degrees:
                    raise ValueError("the reverse Higgs action changed det(V2) degree")
                terms.append(
                    (
                        _FullBasis(subset, ambient_degrees, monomials, cell),
                        extension_coefficient
                        * higgs_coefficient
                        * cast(Eisenstein, minor_coefficient)
                        * sign,
                    )
                )
    return _FullCochain(tuple(terms))


@dataclass(frozen=True, slots=True)
class ReverseHiggsLiftCoefficient:
    """One exact determinant-two correction to the reverse Higgs class."""

    parameter: str
    source_term_count: int
    action: _FullCochain
    correction: _FullCochain
    canonical_action: _FullCochain
    canonical_correction: _FullCochain
    projection_depth: int
    inclusion_depth: int
    homotopy_depth: int
    action_is_cycle: bool
    action_character_exact: bool
    correction_identity_exact: bool
    correction_character_exact: bool
    canonical_action_is_cycle: bool
    canonical_correction_identity_exact: bool
    canonical_action_character_exact: bool
    canonical_correction_character_exact: bool

    @property
    def exact(self) -> bool:
        """Return all common-chain and strict-character gates."""

        return (
            self.parameter in {f"b{index}" for index in range(6)}
            and self.source_term_count > 0
            and bool(self.action.terms)
            and self.action_is_cycle
            and self.action_character_exact
            and self.correction_identity_exact
            and self.correction_character_exact
            and self.canonical_action_is_cycle
            and self.canonical_correction_identity_exact
            and self.canonical_action_character_exact
            and self.canonical_correction_character_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one exact coefficient without calling it a coupling."""

        return {
            "parameter": self.parameter,
            "source_term_count": self.source_term_count,
            "action_term_count": len(self.action.terms),
            "action_digest": _full_cochain_digest(self.action),
            "correction_term_count": len(self.correction.terms),
            "correction_digest": _full_cochain_digest(self.correction),
            "canonical_action_term_count": len(self.canonical_action.terms),
            "canonical_action_digest": _full_cochain_digest(self.canonical_action),
            "canonical_correction_term_count": len(self.canonical_correction.terms),
            "canonical_correction_digest": _full_cochain_digest(
                self.canonical_correction
            ),
            "projection_depth": self.projection_depth,
            "inclusion_depth": self.inclusion_depth,
            "homotopy_depth": self.homotopy_depth,
            "action_is_cycle": self.action_is_cycle,
            "action_character_exact": self.action_character_exact,
            "correction_identity_exact": self.correction_identity_exact,
            "correction_character_exact": self.correction_character_exact,
            "canonical_action_is_cycle": self.canonical_action_is_cycle,
            "canonical_correction_identity_exact": (
                self.canonical_correction_identity_exact
            ),
            "canonical_action_character_exact": (
                self.canonical_action_character_exact
            ),
            "canonical_correction_character_exact": (
                self.canonical_correction_character_exact
            ),
            "exact": self.exact,
        }


@cache
def reverse_higgs_lift_coefficient(parameter_index: int) -> ReverseHiggsLiftCoefficient:
    """Solve one universal reverse Higgs boundary with no point selection."""

    if not 0 <= parameter_index < 6:
        raise ValueError("the reverse Higgs parameter index is unavailable")
    _action_digest, parameters, extensions = _load_orientation_basis(
        "V2", "V1", "b"
    )
    if parameters != tuple(f"b{index}" for index in range(6)):
        raise ValueError("the reverse extension basis changed")
    extension = extensions[parameter_index]
    source = _source_zero_component(extension)
    higgs = load_certified_higgs_representative()
    action = reverse_extension_higgs_action(extension, higgs)
    primitive = exact_diagonal_ambient_line_primitive(
        action, DET_V2_RAW_DEGREES, 2
    )
    frame_character = constituent_determinant_character(2)
    correction = project_line_character(
        primitive.primitive,
        FORWARD_DOWN_HIGGS_CHARACTER,
        frame_character,
    ).scale(-1)
    canonical_action = canonicalize_q_minus_p_twist(
        action,
        DET_V2_RAW_DEGREES,
        DET_V2_CANONICAL_DEGREES,
    )
    canonical_correction = canonicalize_q_minus_p_twist(
        correction,
        DET_V2_RAW_DEGREES,
        DET_V2_CANONICAL_DEGREES,
    )
    result = ReverseHiggsLiftCoefficient(
        parameters[parameter_index],
        len(source.terms),
        action,
        correction,
        canonical_action,
        canonical_correction,
        primitive.projection_depth,
        primitive.inclusion_depth,
        primitive.homotopy_depth,
        scalar_full_differential(action).is_zero(),
        line_has_character(action, FORWARD_DOWN_HIGGS_CHARACTER, frame_character),
        scalar_full_differential(correction) == action.scale(-1),
        line_has_character(
            correction, FORWARD_DOWN_HIGGS_CHARACTER, frame_character
        ),
        scalar_full_differential(canonical_action).is_zero(),
        scalar_full_differential(canonical_correction)
        == canonical_action.scale(-1),
        line_has_character(
            canonical_action, FORWARD_DOWN_HIGGS_CHARACTER, frame_character
        ),
        line_has_character(
            canonical_correction, FORWARD_DOWN_HIGGS_CHARACTER, frame_character
        ),
    )
    if not result.exact:
        raise ValueError(f"reverse Higgs coefficient failed: {result.as_record()}")
    return result


def write_reverse_higgs_lifts(path: Path = OUTPUT) -> dict[str, object]:
    """Write all six exact reverse Higgs coefficients with provenance."""

    higgs = load_certified_higgs_representative()
    coefficients = tuple(reverse_higgs_lift_coefficient(index) for index in range(6))
    payload: dict[str, object] = {
        "schema": "mixed-schoen-reverse-higgs-lifts-v2",
        "coefficient_field": "Q(omega)",
        "extension_sequence": "0 -> V2 -> E_reverse -> V1 -> 0",
        "carrier_locus": "P^5(Q(omega)) x K_reverse^s",
        "forward_higgs_character_exponents": list(FORWARD_DOWN_HIGGS_CHARACTER),
        "source_higgs_character_exponents": [0, 2],
        "strict_middle_higgs_term_count": len(higgs.terms),
        "strict_middle_higgs_digest": _cochain_digest(higgs),
        "det_v2_raw_ambient_degrees": list(DET_V2_RAW_DEGREES),
        "det_v2_canonical_ambient_degrees": list(DET_V2_CANONICAL_DEGREES),
        "det_v2_frame_character": list(constituent_determinant_character(2)),
        "diagonal_line_identification": (
            "the (0,-1,0,1) q-minus-p twist restricts trivially on the "
            "fiber diagonal and is retained by an exact overlap homotopy"
        ),
        "parameter_coefficients": [item.as_record() for item in coefficients],
        "all_coefficients_exact": all(item.exact for item in coefficients),
        "arbitrary_extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "character_convention": _verified_digest(
                CONVENTION_ARTIFACT,
                "physical_down_higgs_representative_available",
                True,
            ),
            "reverse_universal_cone": _verified_digest(
                REVERSE_UNIVERSAL_ARTIFACT,
                "equivariant_descent_exact",
                True,
            ),
        },
        "next_required_object": (
            "reverse same-chain determinant contraction for one complete "
            "down-type holomorphic Yukawa matrix"
        ),
    }
    if not payload["all_coefficients_exact"]:
        raise ValueError("the reverse Higgs lift is incomplete")
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
    """Regenerate the exact reverse universal Higgs certificate."""

    payload = write_reverse_higgs_lifts()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"coefficient_count: {len(payload['parameter_coefficients'])}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DET_V2_CANONICAL_DEGREES",
    "DET_V2_RAW_DEGREES",
    "ReverseHiggsLiftCoefficient",
    "reverse_extension_higgs_action",
    "reverse_higgs_lift_coefficient",
    "write_reverse_higgs_lifts",
]
