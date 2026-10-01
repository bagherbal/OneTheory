"""Guard explicit neutrino coefficient execution without assigning missing entries.

Owns:
    Actual archived-input reuse, independent seed routing, strict declared-index
    rejection, and the absence of implicit solves for missing checkpoints.

Depends on:
    The sector-specific research orchestrator and verified full mixed witnesses.

Must not:
    Treat execution-boundary tests as a completed coefficient calculation,
    insert synthetic F-F entries, or claim physical neutrino masses.

Phase 0:
    Research execution-contract tests; independent all-entry replay is still required.
"""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from research.experiments.scientific_genesis import alternate_neutrino_ff_entries as coefficients
from research.experiments.scientific_genesis import alternate_neutrino_full_matrix as assembly


@pytest.mark.parametrize("parameter", (-1, 2, True, 0.0))
def test_undeclared_parameters_cannot_enter_the_neutrino_solver(parameter: object) -> None:
    with pytest.raises(ValueError, match="declared a0 or a1"):
        coefficients.write_ff_coefficient(parameter, derive_lifts=True)  # type: ignore[arg-type]


@pytest.mark.parametrize("side,family", ((2, 1), (True, 1), (0.0, 1), (0, 0), (0, 3), (0, True)))
def test_undeclared_matter_directions_cannot_be_named(side: int, family: int) -> None:
    with pytest.raises(ValueError, match="neutrino side|fixed seed basis"):
        coefficients.lift_path(0, side, family)


def test_saved_neutrino_inputs_are_not_the_up_family_seed_order() -> None:
    """The shared Higgs does not authorize the old up-family seed labels."""

    classes, prerequisites = coefficients._inputs()
    assert [classes[side, family].seed_index for side in (0, 1) for family in (1, 2)] == [
        2, 4, 1, 3,
    ]
    assert [classes[side, family].character for side in (0, 1) for family in (1, 2)] == [
        (2, 1), (2, 1), (2, 2), (2, 2),
    ]
    assert prerequisites["actual_neutrino_mixed_pairing"] == coefficients.MIXED_DIGEST
    assert all(len(matter.cohomology_coordinates) == 18 for matter in classes.values())


def test_an_explicit_missing_checkpoint_has_no_solver_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A read-only request may not silently construct the absent physical input."""

    def forbidden_solver(*_args, **_kwargs):
        pytest.fail("the missing-checkpoint path unexpectedly invoked the constituent solver")

    monkeypatch.setattr(coefficients, "_coefficient_job", forbidden_solver)
    with pytest.raises(FileNotFoundError, match="alternate_neutrino_ff_lift_a0_side0_family1"):
        coefficients.write_ff_coefficient(0, tmp_path, derive_lifts=False)


def test_lift_derivation_must_be_explicit() -> None:
    with pytest.raises(TypeError, match="explicitly declare"):
        coefficients.write_ff_coefficient(0, derive_lifts=1)  # type: ignore[arg-type]


def test_incomplete_neutrino_coefficients_do_not_produce_a_partial_matrix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check prerequisites before any replay, matrix construction, or artifact write."""

    def forbidden_replay(*_args, **_kwargs):
        pytest.fail("an incomplete coefficient packet unexpectedly entered scalar replay")

    monkeypatch.setattr(assembly, "_verified_entry", forbidden_replay)
    destination = tmp_path / "matrix.json"
    with pytest.raises(FileNotFoundError, match="actual neutrino coefficient prerequisite"):
        assembly.write_full_neutrino_matrix(destination)
    assert not destination.exists()


def _replay_lift(indices):
    """Check the original full equations in a worker, returning only exact metadata."""

    parameter, side, family = indices
    lift = assembly._verified_lift(parameter, side, family, coefficients.GENERATED)
    return (parameter, side, family, lift.matter.character, lift.matter.seed_index,
            len(lift.constituent_correction.terms), len(lift.line_correction.terms),
            lift.checkpoint_digest)


def test_all_eight_actual_neutrino_lifts_replay_full_source_and_deck() -> None:
    """Hashes bind actual source witnesses only after full algebraic revalidation."""

    expected = (
        (0, 0, 1, (2, 1), 2, 27001, 13071,
         "ffc2ff3bdab420bfc9b16ffd1892aa4b84c2896808f976a09ffbca604d6a1379"),
        (0, 0, 2, (2, 1), 4, 26689, 12855,
         "7da302ec452f693ced8a436b29bed9402257428ce85576e2f36c9b0e3cbeab62"),
        (0, 1, 1, (2, 2), 1, 27198, 12966,
         "ce0af7244b5be8a5d8786243f3378518826294cbb7ffabda2df5e7befe84037c"),
        (0, 1, 2, (2, 2), 3, 27369, 13158,
         "fbde476e5e4e892988e9408ff454603da4afb1bc8f8396cbec9d8313921171be"),
        (1, 0, 1, (2, 1), 2, 24016, 11397,
         "d20d9d68689a66e769a4c637efc8abb365fcb4021990dc021126302e8824004d"),
        (1, 0, 2, (2, 1), 4, 23795, 11163,
         "4002b844a63e4a3de0d909f6b232bc4ad645ce7c835fdf4cbb733ef665ee8245"),
        (1, 1, 1, (2, 2), 1, 23916, 11844,
         "ce3f70ba89af4e70b315a490401a734ecb2ce405b33eeb2d85167d545fdb27c8"),
        (1, 1, 2, (2, 2), 3, 25441, 12294,
         "e26c664effe33ed3ca157b0d357062b119b24c3bbc08a3b74cde43cb15691bde"),
    )
    jobs = [row[:3] for row in expected]
    with ProcessPoolExecutor(max_workers=4) as pool:
        assert tuple(pool.map(_replay_lift, jobs)) == expected
