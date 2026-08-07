"""Construct the published deck action on the exact dP9 blow-up atlas.

Owns:
    Exact affine P/T maps between all six cubic-pencil blow-up charts,
    including derived fiber-coordinate scalings, hypersurface equation units,
    order-three certificates, and affine commutator checks.

Depends on:
    The published homogeneous coordinate lifts, exact Schoen cubic pencil, and
    the existing six-chart blow-up equations over the Eisenstein field.

Must not:
    Attach a candidate bundle to the atlas, infer quotient descent for a
    sheaf, choose physical extension data, or hide projective lift scalars.

Phase 0:
    The geometric deck action on the presentation dP9 atlas is exact; bundle
    frame descent and physical promotion remain separate gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .dp9_actions import CoordinateImage, published_coordinate_images
from .pencil import (
    BlowupChart,
    _source_projective_coordinates,
    tier_a_pencil_model,
)

CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)


def _affine_coordinate_indices(pivot: int) -> tuple[int, int]:
    """Return global coordinate indices represented by local ``u`` and ``v``."""

    if pivot == 0:
        return 1, 2
    if pivot == 1:
        return 0, 2
    if pivot == 2:
        return 0, 1
    raise ValueError("projective pivots are 0, 1, and 2")


def _source_coordinate_image(
    global_index: int,
    source_pivot: int,
) -> tuple[Eisenstein, tuple[int, ...]]:
    """Return one homogeneous source coordinate in local affine variables."""

    exponents = _source_projective_coordinates(source_pivot)[global_index]
    return Eisenstein(1), exponents


def _homogeneous_local_images(
    source_pivot: int,
    images: CoordinateImage,
) -> tuple[tuple[Eisenstein, tuple[int, ...]], ...]:
    """Express transformed homogeneous coordinates in one source chart."""

    result = []
    for coefficient, exponents in images:
        nonzero = tuple(index for index, power in enumerate(exponents) if power)
        if len(nonzero) != 1 or exponents[nonzero[0]] != 1:
            raise ValueError("published deck lifts must be linear monomials")
        _, local_exponents = _source_coordinate_image(nonzero[0], source_pivot)
        result.append((coefficient, local_exponents))
    return tuple(result)


def _target_pivot(
    source_pivot: int,
    homogeneous_images: tuple[tuple[Eisenstein, tuple[int, ...]], ...],
) -> int:
    """Find the transformed coordinate normalized on one source chart."""

    candidates = tuple(
        index
        for index, (coefficient, exponents) in enumerate(homogeneous_images)
        if not coefficient.is_zero() and exponents == (0, 0, 0)
    )
    if len(candidates) != 1:
        raise ValueError(
            f"deck action does not map source pivot {source_pivot} monomially"
        )
    return candidates[0]


def _base_affine_images(
    source_pivot: int,
    images: CoordinateImage,
) -> tuple[int, tuple[tuple[Eisenstein, tuple[int, ...]], ...]]:
    """Return target pivot and normalized target base coordinates."""

    homogeneous = _homogeneous_local_images(source_pivot, images)
    target_pivot = _target_pivot(source_pivot, homogeneous)
    denominator_coefficient, denominator_exponents = homogeneous[target_pivot]
    if denominator_exponents != (0, 0, 0):
        raise ValueError("target pivot must be a unit on the source chart")
    affine = []
    for global_index in _affine_coordinate_indices(target_pivot):
        coefficient, exponents = homogeneous[global_index]
        affine.append((coefficient / denominator_coefficient, exponents))
    return target_pivot, tuple(affine)


def _character(original: Polynomial, transformed: Polynomial) -> Eisenstein:
    """Find the exact cubic-root character relating two homogeneous cubics."""

    matches = tuple(
        character
        for character in CHARACTERS
        if transformed == original.scale(character)
    )
    if len(matches) != 1:
        raise ValueError("deck lift does not act on the cubic by one character")
    return matches[0]


@cache
def _cubic_characters(generator: str) -> tuple[Eisenstein, Eisenstein]:
    """Derive deck characters of the two exact pencil cubics."""

    cox = schoen_geometry().cover.cox
    images = published_coordinate_images(generator)
    return (
        _character(cox.cubic_f, cox.cubic_f.substitute_monomials(images)),
        _character(cox.cubic_g, cox.cubic_g.substitute_monomials(images)),
    )


def _fiber_image(
    generator: str,
    fiber_chart: str,
) -> tuple[tuple[Eisenstein, tuple[int, ...]], Eisenstein]:
    """Derive target fiber coordinate and equation unit from cubic characters."""

    f_character, g_character = _cubic_characters(generator)
    fiber_exponents = (0, 0, 1)
    if fiber_chart == "mu":
        return (f_character / g_character, fiber_exponents), f_character
    if fiber_chart == "nu":
        return (g_character / f_character, fiber_exponents), g_character
    raise ValueError("dP9 fiber charts are mu and nu")


def _compose_images(
    first: CoordinateImage,
    second: CoordinateImage,
) -> CoordinateImage:
    """Compose source-to-middle and middle-to-target monomial chart maps."""

    result = []
    for second_coefficient, second_exponents in second:
        coefficient = second_coefficient
        exponents = [0, 0, 0]
        for power, (first_coefficient, first_exponents) in zip(
            second_exponents,
            first,
            strict=True,
        ):
            coefficient *= first_coefficient**power
            for index, exponent in enumerate(first_exponents):
                exponents[index] += power * exponent
        result.append((coefficient, tuple(exponents)))
    return tuple(result)


def _identity_images() -> CoordinateImage:
    """Return the identity monomial map in three affine variables."""

    return tuple(
        (
            Eisenstein(1),
            tuple(1 if row == column else 0 for column in range(3)),
        )
        for row in range(3)
    )


@dataclass(frozen=True, slots=True)
class DP9DeckChartAction:
    """One exact affine deck map between two dP9 blow-up charts."""

    generator: str
    source_chart: str
    target_chart: str
    coordinate_images: CoordinateImage
    equation_unit: Eisenstein
    equation_compatible: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the full monomial chart map and equation certificate."""

        return {
            "generator": self.generator,
            "source_chart": self.source_chart,
            "target_chart": self.target_chart,
            "coordinate_images": [
                {
                    "coefficient": str(coefficient),
                    "exponents": list(exponents),
                }
                for coefficient, exponents in self.coordinate_images
            ],
            "equation_unit": str(self.equation_unit),
            "equation_compatible": self.equation_compatible,
        }


@dataclass(frozen=True, slots=True)
class DP9DeckAtlasAudit:
    """Complete P/T action audit on the six-chart dP9 atlas."""

    actions: tuple[DP9DeckChartAction, ...]
    p_order_three: bool
    t_order_three: bool
    actions_commute: bool

    @property
    def exact(self) -> bool:
        """Return whether every geometric deck-action gate passes exactly."""

        return (
            len(self.actions) == 12
            and all(action.equation_compatible for action in self.actions)
            and self.p_order_three
            and self.t_order_three
            and self.actions_commute
        )

    def as_record(self) -> dict[str, object]:
        """Serialize all chart maps without attaching a bundle candidate."""

        return {
            "actions": [action.as_record() for action in self.actions],
            "action_count": len(self.actions),
            "cubic_characters": {
                generator: [str(value) for value in _cubic_characters(generator)]
                for generator in ("P", "T")
            },
            "p_order_three": self.p_order_three,
            "t_order_three": self.t_order_three,
            "actions_commute": self.actions_commute,
            "exact": self.exact,
            "status": (
                "exact geometric deck action on the six-chart dP9 atlas; "
                "candidate frame descent remains a separate gate"
            ),
        }


def _chart_action(
    generator: str,
    source: BlowupChart,
    charts: dict[tuple[int, str], BlowupChart],
) -> DP9DeckChartAction:
    """Construct one affine chart action and verify its equation unit."""

    target_pivot, base_images = _base_affine_images(
        source.base_pivot,
        published_coordinate_images(generator),
    )
    fiber_image, equation_unit = _fiber_image(generator, source.fiber_chart)
    target = charts[(target_pivot, source.fiber_chart)]
    affine_images = (*base_images, fiber_image)
    pulled_equation = target.equation.substitute_monomials(affine_images)
    return DP9DeckChartAction(
        generator,
        source.name,
        target.name,
        affine_images,
        equation_unit,
        pulled_equation == source.equation.scale(equation_unit),
    )


def _order_three(
    generator: str,
    actions: dict[tuple[str, str], DP9DeckChartAction],
    chart_names: tuple[str, ...],
) -> bool:
    """Check three successive affine chart maps equal the identity."""

    for source in chart_names:
        first = actions[(generator, source)]
        second = actions[(generator, first.target_chart)]
        third = actions[(generator, second.target_chart)]
        if third.target_chart != source:
            return False
        composed = _compose_images(first.coordinate_images, second.coordinate_images)
        composed = _compose_images(composed, third.coordinate_images)
        if composed != _identity_images():
            return False
    return True


def _commute(
    actions: dict[tuple[str, str], DP9DeckChartAction],
    chart_names: tuple[str, ...],
) -> bool:
    """Check P-then-T and T-then-P affine maps agree on every chart."""

    for source in chart_names:
        p_first = actions[("P", source)]
        p_then_t = actions[("T", p_first.target_chart)]
        t_first = actions[("T", source)]
        t_then_p = actions[("P", t_first.target_chart)]
        if p_then_t.target_chart != t_then_p.target_chart:
            return False
        left = _compose_images(
            p_first.coordinate_images,
            p_then_t.coordinate_images,
        )
        right = _compose_images(
            t_first.coordinate_images,
            t_then_p.coordinate_images,
        )
        if left != right:
            return False
    return True


@cache
def dp9_deck_atlas_audit() -> DP9DeckAtlasAudit:
    """Return the complete exact deck action on the dP9 blow-up atlas."""

    model = tier_a_pencil_model()
    charts = {
        (chart.base_pivot, chart.fiber_chart): chart
        for chart in model.blowup_atlas.charts
    }
    generated = tuple(
        _chart_action(generator, chart, charts)
        for generator in ("P", "T")
        for chart in model.blowup_atlas.charts
    )
    by_source = {
        (action.generator, action.source_chart): action
        for action in generated
    }
    chart_names = tuple(chart.name for chart in model.blowup_atlas.charts)
    audit = DP9DeckAtlasAudit(
        generated,
        _order_three("P", by_source, chart_names),
        _order_three("T", by_source, chart_names),
        _commute(by_source, chart_names),
    )
    if not audit.exact:
        raise ValueError("dP9 deck atlas failed exact action gates")
    return audit


__all__ = [
    "DP9DeckAtlasAudit",
    "DP9DeckChartAction",
    "dp9_deck_atlas_audit",
]
