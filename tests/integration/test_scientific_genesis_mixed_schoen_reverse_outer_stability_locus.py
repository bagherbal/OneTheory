"""Test the exact stable locus of the reverse mixed family.

Owns:
    Orientation-swapped lower-bound rows, rational chamber bounds, parameter
    quantification, structure-group exclusion, and artifact integrity.

Depends on:
    The lawful reverse P5 cone and published extension-stability results.

Must not:
    Guess exchanged inequalities, select a projective point, infer a spectrum,
    or claim a computed HYM metric.

Phase 0:
    Reverse stable genuine-SU(4) regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.visible import STABILITY_ROWS
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_outer_stability_locus import (
    FORWARD_FORCED_CLASS,
    OUTPUT,
    REVERSE_ANCHOR_VALUES,
    REVERSE_FORCED_CLASS,
    mixed_schoen_reverse_outer_stability_locus,
)


def test_reverse_lower_bound_changes_only_the_forced_subobject() -> None:
    """Reversing the extension preserves all eight proper-pair rows."""

    locus = mixed_schoen_reverse_outer_stability_locus()
    record = locus.as_record()
    change = record["orientation_change"]

    assert change["unchanged_proper_pair_inequality_count"] == 8
    assert change["forward_forced_subobject_c1"] == list(FORWARD_FORCED_CLASS)
    assert change["reverse_forced_subobject_c1"] == list(REVERSE_FORCED_CLASS)
    assert change["factor_exchange_assumed"] is False
    assert change["inequalities_guessed"] is False
    reverse_classes = {item.line_class for item in locus.inequalities}
    forward_proper_classes = {
        line_class
        for line_class, _coefficients, _anchor, _linear, _quadratic in STABILITY_ROWS
        if line_class != FORWARD_FORCED_CLASS
    }
    reverse_proper_classes = reverse_classes - {REVERSE_FORCED_CLASS}
    assert tuple(item.line_class for item in locus.inequalities).count(
        REVERSE_FORCED_CLASS
    ) == 1
    assert FORWARD_FORCED_CLASS not in reverse_classes
    assert reverse_proper_classes == forward_proper_classes


def test_reverse_rational_box_is_strictly_stable() -> None:
    """Every sufficient reverse slope stays negative on an open box."""

    locus = mixed_schoen_reverse_outer_stability_locus()

    assert locus.anchor == (Rational(3), Rational(2), Rational(2))
    assert locus.anchor_values == REVERSE_ANCHOR_VALUES
    assert locus.box_radius == Rational(1, 4)
    assert locus.box_is_stable
    assert all(value < 0 for value in locus.box_upper_bounds)
    assert locus.all_nonzero_parameters_stable_in_chamber


def test_reverse_stable_locus_has_genuine_su4_without_a_point() -> None:
    """Stable rank four plus nonzero cover c3 closes the reduction gate."""

    locus = mixed_schoen_reverse_outer_stability_locus()
    record = locus.as_record()

    assert locus.cover_c3 == Rational(-54)
    assert locus.genuine_su4_on_certified_locus
    assert record["extension_parameter_space"] == "P^5(Q(omega))"
    assert record["certified_stable_locus"] == (
        "P^5(Q(omega)) x K_reverse^s"
    )
    assert record["parameter_quantifier"]["every_nonzero_parameter"] is True
    assert record["arbitrary_extension_point_selected"] is False


def test_reverse_stability_artifact_is_current_and_content_addressed() -> None:
    """The frozen reverse certificate matches its exact reconstruction."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == mixed_schoen_reverse_outer_stability_locus().as_record()
