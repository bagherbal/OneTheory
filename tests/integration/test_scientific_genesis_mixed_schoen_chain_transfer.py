"""Integration tests for the lawful mixed-Schoen ambient transfer."""

from __future__ import annotations

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    OUTPUT,
    _full_action,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_transfer import (
    _include,
    _reduced_entries,
    raw_contraction_witness,
    transferred_column,
)


def test_grouped_cech_contraction_and_hpl_column_are_exact() -> None:
    """The derived sign conjugation closes before producing an exact column."""

    witness = raw_contraction_witness(0, 0)
    column = transferred_column(0, 0)

    assert witness.input_term_count == 100
    assert witness.residual_term_count == 0
    assert witness.exact
    assert column.path_depth == 6
    assert column.entries == (
        (821, Eisenstein(1)),
        (1221, Eisenstein(6, 6)),
        (1222, Eisenstein(3, 6)),
        (1281, Eisenstein(3, 6)),
        (1296, Eisenstein(3, 3)),
    )


def test_sparse_chain_actions_retain_exact_group_laws() -> None:
    """Eager action cancellation preserves order three and commutation."""

    source = _include(_reduced_entries(0)[0])
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for name in ("P", "T"):
        image = source
        for _power in range(3):
            image = _full_action(image, actions[name])
        assert image == source
    assert _full_action(_full_action(source, actions["P"]), actions["T"]) == (
        _full_action(_full_action(source, actions["T"]), actions["P"])
    )


def test_required_higgs_transfer_artifact_is_exact_and_fail_closed() -> None:
    """The strict Higgs certificate advances no later Yukawa or vacuum claim."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["required_character"] == [0, 1]
    assert payload["ambient_space_dimensions"] == {"0": 900, "1": 2180, "2": 1539}
    assert payload["character_space_dimensions"] == {"0": 100, "1": 243, "2": 170}
    assert payload["differential_ranks"] == {"0": 100, "1": 142}
    assert payload["character_h1_dimension"] == 1
    assert payload["transferred_differential_squared_zero"] is True
    assert payload["group_relations_exact"] is True
    assert payload["character_bases_exact"] is True
    assert payload["full_representative_is_cycle"] is True
    assert payload["full_representative_has_strict_character"] is True
    assert payload["required_full_cochain"]["term_count"] == 27
    assert payload["physical_higgs_representative_available"] is True
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["yukawa_trace_normalized"] is False
    assert "common-DGA product hull" in payload["next_required_object"]
