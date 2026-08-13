"""Test the exact unavoidable stability walls of the pair-73 family.

Owns:
    Symbolic slope identities, forced Serre subobjects, anchor exclusion, and
    the fail-closed boundary between necessary walls and sufficient stability.

Depends on:
    The content-addressed pair-73 lawful locus, exact quotient intersections,
    sparse polynomial arithmetic, and the necessary-wall research artifact.

Must not:
    Select a polarization or extension point, or promote necessary inequalities
    and published cone membership to genuine SU(4).

Phase 0:
    Necessary-wall tests only; the complete stability chamber remains open.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.pair_73_stability_wall import (
    OUTPUT,
    pair_73_stability_wall,
)


def _variables() -> tuple[Polynomial, Polynomial, Polynomial]:
    return (
        Polynomial.monomial((1, 0, 0)),
        Polynomial.monomial((0, 1, 0)),
        Polynomial.monomial((0, 0, 1)),
    )


def test_forced_subobjects_have_exact_symbolic_slopes() -> None:
    """Every unavoidable subobject contracts with the quotient tensor exactly."""

    wall = pair_73_stability_wall()
    x, y, z = _variables()
    common = (y - x) * (x + y + z.scale(6))

    assert wall.left_slope == common.scale(Rational(1, 3))
    assert wall.right_preimage_slope == common.scale(Rational(1, 9))
    assert wall.left_line_slope == (
        -(x**2)
        + (x * y).scale(6)
        + (y**2).scale(4)
        - (x * z).scale(6)
        + (y * z).scale(24)
    ).scale(Rational(1, 3))


def test_published_anchor_excludes_the_entire_pair_73_family() -> None:
    """The extension-independent subbundles destabilize at the carrier anchor."""

    wall = pair_73_stability_wall()
    record = wall.as_record()

    assert wall.published_anchor_left_slope == Rational(33)
    assert wall.published_anchor_left_line_slope == Rational(384)
    assert record["published_anchor"]["pair_73_stable_there"] is False
    assert record["parameter_dependence"] == (
        "none; the forced sequences occur over the full family"
    )


def test_necessary_region_has_an_exact_kahler_cone_intersection() -> None:
    """A derived ray family proves cone compatibility without selecting data."""

    wall = pair_73_stability_wall()
    consequence = wall.as_record()["positive_coordinate_consequence"]
    for parameter in (6, 7, 19):
        values = (Rational(parameter), Rational(1), Rational(1))
        assert wall.left_slope.substitute(values).coefficient(()) < 0
        assert wall.left_line_slope.substitute(values).coefficient(()) < 0
        assert wall.right_preimage_slope.substitute(values).coefficient(()) < 0
    assert consequence["kahler_cone"] == "j1 > 0, j2 > 0, j3 > 0"
    assert consequence["kahler_cone_source"] == "hep-th/0602073v1"
    assert consequence["kahler_cone_locator"] == "eq. (33)"
    assert consequence["kahler_intersection_nonempty"] is True
    assert consequence["full_kahler_cone_membership_proved"] is True


def test_stability_wall_artifact_keeps_sufficiency_fail_closed() -> None:
    """Necessary walls never become a fabricated complete chamber theorem."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == pair_73_stability_wall().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["necessary_wall_computed"] is True
    assert stored["positive_coordinate_consequence"]["full_kahler_cone_membership_proved"] is True
    assert stored["sufficient_stability_chamber_computed"] is False
    assert stored["genuine_su4_locus_computed"] is False
    assert stored["arbitrary_extension_point_selected"] is False
    assert stored["arbitrary_polarization_selected"] is False
