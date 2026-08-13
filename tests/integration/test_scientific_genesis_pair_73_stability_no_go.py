"""Test the exact scoped pair-73 stability no-go.

Owns:
    Right-line restriction support, lifted-subbundle splitting, opposite slopes,
    and the empty stable locus across the universal pair-73 parameter family.

Depends on:
    Content-addressed pair-73 chain and stability artifacts, exact presentation
    orientation, quotient intersections, and sparse polynomial arithmetic.

Must not:
    Generalize pair 73 to other families, infer structure-group reduction, or
    select an extension coordinate or Kahler polarization.

Phase 0:
    Pair-73 no-go tests only; the next computable carrier family remains open.
"""

import json

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.pair_73_stability_no_go import (
    OUTPUT,
    pair_73_stability_no_go,
)


def test_universal_ext_restricts_trivially_to_the_right_serre_line() -> None:
    """The exact Hom columns prove every pullback extension class is zero."""

    no_go = pair_73_stability_no_go()
    record = no_go.as_record()

    assert no_go.source_hom_support == (20, 21, 22, 23)
    assert no_go.right_line_restriction_indices == (4, 9, 14, 19, 24)
    assert set(no_go.source_hom_support).isdisjoint(no_go.right_line_restriction_indices)
    assert record["restriction_map_zero_on_every_ext_basis_class"] is True
    assert record["restriction_map_zero_on_universal_family"] is True
    assert record["pullback_extension_splits_for_all_parameters"] is True


def test_forced_subbundles_have_opposite_slopes_everywhere() -> None:
    """No polarization can make both forced proper subbundles strictly negative."""

    no_go = pair_73_stability_no_go()
    assert (no_go.left_slope + no_go.lifted_right_line_slope).is_zero()

    for polarization in (
        (Rational(6), Rational(9), Rational(3)),
        (Rational(6), Rational(1), Rational(1)),
        (Rational(1), Rational(1), Rational(1)),
    ):
        left = no_go.left_slope.substitute(polarization).coefficient(())
        lifted = no_go.lifted_right_line_slope.substitute(polarization).coefficient(())
        assert left + lifted == 0
        assert left >= 0 or lifted >= 0


def test_pair_73_stable_locus_is_empty_but_no_go_stays_scoped() -> None:
    """The family is retired without fabricating a global carrier exclusion."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == pair_73_stability_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["affine_slope_stable_locus"] == "empty"
    assert stored["projective_slope_stable_locus"] == "empty"
    assert stored["all_pair_73_parameters_unstable"] is True
    assert stored["pair_73_computable_carrier_route_refuted"] is True
    assert stored["global_schoen_carrier_no_go"] is False
    assert stored["proper_structure_group_reduction_computed"] is False
