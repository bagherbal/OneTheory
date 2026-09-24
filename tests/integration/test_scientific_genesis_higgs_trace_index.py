"""Guard endpoint indexing in the exact strict-Higgs trace.

Owns:
    A finite comparison of indexed Čech candidates against every strict
    Higgs term on small four-factor cells.

Depends on:
    The certified strict Higgs cocycle and signed product Čech cup.

Must not:
    Interpret synthetic cells as physical matter or infer a Yukawa value.

Phase 0:
    Computation-preserving regression for trace support indexing.
"""

from itertools import product

from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    load_certified_higgs_representative,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_tensor import (
    _cell_cup,
)
from research.experiments.scientific_genesis.mixed_schoen_yukawa_trace import (
    _complementary_minor_polynomials,
    _pairing_terms,
)


def test_endpoint_index_retains_every_strict_higgs_cup() -> None:
    """Endpoint candidates give the same signed cups as a full scan."""

    higgs = load_certified_higgs_representative()
    cells = [
        tuple((pivot,) for pivot in pivots)
        for pivots in product(range(2), repeat=4)
    ]
    for overlap_slot in range(4):
        for pivots in product(range(2), repeat=3):
            cell = []
            remaining = iter(pivots)
            for slot in range(4):
                cell.append((0, 1) if slot == overlap_slot else (next(remaining),))
            cells.append(tuple(cell))
    for cell in cells:
        endpoint = tuple(simplex[-1] for simplex in cell)
        exhaustive = [
            (index, _cell_cup(cell, basis.cell))
            for index, (basis, _coefficient) in enumerate(higgs.terms)
            if _cell_cup(cell, basis.cell) is not None
        ]
        indexed = [
            (index, _cell_cup(cell, basis.cell))
            for index, (basis, _coefficient) in enumerate(higgs.terms)
            if tuple(simplex[0] for simplex in basis.cell) == endpoint
            and _cell_cup(cell, basis.cell) is not None
        ]
        assert indexed == exhaustive


def test_exact_determinant_pairing_is_reused() -> None:
    """Repeated trace terms never rebuild the same Hilbert–Burch minors."""

    first = _pairing_terms(1, 1)
    assert first
    assert _pairing_terms(1, 1) is first
    assert _complementary_minor_polynomials(1) is _complementary_minor_polynomials(1)
