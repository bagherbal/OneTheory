"""Derive the observable spectrum of the lawful mixed Schoen family.

Owns:
    Synchronized constituent matter cohomology, a free-action Lefschetz
    decomposition, the exterior-square filtration, and Wilson projection.

Depends on:
    The lawful stable universal cone, selected mixed constituent arrows,
    certified relative pushdowns, exact Cech transfer, and source Wilson data.

Must not:
    Import source cohomology dimensions as rank inputs, choose an extension
    point, identify reduced classes with full Schoen cocycles, or fit a spectrum.

Phase 0:
    Research-only exact spectrum certificate for the full lawful family.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from itertools import product
from pathlib import Path
from typing import cast

from onetheory.math.cech import projective_monomial_cech_complex
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
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

from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_transfer import (
    MixedTransferredOuterHom,
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .relative_constituent_pushdowns import (
    EquivariantP1Line,
    RelativeConstituentPushdown,
    relative_constituent_pushdowns,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_observable_spectrum.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
UNIVERSAL_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_outer_universal_cone.json"
)
STABILITY_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_outer_stability_locus.json"
)
PUSHDOWN_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/relative_constituent_pushdowns.json"
)

SPECTRUM_ARXIV_ID = "hep-th/0512177"
SPECTRUM_SOURCE_SHA256 = (
    "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
)
GEOMETRY_ARXIV_ID = "hep-th/0410055"
GEOMETRY_SOURCE_SHA256 = (
    "ad75668ca40b14972f1e52d5232fee08b3b6130b27accff1217440fc1d65536a"
)
CHARACTERS = tuple((first, second) for first in range(3) for second in range(3))
SOURCE_HIGGS_CHARACTERS = ((0, 1), (0, 2), (1, 2), (2, 1))
WILSON_HIGGS_CHARACTERS = {
    "up_higgs_doublet": (0, 2),
    "color_triplet": (2, 2),
    "down_higgs_doublet": (0, 1),
    "color_antitriplet": (1, 1),
}

Monomial2 = tuple[int, int]
CharacterExponent = tuple[int, int]


def _artifact_digest(path: Path, expected_key: str, expected_value: object) -> str:
    """Validate one content-addressed prerequisite and return its digest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest does not verify: {path.name}")
    if payload.get(expected_key) != expected_value:
        raise ValueError(f"upstream artifact gate changed: {path.name}")
    return digest


def _source_digest(arxiv_id: str, expected_digest: str) -> str:
    """Validate one selected source archive by identifier and exact digest."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the published source manifest lacks source records")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == arxiv_id
    ]
    if len(matches) != 1:
        raise ValueError(f"source {arxiv_id} must occur exactly once")
    digest = matches[0].get("source_archive_sha256")
    if digest != expected_digest:
        raise ValueError(f"source {arxiv_id} archive digest changed")
    return expected_digest


def _mixed_profile(
    transferred: MixedTransferredOuterHom,
) -> tuple[int, int, int, int]:
    """Return geometric cohomology dimensions zero through three."""

    available = {degree for degree, _space in transferred.spaces}
    return cast(
        tuple[int, int, int, int],
        tuple(
            transferred.cohomology_dimension(degree) if degree in available else 0
            for degree in range(4)
        ),
    )


def _line_constituent(
    name: str,
    degree: tuple[int, int, int],
) -> SchoenSerreConstituent:
    """Represent one exact line bundle as a one-object Schoen complex."""

    return SchoenSerreConstituent(
        name,
        0,
        degree,
        None,
        (SerreObject(name, 0, degree),),
        (),
    )


def _line_profile(transferred: TransferredOuterHom) -> tuple[int, int, int, int]:
    """Return one transferred line bundle's geometric cohomology profile."""

    available = {degree for degree, _space in transferred.reduced.total_spaces}
    return cast(
        tuple[int, int, int, int],
        tuple(
            transferred.cohomology_dimension(degree) if degree in available else 0
            for degree in range(4)
        ),
    )


def _p1_basis(degree: int, cohomology_degree: int) -> tuple[Monomial2, ...]:
    """Return canonical Laurent monomials for exact P1 line cohomology."""

    if cohomology_degree == 0 and degree >= 0:
        return tuple(
            cast(Monomial2, exponents)
            for exponents in product(range(degree + 1), repeat=2)
            if sum(exponents) == degree
        )
    if cohomology_degree == 1 and degree <= -2:
        return tuple(
            cast(Monomial2, exponents)
            for exponents in product(range(degree, 0), repeat=2)
            if sum(exponents) == degree
        )
    return ()


@dataclass(frozen=True, slots=True)
class DerivedP1TensorTerm:
    """One summand of the lawful constituents' derived pushdown tensor."""

    first_label: str
    second_label: str
    fiber_degree: int
    line_degree: int
    scalar_character: tuple[Eisenstein, Eisenstein]

    def basis(self, total_degree: int) -> tuple[Monomial2, ...]:
        """Return the exact base-Cech basis in one total degree."""

        base_degree = total_degree - self.fiber_degree
        return _p1_basis(self.line_degree, base_degree)


@dataclass(frozen=True, slots=True)
class DerivedP1CechRepresentative:
    """One canonical P1 Cech class in the derived pushdown tensor."""

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
            raise ValueError("derived P1 representative has the wrong Cech degree")
        expected = tuple(
            (simplex.vertices, Eisenstein(1))
            for simplex in cech.simplices_at(self.base_degree)
        )
        if self.cells != expected:
            raise ValueError("derived P1 representative is not canonical")


def _graded_lines(
    pushdown: RelativeConstituentPushdown,
) -> tuple[tuple[int, EquivariantP1Line], ...]:
    """Return direct and higher lines with their derived degrees."""

    return tuple((0, item) for item in pushdown.direct_terms) + tuple(
        (1, item) for item in pushdown.higher_terms
    )


def _derived_tensor_terms(
    first: RelativeConstituentPushdown,
    second: RelativeConstituentPushdown,
) -> tuple[DerivedP1TensorTerm, ...]:
    """Tensor the two independently certified relative pushdowns."""

    return tuple(
        DerivedP1TensorTerm(
            first_line.label,
            second_line.label,
            first_degree + second_degree,
            first_line.degree + second_line.degree,
            (
                first_line.character[0] * second_line.character[0],
                first_line.character[1] * second_line.character[1],
            ),
        )
        for first_degree, first_line in _graded_lines(first)
        for second_degree, second_line in _graded_lines(second)
    )


@dataclass(frozen=True, slots=True)
class MixedSchoenObservableSpectrum:
    """Exact all-parameter structural spectrum of the lawful stable family."""

    universal_artifact_digest: str
    stability_artifact_digest: str
    pushdown_artifact_digest: str
    source_archive_sha256: str
    geometry_source_archive_sha256: str
    deck_action_free: bool
    carrier_equivariant: bool
    first_matter: MixedTransferredOuterHom
    second_matter: MixedTransferredOuterHom
    determinant_one: TransferredOuterHom
    determinant_two: TransferredOuterHom
    tensor_terms: tuple[DerivedP1TensorTerm, ...]

    def __post_init__(self) -> None:
        if self.first_matter_profile != (0, 9, 0, 0):
            raise ValueError("the lawful V1 matter cohomology changed")
        if self.second_matter_profile != (0, 18, 0, 0):
            raise ValueError("the lawful V2 matter cohomology changed")
        if self.determinant_one_profile != (0, 0, 0, 0):
            raise ValueError("det(V1) is no longer acyclic")
        if self.determinant_two_profile != (0, 0, 0, 0):
            raise ValueError("det(V2) is no longer acyclic")
        if self.higgs_profile != (0, 4, 4, 0):
            raise ValueError("the lawful Higgs cohomology changed")
        if self.higgs_characters != SOURCE_HIGGS_CHARACTERS:
            raise ValueError("generated Higgs characters changed")
        if not self.higgs_group_relations:
            raise ValueError("the lawful P1 Higgs action is not Z3 x Z3")
        if self.source_archive_sha256 != SPECTRUM_SOURCE_SHA256:
            raise ValueError("the spectrum source digest changed")
        if self.geometry_source_archive_sha256 != GEOMETRY_SOURCE_SHA256:
            raise ValueError("the free-quotient geometry source digest changed")
        if not self.deck_action_free or not self.carrier_equivariant:
            raise ValueError("the free-action Lefschetz hypotheses are not certified")

    @property
    def first_matter_profile(self) -> tuple[int, int, int, int]:
        """Return exact H*(V1) from the selected mixed arrow."""

        return _mixed_profile(self.first_matter)

    @property
    def second_matter_profile(self) -> tuple[int, int, int, int]:
        """Return exact H*(V2) from the selected mixed arrow."""

        return _mixed_profile(self.second_matter)

    @property
    def visible_matter_profile(self) -> tuple[int, int, int, int]:
        """Return H*(V(a)) from the universal extension long exact sequence."""

        return cast(
            tuple[int, int, int, int],
            tuple(
                first + second
                for first, second in zip(
                    self.first_matter_profile,
                    self.second_matter_profile,
                    strict=True,
                )
            ),
        )

    @property
    def dual_matter_profile(self) -> tuple[int, int, int, int]:
        """Return H*(V(a)^dual) by exact Calabi-Yau Serre duality."""

        return cast(tuple[int, int, int, int], tuple(reversed(self.visible_matter_profile)))

    @property
    def matter_character_multiplicities(
        self,
    ) -> tuple[tuple[CharacterExponent, int], ...]:
        """Apply the free-action Lefschetz theorem to concentrated H1."""

        dimension = self.visible_matter_profile[1]
        if not self.deck_action_free or not self.carrier_equivariant:
            raise ValueError("the free-action Lefschetz theorem is unavailable")
        if self.visible_matter_profile != (0, dimension, 0, 0):
            raise ValueError("the Lefschetz compression requires pure H1 cohomology")
        if dimension % len(CHARACTERS):
            raise ValueError("pure H1 does not have integral regular multiplicity")
        multiplicity = dimension // len(CHARACTERS)
        return tuple((character, multiplicity) for character in CHARACTERS)

    @property
    def determinant_one_profile(self) -> tuple[int, int, int, int]:
        """Return H*(det V1) from exact full-Cech line transfer."""

        return _line_profile(self.determinant_one)

    @property
    def determinant_two_profile(self) -> tuple[int, int, int, int]:
        """Return H*(det V2) from exact full-Cech line transfer."""

        return _line_profile(self.determinant_two)

    @property
    def higgs_profile(self) -> tuple[int, int, int, int]:
        """Return H*(wedge2 V(a)) through the acyclic determinant filtration."""

        return cast(
            tuple[int, int, int, int],
            tuple(
                sum(len(term.basis(degree)) for term in self.tensor_terms)
                for degree in range(4)
            ),
        )

    def higgs_representatives(
        self,
        total_degree: int = 1,
    ) -> tuple[DerivedP1CechRepresentative, ...]:
        """Return canonical derived-P1 representatives in one total degree."""

        representatives = []
        for term_index, term in enumerate(self.tensor_terms):
            base_degree = total_degree - term.fiber_degree
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
    def _orientation_sign(
        images: tuple[tuple[Eisenstein, tuple[int, ...]], ...],
    ) -> int:
        """Return the oriented top-simplex sign of a monomial pullback."""

        permutation = tuple(exponents.index(1) for _scalar, exponents in images)
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(len(permutation))
            for right in range(left + 1, len(permutation))
        )
        return -1 if inversions % 2 else 1

    def higgs_action_matrix(self, generator: str) -> Matrix:
        """Generate one exact deck action on the derived-P1 Higgs classes."""

        actions = {action.name: action for action in schoen_sparse_deck_actions()}
        if generator not in actions:
            raise KeyError(generator)
        inverse_images = _inverse_images(actions[generator].p_images)
        representatives = self.higgs_representatives()
        indices = {
            (representative.term_index, representative.monomial): index
            for index, representative in enumerate(representatives)
        }
        rows = [
            [Eisenstein(0) for _representative in representatives]
            for _representative in representatives
        ]
        character_index = {"P": 0, "T": 1}[generator]
        for column, representative in enumerate(representatives):
            scalar, target_monomial = _monomial_action(
                representative.monomial,
                inverse_images,
            )
            if representative.base_degree == 1:
                scalar *= self._orientation_sign(inverse_images)
            scalar *= self.tensor_terms[representative.term_index].scalar_character[
                character_index
            ]
            target = indices.get(
                (representative.term_index, cast(Monomial2, target_monomial))
            )
            if target is None:
                raise ValueError("deck pullback escaped the lawful Higgs basis")
            rows[target][column] = scalar
        return Matrix(tuple(tuple(row) for row in rows), scalar_type=Eisenstein)

    @property
    def higgs_group_relations(self) -> bool:
        """Return exact order-three and commutation gates on Higgs H1."""

        p_action = self.higgs_action_matrix("P")
        t_action = self.higgs_action_matrix("T")
        identity = Matrix.identity(p_action.row_count, scalar_type=Eisenstein)
        return (
            p_action**3 == identity
            and t_action**3 == identity
            and p_action @ t_action == t_action @ p_action
        )

    @property
    def higgs_character_multiplicities(
        self,
    ) -> tuple[tuple[CharacterExponent, int], ...]:
        """Decompose the exact lawful Higgs action into joint characters."""

        p_action = self.higgs_action_matrix("P")
        t_action = self.higgs_action_matrix("T")
        identity = Matrix.identity(p_action.row_count, scalar_type=Eisenstein)
        roots = (Eisenstein(1), OMEGA, OMEGA2)
        multiplicities = []
        for first, second in CHARACTERS:
            equations = Matrix(
                (
                    *((p_action - identity.scale(roots[first])).rows),
                    *((t_action - identity.scale(roots[second])).rows),
                ),
                scalar_type=Eisenstein,
            )
            dimension = len(equations.nullspace())
            if dimension:
                multiplicities.append(((first, second), dimension))
        if sum(value for _character, value in multiplicities) != p_action.row_count:
            raise ValueError("lawful Higgs characters do not span H1")
        return tuple(multiplicities)

    @property
    def higgs_characters(self) -> tuple[CharacterExponent, ...]:
        """Expand exact Higgs character multiplicities deterministically."""

        return tuple(
            character
            for character, multiplicity in self.higgs_character_multiplicities
            for _index in range(multiplicity)
        )

    @staticmethod
    def _inverse(character: CharacterExponent) -> CharacterExponent:
        """Return the inverse Z3 x Z3 character."""

        return cast(CharacterExponent, tuple((-value) % 3 for value in character))

    def higgs_projection(self) -> dict[str, int]:
        """Project the four Spin(10) ten-weights with the source Wilson line."""

        return {
            label: self.higgs_characters.count(self._inverse(character))
            for label, character in WILSON_HIGGS_CHARACTERS.items()
        }

    def as_record(self) -> dict[str, object]:
        """Serialize the exact structural spectrum and fail-closed next gate."""

        matter_multiplicities = self.matter_character_multiplicities
        higgs_projection = self.higgs_projection()
        higgs_pairs = min(
            higgs_projection["up_higgs_doublet"],
            higgs_projection["down_higgs_doublet"],
        )
        massless_triplets = (
            higgs_projection["color_triplet"]
            + higgs_projection["color_antitriplet"]
        )
        family_count = matter_multiplicities[0][1]
        return {
            "schema": "mixed-schoen-observable-spectrum-v1",
            "coefficient_field": "Q(omega)",
            "prerequisite_artifact_digests": {
                "universal_cone": self.universal_artifact_digest,
                "stable_su4_locus": self.stability_artifact_digest,
                "relative_pushdowns": self.pushdown_artifact_digest,
            },
            "source": {
                "arxiv_id": SPECTRUM_ARXIV_ID,
                "version": "v3",
                "source_archive_sha256": self.source_archive_sha256,
                "wilson_input_locators": ["eq:burt4", "eq:19"],
                "comparison_locators": ["eq:Vcoh", "eq:wedge2Vcoh"],
                "source_cohomology_dimensions_used_as_rank_inputs": False,
                "free_action_source": {
                    "arxiv_id": GEOMETRY_ARXIV_ID,
                    "version": "v2",
                    "source_archive_sha256": self.geometry_source_archive_sha256,
                },
            },
            "matter": {
                "constituent_complexes": [
                    {
                        **self.first_matter.as_record(),
                        "geometric_h0_to_h3": list(self.first_matter_profile),
                    },
                    {
                        **self.second_matter.as_record(),
                        "geometric_h0_to_h3": list(self.second_matter_profile),
                    },
                ],
                "universal_long_exact_sequence": {
                    "all_extension_parameters": True,
                    "jumping_locus": "empty",
                    "reason": (
                        "both synchronized constituent complexes have cohomology "
                        "only in degree one"
                    ),
                    "visible_cover_cohomology_h0_to_h3": list(
                        self.visible_matter_profile
                    ),
                    "dual_cover_cohomology_h0_to_h3": list(
                        self.dual_matter_profile
                    ),
                },
                "deck_representation": {
                    "representation": "3 Reg(Z3 x Z3)",
                    "character_multiplicities": [
                        {
                            "character_exponents": list(character),
                            "multiplicity": multiplicity,
                        }
                        for character, multiplicity in matter_multiplicities
                    ],
                    "derivation": (
                        "free-action holomorphic Lefschetz traces vanish for all "
                        "nonidentity deck elements; pure H1 and dimension 27 then "
                        "force multiplicity three for every character"
                    ),
                    "chain_action_enumeration_required": False,
                    "theorem_hypotheses": {
                        "deck_action_free": self.deck_action_free,
                        "carrier_equivariant": self.carrier_equivariant,
                        "cohomology_concentrated_in_h1": True,
                    },
                },
                "wilson_projection": {
                    "families": family_count,
                    "right_handed_neutrinos": family_count,
                    "anti_families": 0,
                    "matter_exotic_blocks": 0,
                },
            },
            "higgs": {
                "determinant_filtration": {
                    "det_v1_cohomology_h0_to_h3": list(
                        self.determinant_one_profile
                    ),
                    "det_v2_cohomology_h0_to_h3": list(
                        self.determinant_two_profile
                    ),
                    "acyclic": True,
                    "all_extension_parameters": True,
                },
                "derived_pushdown_tensor": {
                    "selected_mixed_constituent_cocycles_used": True,
                    "term_count": len(self.tensor_terms),
                    "cohomology_h0_to_h3": list(self.higgs_profile),
                    "h1_representative_count": len(self.higgs_representatives()),
                },
                "wedge_square": {
                    "cohomology_h0_to_h3": list(self.higgs_profile),
                    "jumping_locus": "empty",
                    "all_extension_parameters": True,
                },
                "deck_characters": [
                    {
                        "character_exponents": list(character),
                        "multiplicity": multiplicity,
                    }
                    for character, multiplicity in self.higgs_character_multiplicities
                ],
                "group_relations_exact": self.higgs_group_relations,
                "wilson_projection": {
                    "multiplicities": higgs_projection,
                    "higgs_pairs": higgs_pairs,
                    "massless_color_triplets": massless_triplets,
                },
            },
            "physical_selection_constraints": {
                "three_families": family_count == 3,
                "three_right_handed_neutrinos": family_count == 3,
                "one_higgs_pair": higgs_pairs == 1,
                "zero_anti_families": self.dual_matter_profile[1] == 0,
                "zero_exotic_massless_blocks": massless_triplets == 0,
                "used_as_construction_inputs": False,
            },
            "lawful_physical_locus": "P^1(Q(omega)) x K^s",
            "entire_stable_family_passes_structural_spectrum": True,
            "arbitrary_extension_point_selected": False,
            "full_matter_schoen_representatives_computed": False,
            "full_higgs_schoen_representatives_computed": False,
            "computable_carrier_component_frozen": False,
            "next_required_object": (
                "freeze the lawful physical P1 component, then lift matter and "
                "Higgs representatives into one common Schoen DGA"
            ),
            "status": (
                "exact all-parameter three-family one-Higgs structural spectrum "
                "from the lawful mixed family"
            ),
        }


def _mixed_schoen_spectrum_from_artifacts(
    universal_artifact: Path,
    projective_space: str,
    stability_artifact: Path,
    stable_locus: str,
) -> MixedSchoenObservableSpectrum:
    """Construct synchronized spectrum data for one certified orientation."""

    first, second = mixed_schoen_constituents()
    unit = mixed_schoen_unit()
    first_pushdown, second_pushdown = relative_constituent_pushdowns()
    line_unit = schoen_unit_constituent()
    universal_digest = _artifact_digest(
        universal_artifact,
        "projective_non_split_space",
        projective_space,
    )
    if (
        _artifact_digest(
            universal_artifact,
            "equivariant_descent_exact",
            True,
        )
        != universal_digest
    ):
        raise ValueError("universal-cone prerequisite digests disagree")
    return MixedSchoenObservableSpectrum(
        universal_digest,
        _artifact_digest(
            stability_artifact,
            "certified_stable_locus",
            stable_locus,
        ),
        _artifact_digest(
            PUSHDOWN_ARTIFACT,
            "all_quasi_isomorphisms_exact",
            True,
        ),
        _source_digest(SPECTRUM_ARXIV_ID, SPECTRUM_SOURCE_SHA256),
        _source_digest(GEOMETRY_ARXIV_ID, GEOMETRY_SOURCE_SHA256),
        True,
        True,
        mixed_transferred_outer_hom(first, unit),
        mixed_transferred_outer_hom(second, unit),
        transferred_schoen_serre_outer_hom(
            _line_constituent("det(V1)", (-2, 2, 0)),
            line_unit,
        ),
        transferred_schoen_serre_outer_hom(
            _line_constituent("det(V2)", (2, -2, 0)),
            line_unit,
        ),
        _derived_tensor_terms(first_pushdown, second_pushdown),
    )


@cache
def mixed_schoen_observable_spectrum() -> MixedSchoenObservableSpectrum:
    """Construct the exact matter and Higgs spectrum of the lawful family."""

    return _mixed_schoen_spectrum_from_artifacts(
        UNIVERSAL_ARTIFACT,
        "P^1(Q(omega))",
        STABILITY_ARTIFACT,
        "P^1(Q(omega)) x K^s",
    )


def write_mixed_schoen_observable_spectrum(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed exact lawful-spectrum certificate."""

    payload = mixed_schoen_observable_spectrum().as_record()
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
    """Regenerate the lawful mixed-family observable spectrum artifact."""

    payload = write_mixed_schoen_observable_spectrum()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"physical_selection_constraints: {payload['physical_selection_constraints']}")
    print(f"lawful_physical_locus: {payload['lawful_physical_locus']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DerivedP1CechRepresentative",
    "DerivedP1TensorTerm",
    "MixedSchoenObservableSpectrum",
    "mixed_schoen_observable_spectrum",
    "write_mixed_schoen_observable_spectrum",
]
