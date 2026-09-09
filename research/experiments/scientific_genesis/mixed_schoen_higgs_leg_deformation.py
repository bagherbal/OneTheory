"""Lift the strict Higgs class along one universal extension direction.

Owns:
    The extension action on the strict V1-tensor-V2 Higgs cocycle, its exact
    determinant-line cycle, and the canonical parameter-linear primitive.

Depends on:
    The source-derived universal extension basis, local diagonal comparison,
    Hilbert--Burch determinant orientation, and exact line contraction.

Must not:
    Pair two V2 matter classes without the full local Pluecker chain map,
    choose an extension point, infer a Yukawa value, or import observations.

Phase 0:
    Research-only Higgs-leg lift for the first lawful higher product.
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

from .diagonal_schoen_line_contraction import (
    exact_diagonal_ambient_line_primitive,
)
from .diagonal_schoen_lines import (
    LineDegree4,
    Monomial,
    _FullBasis,
    _FullCochain,
    _subtract_degrees,
)
from .mixed_schoen_chain_actions import mixed_schoen_higgs_deck_action
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalCochain,
    chain_diagonal_objects,
)
from .mixed_schoen_diagonal_chain_map import diagonal_compare_common_matter
from .mixed_schoen_matter_tensor import _cell_cup
from .mixed_schoen_outer_universal_cone import _load_forward_basis
from .mixed_schoen_yukawa_trace import (
    _complementary_minor_polynomials,
    _full_cochain_digest,
    scalar_full_differential,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_higgs_leg_deformation.json"
DETERMINANT_AMBIENT_DEGREES: LineDegree4 = (-2, 1, 2, -1)


def _add_monomials(*values: Monomial) -> Monomial:
    """Add equally based Laurent exponent vectors."""

    return tuple(sum(entries) for entries in zip(*values, strict=True))


def _source_zero_component(
    extension: SparseOuterCechCochain,
) -> SparseOuterCechCochain:
    """Retain exactly the extension terms composable with the Higgs A2 object."""

    result = SparseOuterCechCochain(
        tuple(
            (basis, coefficient)
            for basis, coefficient in extension.terms
            if basis.component.right_index == 0
        )
    )
    if result.is_zero():
        raise ValueError("the universal extension has no Higgs-composable terms")
    return result


def extension_higgs_action(
    extension: SparseOuterCechCochain,
    higgs: ChainDiagonalCochain,
) -> _FullCochain:
    """Apply one extension coefficient to the V2 leg and pair the two V1 legs."""

    compared = diagonal_compare_common_matter(_source_zero_component(extension))
    objects = chain_diagonal_objects()
    minors = _complementary_minor_polynomials(1)
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    for extension_basis, extension_coefficient in compared.terms:
        if extension_basis.object_index == 0:
            continue
        if extension_basis.object_index > len(minors):
            continue
        minor = minors[extension_basis.object_index - 1]
        for higgs_basis, higgs_coefficient in higgs.terms:
            higgs_object = objects[higgs_basis.component.object_index]
            if (higgs_object.first_index, higgs_object.second_index) != (0, 0):
                raise ValueError("the extension action requires the strict A1-A2 Higgs")
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
                + extension_basis.cech_degree * higgs_basis.component.structural_degree
            )
            sign = cell_sign * (-1 if (inversions + crossing) % 2 else 1)
            ambient_degrees = _subtract_degrees(
                DETERMINANT_AMBIENT_DEGREES,
                subset,
            )
            for exponents, minor_coefficient in minor.terms:
                monomials = cast(
                    tuple[Monomial, Monomial, Monomial, Monomial],
                    (
                        _add_monomials(
                            extension_basis.monomials[0],
                            higgs_basis.monomials[0],
                            cast(Monomial, exponents),
                        ),
                        *(
                            _add_monomials(
                                extension_basis.monomials[factor],
                                higgs_basis.monomials[factor],
                            )
                            for factor in range(1, 4)
                        ),
                    ),
                )
                if tuple(sum(monomial) for monomial in monomials) != ambient_degrees:
                    raise ValueError("the Higgs extension action changed line degree")
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
class HiggsLegDeformationWitness:
    """One exact coefficient of the universal Higgs exterior-square lift."""

    parameter: str
    extension_source_term_count: int
    action: _FullCochain
    correction: _FullCochain
    projection_depth: int
    inclusion_depth: int
    homotopy_depth: int
    action_is_cycle: bool
    correction_identity_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether the full determinant-line lift closes exactly."""

        return (
            self.parameter == "a0"
            and self.extension_source_term_count > 0
            and bool(self.action.terms)
            and bool(self.correction.terms)
            and self.action_is_cycle
            and self.correction_identity_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact Higgs-leg lift without a bottom-matter pairing."""

        return {
            "parameter": self.parameter,
            "determinant_ambient_degrees": list(DETERMINANT_AMBIENT_DEGREES),
            "diagonal_line_identification": (
                "the (0,1,0,-1) p-q twist restricts trivially on the fiber "
                "diagonal and is retained explicitly"
            ),
            "extension_source_term_count": self.extension_source_term_count,
            "action_term_count": len(self.action.terms),
            "action_digest": _full_cochain_digest(self.action),
            "correction_term_count": len(self.correction.terms),
            "correction_digest": _full_cochain_digest(self.correction),
            "projection_depth": self.projection_depth,
            "inclusion_depth": self.inclusion_depth,
            "homotopy_depth": self.homotopy_depth,
            "action_is_cycle": self.action_is_cycle,
            "correction_identity_exact": self.correction_identity_exact,
            "exact": self.exact,
            "bottom_matter_determinant_pairing_available": False,
            "holomorphic_yukawa_entry_available": False,
            "extension_point_selected": False,
            "observational_inputs_used": False,
            "first_missing_input": (
                "the full local Pluecker chain map pairing two V2 matter "
                "representatives into the inverse determinant line"
            ),
        }


@cache
def first_higgs_leg_deformation() -> HiggsLegDeformationWitness:
    """Derive the `a0` Higgs correction without selecting a carrier point."""

    _action_digest, parameters, extensions = _load_forward_basis()
    if parameters != ("a0", "a1"):
        raise ValueError("the universal extension parameter basis changed")
    source = _source_zero_component(extensions[0])
    higgs = mixed_schoen_higgs_deck_action().required_full_cochain
    action = extension_higgs_action(extensions[0], higgs)
    primitive = exact_diagonal_ambient_line_primitive(
        action,
        DETERMINANT_AMBIENT_DEGREES,
        2,
    )
    correction = primitive.primitive.scale(-1)
    result = HiggsLegDeformationWitness(
        parameters[0],
        len(source.terms),
        action,
        correction,
        primitive.projection_depth,
        primitive.inclusion_depth,
        primitive.homotopy_depth,
        scalar_full_differential(action).is_zero(),
        scalar_full_differential(correction) == action.scale(-1),
    )
    if not result.exact:
        raise ValueError("the first Higgs-leg deformation lift failed")
    return result


def write_higgs_leg_deformation(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed first Higgs-leg lift certificate."""

    payload: dict[str, object] = {
        "schema": "mixed-schoen-higgs-leg-deformation-v1",
        "coefficient_field": "Q(omega)",
        **first_higgs_leg_deformation().as_record(),
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
    """Regenerate the exact first Higgs-leg deformation certificate."""

    payload = write_higgs_leg_deformation()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"action_is_cycle: {payload['action_is_cycle']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DETERMINANT_AMBIENT_DEGREES",
    "HiggsLegDeformationWitness",
    "OUTPUT",
    "extension_higgs_action",
    "first_higgs_leg_deformation",
    "write_higgs_leg_deformation",
]
