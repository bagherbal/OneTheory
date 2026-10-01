"""Verify the actual complete neutrino matrix and exact formal rank loci.

Owns:
    Independent scalar-level determinant expansion, all-entry source matching,
    fixed quotient normalization, and common up/neutrino rank compatibility.

Depends on:
    Actual completed coefficient packets, literal source archives, exact
    Q(omega) arithmetic, and the explicitly conditional research matrix.

Must not:
    Fabricate entries, identify up and neutrino family bases, select a vacuum,
    equate holomorphic ranks with predicted masses, or use observations.

Phase 0:
    Conditional heterotic holomorphic verification; physical normalization is open.
"""

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_neutrino_ff_entries as coefficients
from research.experiments.scientific_genesis import alternate_neutrino_full_matrix as matrix
from research.experiments.scientific_genesis import alternate_neutrino_mixed_pairing as mixed
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text as exact,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _verified_payload,
)

ENTRY_DIGESTS = (
    "b756d7078882c84ab8115320e729b0dbc4d5a34b06d77bccc411762cb2a72265",
    "56887cf77095486901c0a1327e7004435e13c7c73a2dfa031bd5bb17ef1eca5a",
    "1f7243d848789b04ff39d2adc66eb2455fd36df2fa4136902e11a34ea036b8e7",
    "ef44e13e813c8c35f8c7f3d27861d840787968a489f2b2696fd75152b9382143",
    "31f01478088bb6ede78b54fe556706a17413f3d32f5e0d62ef4ccbbdb1457b74",
    "09c7e8e0b8cdcf990955412d6a028678cc1dcbe414b0c51534738ad8c1f8f16b",
    "7420fb17560d7cdaec8f78977bfc3d057e7871fb8e35a1480bc50325d55b623e",
    "e325c129ac8ad049cfa42ccbeac94ef2ef835193af779c0bd4857432a261b174",
)


def _actual_entries():
    """Read only actual completed inputs; no absent coefficient is filled."""

    packet, _ = mixed.load_mixed_pairing(expected_digest=coefficients.MIXED_DIGEST)
    entries = {(0, 0): {}}
    for item in packet["evaluated_entries"]:
        entries[item["row"], item["column"]] = {(0, 0): exact(item["cover_residue"]) / 9}
    for index, (parameter, row, column) in enumerate(
        (parameter, row, column)
        for parameter in (0, 1) for row in (1, 2) for column in (1, 2)
    ):
        digest, record = _verified_payload(coefficients.GENERATED / (
            f"alternate_neutrino_ff_a{parameter}_r{row}_c{column}.json"
        ))
        assert digest == ENTRY_DIGESTS[index]
        assert record["quotient_residue"] == str(exact(record["cover_residue"]) / 9)
        entries.setdefault((row, column), {})[(int(parameter == 0), int(parameter == 1))] = (
            exact(record["cover_residue"]) / 9
        )
    return entries


def _determinant_coefficients(entries):
    """Use the four-term scalar expansion, not the polynomial determinant engine."""

    r1, r2, c1, c2 = (entries[key][0, 0] for key in ((0, 1), (0, 2), (1, 0), (2, 0)))
    return {powers: (-r1*c1*entries[2, 2][powers] + r1*c2*entries[1, 2][powers]
                     + r2*c1*entries[2, 1][powers] - r2*c2*entries[1, 1][powers])
            for powers in ((1, 0), (0, 1))}


def test_actual_neutrino_coefficient_blocks_have_exact_complementary_rank_loci() -> None:
    """The formal determinant is supported on a0, without choosing a point."""

    entries = _actual_entries()
    assert _determinant_coefficients(entries) == {
        (1, 0): Eisenstein(Rational(3, 2), Rational(3, 4)), (0, 1): Eisenstein(0),
    }
    assert -entries[0, 1][0, 0] * entries[1, 0][0, 0] == (
        Eisenstein(Rational(-1, 42), Rational(-1, 63))
    )


def test_missing_complete_matrix_has_no_coefficient_replay_fallback(tmp_path, monkeypatch) -> None:
    """A requested absent result stays absent, even when its constituent inputs exist."""

    def forbidden_replay(*args, **kwargs):
        raise AssertionError("a read-only matrix request must not start a coefficient replay")

    monkeypatch.setattr(matrix, "_replay_blocks", forbidden_replay)
    with pytest.raises(FileNotFoundError):
        matrix.load_full_neutrino_matrix(tmp_path / matrix.OUTPUT.name, expected_digest="0"*64)
