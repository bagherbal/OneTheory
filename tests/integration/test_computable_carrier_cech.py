"""Test bounded localized Čech computations as explicit truncations.

Owns:
    Exact restriction incidence, square-zero checks, deterministic monomial
    bases, and explicit non-convergence status for finite section windows.

Depends on:
    The computable-carrier chart cover, bounded Čech section engine, and pytest.

Must not:
    Promote truncated dimensions to sheaf cohomology, infer Ext representatives,
    or claim global generation from a finite window.

Phase 0:
    Bounded research computation only; convergence remains a required gate.
"""

from __future__ import annotations

from research.experiments.computable_carrier.cech_sections import bounded_cech_sections
from research.experiments.computable_carrier.constituents import tier_a_constituents


def test_bounded_cech_sections_have_exact_differentials() -> None:
    """The finite localized complexes satisfy d squared equals zero."""

    candidate = tier_a_constituents()[0]
    sections = bounded_cech_sections(candidate.cover, 1)

    assert sections.bound == 1
    assert sections.complex.cohomology_dimension(0) == 8
    assert sections.complex.cohomology_dimension(1) == 0
    assert sections.complex.cohomology_dimension(2) == 1
    assert all(
        sections.complex.differential(degree + 1).compose(
            sections.complex.differential(degree)
        ).is_zero()
        for degree in (0, 1)
    )


def test_bounded_cech_record_keeps_cutoff_explicit() -> None:
    """The generated basis remains inspectable rather than silently extended."""

    candidate = tier_a_constituents()[1]
    sections = bounded_cech_sections(candidate.cover, 0)

    assert sections.sections_on(0) == ((0, 0, 0),)
    assert sections.sections_on_intersection((0, 1)) == ((0, 0, 0),)
    assert sections.complex.cohomology_dimension(1) == 0
