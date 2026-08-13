"""Compute the right-line lifting locus in the next surviving carrier block.

Owns:
    Exact restriction from outer-extension cocycles to the right Serre line,
    its target cochain complex, and the induced cohomology rank.

Depends on:
    Frozen invariant cocycles, sparse Schoen Hom totalizations, and exact
    Eisenstein linear algebra.

Must not:
    Select an extension point, infer stability from raw cocycle support, or
    promote candidates 4 and 24 into a physical carrier.

Phase 0:
    Research-only chain-level restriction is executable for the next block.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_INVARIANT_ARTIFACT,
    _canonical_digest,
    _read_partial,
    _validated_invariant_records,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_PARTIAL as AUTOMORPHISM_ARTIFACT,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    SparseOuterHom,
    sparse_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _total_basis_coordinates,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _stored_cover_representatives,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    _clear_worker_caches,
    declared_schoen_outer_pairs,
)

from .forced_subobject_stability_screen import (
    _constituent_c1_hyperplanes,
    _forced_subobjects,
    _side_data,
)
from .lifted_line_slope_identity_no_go import OUTPUT as PRIOR_NO_GO_ARTIFACT
from .lifted_line_slope_identity_no_go import lifted_line_slope_identity_no_go
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/next_survivor_restriction.json"
BLOCKS = ((4, 109, 144), (24, 829, 864))
EXPECTED_SOURCE_DIMENSIONS = Counter({50: 36, 52: 36})
EXPECTED_KERNEL_DIMENSIONS = Counter({30: 36, 32: 36})
EXPECTED_ORBITS = Counter({"P^49(Q(omega))": 36, "P^51(Q(omega))": 36})


def _identity_inclusion(
    source: VectorSpace,
    selected: tuple[int, ...],
    target: VectorSpace,
) -> SparseMap:
    """Include a coordinate-selected target into its source cochain space."""

    positions = {
        source_index: target_index
        for target_index, source_index in enumerate(selected)
    }
    rows = tuple(
        ((positions[index], Eisenstein(1)),) if index in positions else ()
        for index in range(source.dimension)
    )
    return SparseMap(target, source, rows)


def _coordinate_projection(
    source: VectorSpace,
    selected: tuple[int, ...],
    target: VectorSpace,
) -> SparseMap:
    """Project a source cochain space onto selected coordinates exactly."""

    return SparseMap(
        source,
        target,
        tuple(((source_index, Eisenstein(1)),) for source_index in selected),
    )


def _right_line_selectors(outer: SparseOuterHom) -> tuple[tuple[int, int], ...]:
    """Return Hom-term selectors induced by the right target-line inclusion."""

    right_target_rank = len(outer.right.candidate.target_shifts)
    selected_column = right_target_rank - 1
    minus_one = tuple(
        (-1, target * right_target_rank + selected_column)
        for target in range(len(outer.left.candidate.source_shifts))
    )
    zero = tuple(
        (0, target * right_target_rank + selected_column)
        for target in range(len(outer.left.candidate.target_shifts))
    )
    return minus_one + zero


@dataclass(frozen=True, slots=True)
class RightLineRestrictionComplex:
    """The exact projected total complex for ``RHom(L_right, V_left)``."""

    outer: SparseOuterHom
    selectors: tuple[tuple[int, int], ...]
    spaces: tuple[tuple[int, VectorSpace], ...]
    projections: tuple[tuple[int, SparseMap], ...]
    inclusions: tuple[tuple[int, SparseMap], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    chain_map_exact: bool
    squared_zero: bool

    @property
    def exact(self) -> bool:
        """Return whether restriction and target-complex identities close."""

        return self.chain_map_exact and self.squared_zero

    def restrict(self, degree: int, cochains: SparseMap) -> SparseMap:
        """Restrict cochains in one total degree to the right-line target."""

        source = self.outer.total.get(degree)
        if source is None or cochains.codomain != source:
            raise ValueError("restriction cochains do not inhabit the requested degree")
        return dict(self.projections)[degree].compose(cochains)


def right_line_restriction_complex(
    outer: SparseOuterHom,
) -> RightLineRestrictionComplex:
    """Construct and validate the exact right-line restriction complex."""

    selectors = _right_line_selectors(outer)
    source_spaces = outer.total
    selected_by_degree = {
        degree: tuple(
            index
            for index, coordinate in enumerate(_total_basis_coordinates(outer, degree))
            if (coordinate[0], coordinate[2]) in selectors
        )
        for degree in source_spaces
    }
    spaces = {
        degree: VectorSpace(
            f"RHom-right-line:{degree}",
            tuple(source.basis[index] for index in selected_by_degree[degree]),
            Eisenstein,
        )
        for degree, source in source_spaces.items()
    }
    projections = {
        degree: _coordinate_projection(
            source,
            selected_by_degree[degree],
            spaces[degree],
        )
        for degree, source in source_spaces.items()
    }
    inclusions = {
        degree: _identity_inclusion(
            source,
            selected_by_degree[degree],
            spaces[degree],
        )
        for degree, source in source_spaces.items()
    }
    source_differentials = dict(outer.total_differentials)
    differentials = {
        degree: projections[degree + 1].compose(differential).compose(
            inclusions[degree]
        )
        for degree, differential in source_differentials.items()
        if degree + 1 in spaces
    }
    chain_map_exact = all(
        differentials[degree].compose(projections[degree])
        == projections[degree + 1].compose(differential)
        for degree, differential in source_differentials.items()
        if degree + 1 in spaces
    )
    squared_zero = all(
        differentials[degree + 1].compose(differential).is_zero()
        for degree, differential in differentials.items()
        if degree + 1 in differentials
    )
    return RightLineRestrictionComplex(
        outer,
        selectors,
        tuple(sorted(spaces.items())),
        tuple(sorted(projections.items())),
        tuple(sorted(inclusions.items())),
        tuple(sorted(differentials.items())),
        chain_map_exact,
        squared_zero,
    )


@dataclass(frozen=True, slots=True)
class RightLineCohomologyRestriction:
    """Exact rank data for restriction on invariant Ext-one classes."""

    source_dimension: int
    target_cochain_dimension: int
    target_boundary_rank: int
    target_cycle_dimension: int
    target_cohomology_dimension: int
    induced_rank: int
    kernel_dimension: int
    restricted_cycles_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether all dimensions form a valid exact quotient."""

        return (
            self.restricted_cycles_exact
            and 0 <= self.induced_rank <= self.target_cohomology_dimension
            and self.kernel_dimension == self.source_dimension - self.induced_rank
        )


def right_line_cohomology_restriction(
    complex_: RightLineRestrictionComplex,
    representatives: SparseMap,
) -> RightLineCohomologyRestriction:
    """Compute the induced invariant Ext-one restriction rank exactly."""

    if not complex_.exact:
        raise ValueError("right-line restriction requires an exact target complex")
    spaces = dict(complex_.spaces)
    differentials = dict(complex_.differentials)
    image = complex_.restrict(1, representatives)
    boundaries = differentials[0]
    outgoing = differentials[1]
    boundary_rank = boundaries.rank()
    outgoing_rank = outgoing.rank()
    target_cycle_dimension = spaces[1].dimension - outgoing_rank
    target_cohomology_dimension = target_cycle_dimension - boundary_rank
    combined = SparseMap.block(((boundaries, image),))
    induced_rank = combined.rank() - boundary_rank
    return RightLineCohomologyRestriction(
        representatives.domain.dimension,
        spaces[1].dimension,
        boundary_rank,
        target_cycle_dimension,
        target_cohomology_dimension,
        induced_rank,
        representatives.domain.dimension - induced_rank,
        outgoing.compose(image).is_zero(),
    )


@dataclass(frozen=True, slots=True)
class PairRestrictionAudit:
    """One exact induced right-line restriction on invariant Ext-one."""

    global_pair_index: int
    candidate_index: int
    source_dimension: int
    target_cohomology_dimension: int
    induced_rank: int
    kernel_dimension: int
    chain_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether this pair has the certified rank-20 restriction."""

        return (
            self.candidate_index in (4, 24)
            and self.source_dimension in (50, 52)
            and self.target_cohomology_dimension == 216
            and self.induced_rank == 20
            and self.kernel_dimension == self.source_dimension - 20
            and self.chain_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one pair-level restriction certificate."""

        return {
            "global_pair_index": self.global_pair_index,
            "candidate_index": self.candidate_index,
            "source_dimension": self.source_dimension,
            "target_cohomology_dimension": self.target_cohomology_dimension,
            "induced_rank": self.induced_rank,
            "kernel_dimension": self.kernel_dimension,
            "exact": self.exact,
        }


@dataclass(frozen=True, slots=True)
class NextSurvivorRestriction:
    """The exact lifting stratification of candidates 4 and 24."""

    pairs: tuple[PairRestrictionAudit, ...]
    source_dimension_counts: tuple[tuple[int, int], ...]
    kernel_dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    first_orientation_slope_identity: bool
    second_orientation_slope_identity: bool

    def __post_init__(self) -> None:
        if len(self.pairs) != 72 or tuple(
            pair.global_pair_index for pair in self.pairs
        ) != tuple(
            (*range(109, 145), *range(829, 865))
        ):
            raise ValueError("the next-survivor restriction must cover 72 pairs")
        if not all(pair.exact for pair in self.pairs):
            raise ValueError("one next-survivor restriction certificate failed")
        if Counter(dict(self.source_dimension_counts)) != EXPECTED_SOURCE_DIMENSIONS:
            raise ValueError("next-survivor source dimensions changed")
        if Counter(dict(self.kernel_dimension_counts)) != EXPECTED_KERNEL_DIMENSIONS:
            raise ValueError("next-survivor kernel dimensions changed")
        if Counter(dict(self.orbit_space_counts)) != EXPECTED_ORBITS:
            raise ValueError("next-survivor projective orbit spaces changed")
        if not (
            self.first_orientation_slope_identity
            and self.second_orientation_slope_identity
        ):
            raise ValueError("the right-line kernel lacks its slope obstruction")

    def as_record(self) -> dict[str, object]:
        """Serialize the exact lifting kernel without asserting generic stability."""

        return {
            "schema": "next-survivor-right-line-restriction-v1",
            "candidate_blocks": [
                {
                    "candidate_index": candidate,
                    "global_pair_range": [start, end],
                    "pair_count": end - start + 1,
                }
                for candidate, start, end in BLOCKS
            ],
            "checked_pair_count": len(self.pairs),
            "invariant_ext_dimension_counts": {
                str(dimension): count
                for dimension, count in self.source_dimension_counts
            },
            "nonzero_orbit_space_counts": dict(self.orbit_space_counts),
            "target_ext_one_dimension": 216,
            "induced_restriction_rank": 20,
            "kernel_vector_dimension_counts": {
                str(dimension): count
                for dimension, count in self.kernel_dimension_counts
            },
            "projective_lifting_loci": {
                "P^49(Q(omega))": "P^29(Q(omega))",
                "P^51(Q(omega))": "P^31(Q(omega))",
            },
            "restriction_chain_map_exact_for_every_pair": True,
            "restricted_classes_are_target_cycles": True,
            "lifting_locus_is_exact_linear_kernel": True,
            "kernel_slope_identity": (
                "3*mu(preimage(L_right))+mu(L_right)=0"
            ),
            "kernel_contains_no_stable_extension": True,
            "nonlifting_open_complement_nonempty": True,
            "nonlifting_open_complement_stability_proved": False,
            "global_computable_carrier_no_go": False,
            "arbitrary_extension_point_selected": False,
            "pair_certificates": [pair.as_record() for pair in self.pairs],
            "next_invariant_ext_dimension": 50,
            "next_candidate_blocks": [4, 24],
            "next_required_object": (
                "exact stability classification on the nonlifting projective "
                "open complements in candidate blocks 4 and 24"
            ),
            "status": (
                "exact codimension-20 right-line lifting kernels for all 72 "
                "families; each kernel is unstable and each complement remains open"
            ),
        }


def _slope_identity(
    record: dict[str, object],
    c1_hyperplanes,
) -> bool:
    """Check the zero slope sum on one lifting kernel exactly."""

    subobjects = {
        subobject.name: subobject
        for subobject in _forced_subobjects(record, c1_hyperplanes)
    }
    right = _side_data(record, "right")
    right_line_degree = _serre_line_degree(right[0], right[1], right[2])
    right_line_slope = _slope_polynomial(
        schoen_geometry().quotient_divisor(right_line_degree),
        1,
    )
    return (
        subobjects["preimage(L_right)"].slope.scale(3) + right_line_slope
    ).is_zero()


@cache
def next_survivor_restriction() -> NextSurvivorRestriction:
    """Certify every induced right-line restriction and its unstable kernel."""

    prior = json.loads(PRIOR_NO_GO_ARTIFACT.read_text(encoding="utf-8"))
    digest = prior.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(prior):
        raise ValueError("the prior lifted-line no-go digest does not verify")
    if prior != lifted_line_slope_identity_no_go().as_record():
        raise ValueError("the prior lifted-line no-go artifact is stale")

    invariant_digest, records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    declared_pairs = declared_schoen_outer_pairs()
    c1_hyperplanes = _constituent_c1_hyperplanes()
    audits: list[PairRestrictionAudit] = []
    dimensions: Counter[int] = Counter()
    kernels: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    slope_identities: dict[int, bool] = {}
    for candidate_index, start, end in BLOCKS:
        try:
            for global_index in range(start, end + 1):
                record = records[global_index - 1]
                if record.get("candidate_index") != candidate_index:
                    raise ValueError("next-survivor candidate ordering changed")
                pair_candidate, candidate, left_ray, right_ray = declared_pairs[
                    global_index - 1
                ]
                if pair_candidate != candidate_index:
                    raise ValueError("declared and frozen candidate indices differ")
                outer = sparse_outer_hom(
                    left_ray,
                    right_ray,
                    candidate.left_factor,
                    candidate.left_twist,
                    candidate.right_factor,
                    candidate.right_twist,
                )
                representatives = _stored_cover_representatives(outer, record)
                complex_ = right_line_restriction_complex(outer)
                result = right_line_cohomology_restriction(
                    complex_, representatives
                )
                audit = PairRestrictionAudit(
                    global_index,
                    candidate_index,
                    result.source_dimension,
                    result.target_cohomology_dimension,
                    result.induced_rank,
                    result.kernel_dimension,
                    complex_.exact and result.exact,
                )
                if not audit.exact:
                    raise ValueError("one induced right-line restriction failed")
                action = actions.get(global_index, {}).get("automorphism_action")
                orbit = f"P^{result.source_dimension - 1}(Q(omega))"
                if not isinstance(action, dict) or action.get(
                    "nonzero_orbit_space"
                ) != orbit:
                    raise ValueError("one next-survivor orbit certificate changed")
                audits.append(audit)
                dimensions[result.source_dimension] += 1
                kernels[result.kernel_dimension] += 1
                orbit_spaces[orbit] += 1
                slope_identities.setdefault(
                    candidate_index,
                    _slope_identity(record, c1_hyperplanes),
                )
        finally:
            _clear_worker_caches()
    return NextSurvivorRestriction(
        tuple(audits),
        tuple(sorted(dimensions.items())),
        tuple(sorted(kernels.items())),
        tuple(sorted(orbit_spaces.items())),
        slope_identities.get(4, False),
        slope_identities.get(24, False),
    )


def write_next_survivor_restriction(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed restriction artifact atomically."""

    payload = next_survivor_restriction().as_record()
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
    """Regenerate the exact next-survivor restriction artifact."""

    payload = write_next_survivor_restriction()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"induced_restriction_rank: {payload['induced_restriction_rank']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "RightLineCohomologyRestriction",
    "RightLineRestrictionComplex",
    "NextSurvivorRestriction",
    "right_line_cohomology_restriction",
    "right_line_restriction_complex",
    "next_survivor_restriction",
]
