"""Linearize the selected constituent atlases under both deck generators.

Owns:
    Local line-frame trivializations, exact P/T comparison matrices, relation
    squares, overlap equivariance, order-three laws, and deck commutation.

Depends on:
    The selected mixed constituent atlases, exact dP9 chart actions, derived
    Hilbert--Burch frame actions, and homogeneous Laurent arithmetic.

Must not:
    Replace local frame factors by projective constants, infer the rank-four
    outer extension, or promote source-bound equivariance as a derivation.

Phase 0:
    Research-only deck linearizations of the published W1/W2 constituents.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial
from research.experiments.computable_carrier.dp9_actions import (
    published_coordinate_images,
)
from research.experiments.computable_carrier.dp9_deck_atlas import (
    DP9DeckChartAction,
    dp9_deck_atlas_audit,
)
from research.experiments.computable_carrier.dp9_serre_actions import (
    _fiber_coordinate_images,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import (
    BlowupChart,
    tier_a_pencil_model,
)
from research.experiments.computable_carrier.resolution_actions import (
    ResolutionAction,
    tier_a_resolution_actions,
)

from .published_constituent_full_cech import (
    PublishedConstituentFullCech,
    published_constituent_full_cech,
)
from .published_constituent_overlap_transitions import (
    PublishedConstituentOverlapAtlas,
    _relation_columns,
    published_constituent_overlap_atlases,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/published_constituent_deck_atlases.json"
)

Shift = tuple[int, int]
CoordinateImages = tuple[tuple[Eisenstein, tuple[int, ...]], ...]


def _zero() -> LaurentPolynomial:
    """Return zero in the five-coordinate homogeneous Laurent ring."""

    return LaurentPolynomial.zero(5, scalar_type=Eisenstein)


def _one() -> LaurentPolynomial:
    """Return one in the five-coordinate homogeneous Laurent ring."""

    return LaurentPolynomial.one(5, scalar_type=Eisenstein)


def _constant_matrix(matrix: Matrix) -> LaurentMatrix:
    """Embed one exact scalar matrix in the homogeneous Laurent ring."""

    zero = _zero()
    one = _one()
    return LaurentMatrix(
        tuple(
            tuple(
                zero if matrix[row][column].is_zero() else one.scale(matrix[row][column])
                for column in range(matrix.column_count)
            )
            for row in range(matrix.row_count)
        )
    )


def _diagonal(values: tuple[LaurentPolynomial, ...]) -> LaurentMatrix:
    """Return one exact Laurent diagonal matrix."""

    zero = _zero()
    return LaurentMatrix(
        tuple(
            tuple(values[row] if row == column else zero for column in range(len(values)))
            for row in range(len(values))
        )
    )


def _trivialization(
    chart: BlowupChart,
    shifts: tuple[Shift, ...],
) -> LaurentMatrix:
    """Return local homogeneous frames for declared base/fiber shifts."""

    fiber_pivot = 3 if chart.fiber_chart == "mu" else 4
    values = []
    for base_degree, fiber_degree in shifts:
        exponents = [0] * 5
        exponents[chart.base_pivot] = base_degree
        exponents[fiber_pivot] = fiber_degree
        values.append(
            LaurentPolynomial.monomial(exponents, scalar_type=Eisenstein)
        )
    return _diagonal(tuple(values))


def _inverse_trivialization(
    chart: BlowupChart,
    shifts: tuple[Shift, ...],
) -> LaurentMatrix:
    """Return the exact inverse local-frame diagonal."""

    return _trivialization(
        chart,
        tuple((-base, -fiber) for base, fiber in shifts),
    )


def _pullback(
    matrix: LaurentMatrix,
    images: CoordinateImages,
) -> LaurentMatrix:
    """Apply one homogeneous deck substitution entrywise."""

    return LaurentMatrix(
        tuple(
            tuple(entry.substitute_monomials(images) for entry in row)
            for row in matrix.rows
        )
    )


def _coordinate_images(
    generator: str,
    surface_factor: int,
) -> CoordinateImages:
    """Embed the base and selected dP9 fiber lifts in five variables."""

    base = published_coordinate_images(generator)
    fiber = _fiber_coordinate_images(generator, surface_factor)
    return tuple((scalar, (*exponents, 0, 0)) for scalar, exponents in base) + tuple(
        (scalar, (0, 0, 0, *exponents)) for scalar, exponents in fiber
    )


def _middle_shifts(generator_count: int) -> tuple[Shift, ...]:
    """Return the ideal-generator and extension-line module shifts."""

    generator_degree = generator_count - 1
    return tuple((-generator_degree, 0) for _ in range(generator_count)) + (
        (0, -2),
    )


def _relation_shifts(syzygy_count: int) -> tuple[Shift, ...]:
    """Return the Hilbert--Burch source-module shifts."""

    return tuple((-syzygy_count - 2, 0) for _ in range(syzygy_count))


def _homogeneous_middle_action(
    action: ResolutionAction,
    line_character: Eisenstein,
) -> Matrix:
    """Extend the ideal-generator frame by the selected extension line."""

    size = action.target_action.row_count
    zero = Eisenstein(0)
    return Matrix(
        tuple(
            tuple(
                action.target_action[row][column]
                if row < size and column < size
                else line_character
                if row == size and column == size
                else zero
                for column in range(size + 1)
            )
            for row in range(size + 1)
        ),
        scalar_type=Eisenstein,
    )


def _localized_relation(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
    middle_shifts: tuple[Shift, ...],
    relation_shifts: tuple[Shift, ...],
) -> LaurentMatrix:
    """Express one homogeneous pushout relation in local line frames."""

    return (
        _inverse_trivialization(chart, middle_shifts)
        .compose(_relation_columns(result, chart))
        .compose(_trivialization(chart, relation_shifts))
    )


def _localized_transition(
    transition: LaurentMatrix,
    source: BlowupChart,
    target: BlowupChart,
    shifts: tuple[Shift, ...],
) -> LaurentMatrix:
    """Insert the omitted line-frame factors into one overlap gauge."""

    return (
        _inverse_trivialization(source, shifts)
        .compose(transition)
        .compose(_trivialization(target, shifts))
    )


@dataclass(frozen=True, slots=True)
class ConstituentDeckComparison:
    """One exact pullback comparison on a selected constituent chart."""

    constituent: str
    generator: str
    source: BlowupChart
    target: BlowupChart
    coordinate_images: CoordinateImages
    extension_line_character: Eisenstein
    middle: LaurentMatrix
    relations: LaurentMatrix
    relation_compatible: bool

    def as_record(self) -> dict[str, object]:
        """Serialize one chart comparison and its exact relation square."""

        return {
            "constituent": self.constituent,
            "generator": self.generator,
            "source": self.source.name,
            "target": self.target.name,
            "extension_line_character": str(self.extension_line_character),
            "middle": _matrix_record(self.middle),
            "relations": _matrix_record(self.relations),
            "relation_compatible": self.relation_compatible,
        }


def _matrix_record(matrix: LaurentMatrix) -> list[list[list[dict[str, object]]]]:
    """Serialize one sparse exact Laurent matrix."""

    return [
        [
            [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in entry.terms
            ]
            for entry in row
        ]
        for row in matrix.rows
    ]


@dataclass(frozen=True, slots=True)
class PublishedConstituentDeckAtlas:
    """The complete exact Z3 x Z3 linearization of one constituent atlas."""

    constituent: str
    comparisons: tuple[ConstituentDeckComparison, ...]
    overlap_equivariant: bool
    p_order_three: bool
    t_order_three: bool
    actions_commute: bool

    @property
    def all_relations_compatible(self) -> bool:
        """Return whether every local comparison preserves its presentation."""

        return all(item.relation_compatible for item in self.comparisons)

    @property
    def exact(self) -> bool:
        """Return all local, overlap, and deck-group gates."""

        return (
            len(self.comparisons) == 12
            and self.all_relations_compatible
            and self.overlap_equivariant
            and self.p_order_three
            and self.t_order_three
            and self.actions_commute
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one global linearization without claiming an outer cone."""

        return {
            "constituent": self.constituent,
            "comparison_count": len(self.comparisons),
            "comparisons": [item.as_record() for item in self.comparisons],
            "all_relations_compatible": self.all_relations_compatible,
            "overlap_equivariant": self.overlap_equivariant,
            "p_order_three": self.p_order_three,
            "t_order_three": self.t_order_three,
            "actions_commute": self.actions_commute,
            "exact": self.exact,
        }


def _comparison(
    result: PublishedConstituentFullCech,
    generator: str,
    source: BlowupChart,
    target: BlowupChart,
    chart_action: DP9DeckChartAction,
    resolution_action: ResolutionAction,
    source_character: Eisenstein,
    middle_shifts: tuple[Shift, ...],
    relation_shifts: tuple[Shift, ...],
) -> ConstituentDeckComparison:
    """Build one local comparison from homogeneous frames and line factors."""

    aligned = result.alignment.action
    twist = aligned.p_twist if generator == "P" else aligned.t_twist
    line_character = twist / source_character
    images = _coordinate_images(generator, result.alignment.action.derived.extension.surface_factor)
    middle = (
        _inverse_trivialization(source, middle_shifts)
        .compose(
            _constant_matrix(
                _homogeneous_middle_action(resolution_action, line_character)
            )
        )
        .compose(_pullback(_trivialization(target, middle_shifts), images))
    )
    relations = (
        _inverse_trivialization(source, relation_shifts)
        .compose(_constant_matrix(resolution_action.source_action))
        .compose(_pullback(_trivialization(target, relation_shifts), images))
    )
    source_relation = _localized_relation(
        result,
        source,
        middle_shifts,
        relation_shifts,
    )
    target_relation = _localized_relation(
        result,
        target,
        middle_shifts,
        relation_shifts,
    )
    return ConstituentDeckComparison(
        result.alignment.action.published.name,
        generator,
        source,
        target,
        images,
        line_character,
        middle,
        relations,
        middle.compose(_pullback(target_relation, images))
        == source_relation.compose(relations),
    )


def _overlap_equivariant(
    comparisons: dict[tuple[str, str], ConstituentDeckComparison],
    transitions: dict[tuple[str, str], LaurentMatrix],
) -> bool:
    """Check every deck comparison against every ordered overlap gauge."""

    return all(
        comparisons[(generator, source)]
        .middle.compose(
            _pullback(
                transitions[
                    (
                        comparisons[(generator, source)].target.name,
                        comparisons[(generator, target)].target.name,
                    )
                ],
                comparisons[(generator, source)].coordinate_images,
            )
        )
        == transition.compose(comparisons[(generator, target)].middle)
        for generator in ("P", "T")
        for (source, target), transition in transitions.items()
    )


def _order_three(
    generator: str,
    comparisons: dict[tuple[str, str], ConstituentDeckComparison],
) -> bool:
    """Check three successive semilinear local comparisons equal identity."""

    for source in {chart for _generator, chart in comparisons}:
        first = comparisons[(generator, source)]
        second = comparisons[(generator, first.target.name)]
        third = comparisons[(generator, second.target.name)]
        twice_pulled = _pullback(
            _pullback(third.middle, first.coordinate_images),
            first.coordinate_images,
        )
        product = (
            first.middle
            .compose(_pullback(second.middle, first.coordinate_images))
            .compose(twice_pulled)
        )
        if third.target.name != source or not product.is_identity():
            return False
    return True


def _commute(
    comparisons: dict[tuple[str, str], ConstituentDeckComparison],
) -> bool:
    """Check the two semilinear deck comparisons commute on every chart."""

    for source in {chart for _generator, chart in comparisons}:
        p = comparisons[("P", source)]
        t = comparisons[("T", source)]
        t_after_p = comparisons[("T", p.target.name)]
        p_after_t = comparisons[("P", t.target.name)]
        if t_after_p.target != p_after_t.target:
            return False
        left = p.middle.compose(_pullback(t_after_p.middle, p.coordinate_images))
        right = t.middle.compose(_pullback(p_after_t.middle, t.coordinate_images))
        if left != right:
            return False
    return True


def _deck_atlas(
    result: PublishedConstituentFullCech,
    overlap: PublishedConstituentOverlapAtlas,
    factor_index: int,
) -> PublishedConstituentDeckAtlas:
    """Construct and certify one complete constituent deck linearization."""

    charts = {chart.name: chart for chart in tier_a_pencil_model().blowup_atlas.charts}
    chart_actions = {
        (action.generator, action.source_chart): action
        for action in dp9_deck_atlas_audit().actions
    }
    resolution_pair = tier_a_resolution_actions()[factor_index]
    generator_count = len(result.alignment.action.derived.extension.generator_bundles)
    syzygy_count = len(result.alignment.action.derived.extension.syzygy_bundles)
    middle_shifts = _middle_shifts(generator_count)
    relation_shifts = _relation_shifts(syzygy_count)
    generated = []
    for generator, source_character in zip(
        ("P", "T"),
        result.alignment.source_character,
        strict=True,
    ):
        for source in charts.values():
            chart_action = chart_actions[(generator, source.name)]
            target = charts[chart_action.target_chart]
            generated.append(
                _comparison(
                    result,
                    generator,
                    source,
                    target,
                    chart_action,
                    resolution_pair.action(generator),
                    source_character,
                    middle_shifts,
                    relation_shifts,
                )
            )
    by_comparison = {
        (item.generator, item.source.name): item for item in generated
    }
    transitions = {
        (item.source.name, item.target.name): _localized_transition(
            item.transition,
            item.source,
            item.target,
            middle_shifts,
        )
        for item in overlap.transitions
    }
    atlas = PublishedConstituentDeckAtlas(
        result.alignment.action.published.name,
        tuple(generated),
        _overlap_equivariant(by_comparison, transitions),
        _order_three("P", by_comparison),
        _order_three("T", by_comparison),
        _commute(by_comparison),
    )
    if not atlas.exact:
        raise ValueError("a selected constituent deck atlas failed")
    return atlas


@cache
def published_constituent_deck_atlases(
) -> tuple[PublishedConstituentDeckAtlas, ...]:
    """Return exact P/T linearizations of both selected constituent atlases."""

    return tuple(
        _deck_atlas(result, overlap, index)
        for index, (result, overlap) in enumerate(
            zip(
                published_constituent_full_cech(),
                published_constituent_overlap_atlases(),
                strict=True,
            )
        )
    )


def write_published_constituent_deck_atlases(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed constituent deck-atlas certificate."""

    atlases = published_constituent_deck_atlases()
    payload: dict[str, object] = {
        "schema": "published-constituent-deck-atlases-v1",
        "atlases": [atlas.as_record() for atlas in atlases],
        "all_constituent_deck_atlases_exact": all(atlas.exact for atlas in atlases),
        "local_line_frame_factors_included": True,
        "projective_resolution_commutators_used_as_group_law": False,
        "outer_rank_four_extension_reconstructed": False,
        "next_required_object": (
            "rebuild the synchronized Schoen outer and Higgs transfers from "
            "the mixed, deck-linearized constituent atlases"
        ),
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
    """Regenerate both exact constituent deck-atlas certificates."""

    payload = write_published_constituent_deck_atlases()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_constituent_deck_atlases_exact: "
        f"{payload['all_constituent_deck_atlases_exact']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ConstituentDeckComparison",
    "PublishedConstituentDeckAtlas",
    "published_constituent_deck_atlases",
]
