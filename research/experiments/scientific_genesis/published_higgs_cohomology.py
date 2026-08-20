"""Derive the parameter-independent Higgs cohomology and Wilson projection.

Owns:
    Acyclic determinant checks, the exact derived-P1 pushdown tensor, the
    exterior-square filtration theorem, and generated base-Cech deck action.

Depends on:
    Full-Čech line-bundle transfer, published W1/W2 pushdowns, exact P1
    cohomology, the matter artifact, and the published Wilson embedding.

Must not:
    Use source character comparisons as construction input, choose an extension
    point, hide a jumping locus, or claim a full Schoen cocycle lift.

Phase 0:
    Exact Higgs dimensions and base-Cech projection are certified; full lifts are open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from itertools import product
from pathlib import Path

from onetheory.math.cech import projective_monomial_cech_complex
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pushdown import (
    P1PushdownConstraint,
    P1Summand,
    tier_a_pushdown_constraints,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    SchoenSerreConstituent,
    SerreObject,
    schoen_unit_constituent,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    TransferredOuterHom,
    transferred_schoen_serre_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    _inverse_images,
    _monomial_action,
    schoen_sparse_deck_actions,
)

from .published_matter_cohomology import OUTPUT as MATTER_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_higgs_cohomology.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
SPECTRUM_ARXIV_ID = "hep-th/0512177"
SPECTRUM_SOURCE_SHA256 = (
    "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
)
SOURCE_H1_CHARACTERS = ((0, 1), (0, 2), (1, 2), (2, 1))
Monomial2 = tuple[int, int]
CharacterExponent = tuple[int, int]


def _artifact_digest(path: Path, expected_key: str, expected_value: object) -> str:
    """Validate one content-addressed upstream artifact."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest does not verify: {path.name}")
    if payload.get(expected_key) != expected_value:
        raise ValueError(f"upstream artifact gate changed: {path.name}")
    return digest


def _source_digest() -> str:
    """Validate the selected one-Higgs spectrum source."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the published source manifest lacks source records")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == SPECTRUM_ARXIV_ID
    ]
    if len(matches) != 1:
        raise ValueError("the Higgs spectrum source must occur exactly once")
    if matches[0].get("source_archive_sha256") != SPECTRUM_SOURCE_SHA256:
        raise ValueError("the Higgs spectrum source archive digest changed")
    return SPECTRUM_SOURCE_SHA256


def _p1_basis(degree: int, cohomology_degree: int) -> tuple[Monomial2, ...]:
    """Return exact Laurent-monomial bases for P1 line cohomology."""

    if cohomology_degree == 0 and degree >= 0:
        return tuple(
            exponents
            for exponents in product(range(degree + 1), repeat=2)
            if sum(exponents) == degree
        )
    if cohomology_degree == 1 and degree <= -2:
        return tuple(
            exponents
            for exponents in product(range(degree, 0), repeat=2)
            if sum(exponents) == degree
        )
    return ()


def _line_constituent(
    name: str,
    degree: tuple[int, int, int],
) -> SchoenSerreConstituent:
    """Represent one line bundle as a one-object Schoen complex."""

    return SchoenSerreConstituent(
        name,
        0,
        degree,
        None,
        (SerreObject(name, 0, degree),),
        (),
    )


def _line_dimensions(transferred: TransferredOuterHom) -> tuple[int, int, int, int]:
    """Return geometric cohomology dimensions zero through three."""

    available = {degree for degree, _ in transferred.reduced.total_spaces}
    return tuple(
        transferred.cohomology_dimension(degree) if degree in available else 0
        for degree in range(4)
    )  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class DerivedP1TensorTerm:
    """One exact summand in the derived tensor of two P1 pushdowns."""

    first_label: str
    second_label: str
    fiber_degree: int
    line_degree: int
    scalar_character: tuple[Eisenstein, Eisenstein]

    def basis(self, total_degree: int) -> tuple[Monomial2, ...]:
        """Return the exact base-cohomology basis in one total degree."""

        base_degree = total_degree - self.fiber_degree
        if base_degree not in (0, 1):
            return ()
        return _p1_basis(self.line_degree, base_degree)


@dataclass(frozen=True, slots=True)
class DerivedP1CechRepresentative:
    """One canonical monomial Čech class in the derived pushdown tensor."""

    term_index: int
    total_degree: int
    base_degree: int
    monomial: Monomial2
    cells: tuple[tuple[tuple[int, ...], Eisenstein], ...]

    def __post_init__(self) -> None:
        cech = projective_monomial_cech_complex(
            ("p0", "p1"),
            self.monomial,
            scalar_type=Eisenstein,
        )
        if cech.expected_cohomology_degree != self.base_degree:
            raise ValueError("derived P1 representative has the wrong Čech degree")
        canonical_cells = tuple(
            (simplex.vertices, Eisenstein(1))
            for simplex in cech.simplices_at(self.base_degree)
        )
        if self.cells != canonical_cells:
            raise ValueError("derived P1 representative is not the canonical cocycle")


def _summands(
    constraint: P1PushdownConstraint,
) -> tuple[tuple[int, P1Summand], ...]:
    """Return direct and higher images with their derived degrees."""

    return tuple((0, item) for item in constraint.direct_terms) + tuple(
        (1, item) for item in constraint.higher_terms
    )


def _derived_tensor_terms(
    first: P1PushdownConstraint,
    second: P1PushdownConstraint,
) -> tuple[DerivedP1TensorTerm, ...]:
    """Tensor exact locally free direct-image summands over the common P1."""

    terms = []
    for first_degree, first_term in _summands(first):
        for second_degree, second_term in _summands(second):
            if first_term.degree is None or second_term.degree is None:
                raise ValueError("the published W1/W2 pushdowns must be locally free")
            terms.append(
                DerivedP1TensorTerm(
                    first_term.label,
                    second_term.label,
                    first_degree + second_degree,
                    first_term.degree + second_term.degree,
                    (
                        first_term.character[0] * second_term.character[0],
                        first_term.character[1] * second_term.character[1],
                    ),
                )
            )
    return tuple(terms)


@dataclass(frozen=True, slots=True)
class PublishedHiggsCohomology:
    """Exact all-parameter Higgs dimensions with scoped character provenance."""

    matter_artifact_digest: str
    source_archive_sha256: str
    determinant_one: TransferredOuterHom
    determinant_two: TransferredOuterHom
    tensor_terms: tuple[DerivedP1TensorTerm, ...]

    def __post_init__(self) -> None:
        if self.determinant_one_dimensions != (0, 0, 0, 0):
            raise ValueError("det(V1) is no longer acyclic")
        if self.determinant_two_dimensions != (0, 0, 0, 0):
            raise ValueError("det(V2) is no longer acyclic")
        if self.tensor_dimensions != (0, 4, 4, 0):
            raise ValueError("the derived pushdown tensor no longer gives four Higgs classes")
        if self.generated_h1_characters != SOURCE_H1_CHARACTERS:
            raise ValueError("generated Higgs characters disagree with the source comparison")
        if not self.p1_group_relations:
            raise ValueError("derived P1 deck actions do not realize Z3 x Z3")
        if self.source_archive_sha256 != SPECTRUM_SOURCE_SHA256:
            raise ValueError("the Higgs source digest changed")

    @property
    def determinant_one_dimensions(self) -> tuple[int, int, int, int]:
        """Return H*(det V1) from the full Čech line transfer."""

        return _line_dimensions(self.determinant_one)

    @property
    def determinant_two_dimensions(self) -> tuple[int, int, int, int]:
        """Return H*(det V2) from the full Čech line transfer."""

        return _line_dimensions(self.determinant_two)

    @property
    def tensor_dimensions(self) -> tuple[int, int, int, int]:
        """Return H*(V1 tensor V2) from its exact derived pushdown terms."""

        return tuple(
            sum(len(term.basis(degree)) for term in self.tensor_terms)
            for degree in range(4)
        )  # type: ignore[return-value]

    @property
    def wedge_square_dimensions(self) -> tuple[int, int, int, int]:
        """Return H*(wedge2 V(a)) through the acyclic determinant filtration."""

        return self.tensor_dimensions

    def p1_cech_representatives(
        self,
        total_degree: int,
    ) -> tuple[DerivedP1CechRepresentative, ...]:
        """Return canonical exact Čech representatives in one derived degree."""

        representatives = []
        for term_index, term in enumerate(self.tensor_terms):
            base_degree = total_degree - term.fiber_degree
            if base_degree not in (0, 1):
                continue
            for monomial in term.basis(total_degree):
                cech = projective_monomial_cech_complex(
                    ("p0", "p1"),
                    monomial,
                    scalar_type=Eisenstein,
                )
                representatives.append(
                    DerivedP1CechRepresentative(
                        term_index,
                        total_degree,
                        base_degree,
                        monomial,
                        tuple(
                            (simplex.vertices, Eisenstein(1))
                            for simplex in cech.simplices_at(base_degree)
                        ),
                    )
                )
        return tuple(representatives)

    @staticmethod
    def _orientation_sign(images: tuple[tuple[Eisenstein, tuple[int, ...]], ...]) -> int:
        """Return the oriented top-simplex sign of a monomial pullback."""

        permutation = tuple(exponents.index(1) for _, exponents in images)
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(len(permutation))
            for right in range(left + 1, len(permutation))
        )
        return -1 if inversions % 2 else 1

    def p1_action_matrix(self, generator: str, total_degree: int = 1) -> Matrix:
        """Generate one deck action by inverse pullback on P1 Čech cocycles."""

        actions = {action.name: action for action in schoen_sparse_deck_actions()}
        if generator not in actions:
            raise KeyError(generator)
        action = actions[generator]
        inverse_images = _inverse_images(action.p_images)
        representatives = self.p1_cech_representatives(total_degree)
        indices = {
            (representative.term_index, representative.monomial): index
            for index, representative in enumerate(representatives)
        }
        rows = [
            [Eisenstein(0) for _ in representatives]
            for _ in representatives
        ]
        character_index = {"P": 0, "T": 1}[generator]
        for column, representative in enumerate(representatives):
            scalar, target_monomial = _monomial_action(
                representative.monomial,
                inverse_images,
            )
            if representative.base_degree == 1:
                scalar *= self._orientation_sign(inverse_images)
            term = self.tensor_terms[representative.term_index]
            scalar *= term.scalar_character[character_index]
            target = indices.get((representative.term_index, target_monomial))
            if target is None:
                raise ValueError("deck pullback escaped the derived P1 Čech basis")
            rows[target][column] = scalar
        return Matrix(tuple(tuple(row) for row in rows), scalar_type=Eisenstein)

    @property
    def p1_group_relations(self) -> bool:
        """Return exact order-three and commutation gates on derived H1."""

        p = self.p1_action_matrix("P")
        t = self.p1_action_matrix("T")
        identity = Matrix.identity(p.row_count, scalar_type=Eisenstein)
        return (
            p @ p @ p == identity
            and t @ t @ t == identity
            and p @ t == t @ p
        )

    @property
    def h1_character_multiplicities(
        self,
    ) -> tuple[tuple[CharacterExponent, int], ...]:
        """Derive the joint character decomposition of the P1 Čech classes."""

        p = self.p1_action_matrix("P")
        t = self.p1_action_matrix("T")
        identity = Matrix.identity(p.row_count, scalar_type=Eisenstein)
        roots = (Eisenstein(1), OMEGA, OMEGA2)
        multiplicities = []
        for first, second in product(range(3), repeat=2):
            equations = Matrix(
                (
                    *((p - identity.scale(roots[first])).rows),
                    *((t - identity.scale(roots[second])).rows),
                ),
                scalar_type=Eisenstein,
            )
            dimension = len(equations.nullspace())
            if dimension:
                multiplicities.append(((first, second), dimension))
        if sum(value for _, value in multiplicities) != p.row_count:
            raise ValueError("derived P1 deck characters do not span H1")
        return tuple(multiplicities)

    @property
    def generated_h1_characters(self) -> tuple[CharacterExponent, ...]:
        """Expand the exact generated character multiplicities deterministically."""

        return tuple(
            character
            for character, multiplicity in self.h1_character_multiplicities
            for _ in range(multiplicity)
        )

    @staticmethod
    def _inverse(character: CharacterExponent) -> CharacterExponent:
        """Return the inverse Z3 x Z3 character."""

        return tuple((-value) % 3 for value in character)  # type: ignore[return-value]

    def projected_multiplicity(self, wilson_character: CharacterExponent) -> int:
        """Count invariant products with one declared Wilson character."""

        required = self._inverse(wilson_character)
        return self.generated_h1_characters.count(required)

    def as_record(self) -> dict[str, object]:
        """Serialize exact dimensions and preserve the chain-character boundary."""

        projections = {
            "up_higgs_doublet": self.projected_multiplicity((0, 2)),
            "color_triplet": self.projected_multiplicity((2, 2)),
            "down_higgs_doublet": self.projected_multiplicity((0, 1)),
            "color_antitriplet": self.projected_multiplicity((1, 1)),
        }
        return {
            "schema": "published-higgs-cohomology-v1",
            "coefficient_field": "Q(omega)",
            "matter_artifact_digest": self.matter_artifact_digest,
            "source": {
                "arxiv_id": SPECTRUM_ARXIV_ID,
                "version": "v3",
                "source_archive_sha256": self.source_archive_sha256,
                "dimension_comparison_locator": "eq:10",
                "character_comparison_locator": "eq:17",
                "wilson_locator": "eq:19",
                "published_dimensions_used_as_rank_inputs": False,
            },
            "determinant_filtration": {
                "det_v1_line_degree": [-2, 2, 0],
                "det_v1_cohomology_h0_to_h3": list(
                    self.determinant_one_dimensions
                ),
                "det_v2_line_degree": [2, -2, 0],
                "det_v2_cohomology_h0_to_h3": list(
                    self.determinant_two_dimensions
                ),
                "both_acyclic_from_full_cech_transfer": True,
                "consequence": (
                    "H*(wedge^2 V(a)) is isomorphic to H*(V1 tensor V2) "
                    "for every outer extension parameter"
                ),
            },
            "derived_pushdown_tensor": {
                "base": "P1",
                "term_count": len(self.tensor_terms),
                "terms": [
                    {
                        "first": term.first_label,
                        "second": term.second_label,
                        "fiber_degree": term.fiber_degree,
                        "line_degree": term.line_degree,
                        "scalar_character": [
                            str(value) for value in term.scalar_character
                        ],
                        "basis_counts_h0_to_h3": [
                            len(term.basis(degree)) for degree in range(4)
                        ],
                    }
                    for term in self.tensor_terms
                ],
                "cohomology_h0_to_h3": list(self.tensor_dimensions),
                "exact": True,
            },
            "derived_p1_cech": {
                "h1_representatives": [
                    {
                        "term_index": representative.term_index,
                        "base_degree": representative.base_degree,
                        "monomial": list(representative.monomial),
                        "cells": [
                            {
                                "simplex": list(cell),
                                "coefficient": str(coefficient),
                            }
                            for cell, coefficient in representative.cells
                        ],
                    }
                    for representative in self.p1_cech_representatives(1)
                ],
                "P_action": [
                    [str(value) for value in row]
                    for row in self.p1_action_matrix("P").rows
                ],
                "T_action": [
                    [str(value) for value in row]
                    for row in self.p1_action_matrix("T").rows
                ],
                "inverse_pullback_convention_explicit": True,
                "group_relations": self.p1_group_relations,
            },
            "wedge_square": {
                "cohomology_h0_to_h3": list(self.wedge_square_dimensions),
                "all_extension_parameters": True,
                "jumping_locus": "empty",
                "h1_dimension": self.wedge_square_dimensions[1],
            },
            "deck_characters": {
                "h1_character_exponents": [
                    list(character) for character in self.generated_h1_characters
                ],
                "multiplicities": [
                    {
                        "character_exponents": list(character),
                        "multiplicity": multiplicity,
                    }
                    for character, multiplicity in self.h1_character_multiplicities
                ],
                "status": "COMPUTED",
                "source_bound_pushdown_inputs": True,
                "generated_from_derived_p1_cech_action": True,
                "matches_source_comparison": True,
            },
            "wilson_projection": {
                "multiplicities": projections,
                "higgs_pairs": min(
                    projections["up_higgs_doublet"],
                    projections["down_higgs_doublet"],
                ),
                "massless_color_triplets": (
                    projections["color_triplet"]
                    + projections["color_antitriplet"]
                ),
                "character_arithmetic_exact": True,
                "character_input_status": "COMPUTED_FROM_SELECTED_PUSHDOWNS",
            },
            "arbitrary_extension_point_selected": False,
            "derived_p1_cech_representatives_computed": True,
            "full_higgs_cech_representatives_computed": False,
            "next_required_object": (
                "a synchronized lift of the four derived-P1 representatives "
                "into the full Schoen Cech complex"
            ),
            "status": (
                "exact all-parameter four-dimensional Higgs cohomology and "
                "generated one-pair Wilson projection from selected pushdowns"
            ),
        }


@cache
def published_higgs_cohomology() -> PublishedHiggsCohomology:
    """Construct the exact determinant filtration and derived pushdown tensor."""

    unit = schoen_unit_constituent()
    first, second = tier_a_pushdown_constraints()
    return PublishedHiggsCohomology(
        _artifact_digest(MATTER_ARTIFACT, "schema", "published-matter-cohomology-v1"),
        _source_digest(),
        transferred_schoen_serre_outer_hom(
            _line_constituent("det(V1)", (-2, 2, 0)),
            unit,
        ),
        transferred_schoen_serre_outer_hom(
            _line_constituent("det(V2)", (2, -2, 0)),
            unit,
        ),
        _derived_tensor_terms(first, second),
    )


def write_published_higgs_cohomology(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed Higgs-cohomology certificate."""

    payload = published_higgs_cohomology().as_record()
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
    """Regenerate the exact all-parameter Higgs artifact."""

    payload = write_published_higgs_cohomology()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"wedge_square: {payload['wedge_square']}")
    print(f"wilson_projection: {payload['wilson_projection']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DerivedP1CechRepresentative",
    "DerivedP1TensorTerm",
    "PublishedHiggsCohomology",
    "published_higgs_cohomology",
]
