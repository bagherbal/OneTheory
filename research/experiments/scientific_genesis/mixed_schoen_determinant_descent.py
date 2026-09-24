"""Audit the selected mixed carrier's equivariant determinant descent.

Owns:
    Alternating line-degree and frame-character calculations for both selected
    constituent resolutions, plus the induced character of scalar H3.

Depends on:
    The exact mixed constituent frames, Schoen deck action, and scalar
    Cech--Koszul residue contraction.

Must not:
    Equate vanishing rational c1 with an equivariantly trivial determinant,
    change a selected linearization, or refute a distinct published carrier.

Phase 0:
    Research-only obstruction audit for the current synchronized realization.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .diagonal_schoen_line_actions import (
    constituent_determinant_character,
    diagonal_line_full_action,
)
from .diagonal_schoen_line_contraction import strict_line_inclusion
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_observable_spectrum import (
    SOURCE_HIGGS_CHARACTERS,
    WILSON_HIGGS_CHARACTERS,
)
from .mixed_schoen_outer_actions import _constituent_frame
from .mixed_schoen_yukawa_trace import scalar_full_differential, scalar_residue

Character = tuple[int, int]
Degree = tuple[int, int, int]
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_determinant_descent.json"
REVERSE_SPECTRUM = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_reverse_observable_spectrum.json"
)


def _exponent(value: Eisenstein) -> int:
    for exponent in range(3):
        if value == OMEGA**exponent:
            return exponent
    raise ValueError("the scalar action is not a cubic-root character")


def _alternating_degree(factor: int) -> Degree:
    constituent = mixed_schoen_constituents()[factor - 1]
    totals = [0, 0, 0]
    for item in constituent.objects:
        sign = 1 if item.position % 2 == 0 else -1
        for index, coordinate in enumerate(item.line_degree):
            totals[index] += sign * coordinate
    return totals[0], totals[1], totals[2]


def _independent_frame_character(factor: int) -> Character:
    constituent = mixed_schoen_constituents()[factor - 1]
    exponents: list[int] = []
    for generator in ("P", "T"):
        frame = _constituent_frame(factor, generator)
        scalar = Eisenstein(1)
        for position in sorted({item.position for item in constituent.objects}):
            indices = tuple(
                index for index, item in enumerate(constituent.objects)
                if item.position == position
            )
            block = Matrix(
                ((frame[row][column] for column in indices) for row in indices),
                scalar_type=Eisenstein,
            )
            determinant = block.determinant()
            scalar *= determinant if position % 2 == 0 else 1 / determinant
        exponents.append(_exponent(scalar))
    return exponents[0], exponents[1]


def _sum_characters(left: Character, right: Character) -> Character:
    return (left[0] + right[0]) % 3, (left[1] + right[1]) % 3


def _uniform_twist_screen(determinant: Character) -> dict[str, object]:
    """Test only common character twists under the fixed Wilson embedding."""

    spectrum = json.loads(REVERSE_SPECTRUM.read_text(encoding="utf-8"))
    digest = spectrum.pop("artifact_digest", None)
    if digest != _canonical_digest(spectrum):
        raise ValueError("the reverse spectrum artifact digest does not verify")
    higgs = spectrum.get("higgs")
    if not isinstance(higgs, dict):
        raise ValueError("the reverse Higgs character record is absent")
    characters = tuple(
        tuple(item["character_exponents"])
        for item in higgs["deck_characters"]
        for _index in range(item["multiplicity"])
    )
    if tuple(sorted(characters)) != SOURCE_HIGGS_CHARACTERS:
        raise ValueError("the selected Higgs characters changed")

    trivializing = tuple(
        character for character in ((a, b) for a in range(3) for b in range(3))
        if _sum_characters(
            determinant, ((4 * character[0]) % 3, (4 * character[1]) % 3)
        ) == (0, 0)
    )
    if len(trivializing) != 1:
        raise ValueError("the rank-four uniform determinant twist is not unique")
    twist = trivializing[0]
    exterior_shift = ((2 * twist[0]) % 3, (2 * twist[1]) % 3)
    shifted = tuple(sorted(
        _sum_characters(character, exterior_shift)
        for character in characters
    ))
    multiplicities = {
        label: shifted.count(tuple((-value) % 3 for value in wilson))
        for label, wilson in WILSON_HIGGS_CHARACTERS.items()
    }
    return {
        "common_twists_enumerated": 9,
        "rank_four_uniform_twist": list(twist),
        "exterior_square_character_shift": list(exterior_shift),
        "shifted_higgs_characters": [list(character) for character in shifted],
        "fixed_wilson_multiplicities": multiplicities,
        "one_higgs_zero_triplet_spectrum_preserved": (
            multiplicities["up_higgs_doublet"] == 1
            and multiplicities["down_higgs_doublet"] == 1
            and multiplicities["color_triplet"] == 0
            and multiplicities["color_antitriplet"] == 0
        ),
    }


@cache
def determinant_descent_audit() -> dict[str, object]:
    """Return exact evidence for the current selected determinant frame."""

    degrees = (_alternating_degree(1), _alternating_degree(2))
    total_degree = tuple(left + right for left, right in zip(*degrees, strict=True))
    if total_degree != (0, 0, 0):
        raise ValueError("the mixed determinant has nonzero cover line degree")
    characters = (_independent_frame_character(1), _independent_frame_character(2))
    if characters != tuple(
        constituent_determinant_character(factor) for factor in (1, 2)
    ):
        raise ValueError("the two determinant-frame computations disagree")
    total_character = _sum_characters(*characters)

    top, _depth = strict_line_inclusion(
        (0, 0, 0, 0), 3, ((0, Eisenstein(1)),)
    )
    if scalar_residue(top)[0] != Eisenstein(1):
        raise ValueError("the scalar top generator lost normalization")
    actions = {action.name: action for action in schoen_sparse_deck_actions()}

    def top_character(frame: Character) -> Character:
        exponents = []
        for generator in ("P", "T"):
            image = diagonal_line_full_action(top, actions[generator], frame)
            if not scalar_full_differential(image).is_zero():
                raise ValueError("the deck action did not preserve scalar cycles")
            exponents.append(_exponent(scalar_residue(image)[0]))
        return exponents[0], exponents[1]

    geometric_top = top_character((0, 0))
    framed_top = top_character(total_character)
    if geometric_top != (0, 0) or framed_top != total_character:
        raise ValueError("the determinant-frame action disagrees with scalar H3")
    uniform_twist = _uniform_twist_screen(total_character)
    return {
        "schema": "mixed-schoen-determinant-descent-audit-v2",
        "scope": "current selected mixed constituent linearizations",
        "constituent_cover_line_degrees": [list(degree) for degree in degrees],
        "total_cover_line_degree": list(total_degree),
        "constituent_determinant_characters": [
            list(character) for character in characters
        ],
        "total_determinant_character": list(total_character),
        "geometric_scalar_h3_character": list(geometric_top),
        "framed_scalar_h3_character": list(framed_top),
        "trivial_character_scalar_residue_available": (
            framed_top == (0, 0)
        ),
        "equivariantly_trivial_determinant_certified": (
            total_character == (0, 0)
        ),
        "quotient_su4_certified_by_this_gate": (
            total_character == (0, 0)
        ),
        "published_carrier_refuted": False,
        "uniform_twist_screen": uniform_twist,
        "first_missing_input": (
            "an independently verified determinant trivialization or a "
            "non-uniform lawful equivariant relinearization preserving the "
            "Wilson spectrum"
        ),
    }


def write_determinant_descent_audit(path: Path = OUTPUT) -> dict[str, object]:
    """Write one content-addressed scoped determinant obstruction."""

    record = dict(determinant_descent_audit())
    record["artifact_digest"] = _canonical_digest(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


if __name__ == "__main__":
    print(write_determinant_descent_audit()["artifact_digest"])


__all__ = ["OUTPUT", "determinant_descent_audit", "write_determinant_descent_audit"]
