"""Test exact line-bundle Koszul complexes on the Schoen cover.

Owns:
    Small exact regression cases for the ambient Künneth basis, the two
    Schoen equations, and factor-polynomial chain maps.

Depends on:
    The research-only Schoen cover line-bundle module.

Must not:
    Treat cover cohomology as quotient-invariant Ext or promote a line bundle
    to a physical constituent.

Phase 0:
    These tests certify only the reusable cover calculation boundary.
"""

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.schoen_linebundles import (
    schoen_line_bundle,
)


def test_trivial_cover_line_bundle_has_calabi_yau_cohomology() -> None:
    """The exact Koszul model gives one section and one top form."""

    line = schoen_line_bundle(0, 0, 0)

    assert line.squared_zero
    assert line.cohomology_dimensions == ((0, 1), (1, 0), (2, 0), (3, 1))


def test_negative_fiber_line_bundle_is_computed_exactly() -> None:
    """A nontrivial fiber twist exercises the P1 top cohomology block."""

    line = schoen_line_bundle(0, 0, -1)

    assert line.squared_zero
    assert line.cohomology_dimensions == ((0, 0), (1, 0), (2, 2), (3, 2))


def test_x_factor_multiplication_is_a_typed_chain_map() -> None:
    """Multiplication by an x-coordinate preserves the two-equation cone."""

    source = schoen_line_bundle(0, 0, 0)
    target = schoen_line_bundle(1, 0, 0)
    x0 = Polynomial.monomial((1, 0, 0), scalar_type=Eisenstein)

    multiplication = source.multiplication(target, x0, "x")

    assert multiplication.source == source.complex
    assert multiplication.target == target.complex
