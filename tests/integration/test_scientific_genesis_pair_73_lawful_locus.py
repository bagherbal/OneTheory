"""Test the exact pair-73 algebraic lawful-locus certificate.

Owns:
    Family-wide local freeness, descent, determinant, Chern, and split-locus
    checks together with the unresolved genuine-SU(4) boundary.

Depends on:
    Content-addressed pair-73 chain and constituent certificates plus exact
    quotient intersection arithmetic.

Must not:
    Infer stability, select an extension point, or promote determinant-trivial
    rank four to a genuine SU(4) physical carrier.

Phase 0:
    Algebraic locus tests only; stability and proper reduction remain open.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.pair_73_lawful_locus import (
    OUTPUT,
    pair_73_algebraic_locus,
)


def test_pair_73_algebraic_locus_is_the_full_nonzero_extension_space() -> None:
    """Local freeness and descent exclude no additional extension parameter."""

    locus = pair_73_algebraic_locus()
    record = locus.as_record()

    assert record["algebraic_lawful_locus"] == "A^4(Q(omega)) minus the origin"
    assert record["projective_algebraic_lawful_locus"] == "P^3(Q(omega))"
    assert record["local_freeness_excluded_locus"] == "empty"
    assert record["descent_excluded_locus"] == "empty"
    assert locus.extension_local_freeness_exact
    assert locus.invariant_descent_exact
    assert locus.non_split_locus_exact


def test_pair_73_chern_data_are_exact_and_parameter_independent() -> None:
    """The extension identity fixes rank, determinant, and Chern classes."""

    record = pair_73_algebraic_locus().as_record()
    chern = record["chern_classes"]

    assert record["rank"] == 4
    assert record["determinant_trivial"] is True
    assert chern["c1_left"] == ["2", "-2", "0"]
    assert chern["c1_right"] == ["-2", "2", "0"]
    assert chern["c1_total"] == ["0", "0", "0"]
    assert chern["c2_total"] == ["2/3", "5/3", "4"]
    assert chern["integral_c3_total"] == "-6"
    assert chern["quotient_index"] == "-3"
    assert chern["parameter_independent"] is True


def test_pair_73_locus_keeps_genuine_su4_fail_closed() -> None:
    """Trivial determinant does not silently prove stability or irreducibility."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == pair_73_algebraic_locus().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["arbitrary_extension_point_selected"] is False
    assert stored["genuine_su4_locus_computed"] is False
    assert "stability chamber" in stored["genuine_su4_first_missing_input"]
