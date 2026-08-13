"""Test the universal pair-73 Ext-family certificate.

Owns:
    Exact parameter assembly, basis specialization, split-locus, and quotient
    checks while preserving the missing mapping-cone lift.

Depends on:
    Content-addressed pair-73 certificates and exact polynomial arithmetic.

Must not:
    Select a projective point, claim a rank-four bundle, or infer physical
    local freeness, descent, stability, or spectrum.

Phase 0:
    Universal Ext-family tests only; chain-level carrier construction is open.
"""

import json
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis.pair_73_universal import (
    FIRST_MISSING_INPUT,
    _canonical_digest,
    pair_73_universal_ext_family,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "data/generated/scientific_genesis/pair_73_universal_ext.json"


def test_pair_73_universal_ext_specializes_to_every_certified_basis_class() -> None:
    """The parameter-linear family recovers all four exact source cocycles."""

    family = pair_73_universal_ext_family()

    assert family.parameter_dimension == 4
    assert family.ambient_dimension == 540
    assert family.basis_names == ("class:0", "class:1", "class:2", "class:3")
    assert family.nonzero_coordinate_count == 48
    assert family.universal_class_exact
    for index, column in enumerate(family.basis_columns):
        values = tuple(Eisenstein(int(position == index)) for position in range(4))
        assert family.specialize(values) == column


def test_pair_73_universal_ext_preserves_the_carrier_boundary() -> None:
    """Only the origin splits and no mapping cone or orbit point is fabricated."""

    family = pair_73_universal_ext_family()
    record = family.as_record()

    assert family.specialize((Eisenstein(0),) * 4) == (Eisenstein(0),) * 540
    assert len(family.split_locus_ideal.generators) == 4
    assert record["non_split_locus"] == "A^4(Q(omega)) minus the origin"
    assert record["automorphism_quotient"] == "P^3(Q(omega))"
    assert record["arbitrary_extension_point_selected"] is False
    assert record["mapping_cone_constructed"] is False
    assert record["first_missing_input"] == FIRST_MISSING_INPUT


def test_pair_73_universal_ext_artifact_matches_fresh_reconstruction() -> None:
    """The frozen universal certificate is deterministic and current."""

    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rebuilt = pair_73_universal_ext_family().as_record()
    digest = stored.pop("artifact_digest")

    assert stored == rebuilt
    assert digest == _canonical_digest(stored)
