"""Exact stability-wall valuation audit for the frozen alternate carrier.

Owns:
    Exact extension-degree patterns of the four completed holomorphic Yukawa
    matrices, their induced anomalous-U(1) charge solution, invariant-factor
    valuations along a near-split degeneration, and the exact slope polynomial
    locating the first-constituent stability wall in the Kähler cone.

Depends on:
    The completed content-addressed holomorphic matrix artifacts, exact
    Eisenstein arithmetic, and the production Schoen cover intersection tensor.

Must not:
    Choose an extension point, Kähler class or hierarchy parameter, assign
    canonical matter metrics, supply physical masses, or use observations.

Phase 0:
    Research valuation theorem only; the D-term identification of the wall
    flavon and the stability of both constituents at the wall remain explicit
    premises recorded in the report.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path

from onetheory.math.geometry import triple_product
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text,
)

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "data/generated/scientific_genesis"

# Sector name, artifact, and coupling selector inside a multi-sector artifact.
SECTORS: tuple[tuple[str, str, tuple[str, str, str] | None], ...] = (
    ("up", "alternate_up_full_holomorphic_matrix.json", None),
    ("neutrino", "alternate_neutrino_full_holomorphic_matrix.json", None),
    ("down", "alternate_down_lepton_full_holomorphic_matrices.json", ("Q", "d^c", "H_d")),
    (
        "charged_lepton",
        "alternate_down_lepton_full_holomorphic_matrices.json",
        ("L", "e^c", "H_d"),
    ),
)

# First Chern class of the rank-two subobject V1 of the frozen alternate
# extension 0 -> V1 -> V -> V2 -> 0, cover basis (tau1, tau2, phi).
FIRST_CONSTITUENT_C1 = (-2, 2, 0)
# Retained-polarization degree recorded in RETAINED_SLOPE_STABILITY_NOTE.md.
RETAINED_POLARIZATION = (14, 16, 1)
RETAINED_V1_DEGREE = Rational(-432)

ZERO = Eisenstein(0)
Poly = dict[tuple[int, int], Eisenstein]


def _poly(entry: list[dict[str, object]]) -> Poly:
    result: Poly = {}
    for term in entry:
        powers = term["powers"]
        coefficient = term["coefficient"]
        if not isinstance(powers, list) or not isinstance(coefficient, str):
            raise ValueError("matrix term must carry text coefficient and power list")
        key = (int(powers[0]), int(powers[1]))
        if key in result:
            raise ValueError("matrix term repeats a monomial")
        value = _parse_eisenstein_text(coefficient)
        if value != ZERO:
            result[key] = value
    return result


def _mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (i, j), a in left.items():
        for (k, m), b in right.items():
            key = (i + k, j + m)
            result[key] = result.get(key, ZERO) + a * b
    return {key: value for key, value in result.items() if value != ZERO}


def _sub(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, ZERO) - value
    return {key: value for key, value in result.items() if value != ZERO}


def _degree(poly: Poly) -> int | None:
    """Return the homogeneous degree, ``None`` for zero; reject mixed degrees."""

    degrees = {i + j for i, j in poly}
    if not degrees:
        return None
    if len(degrees) != 1:
        raise ValueError("entry is not homogeneous in the extension parameters")
    return degrees.pop()


def _minor(matrix: tuple[tuple[Poly, ...], ...], rows: tuple[int, int],
           cols: tuple[int, int]) -> Poly:
    (r0, r1), (c0, c1) = rows, cols
    return _sub(_mul(matrix[r0][c0], matrix[r1][c1]), _mul(matrix[r0][c1], matrix[r1][c0]))


def _det3(matrix: tuple[tuple[Poly, ...], ...]) -> Poly:
    """First-row cofactor expansion, independent of the producer's null channel."""

    plus = _mul(matrix[0][0], _minor(matrix, (1, 2), (1, 2)))
    minus = _mul(matrix[0][1], _minor(matrix, (1, 2), (0, 2)))
    last = _mul(matrix[0][2], _minor(matrix, (1, 2), (0, 1)))
    return _sub(_sub(plus, minus), _sub({}, last))


def sector_matrix(name: str) -> tuple[tuple[Poly, ...], ...]:
    """Load one completed holomorphic matrix with E-first basis validation."""

    for sector, artifact, coupling in SECTORS:
        if sector != name:
            continue
        data = json.loads((GENERATED / artifact).read_text())
        if coupling is None:
            record = data
        else:
            matches = [m for m in data["matrices"] if tuple(m["coupling"]) == coupling]
            if len(matches) != 1:
                raise ValueError(f"expected exactly one {coupling} matrix")
            record = matches[0]
        if data.get("observational_inputs_used") is not False:
            raise ValueError("matrix artifact must certify no observational input")
        basis = record["basis_order"]
        for labels in (basis["rows"], basis["columns"]):
            kinds = tuple(label[0] for label in labels)
            if kinds != ("E", "F", "F"):
                raise ValueError("basis must be one E family followed by two F families")
        entries = record["matrix_entries"]
        return tuple(tuple(_poly(entry) for entry in row) for row in entries)
    raise KeyError(f"unknown sector {name!r}")


@dataclass(frozen=True)
class SectorValuation:
    """Exact near-split valuation data for one holomorphic Yukawa sector."""

    sector: str
    degree_pattern: tuple[tuple[int | None, ...], ...]
    row_charges: tuple[int, int, int]
    column_charges: tuple[int, int, int]
    offset: int
    constant_minor_count: int
    determinant_degree: int
    singular_value_orders: tuple[int, int, int]


def charge_solution(
    pattern: tuple[tuple[int | None, ...], ...],
) -> tuple[tuple[int, int, int], tuple[int, int, int], int]:
    """Solve deg(i,j) = q_row(i) + q_col(j) + offset with F charges zero.

    A vanishing entry is admitted only if its predicted degree is negative,
    i.e. holomorphically forbidden; otherwise the solution is rejected.
    """

    offset = pattern[1][1]
    if offset is None:
        raise ValueError("F-F entry must be nonzero to fix the offset")
    q_row_e = pattern[0][1]
    q_col_e = pattern[1][0]
    if q_row_e is None or q_col_e is None:
        raise ValueError("mixed E-F entries must be nonzero")
    rows = (q_row_e - offset, 0, 0)
    cols = (q_col_e - offset, 0, 0)
    for i in range(3):
        for j in range(3):
            predicted = rows[i] + cols[j] + offset
            observed = pattern[i][j]
            if observed is None:
                if predicted >= 0:
                    raise ValueError("a holomorphically allowed entry vanishes")
            elif observed != predicted:
                raise ValueError("degree pattern is not a single U(1) charge pattern")
    return rows, cols, offset


def sector_valuation(name: str) -> SectorValuation:
    """Invariant-factor orders of M(eps) = Y(eps * a_hat) for generic a_hat.

    For a homogeneous entry of degree k, substitution gives eps^k times a
    nonzero polynomial in a_hat, so generic directions realize the minimal
    degrees. Over C[[eps]] the cumulative invariant-factor orders are the
    minimal degrees of nonzero 1x1, 2x2 and 3x3 minors.
    """

    matrix = sector_matrix(name)
    pattern = tuple(tuple(_degree(entry) for entry in row) for row in matrix)
    rows, cols, offset = charge_solution(pattern)
    entry_degrees = [d for row in pattern for d in row if d is not None]
    minor_degrees = []
    constant_minors = 0
    for r in combinations(range(3), 2):
        for c in combinations(range(3), 2):
            degree = _degree(_minor(matrix, r, c))
            if degree is not None:
                minor_degrees.append(degree)
                constant_minors += degree == 0
    determinant_degree = _degree(_det3(matrix))
    if determinant_degree is None:
        raise ValueError("determinant vanishes identically; rank is two everywhere")
    d1 = min(entry_degrees)
    d2 = min(minor_degrees)
    orders = (d1, d2 - d1, determinant_degree - d2)
    return SectorValuation(
        name, pattern, rows, cols, offset, constant_minors, determinant_degree, orders,
    )


@dataclass(frozen=True)
class StabilityWall:
    """Exact cover slope quadratic form of the first constituent."""

    c1: tuple[int, int, int]
    quadratic_form: tuple[tuple[str, ...], ...]
    factorization: str
    factorization_verified: bool
    retained_degree: str


def stability_wall() -> StabilityWall:
    """Compute c1(V1).J^2 on the cover and verify 6(j1-j2)(j1+j2+6 j3)."""

    geometry = schoen_geometry()
    tensor = geometry.cover_intersections
    c1 = geometry.cover_divisor(FIRST_CONSTITUENT_C1)
    unit = [geometry.cover_divisor(tuple(int(i == k) for i in range(3))) for k in range(3)]
    form = tuple(
        tuple(triple_product(tensor, c1, unit[a], unit[b]) for b in range(3)) for a in range(3)
    )
    # Expanded 6(j1-j2)(j1+j2+6 j3) = 6 j1^2 - 6 j2^2 + 36 j1 j3 - 36 j2 j3.
    expected = ((6, 0, 18), (0, -6, -18), (18, -18, 0))
    verified = all(form[a][b] == Rational(expected[a][b]) for a in range(3) for b in range(3))
    polarization = geometry.cover_divisor(RETAINED_POLARIZATION)
    retained = triple_product(tensor, c1, polarization, polarization)
    if retained != RETAINED_V1_DEGREE:
        raise ValueError("retained-polarization degree disagrees with the frozen certificate")
    return StabilityWall(
        FIRST_CONSTITUENT_C1,
        tuple(tuple(str(value) for value in row) for row in form),
        "c1(V1).J^2 = 6 (j1 - j2) (j1 + j2 + 6 j3)",
        verified,
        str(retained),
    )


@dataclass(frozen=True)
class WallValuationReport:
    """Complete exact audit and its explicit physical premises."""

    sectors: tuple[SectorValuation, ...]
    wall: StabilityWall
    premises: tuple[str, ...]
    conclusion: str
    hierarchy_parameter_assigned: bool = False
    observational_inputs_used: bool = False


PREMISES = (
    "near the wall j1=j2 the extension modulus is the only parametrically small "
    "quantity, with |a|^2 proportional to the anomalous-U(1) FI term (D-flatness)",
    "V1 and V2 remain stable at the wall and V is stable on the side j2>j1 adjacent "
    "to it (not yet certified at the wall; certified at (14,16,1) and near (6,9,3))",
    "canonical matter and Higgs metrics have finite nondegenerate limits at the wall, "
    "given by the split bundle V1+V2",
)


def audit() -> WallValuationReport:
    """Run the exact audit for all four completed holomorphic sectors."""

    sectors = tuple(sector_valuation(name) for name, _, _ in SECTORS)
    orders = {sector.singular_value_orders for sector in sectors}
    conclusion = (
        "every sector has invariant-factor orders "
        f"{sorted(orders)} in the wall flavon: two unsuppressed families and one "
        "family suppressed by exactly one power; no (8,4,0), (5,3,0) or deeper "
        "parametric hierarchy can arise from the extension modulus of this carrier"
    )
    return WallValuationReport(sectors, stability_wall(), PREMISES, conclusion)


def main() -> None:
    print(json.dumps(asdict(audit()), indent=2))


if __name__ == "__main__":
    main()
