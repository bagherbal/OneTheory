"""Stratify lifts of maximal quotient-generator lines in the next block.

Owns:
    Exact equivariant generator eigenlines, their restriction maps on invariant
    outer Ext, and the resulting unstable projective lifting kernels.

Depends on:
    Frozen invariant cocycles, exact presentation linearizations, sparse target
    restriction complexes, and the candidate-4/24 chamber certificate.

Must not:
    Treat this finite line stratum as a complete stability proof, select a
    generic extension point, or omit lower proper sublines of a constituent.

Phase 0:
    Research-only maximal-generator restriction stratification is executable.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_INVARIANT_ARTIFACT,
    _canonical_digest,
    _validated_invariant_records,
)
from research.experiments.computable_carrier.pushout_linearization import (
    _middle_action,
)
from research.experiments.computable_carrier.schoen_outer import schoen_presentation
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _factor_resolution_data,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _stored_cover_representatives,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    _clear_worker_caches,
    declared_schoen_outer_pairs,
)

from .next_survivor_forced_chamber import OUTPUT as CHAMBER_ARTIFACT
from .next_survivor_restriction import (
    right_line_cohomology_restriction,
    right_target_line_restriction_complex,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / (
    "data/generated/scientific_genesis/"
    "next_survivor_generator_restrictions.json"
)
BLOCKS = ((4, 109, 144), (24, 829, 864))
UNITS = (Eisenstein(1), OMEGA, OMEGA2)


def _normalized(vector: Vector) -> tuple[Eisenstein, ...]:
    """Normalize one nonzero eigenvector at its first coordinate."""

    pivot = next(
        (value for value in vector.values if not value.is_zero()),
        None,
    )
    if pivot is None:
        raise ValueError("a target eigenline requires a nonzero vector")
    inverse = Eisenstein(1) / pivot
    return tuple(value * inverse for value in vector.values)


def _target_generator_eigenlines(presentation) -> tuple[
    tuple[Eisenstein, Eisenstein, tuple[Eisenstein, ...]], ...
]:
    """Return all common P/T eigenlines in the ideal-generator target term."""

    pair, characters = _factor_resolution_data(presentation)
    p_action = _middle_action(pair.action("P"), characters[0]).transpose()
    t_action = _middle_action(pair.action("T"), characters[1]).transpose()
    identity = Matrix.identity(p_action.row_count, scalar_type=Eisenstein)
    lines: set[tuple[Eisenstein, Eisenstein, tuple[Eisenstein, ...]]] = set()
    for p_character in UNITS:
        for vector in (p_action - identity.scale(p_character)).nullspace():
            for t_character in UNITS:
                if t_action @ vector != vector.scale(t_character):
                    continue
                normalized = _normalized(vector)
                if not normalized[-1].is_zero():
                    continue
                lines.add((p_character, t_character, normalized))
    result = tuple(
        sorted(
            lines,
            key=lambda item: (
                str(item[0]),
                str(item[1]),
                tuple(str(value) for value in item[2]),
            ),
        )
    )
    if len(result) != 4:
        raise ValueError("a right presentation no longer has four generator eigenlines")
    return result


@dataclass(frozen=True, slots=True)
class GeneratorLineRestriction:
    """One exact maximal generator-line restriction on invariant Ext-one."""

    global_pair_index: int
    candidate_index: int
    source_dimension: int
    p_character: Eisenstein
    t_character: Eisenstein
    target_vector: tuple[Eisenstein, ...]
    target_cohomology_dimension: int
    induced_rank: int
    kernel_dimension: int
    exact: bool

    def __post_init__(self) -> None:
        if self.candidate_index not in (4, 24):
            raise ValueError("a generator restriction left candidates 4 and 24")
        if self.source_dimension not in (50, 52):
            raise ValueError("a generator restriction has an unexpected source")
        if len(self.target_vector) != 5 or not self.target_vector[-1].is_zero():
            raise ValueError("a generator line escaped the four ideal generators")
        if self.target_cohomology_dimension <= 0:
            raise ValueError("a generator restriction target must be nonzero")
        if not 0 < self.induced_rank < self.source_dimension:
            raise ValueError("a generator restriction must have a proper kernel")
        if self.kernel_dimension != self.source_dimension - self.induced_rank:
            raise ValueError("a generator restriction kernel dimension is inconsistent")
        if not self.exact:
            raise ValueError("a generator restriction failed its exact gates")

    def as_record(self) -> dict[str, object]:
        """Serialize one exact generator-line lifting kernel."""

        return {
            "global_pair_index": self.global_pair_index,
            "candidate_index": self.candidate_index,
            "source_dimension": self.source_dimension,
            "characters": [str(self.p_character), str(self.t_character)],
            "target_vector": [str(value) for value in self.target_vector],
            "target_cohomology_dimension": self.target_cohomology_dimension,
            "induced_rank": self.induced_rank,
            "kernel_dimension": self.kernel_dimension,
            "projective_kernel": f"P^{self.kernel_dimension - 1}(Q(omega))",
            "exact": self.exact,
        }


@dataclass(frozen=True, slots=True)
class NextSurvivorGeneratorRestrictions:
    """All maximal quotient-generator lifting strata in candidates 4 and 24."""

    restrictions: tuple[GeneratorLineRestriction, ...]
    target_dimension_counts: tuple[tuple[int, int], ...]
    rank_counts: tuple[tuple[int, int], ...]
    kernel_counts: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if len(self.restrictions) != 288:
            raise ValueError("the generator screen must contain four lines per pair")
        if Counter(item.global_pair_index for item in self.restrictions) != Counter(
            {
                index: 4
                for start, end in ((109, 144), (829, 864))
                for index in range(start, end + 1)
            }
        ):
            raise ValueError("the generator screen does not cover all 72 pairs")
        if sum(count for _, count in self.rank_counts) != 288:
            raise ValueError("the generator rank distribution is incomplete")
        if sum(count for _, count in self.target_dimension_counts) != 288:
            raise ValueError("the generator target distribution is incomplete")
        if sum(count for _, count in self.kernel_counts) != 288:
            raise ValueError("the generator kernel distribution is incomplete")

    def as_record(self) -> dict[str, object]:
        """Serialize the finite unstable strata and preserve lower-line gaps."""

        return {
            "schema": "next-survivor-generator-restrictions-v1",
            "candidate_blocks": [
                {
                    "candidate_index": candidate,
                    "global_pair_range": [start, end],
                    "pair_count": end - start + 1,
                }
                for candidate, start, end in BLOCKS
            ],
            "checked_pair_count": 72,
            "generator_line_count_per_pair": 4,
            "checked_restriction_count": len(self.restrictions),
            "generator_line_c1": ["-4", "1", "-1"],
            "factor_exchanged_generator_line_c1": ["1", "-4", "-1"],
            "slope_identity": "mu(L_left)+mu(generator_line)=0",
            "target_ext_one_dimension_counts": {
                str(dimension): count
                for dimension, count in self.target_dimension_counts
            },
            "induced_rank_counts": {
                str(rank): count for rank, count in self.rank_counts
            },
            "kernel_vector_dimension_counts": {
                str(dimension): count for dimension, count in self.kernel_counts
            },
            "every_lifting_kernel_is_proper": True,
            "every_lifting_kernel_is_unstable": True,
            "finite_union_complement_nonempty": True,
            "generic_class_avoids_all_maximal_generator_lifts": True,
            "full_slope_stability_proved": False,
            "lower_proper_subline_restrictions_classified": False,
            "arbitrary_extension_point_selected": False,
            "restrictions": [item.as_record() for item in self.restrictions],
            "next_required_object": (
                "exact restriction maps for lower proper sublines of the right "
                "Serre and generator lines, beginning with O(3*tau1-phi)"
            ),
            "status": (
                "all 288 maximal quotient-generator restrictions are exact; "
                "their unstable kernels are proper and generic stability remains open"
            ),
        }


@cache
def next_survivor_generator_restrictions() -> NextSurvivorGeneratorRestrictions:
    """Compute every maximal generator-line restriction exactly."""

    chamber = json.loads(CHAMBER_ARTIFACT.read_text(encoding="utf-8"))
    digest = chamber.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(chamber):
        raise ValueError("the next-survivor chamber digest does not verify")
    if not (
        chamber.get("common_forced_subobject_chamber_nonempty") is True
        and chamber.get("full_slope_stability_proved") is False
    ):
        raise ValueError("the chamber artifact does not expose the stability gap")

    _, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs = declared_schoen_outer_pairs()
    restrictions: list[GeneratorLineRestriction] = []
    targets: Counter[int] = Counter()
    ranks: Counter[int] = Counter()
    kernels: Counter[int] = Counter()
    for candidate_index, start, end in BLOCKS:
        try:
            for global_index in range(start, end + 1):
                pair_candidate, candidate, left_ray, right_ray = pairs[
                    global_index - 1
                ]
                record = records[global_index - 1]
                if pair_candidate != candidate_index or record.get(
                    "candidate_index"
                ) != candidate_index:
                    raise ValueError("the generator restriction block order changed")
                outer = sparse_outer_hom(
                    left_ray,
                    right_ray,
                    candidate.left_factor,
                    candidate.left_twist,
                    candidate.right_factor,
                    candidate.right_twist,
                )
                representatives = _stored_cover_representatives(outer, record)
                right_presentation = schoen_presentation(
                    right_ray,
                    candidate.right_factor,
                    candidate.right_twist,
                )
                for p_character, t_character, vector in _target_generator_eigenlines(
                    right_presentation
                ):
                    complex_ = right_target_line_restriction_complex(outer, vector)
                    result = right_line_cohomology_restriction(
                        complex_, representatives
                    )
                    restriction = GeneratorLineRestriction(
                        global_index,
                        candidate_index,
                        result.source_dimension,
                        p_character,
                        t_character,
                        vector,
                        result.target_cohomology_dimension,
                        result.induced_rank,
                        result.kernel_dimension,
                        complex_.exact and result.exact,
                    )
                    restrictions.append(restriction)
                    targets[result.target_cohomology_dimension] += 1
                    ranks[result.induced_rank] += 1
                    kernels[result.kernel_dimension] += 1
        finally:
            _clear_worker_caches()
    return NextSurvivorGeneratorRestrictions(
        tuple(restrictions),
        tuple(sorted(targets.items())),
        tuple(sorted(ranks.items())),
        tuple(sorted(kernels.items())),
    )


def write_next_survivor_generator_restrictions(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed generator restriction artifact atomically."""

    payload = next_survivor_generator_restrictions().as_record()
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
    """Regenerate the exact maximal-generator restriction artifact."""

    payload = write_next_survivor_generator_restrictions()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_restriction_count: {payload['checked_restriction_count']}")
    print(f"induced_rank_counts: {payload['induced_rank_counts']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "GeneratorLineRestriction",
    "NextSurvivorGeneratorRestrictions",
    "next_survivor_generator_restrictions",
]
