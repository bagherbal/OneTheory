"""Independently verify actual down and charged-lepton mixed scalar witnesses.

Owns:
    Original constituent cycles and characters, separate Hom-composition
    scalar identities, quotient traces, missing-input guards, and scope attacks.

Depends on:
    Literal same-carrier inputs, original exact Hom and contraction engines,
    the archived mixed scalar packet, and pytest.

Must not:
    Reuse up/neutrino values, infer F-F blocks or physical matrices, select
    parameters, or treat negative-control mutations as scientific evidence.

Phase 0:
    Conditional heterotic holomorphic research verification; metrics remain open.
"""

import json

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions
from research.experiments.scientific_genesis import alternate_down_lepton_mixed_pairing as mixed
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import _common_frame
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import _contract
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    _constituent,
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_outer_yoneda import compose_outer_cochains
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
    _perturbed_projection,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)


def _saved():
    return mixed.load_mixed_pairing(
        expected_digest="ae7f62edaf3621af9b8dc8142f597218cd5426b8b922fd9b6b1e8ae2cb1ed1b1",
    )


def test_actual_mixed_inputs_keep_full_cycles_and_original_atlas_characters() -> None:
    """Check every literal matter input and both strict deck generators."""

    _, witnesses = _saved()
    first = mixed_schoen_constituents()[0]
    second = mixed.alternate_higgs_quotient_models()[0]
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for sector, characters in enumerate(mixed.CHARACTERS):
        for side, character in zip(("row", "column"), characters, strict=True):
            objects = [(witnesses[f"first_s{sector}_{side}"], first)] + [
                (witnesses[f"second_s{sector}_{side}_f{family}"], second) for family in (1, 2)
            ]
            for cycle, constituent in objects:
                context = _MixedContraction(constituent, mixed_schoen_unit())
                assert context.differential(cycle).is_zero()
                for index, name in enumerate(("P", "T")):
                    frame = (_common_frame(constituent, actions[name]),
                             Matrix.identity(1, scalar_type=Eisenstein))
                    assert _full_action(cycle, context.left, context.right,
                                        actions[name], frame) == cycle.scale(
                        OMEGA**character[index],
                    )


def test_all_eight_actual_scalars_equal_independent_full_hom_composition() -> None:
    """The separate verification path uses no quotient mixed-product evaluator."""

    record, witnesses = _saved()
    first = mixed_schoen_constituents()[0]
    ray = lift_joint_character_ray(published_constituent_deck_actions()[1], 1, OMEGA)
    second = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    determinant = MixedSchoenUnit("det V1", 0, (-2, 2, 0), (
        MixedConstituentObject("det V1", 0, (-2, 2, 0)),
    ))
    hom_context = _MixedContraction(first, second)
    matter_context = _MixedContraction(second, determinant)
    target = _MixedContraction(first, determinant)
    hom = witnesses["actual_down_higgs_hom"]
    assert hom_context.differential(hom).is_zero()
    for sector in record["sectors"]:
        s = sector["sector"]
        for entry in sector["evaluated_entries"]:
            row, column = entry["row"], entry["column"]
            first_side, second_side, family = (("row", "column", column) if row == 0
                                               else ("column", "row", row))
            vector = witnesses[f"second_s{s}_{second_side}_f{family}"]
            assert matter_context.differential(vector).is_zero()
            evaluated = compose_outer_cochains(hom, vector, target.components,
                left_middle=hom_context.right, right_middle=matter_context.left)
            assert target.differential(evaluated).is_zero()
            independent = _contract(witnesses[f"first_s{s}_{first_side}"], evaluated).scale(-1)
            prefix = f"s{s}_r{row}_c{column}"
            scalar = witnesses[f"{prefix}_scalar"]
            reverse = witnesses[f"{prefix}_reverse"]
            primitive = witnesses[f"{prefix}_exchange_primitive"]
            assert scalar == independent
            assert mixed.engine._scalar_context().differential(scalar).is_zero()
            assert mixed.engine._scalar_context().differential(primitive) == (
                reverse + scalar.scale(-1)
            )
            direct = mixed.engine.direct_ordered_scalar_residue(independent)
            projection, _ = _perturbed_projection(scalar, mixed.engine._scalar_context(), 3)
            assert projection == {0: direct}
            assert entry["cover_residue"] == str(direct)
            assert entry["quotient_residue"] == str(direct * Rational(1, 9))


def test_mixed_producer_reproduces_all_literal_inputs_and_archive_bytes(tmp_path) -> None:
    """All eight actual entries reproduce without filling either F-F block."""

    record, _ = _saved()
    path = tmp_path / mixed.OUTPUT.name
    assert mixed.write_mixed_pairing(path) == record
    assert path.read_bytes() == mixed.OUTPUT.read_bytes()
    assert path.with_suffix(".cochains.json.gz").read_bytes() == (
        mixed.OUTPUT.with_suffix(".cochains.json.gz").read_bytes()
    )
    assert record["Q_first_class_reproduced_from_existing_generator"] is True
    assert record["Q_and_L_matter_corrections_recomputed"] is False
    assert record["first_first_entry_zero_by_B_wedge_B"] is True
    assert record["second_second_entries_assigned"] is False


def test_missing_mixed_packet_has_no_generation_or_solver_fallback(tmp_path, monkeypatch) -> None:
    def forbidden_generation(*args, **kwargs):
        raise AssertionError("an absent read-only mixed result must not trigger a calculation")

    monkeypatch.setattr(mixed, "matter_inputs", forbidden_generation)
    monkeypatch.setattr(mixed, "actual_higgs", forbidden_generation)
    with pytest.raises(FileNotFoundError):
        mixed.load_mixed_pairing(tmp_path / mixed.OUTPUT.name, expected_digest="0"*64)


@pytest.mark.parametrize("field,value", (
    ("outer_parameter_basis", ["a1", "a0"]), ("cover_to_quotient_trace_factor", "1"),
    ("native_down_higgs_hom_character", [2, 0]),
    ("Q_and_L_matter_corrections_recomputed", True), ("second_second_entries_assigned", True),
    ("complete_down_matrix_available", True), ("complete_charged_lepton_matrix_available", True),
    ("physical_yukawas_available", True), ("extension_point_selected", True),
))
def test_rehashed_mixed_packet_cannot_inflate_scope_or_change_bases(tmp_path, field, value) -> None:
    record = json.loads(mixed.OUTPUT.read_text())
    record.pop("artifact_digest")
    record[field] = value
    record["artifact_digest"] = _canonical_digest(record)
    path = tmp_path / mixed.OUTPUT.name
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="scope, bases, or inputs"):
        mixed.load_mixed_pairing(path, expected_digest=record["artifact_digest"])


@pytest.mark.parametrize("order,family", ((1, 1), (None, 1), (True, True), (False, 0),
                                         (True, 3), (True, 1.0)))
def test_mixed_evaluator_rejects_undeclared_order_or_family_before_products(order, family) -> None:
    with pytest.raises(ValueError, match="declared order and family"):
        mixed.engine.evaluate_mixed_entry(None, None, None, line_first=order, family=family,
            first_character=(0, 0), second_character=(1, 1), second_seed_index=2)
