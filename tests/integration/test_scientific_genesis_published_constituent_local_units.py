"""Test local dualizing-unit evaluations of the selected W1/W2 rays.

Owns:
    Six support evaluations, residue cokernels, fiber-chart independence,
    lci unit criteria, local freeness scope, and artifact addressing.

Depends on:
    The Scientific Genesis local constituent-unit experiment.

Must not:
    Promote stalkwise units to global transitions or quotient descent.

Phase 0:
    Selected constituent local-unit regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_local_units import (
    OUTPUT,
    published_constituent_local_units,
)


def test_all_six_selected_stalk_classes_are_dualizing_units() -> None:
    """Each selected mixed ray has nonzero residue in the one-dimensional cokernel."""

    units = published_constituent_local_units()

    assert len(units) == 6
    assert tuple(unit.constituent for unit in units) == ("I3",) * 3 + ("I6",) * 3
    assert all(unit.local_ext_residue_dimension == 1 for unit in units)
    assert all(unit.every_chart_nonzero_in_cokernel for unit in units)
    assert all(unit.unit_in_local_dualizing_algebra for unit in units)


def test_both_fiber_chart_evaluations_define_the_same_local_ext_class() -> None:
    """The full Čech lift changes chart representatives only by boundaries."""

    units = published_constituent_local_units()

    assert all(len(unit.chart_values) == 2 for unit in units)
    assert all(unit.chart_independent_modulo_boundaries for unit in units)


def test_local_unit_artifact_is_current_and_content_addressed() -> None:
    """The frozen six-stalk certificate retains the global-gluing boundary."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["unit_count"] == 6
    assert stored["all_selected_rays_are_local_units"] is True
    assert stored["constituent_middle_terms_locally_free_at_support"] is True
    assert stored["global_transition_matrices_materialized"] is False
