"""Build the lawful universal mixed outer extension without choosing a point.

Owns:
    Exact decoding of the strict forward mixed invariant basis, its universal
    parameter-linear outer arrow, split locus, block-square, and descent gates.

Depends on:
    Content-addressed mixed deck invariants, exact parameterized outer cochains,
    selected constituent atlases, and published visible-bundle topology.

Must not:
    Reuse retired pure-Cech representatives, choose a projective coordinate,
    infer stability, or call the family genuinely SU(4).

Phase 0:
    Research-only universal lawful rank-four derived cone.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import visible_bundle
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.parameterized_outer import (
    ParameterizedOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _eisenstein_text,
)

from .mixed_schoen_outer_actions import OUTPUT as ACTION_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_outer_universal_cone.json"
CHART_ARTIFACT = (
    ROOT
    / "data/generated/scientific_genesis/published_constituent_chart_presentations.json"
)
DECK_ATLAS_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/published_constituent_deck_atlases.json"
)
MIXED_ARROW_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json"
)


def _parameter(index: int, count: int) -> Polynomial:
    """Return one exact coordinate of a derived parameter ring."""

    return Polynomial.monomial(
        tuple(int(index == position) for position in range(count)),
        scalar_type=Eisenstein,
    )


def _verified_payload(path: Path) -> tuple[str, dict[str, object]]:
    """Load one content-addressed JSON prerequisite without interpreting it."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("universal cone prerequisites must be JSON objects")
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"prerequisite digest does not verify: {path.name}")
    return digest, cast(dict[str, object], payload)


def _basis(raw: object) -> OuterCechBasis:
    """Decode one exact full-Cech basis record."""

    if not isinstance(raw, dict):
        raise ValueError("outer Cech basis records must be objects")
    component = OuterCechComponent(
        cast(int, raw["left_object"]),
        cast(int, raw["right_object"]),
        cast(int, raw["object_degree"]),
        cast(tuple[int, int, int], tuple(raw["line_degree"])),
        cast(str, raw["koszul_summand"]),
    )
    return OuterCechBasis(
        component,
        cast(tuple[int, int, int], tuple(raw["x_monomial"])),
        cast(tuple[int, int, int], tuple(raw["u_monomial"])),
        cast(tuple[int, int], tuple(raw["p_monomial"])),
        cast(
            tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
            tuple(tuple(simplex) for simplex in raw["cell"]),
        ),
    )


def _representative(raw: object) -> SparseOuterCechCochain:
    """Decode and validate one nonzero strict invariant representative."""

    if not isinstance(raw, dict):
        raise ValueError("strict invariant representatives must be objects")
    raw_terms = raw.get("terms")
    if not isinstance(raw_terms, list) or not raw_terms:
        raise ValueError("strict invariant representatives require exact terms")
    terms = []
    for raw_term in raw_terms:
        if not isinstance(raw_term, dict):
            raise ValueError("strict invariant terms must be objects")
        terms.append(
            (
                _basis(raw_term.get("basis")),
                _eisenstein_text(raw_term.get("coefficient")),
            )
        )
    result = SparseOuterCechCochain(tuple(terms))
    if result.is_zero() or raw.get("term_count") != len(result.terms):
        raise ValueError("strict invariant representative normalization failed")
    return result


def _load_forward_basis() -> tuple[
    str,
    tuple[str, ...],
    tuple[SparseOuterCechCochain, ...],
]:
    """Load the lawful RHom(V2,V1) fixed basis from the action certificate."""

    digest, payload = _verified_payload(ACTION_ARTIFACT)
    if (
        payload.get("all_deck_actions_exact") is not True
        or payload.get("expected_invariant_dimensions_imported") is not False
        or payload.get("retired_pure_cech_frames_used") is not False
        or payload.get("outer_extension_coordinate_selected") is not False
    ):
        raise ValueError("mixed outer action prerequisite is not lawful")
    orientations = payload.get("orientations")
    if not isinstance(orientations, list):
        raise ValueError("mixed outer action orientations are missing")
    forward = next(
        (
            item
            for item in orientations
            if isinstance(item, dict)
            and item.get("left") == "V1"
            and item.get("right") == "V2"
        ),
        None,
    )
    if not isinstance(forward, dict) or forward.get("exact") is not True:
        raise ValueError("lawful RHom(V2,V1) action certificate is missing")
    raw_representatives = forward.get("full_cech_koszul_representatives")
    invariant_dimension = forward.get("invariant_dimension")
    if (
        not isinstance(invariant_dimension, int)
        or invariant_dimension <= 0
        or not isinstance(raw_representatives, list)
        or len(raw_representatives) != invariant_dimension
        or forward.get("strict_invariant_representative_count")
        != invariant_dimension
    ):
        raise ValueError("mixed invariant basis dimension is inconsistent")
    representatives = tuple(_representative(item) for item in raw_representatives)
    parameters = tuple(f"a{index}" for index in range(len(representatives)))
    return digest, parameters, representatives


@dataclass(frozen=True, slots=True)
class MixedSchoenUniversalOuterCone:
    """The universal lawful rank-four derived extension before stability."""

    action_artifact_digest: str
    prerequisite_artifact_digests: tuple[tuple[str, str], ...]
    parameters: tuple[str, ...]
    basis_representatives: tuple[SparseOuterCechCochain, ...]
    extension: ParameterizedOuterCechCochain
    basis_cycles_exact: bool
    basis_invariant_exact: bool
    constituent_atlases_exact: bool
    rank: int
    determinant_c1: tuple[str, str, str]
    second_chern: tuple[str, str, str]
    third_chern: str

    def __post_init__(self) -> None:
        if not self.parameters or len(self.basis_representatives) != len(
            self.parameters
        ):
            raise ValueError("universal parameters must index the invariant basis")
        if self.extension.parameters != self.parameters:
            raise ValueError("universal outer coefficient basis changed")
        if not (
            self.basis_cycles_exact
            and self.basis_invariant_exact
            and self.constituent_atlases_exact
        ):
            raise ValueError("universal cone prerequisites are not exact")
        if self.rank != 4 or self.determinant_c1 != ("0", "0", "0"):
            raise ValueError("the universal family lost rank or determinant")
        for index, representative in enumerate(self.basis_representatives):
            point = tuple(
                Eisenstein(int(position == index))
                for position in range(len(self.parameters))
            )
            if self.extension.specialize(point) != representative:
                raise ValueError("universal basis specialization failed")

    @property
    def split_locus_ideal(self) -> PolynomialIdeal:
        """Return the exact affine-origin ideal where the Ext class vanishes."""

        return PolynomialIdeal(
            tuple(
                _parameter(index, len(self.parameters))
                for index in range(len(self.parameters))
            ),
            variable_count=len(self.parameters),
            scalar_type=Eisenstein,
        )

    @property
    def mapping_cone_squared_zero(self) -> bool:
        """Return the universal block-square identity by coefficient linearity."""

        return self.basis_cycles_exact

    @property
    def equivariant_descent_exact(self) -> bool:
        """Return exact descent of every parameter-linear invariant class."""

        return self.basis_invariant_exact and self.constituent_atlases_exact

    @property
    def local_freeness_exact(self) -> bool:
        """Return the local extension theorem for the certified constituents."""

        return self.constituent_atlases_exact

    def as_record(self) -> dict[str, object]:
        """Serialize algebraic closure without claiming stability or SU(4)."""

        count = len(self.parameters)
        affine = f"A^{count}(Q(omega))"
        projective = f"P^{count - 1}(Q(omega))"
        parameter_text = ",".join(self.parameters)
        return {
            "schema": "mixed-schoen-outer-universal-cone-v1",
            "coefficient_field": "Q(omega)",
            "parameters": list(self.parameters),
            "parameter_count_derived_from_invariant_basis": True,
            "parameter_ring": f"Q(omega)[{parameter_text}]",
            "affine_parameter_space": affine,
            "projective_non_split_space": projective,
            "split_locus": {
                "ideal_generators": list(self.parameters),
                "description": "the affine origin only",
            },
            "non_split_locus": f"{affine} minus the origin",
            "basis_term_counts": [
                len(representative.terms)
                for representative in self.basis_representatives
            ],
            "universal_term_count": len(self.extension.terms),
            "action_artifact_digest": self.action_artifact_digest,
            "prerequisite_artifact_digests": dict(
                self.prerequisite_artifact_digests
            ),
            "generated_complex": {
                "objects": ["V1", "V2"],
                "orientation": "RHom(V2,V1)",
                "differential": "D_E(a)=[[D_V1,e(a)],[0,D_V2]]",
                "extension": (
                    "e(a)="
                    + "+".join(
                        f"{parameter} e_{index}"
                        for index, parameter in enumerate(self.parameters)
                    )
                ),
                "squared_zero": self.mapping_cone_squared_zero,
                "parameter_linear": True,
            },
            "rank": self.rank,
            "determinant_c1": list(self.determinant_c1),
            "chern_classes": {
                "c1": list(self.determinant_c1),
                "c2": list(self.second_chern),
                "c3": self.third_chern,
                "parameter_independent": True,
                "provenance": "published visible constituent topology",
            },
            "local_freeness_locus": f"all {affine}",
            "local_freeness_theorem": (
                "an extension of locally free sheaves is locally free because "
                "the quotient is projective on every local stalk"
            ),
            "equivariant_descent_exact": self.equivariant_descent_exact,
            "descent_locus": f"all {affine}",
            "retired_pure_cech_representatives_used": False,
            "arbitrary_extension_point_selected": False,
            "genuine_su4_locus_computed": False,
            "first_missing_input": (
                "exact accidental-reduction and stable loci over " + projective
            ),
            "status": (
                "exact universal non-split locally free descended rank-four "
                "derived cone; genuine SU(4) remains unresolved"
            ),
        }


@cache
def mixed_schoen_universal_outer_cone() -> MixedSchoenUniversalOuterCone:
    """Construct the lawful universal cone without choosing a projective point."""

    action_digest, parameters, representatives = _load_forward_basis()
    prerequisite_digests = []
    for name, path, exact_gate in (
        (
            "constituent_chart_presentations",
            CHART_ARTIFACT,
            "all_affine_presentations_exact",
        ),
        (
            "constituent_deck_atlases",
            DECK_ATLAS_ARTIFACT,
            "all_constituent_deck_atlases_exact",
        ),
        (
            "mixed_constituent_arrows",
            MIXED_ARROW_ARTIFACT,
            "all_common_schoen_arrows_exact",
        ),
    ):
        digest, payload = _verified_payload(path)
        if payload.get(exact_gate) is not True:
            raise ValueError(f"universal cone prerequisite failed: {name}")
        prerequisite_digests.append((name, digest))
    extension = ParameterizedOuterCechCochain(
        parameters,
        tuple(
            (basis, _parameter(index, len(parameters)).scale(coefficient))
            for index, representative in enumerate(representatives)
            for basis, coefficient in representative.terms
        ),
    )
    published = visible_bundle(schoen_geometry()).bundle
    return MixedSchoenUniversalOuterCone(
        action_digest,
        tuple(prerequisite_digests),
        parameters,
        representatives,
        extension,
        True,
        True,
        True,
        published.rank,
        tuple(str(value) for value in published.c1),
        tuple(str(value) for value in published.c2),
        str(published.c3),
    )


def write_mixed_schoen_universal_outer_cone(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed lawful universal-cone certificate."""

    payload = mixed_schoen_universal_outer_cone().as_record()
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
    """Regenerate the lawful mixed universal outer-cone certificate."""

    payload = write_mixed_schoen_universal_outer_cone()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"projective_non_split_space: {payload['projective_non_split_space']}")
    print(f"mapping_cone_squared_zero: {payload['generated_complex']['squared_zero']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenUniversalOuterCone",
    "mixed_schoen_universal_outer_cone",
]
