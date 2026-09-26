"""Guard the exact alternate universal cone without promoting stability.

Owns:
    Content-addressed rank, split, descent, determinant, and topology gates
    over the full invariant ray (0,1) parameter space.

Depends on:
    The generated alternate cone and invariant-Ext certificates.

Must not:
    Treat a non-split locally free cone as a stable physical SU(4) carrier.

Phase 0:
    Research-only regression for the next carrier prerequisite.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_invariants import (
    OUTPUT as INVARIANTS,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_universal_cone import (
    OUTPUT,
)


def test_alternate_universal_cone_is_exact_but_not_yet_stable() -> None:
    """The two-parameter cone must retain its scientific boundary."""

    invariant = json.loads(INVARIANTS.read_text(encoding="utf-8"))
    invariant_digest = invariant.pop("artifact_digest")
    assert invariant_digest == _canonical_digest(invariant)

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == _canonical_digest(record)
    assert record["schema"] == "alternate-constituent-outer-universal-cone-v1"
    assert record["invariant_artifact_digest"] == invariant_digest
    assert record["ray_character_exponents"] == [0, 1]
    assert record["cover_ext1_dimension"] == 18
    assert record["invariant_ext1_dimension"] == 2
    assert record["parameters"] == ["a0", "a1"]
    assert record["projective_non_split_space"] == "P^1(Q(omega))"
    assert record["split_locus"]["ideal_generators"] == ["a0", "a1"]
    assert record["basis_term_counts"] == [38703, 32448]
    assert record["universal_term_count"] > max(record["basis_term_counts"])
    assert record["generated_complex"]["orientation"] == "RHom(V2,V1)"
    assert record["generated_complex"]["squared_zero"] is True
    assert record["strict_basis_rechecked_from_saved_terms"] is True
    assert record["constituent_graded_line_objects_match_published_selected_ray"] is True
    assert record["rank"] == 4
    assert record["chern_classes"]["c1"] == ["0", "0", "0"]
    assert record["chern_classes"]["c2"] == ["8/3", "5/3", "4"]
    assert record["chern_classes"]["c3"] == "-6"
    assert record["rational_chern_data_only"] is True
    assert record["equivariant_descent_exact"] is True
    assert record["determinant_character_before_common_twist"] == [2, 1]
    assert record["common_flat_character_twist"] == [1, 2]
    assert record["determinant_character_after_common_twist"] == [0, 0]
    assert record["common_twist_cancels_in_outer_hom"] is True
    assert record["quotient_determinant_trivial_exact"] is True
    assert record["local_freeness_locus"] == "all A^2(Q(omega))"
    assert record["arbitrary_extension_point_selected"] is False
    assert record["stability_chamber_certified"] is False
    assert record["genuine_su4_locus_computed"] is False
    assert record["physical_higgs_cocycles_available"] is False
