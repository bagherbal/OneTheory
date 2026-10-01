"""Guard the actual remaining scalar execution boundary.

Owns:
    Exact source routing, declared parameter/sector/family indices, bounded
    worker counts, and fail-closed missing coefficient behavior.

Depends on:
    Actual archived same-carrier inputs and the existing scalar orchestration.

Must not:
    Supply synthetic scalars, turn a missing checkpoint into a calculation,
    or infer a complete matrix from execution controls.

Phase 0:
    Research execution guards; generated entries need independent full replay.
"""

import pytest

from research.experiments.scientific_genesis import alternate_down_lepton_ff_entries as entries


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
