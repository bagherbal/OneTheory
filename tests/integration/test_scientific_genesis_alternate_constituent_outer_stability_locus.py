"""Guard the source-scoped alternate stable SU(4) chamber.

Owns:
    Content-addressed checks for the full nonzero parameter quantifier,
    rational open Kähler witness, and unresolved physical spectrum.

Depends on:
    The alternate universal-cone and stability research artifacts.

Must not:
    Convert a sufficient chamber into the complete stable cone or infer
    matter, Higgs, or Yukawa data from stability alone.

Phase 0:
    Research-only regression for the first stable alternate carrier locus.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_stability_locus import (
    OUTPUT,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_universal_cone import (
    OUTPUT as CONE,
)


def test_alternate_stable_locus_is_sufficient_and_not_a_spectrum() -> None:
    """The theorem transfer must retain every source-scope boundary."""

    cone = json.loads(CONE.read_text(encoding="utf-8"))
    cone_digest = cone.pop("artifact_digest")
    assert cone_digest == _canonical_digest(cone)

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == _canonical_digest(record)
    assert record["schema"] == "alternate-constituent-outer-stability-locus-v1"
    assert record["universal_cone_digest"] == cone_digest
    assert record["ray_character_exponents"] == [0, 1]
    assert record["alternate_invariant_ext_dimension"] == 2
    assert record["serre_quotient_ideals_unchanged"] == ["I3", "I6"]
    assert record["serre_line_and_ideal_presentation_type_unchanged"] is True
    assert record["alternate_serre_ray_nontrivial_and_locally_free"] is True
    assert record["common_flat_twist_preserves_slopes"] is True
    assert record["source_stability_bound_uses_serre_sequences_not_ray_coordinates"] is True
    assert record["extension_parameter_space"] == "P^1(Q(omega))"
    assert record["parameter_quantifier"]["every_nonzero_parameter"] is True
    assert record["parameter_quantifier"]["genericity_assumed"] is False
    assert record["all_nonzero_parameters_stable_in_chamber"] is True
    assert record["certified_stable_locus"] == "P^1(Q(omega)) x K^s"
    chamber = record["kahler_chamber"]
    assert len(chamber["inequalities"]) == 9
    assert chamber["anchor"] == ["6", "9", "3"]
    assert all(int(slope) < 0 for slope in chamber["anchor_slopes"])
    assert chamber["rational_open_box"]["all_slopes_negative"] is True
    assert chamber["rational_open_box"]["inside_positive_cone"] is True
    group = record["structure_group"]
    assert group["cover_c3"] == "-54"
    assert group["determinant_trivial"] is True
    assert group["proper_connected_irreducible_reduction_excluded"] is True
    assert group["genuine_su4_on_certified_locus"] is True
    assert record["full_kahler_stability_chamber_computed"] is False
    assert record["physical_spectrum_computed"] is False
    assert record["arbitrary_extension_point_selected"] is False
