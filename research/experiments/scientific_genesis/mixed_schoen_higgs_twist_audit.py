"""Audit the determinant-twist route to synchronized Schoen Higgs classes.

Owns:
    The rank-two determinant-twist realization of V1 tensor V2, its exact
    transferred cohomology, deck action, and equivariant comparison obstruction.

Depends on:
    The lawful mixed constituents, exact determinant data, synchronized outer
    transfer, full-Schoen deck actions, and sparse cohomology contractions.

Must not:
    Select a raw character by resemblance, identify the Hom realization with the
    physical tensor without a chain comparison, or evaluate a Yukawa coupling.

Phase 0:
    Research-only exact audit of a blocked Higgs representative route.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _matrix_from_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_outer_actions import (
    _apply_transferred_action,
    _MixedContraction,
)
from .mixed_schoen_outer_transfer import (
    MixedTransferredOuterHom,
    mixed_transferred_outer_hom,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_higgs_twist_audit.json"
SPECTRUM_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_observable_spectrum.json"
)
MIXED_ARROW_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json"
)
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
SPECTRUM_ARXIV_ID = "hep-th/0512177"
SPECTRUM_SOURCE_SHA256 = (
    "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
)
DET_V1_DEGREE = (-2, 2, 0)
SOURCE_HIGGS_CHARACTERS = ((0, 1), (0, 2), (1, 2), (2, 1))


def _character_vectors(
    p_action: Matrix,
    t_action: Matrix,
    character: tuple[int, int],
) -> tuple[Vector, ...]:
    """Return one simultaneous character basis, including the empty case."""

    identity = Matrix.identity(p_action.row_count, scalar_type=Eisenstein)
    equations = Matrix(
        (
            *((p_action - identity.scale(OMEGA ** character[0])).rows),
            *((t_action - identity.scale(OMEGA ** character[1])).rows),
        ),
        scalar_type=Eisenstein,
    )
    return equations.nullspace()


def _add_degree(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Add two exact Schoen line degrees."""

    return cast(
        tuple[int, int, int],
        tuple(first + second for first, second in zip(left, right, strict=True)),
    )


def _uniform_character_shift_exists(
    derived: tuple[tuple[int, int], ...],
    expected: tuple[tuple[int, int], ...],
) -> bool:
    """Return whether one scalar linearization aligns two character multisets."""

    expected_sorted = tuple(sorted(expected))
    return any(
        tuple(
            sorted(
                ((first + shift_first) % 3, (second + shift_second) % 3)
                for first, second in derived
            )
        )
        == expected_sorted
        for shift_first in range(3)
        for shift_second in range(3)
    )


@cache
def determinant_twisted_second_constituent() -> MixedSchoenConstituent:
    """Return V2 tensor det(V1) in the synchronized mixed grading."""

    _first, second = mixed_schoen_constituents()
    return replace(
        second,
        name="V2*det(V1)",
        twist=_add_degree(second.twist, DET_V1_DEGREE),
        objects=tuple(
            replace(
                object_,
                line_degree=_add_degree(object_.line_degree, DET_V1_DEGREE),
            )
            for object_ in second.objects
        ),
    )


@cache
def _higgs_contraction() -> _MixedContraction:
    """Return the exact Hom(V2 tensor det(V1), V1) contraction."""

    first, _second = mixed_schoen_constituents()
    return _MixedContraction(determinant_twisted_second_constituent(), first)


def _higgs_action_job(
    job: tuple[int, str, dict[int, Eisenstein]],
) -> tuple[int, str, dict[int, Eisenstein], tuple[int, int]]:
    """Transfer one Higgs-cohomology action in a worker process."""

    column, generator, coefficients = job
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    image, depths = _apply_transferred_action(
        coefficients,
        _higgs_contraction(),
        1,
        actions[generator],
    )
    return column, generator, image, depths


def _artifact_digest(path: Path, gate: str, expected: object) -> str:
    """Validate one content-addressed prerequisite and return its digest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) != expected:
        raise ValueError(f"upstream artifact gate changed: {path.name}")
    return digest


def _source_digest() -> str:
    """Verify the source archive used only for final character comparison."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the visible source manifest is malformed")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == SPECTRUM_ARXIV_ID
    ]
    if (
        len(matches) != 1
        or matches[0].get("source_archive_sha256") != SPECTRUM_SOURCE_SHA256
    ):
        raise ValueError("the Higgs source archive digest changed")
    return SPECTRUM_SOURCE_SHA256


@dataclass(frozen=True, slots=True)
class MixedSchoenHiggsTwistAudit:
    """Exact Hom transfer and its unresolved equivariant tensor comparison."""

    transferred: MixedTransferredOuterHom
    representatives: SparseMap
    p_induced: Matrix
    t_induced: Matrix
    character_multiplicities: tuple[tuple[tuple[int, int], int], ...]
    action_depths: tuple[tuple[str, int, int], ...]
    images_are_cycles: bool
    mixed_arrow_artifact_digest: str
    spectrum_artifact_digest: str
    source_archive_sha256: str

    @property
    def geometric_dimensions(self) -> tuple[int, int, int, int]:
        """Return exact Hom cohomology in geometric degrees zero through three."""

        spaces = dict(self.transferred.spaces)
        return cast(
            tuple[int, int, int, int],
            tuple(
                self.transferred.cohomology_dimension(degree)
                if degree in spaces
                else 0
                for degree in range(4)
            ),
        )

    @property
    def group_relations(self) -> bool:
        """Return exact Z3 x Z3 relations on transferred H1."""

        identity = Matrix.identity(self.p_induced.row_count, scalar_type=Eisenstein)
        return (
            self.p_induced**3 == identity
            and self.t_induced**3 == identity
            and self.p_induced @ self.t_induced
            == self.t_induced @ self.p_induced
        )

    @property
    def derived_characters(self) -> tuple[tuple[int, int], ...]:
        """Expand the exact simultaneous-character multiplicities."""

        return tuple(
            character
            for character, multiplicity in self.character_multiplicities
            for _index in range(multiplicity)
        )

    @property
    def source_characters_match(self) -> bool:
        """Return whether the raw Hom action equals the physical tensor action."""

        return self.derived_characters == SOURCE_HIGGS_CHARACTERS

    @property
    def uniform_character_shift_exists(self) -> bool:
        """Return whether an omitted scalar linearization could repair the action."""

        return _uniform_character_shift_exists(
            self.derived_characters,
            SOURCE_HIGGS_CHARACTERS,
        )

    @property
    def exact_transfer(self) -> bool:
        """Return all purely Hom-transfer exactness gates."""

        return (
            self.transferred.squared_zero
            and self.geometric_dimensions == (0, 4, 4, 0)
            and self.group_relations
            and self.images_are_cycles
            and sum(
                multiplicity
                for _character, multiplicity in self.character_multiplicities
            )
            == 4
        )

    @property
    def route_blocked(self) -> bool:
        """Return whether the exact transfer cannot identify physical Higgs classes."""

        return (
            self.exact_transfer
            and not self.source_characters_match
            and not self.uniform_character_shift_exists
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact transfer and fail-closed comparison boundary."""

        return {
            "schema": "mixed-schoen-higgs-twist-audit-v1",
            "coefficient_field": "Q(omega)",
            "derived_identity_attempted": (
                "V1 tensor V2 = RHom(V2 tensor det(V1), V1), using "
                "det(V2) = det(V1)^-1"
            ),
            "det_v1_degree": list(DET_V1_DEGREE),
            "transfer": self.transferred.as_record(),
            "geometric_cohomology_h0_to_h3": list(self.geometric_dimensions),
            "raw_hom_character_multiplicities": [
                {
                    "character_exponents": list(character),
                    "multiplicity": multiplicity,
                }
                for character, multiplicity in self.character_multiplicities
                if multiplicity
            ],
            "source_tensor_character_comparison": {
                "characters": [list(value) for value in SOURCE_HIGGS_CHARACTERS],
                "matches": self.source_characters_match,
                "used_as_action_input": False,
                "arxiv_id": SPECTRUM_ARXIV_ID,
                "version": "v3",
                "source_archive_sha256": self.source_archive_sha256,
                "locator": "eq:17",
            },
            "uniform_character_shift_exists": self.uniform_character_shift_exists,
            "group_relations_exact": self.group_relations,
            "all_hom_transfer_gates_exact": self.exact_transfer,
            "equivariant_tensor_identification_available": False,
            "physical_higgs_representative_available": False,
            "route_blocked_exact": self.route_blocked,
            "prerequisite_artifact_digests": {
                "mixed_arrows": self.mixed_arrow_artifact_digest,
                "structural_spectrum": self.spectrum_artifact_digest,
            },
            "retired_diagonal_cones_used": False,
            "first_missing_input": (
                "equivariant chain comparison for the determinant-twist tensor "
                "identity or a direct lawful mixed tensor transfer"
            ),
            "status": (
                "exact Hom cohomology and deck action; physical Higgs classes "
                "remain unavailable because the tensor comparison is unresolved"
            ),
        }


@cache
def mixed_schoen_higgs_twist_audit() -> MixedSchoenHiggsTwistAudit:
    """Derive the determinant-twist action without selecting a physical class."""

    first, _second = mixed_schoen_constituents()
    twisted_second = determinant_twisted_second_constituent()
    transferred = mixed_transferred_outer_hom(twisted_second, first)
    spaces = dict(transferred.spaces)
    differentials = dict(transferred.differentials)
    outgoing = differentials[1]
    incoming = differentials[0]
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "H1:higgs-audit")
    representative_columns = tuple(_columns(representatives))
    jobs = [
        (column, generator, coefficients)
        for column, coefficients in enumerate(representative_columns)
        for generator in ("P", "T")
    ]
    with ProcessPoolExecutor(max_workers=len(jobs)) as executor:
        completed = tuple(executor.map(_higgs_action_job, jobs))
    computed = {
        (column, generator): (image, depths)
        for column, generator, image, depths in completed
    }
    boundaries = _independent_columns(incoming)
    solver = _SparseSpanSolver(boundaries + representative_columns)
    boundary_dimension = len(boundaries)
    induced: dict[str, Matrix] = {}
    action_depths = []
    images_are_cycles = True
    for generator in ("P", "T"):
        columns = []
        for column in range(len(representative_columns)):
            image, depths = computed[(column, generator)]
            action_depths.append((generator, *depths))
            cycle_map = SparseMap(
                VectorSpace("one", ("one",), Eisenstein),
                spaces[1],
                _freeze_rows(
                    ({0: image[row]} if row in image else {})
                    for row in range(spaces[1].dimension)
                ),
            )
            images_are_cycles = images_are_cycles and outgoing.compose(
                cycle_map
            ).is_zero()
            coordinates = solver.coordinates(image)
            columns.append(
                {
                    index - boundary_dimension: value
                    for index, value in coordinates.items()
                    if index >= boundary_dimension
                }
            )
        induced[generator] = _matrix_from_columns(
            tuple(columns),
            len(representative_columns),
        )
    p_induced = induced["P"]
    t_induced = induced["T"]
    multiplicities = tuple(
        (
            character,
            len(_character_vectors(p_induced, t_induced, character)),
        )
        for character in (
            (first_exponent, second_exponent)
            for first_exponent in range(3)
            for second_exponent in range(3)
        )
    )
    result = MixedSchoenHiggsTwistAudit(
        transferred,
        representatives,
        p_induced,
        t_induced,
        multiplicities,
        tuple(action_depths),
        images_are_cycles,
        _artifact_digest(
            MIXED_ARROW_ARTIFACT,
            "all_common_schoen_arrows_exact",
            True,
        ),
        _artifact_digest(
            SPECTRUM_ARTIFACT,
            "entire_stable_family_passes_structural_spectrum",
            True,
        ),
        _source_digest(),
    )
    if not result.route_blocked:
        raise ValueError("the determinant-twist comparison audit changed")
    return result


def write_mixed_schoen_higgs_twist_audit(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed determinant-twist obstruction certificate."""

    payload = mixed_schoen_higgs_twist_audit().as_record()
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
    """Regenerate the determinant-twist obstruction certificate."""

    payload = write_mixed_schoen_higgs_twist_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"geometric_cohomology_h0_to_h3: {payload['geometric_cohomology_h0_to_h3']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenHiggsTwistAudit",
    "determinant_twisted_second_constituent",
    "mixed_schoen_higgs_twist_audit",
    "write_mixed_schoen_higgs_twist_audit",
]
