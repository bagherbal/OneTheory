"""Guard the actual remaining scalar execution boundary.

Owns:
    Exact source routing, declared parameter/sector/family indices, bounded
    worker counts, fail-closed missing coefficients, and literal trace checks
    for the four completed actual a0 down-sector coefficients.

Depends on:
    Actual archived same-carrier inputs and the existing scalar orchestration.

Must not:
    Supply synthetic scalars, turn a missing checkpoint into a calculation,
    infer a complete matrix from execution controls, or confuse archive
    trace verification with fresh complete matter/product replay.

Phase 0:
    Research execution guards; generated entries need independent full replay.
"""

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import OuterCechBasis
from research.experiments.scientific_genesis import alternate_down_lepton_ff_entries as entries
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text as exact,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import (
    mixed_outer_cup_coefficient,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _MixedContraction,
    _perturbed_projection,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit

INITIAL_DIGESTS = (
    "ab590cef3f36b64d7636c200f163a69cedaba3e878e8493f95d8695286b5ca6b",
    "c570612d6c3246000c70e03439a54ab8a950b2f9d6fa0ed29805e602316c0246",
    "abd2e360c41591ed88a24c08c43d0d385ab544e5377a80fda2914aa9cd56cca2",
    "471aaa5ce5c3b9e7b5e3d694b895711a2f3679f0919833ff6f5936b6c4a318bd",
)


@pytest.fixture(scope="module")
def actual_trace_inputs():
    """Retarget certified literal inputs; do not rerun the existing Higgs gate.

    The independently checked full down-Higgs input equations remain a
    prerequisite of complete scalar replay. This check only reconstructs
    the coefficient trace of the already archived product witnesses.
    """

    _, witnesses = entries.mixed.down.load_down_higgs_quotient_cone(
        expected_digest=entries.mixed.PINS[0][2],
    )
    model = entries.engine.alternate_coupled_quotient(0)
    indices, exterior_indices = entries.engine.quotient_block_indices(model)
    dual = _MixedContraction(mixed_schoen_unit(), model.quotient)
    return (entries.engine.retarget_quotient_block(witnesses["quotient_covector"], dual,
                indices, dual=True),
            entries.engine.retarget_quotient_block(witnesses["correction_a0"], dual,
                exterior_indices, dual=True))


@pytest.mark.parametrize("row,column,residue,term_counts", (
    (1, 1, "-1399/42-4216/21*omega", (2340, 112446, 53302)),
    (1, 2, "17-89*omega", (2376, 117667, 54616)),
    (2, 1, "-7631/147+3392/147*omega", (2334, 115285, 52262)),
    (2, 2, "-1756/7-1541/14*omega", (2343, 111169, 52822)),
))
def test_initial_actual_down_scalar_archives_have_three_exact_traces(
    actual_trace_inputs, row, column, residue, term_counts,
):
    """This a0 block is not either full two-parameter holomorphic matrix."""

    record, witnesses = entries.load_ff_entry(0, 0, row, column,
        expected_digest=INITIAL_DIGESTS[2*(row-1)+column-1])
    constant, linear, scalar = (witnesses[name] for name in (
        "product_constant", "product_linear", "scalar",
    ))
    assert tuple(len(value.terms) for value in (constant, linear, scalar)) == term_counts
    assert record["cover_residue"] == residue
    assert record["quotient_residue"] == str(exact(residue)/9)
    h, kappa = actual_trace_inputs
    context = entries.engine._scalar_context()
    coordinates, depth = _perturbed_projection(scalar, context, 3)
    assert coordinates == {0: exact(residue)}
    assert depth == record["projection_depth"]
    target = OuterCechBasis(context.components[0, 0, "k2"], (-1, -1, -1), (-1, -1, -1),
                           (-1, -1), ((0, 1, 2), (0, 1, 2), (0, 1)))
    assert (mixed_outer_cup_coefficient(h, linear, target)
            + mixed_outer_cup_coefficient(kappa, constant, target)) == exact(residue)
    assert record["complete_down_matrix_available"] is False
    assert record["complete_charged_lepton_matrix_available"] is False
    assert record["physical_yukawas_available"] is False
    assert record["extension_point_selected"] is False


@pytest.mark.parametrize("field", (
    "complete_down_matrix_available", "complete_charged_lepton_matrix_available",
    "Q_and_L_matter_corrections_recomputed", "up_Higgs_primitives_used",
    "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
))
def test_an_actual_initial_scalar_cannot_inflate_its_scope_even_after_rehashing(tmp_path, field):
    """Attack copies of the actual checkpoint, never supply a physical fixture."""

    source = entries.entry_path(0, 0, 1, 1)
    record = json.loads(source.read_text())
    assert record.pop("artifact_digest") == INITIAL_DIGESTS[0]
    record[field] = True
    record["artifact_digest"] = _canonical_digest(record)
    path = entries.entry_path(0, 0, 1, 1, tmp_path)
    path.write_text(json.dumps(record))
    path.with_suffix(".cochains.json.gz").symlink_to(source.with_suffix(".cochains.json.gz"))
    with pytest.raises(ValueError, match="changed its source or scope"):
        entries.load_ff_entry(0, 0, 1, 1,
            expected_digest=record["artifact_digest"], directory=tmp_path)


@pytest.mark.parametrize("parameter,sector,row,column", (
    (-1, 0, 1, 1), (2, 0, 1, 1), (True, 0, 1, 1), (1.0, 0, 1, 1),
    (0, -1, 1, 1), (0, 2, 1, 1), (0, True, 1, 1), (0, 1.0, 1, 1),
    (0, 0, 0, 1), (0, 0, 3, 1), (0, 0, True, 1), (0, 0, 1.0, 1),
    (0, 0, 1, 0), (0, 0, 1, 3), (0, 0, 1, True), (0, 0, 1, 1.0),
))
def test_remaining_scalar_indices_are_original_declared_indices(parameter, sector, row, column):
    with pytest.raises(ValueError):
        entries.entry_path(parameter, sector, row, column)


@pytest.mark.parametrize("workers", (-1, 0, 3, True, 1.0, None))
def test_remaining_scalar_workers_fail_before_input_access(monkeypatch, workers):
    def forbidden_input(*args):
        raise AssertionError("invalid workers must not access physical input packets")

    monkeypatch.setattr(entries, "_snapshot", forbidden_input)
    with pytest.raises(ValueError, match="one or two workers"):
        entries.write_ff_coefficient(0, workers=workers)


def test_absent_remaining_scalar_has_no_matter_or_higgs_solver_fallback(tmp_path, monkeypatch):
    def forbidden_calculation(*args, **kwargs):
        raise AssertionError("absent read-only scalar must not trigger a calculation")

    monkeypatch.setattr(entries, "verified_lift", forbidden_calculation)
    monkeypatch.setattr(entries, "actual_higgs", forbidden_calculation)
    with pytest.raises(FileNotFoundError):
        entries.replay_ff_entry(0, 0, 1, 1, expected_digest="0"*64, directory=tmp_path)


def test_remaining_row_and_column_sources_are_the_exact_existing_flavor_packets():
    for parameter in (0, 1):
        snapshot = entries._snapshot(parameter)
        assert len(snapshot) == 10
        for sector in (0, 1):
            for side in (0, 1):
                for family in (1, 2):
                    path, digest = entries._lift_source(parameter, sector, side, family)
                    assert snapshot[path.stem]["artifact_digest"] == digest
                    assert path.is_file()
                    if side == 0:
                        assert path.name.startswith(f"alternate_{('up', 'neutrino')[sector]}_")
                    else:
                        assert path.name.startswith("alternate_remaining_flavor_")
