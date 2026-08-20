"""Derive the parameter-independent Higgs cohomology and Wilson projection.

Owns:
    Acyclic determinant checks, the exact derived-P1 pushdown tensor, the
    exterior-square filtration theorem, and source-scoped Higgs projection.

Depends on:
    Full-Čech line-bundle transfer, published W1/W2 pushdowns, exact P1
    cohomology, the matter artifact, and the published Wilson embedding.

Must not:
    Treat source-selected deck characters as generated chain actions, choose an
    extension point, hide a jumping locus, or fabricate Higgs cocycles.

Phase 0:
    Exact Higgs dimensions and projection are certified; full cocycles remain open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from itertools import product
from pathlib import Path

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

from .published_matter_cohomology import OUTPUT as MATTER_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_higgs_cohomology.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
SPECTRUM_ARXIV_ID = "hep-th/0512177"
SPECTRUM_SOURCE_SHA256 = (
    "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
)
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

    def basis(self, total_degree: int) -> tuple[Monomial2, ...]:
        """Return the exact base-cohomology basis in one total degree."""

        base_degree = total_degree - self.fiber_degree
        if base_degree not in (0, 1):
            return ()
        return _p1_basis(self.line_degree, base_degree)


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
    source_h1_characters: tuple[CharacterExponent, ...]

    def __post_init__(self) -> None:
        if self.determinant_one_dimensions != (0, 0, 0, 0):
            raise ValueError("det(V1) is no longer acyclic")
        if self.determinant_two_dimensions != (0, 0, 0, 0):
            raise ValueError("det(V2) is no longer acyclic")
        if self.tensor_dimensions != (0, 4, 4, 0):
            raise ValueError("the derived pushdown tensor no longer gives four Higgs classes")
        if len(set(self.source_h1_characters)) != 4:
            raise ValueError("the selected Higgs character comparison must have four classes")
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

    @staticmethod
    def _inverse(character: CharacterExponent) -> CharacterExponent:
        """Return the inverse Z3 x Z3 character."""

        return tuple((-value) % 3 for value in character)  # type: ignore[return-value]

    def projected_multiplicity(self, wilson_character: CharacterExponent) -> int:
        """Count invariant products with one declared Wilson character."""

        required = self._inverse(wilson_character)
        return self.source_h1_characters.count(required)

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
                        "basis_counts_h0_to_h3": [
                            len(term.basis(degree)) for degree in range(4)
                        ],
                    }
                    for term in self.tensor_terms
                ],
                "cohomology_h0_to_h3": list(self.tensor_dimensions),
                "exact": True,
            },
            "wedge_square": {
                "cohomology_h0_to_h3": list(self.wedge_square_dimensions),
                "all_extension_parameters": True,
                "jumping_locus": "empty",
                "h1_dimension": self.wedge_square_dimensions[1],
            },
            "deck_characters": {
                "h1_character_exponents": [
                    list(character) for character in self.source_h1_characters
                ],
                "status": "SELECTED",
                "source_bound": True,
                "generated_from_current_tensor_chain": False,
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
                "character_input_status": "SELECTED",
            },
            "arbitrary_extension_point_selected": False,
            "full_higgs_cech_representatives_computed": False,
            "next_required_object": (
                "a synchronized monoidal Cech tensor action producing the four "
                "Higgs representatives and their deck characters"
            ),
            "status": (
                "exact all-parameter four-dimensional Higgs cohomology; the "
                "one-pair Wilson projection remains source-character conditional"
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
        ((0, 1), (0, 2), (1, 2), (2, 1)),
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
    "DerivedP1TensorTerm",
    "PublishedHiggsCohomology",
    "published_higgs_cohomology",
]
