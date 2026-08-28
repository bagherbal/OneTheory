"""Derive local determinant pairings for the lawful Schoen constituents.

Owns:
    Signed complementary-minor alternating forms on the rank-two quotient
    presentations and their exact hypersurface-corrected overlap covariance.

Depends on:
    The selected affine constituent presentations, global overlap atlases,
    exact Laurent arithmetic, and the published cubic-pencil equations.

Must not:
    Treat a chart pairing as the grouped hypercohomology contraction, suppress
    hypersurface homotopies, normalize a scalar trace, or report a Yukawa entry.

Phase 0:
    Research-only determinant-pairing certificate before chain totalization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .published_constituent_full_cech import published_constituent_full_cech
from .published_constituent_overlap_transitions import (
    ConstituentOverlapTransition,
    _determinant,
    _hypersurface_equation,
    _relation_columns,
    published_constituent_overlap_atlases,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_schoen_determinant_pairing.json"
)


def _zero() -> LaurentPolynomial:
    """Return zero in the common five-coordinate Laurent ring."""

    return LaurentPolynomial.zero(5, scalar_type=Eisenstein)


def _transpose(matrix: LaurentMatrix) -> LaurentMatrix:
    """Transpose one exact Laurent matrix."""

    return LaurentMatrix(
        tuple(
            tuple(matrix.rows[row][column] for row in range(matrix.shape[0]))
            for column in range(matrix.shape[1])
        )
    )


def _minor_after_deleting(
    relation: LaurentMatrix,
    first: int,
    second: int,
) -> LaurentPolynomial:
    """Return the maximal relation minor complementary to two middle rows."""

    middle_rank, relation_rank = relation.shape
    if middle_rank != relation_rank + 2:
        raise ValueError("a determinant pairing requires a rank-two quotient")
    rows = tuple(
        tuple(relation.rows[row][column] for column in range(relation_rank))
        for row in range(middle_rank)
        if row not in {first, second}
    )
    return _determinant(LaurentMatrix(rows))


def plucker_pairing(relation: LaurentMatrix) -> LaurentMatrix:
    """Return the canonical alternating quotient pairing from maximal minors."""

    middle_rank, relation_rank = relation.shape
    if middle_rank != relation_rank + 2:
        raise ValueError("a Pluecker pairing requires a rank-two quotient")
    rows = [[_zero() for _column in range(middle_rank)] for _row in range(middle_rank)]
    for first, second in combinations(range(middle_rank), 2):
        sign = -1 if (first + second + 1) % 2 else 1
        value = _minor_after_deleting(relation, first, second).scale(sign)
        rows[first][second] = value
        rows[second][first] = -value
    return LaurentMatrix(tuple(tuple(row) for row in rows))


def _adjusted_relation(
    relation: LaurentMatrix,
    transition: ConstituentOverlapTransition,
    equation: LaurentPolynomial,
) -> LaurentMatrix:
    """Insert the certified hypersurface homotopy into the final middle row."""

    rows = list(relation.rows)
    rows[-1] = tuple(
        value + equation * correction
        for value, correction in zip(
            rows[-1],
            transition.hypersurface_homotopy,
            strict=True,
        )
    )
    return LaurentMatrix(tuple(rows))


def _pairing_hypersurface_quotient(
    relation: LaurentMatrix,
    transition: ConstituentOverlapTransition,
) -> LaurentMatrix:
    """Return Q with pairing(R + Fh) - pairing(R) = F Q."""

    middle_rank, relation_rank = relation.shape
    last = middle_rank - 1
    rows = [[_zero() for _column in range(middle_rank)] for _row in range(middle_rank)]
    for first, second in combinations(range(middle_rank), 2):
        if last in {first, second}:
            continue
        minor_rows = []
        for row in range(middle_rank):
            if row in {first, second}:
                continue
            minor_rows.append(
                transition.hypersurface_homotopy
                if row == last
                else relation.rows[row]
            )
        sign = -1 if (first + second + 1) % 2 else 1
        value = _determinant(
            LaurentMatrix(
                tuple(
                    tuple(minor_rows[row][column] for column in range(relation_rank))
                    for row in range(relation_rank)
                )
            )
        ).scale(sign)
        rows[first][second] = value
        rows[second][first] = -value
    return LaurentMatrix(tuple(tuple(row) for row in rows))


def _matrix_difference(left: LaurentMatrix, right: LaurentMatrix) -> LaurentMatrix:
    """Subtract two equally shaped Laurent matrices."""

    if left.shape != right.shape:
        raise ValueError("Laurent matrix subtraction requires equal shapes")
    return LaurentMatrix(
        tuple(
            tuple(
                left.rows[row][column] - right.rows[row][column]
                for column in range(left.shape[1])
            )
            for row in range(left.shape[0])
        )
    )


def _matrix_scale(
    matrix: LaurentMatrix,
    scalar: LaurentPolynomial,
) -> LaurentMatrix:
    """Multiply every Laurent matrix entry by one ring element."""

    return LaurentMatrix(
        tuple(tuple(entry * scalar for entry in row) for row in matrix.rows)
    )


def _is_zero(matrix: LaurentMatrix) -> bool:
    """Return whether every exact Laurent entry vanishes."""

    return all(not entry.terms for row in matrix.rows for entry in row)


def _matrix_digest(matrix: LaurentMatrix) -> str:
    """Hash one Laurent matrix with exact Eisenstein coefficients."""

    digest = hashlib.sha256()
    for row in matrix.rows:
        for entry in row:
            for exponents, coefficient in entry.terms:
                record = (
                    exponents,
                    coefficient.a.numerator,
                    coefficient.a.denominator,
                    coefficient.b.numerator,
                    coefficient.b.denominator,
                )
                digest.update(repr(record).encode("ascii"))
                digest.update(b"\0")
            digest.update(b"\xff")
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class DeterminantPairingAudit:
    """Exact local quotient pairings and corrected overlap identities."""

    constituent_names: tuple[str, ...]
    middle_ranks: tuple[int, ...]
    relation_ranks: tuple[int, ...]
    chart_pairing_count: int
    overlap_count: int
    alternating_pairings: bool
    relation_annihilation_exact: bool
    hypersurface_factorization_exact: bool
    corrected_overlap_covariance_exact: bool
    chart_pairing_digests: tuple[str, ...]

    @property
    def exact(self) -> bool:
        """Return every local pairing and gluing gate."""

        return (
            self.constituent_names == ("I3", "I6")
            and self.middle_ranks == (4, 5)
            and self.relation_ranks == (2, 3)
            and self.chart_pairing_count == 12
            and self.overlap_count == 60
            and self.alternating_pairings
            and self.relation_annihilation_exact
            and self.hypersurface_factorization_exact
            and self.corrected_overlap_covariance_exact
            and len(set(self.chart_pairing_digests)) == 4
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact determinant-pairing gates and content digests."""

        return {
            "constituents": list(self.constituent_names),
            "middle_ranks": list(self.middle_ranks),
            "relation_ranks": list(self.relation_ranks),
            "chart_pairing_count": self.chart_pairing_count,
            "overlap_count": self.overlap_count,
            "alternating_pairings": self.alternating_pairings,
            "relation_annihilation_exact": self.relation_annihilation_exact,
            "hypersurface_factorization_exact": self.hypersurface_factorization_exact,
            "corrected_overlap_covariance_exact": (
                self.corrected_overlap_covariance_exact
            ),
            "chart_pairing_digests": list(self.chart_pairing_digests),
            "distinct_chart_pairing_digest_count": len(
                set(self.chart_pairing_digests)
            ),
            "exact": self.exact,
        }


def mixed_schoen_determinant_pairing_audit() -> DeterminantPairingAudit:
    """Derive both constituent determinant pairings on all affine charts."""

    constituents = published_constituent_full_cech()
    atlases = published_constituent_overlap_atlases()
    names = []
    middle_ranks = []
    relation_ranks = []
    pairings: dict[tuple[str, str], LaurentMatrix] = {}
    alternating = True
    annihilation = True
    factorization = True
    covariance = True
    overlap_count = 0
    for constituent, atlas in zip(constituents, atlases, strict=True):
        name = constituent.alignment.action.derived.extension.scheme.name
        names.append(name)
        charts = {item.source.name: item.source for item in atlas.transitions}
        first_relation = _relation_columns(constituent, next(iter(charts.values())))
        middle_ranks.append(first_relation.shape[0])
        relation_ranks.append(first_relation.shape[1])
        for chart_name, chart in charts.items():
            relation = _relation_columns(constituent, chart)
            pairing = plucker_pairing(relation)
            pairings[(name, chart_name)] = pairing
            alternating = alternating and all(
                pairing.rows[row][column] == -pairing.rows[column][row]
                for row in range(pairing.shape[0])
                for column in range(pairing.shape[1])
            )
            annihilation = annihilation and _is_zero(
                _transpose(relation).compose(pairing)
            )
        equation = _hypersurface_equation(constituent)
        for transition in atlas.transitions:
            overlap_count += 1
            source_relation = _relation_columns(constituent, transition.source)
            target_relation = _relation_columns(constituent, transition.target)
            adjusted = _adjusted_relation(source_relation, transition, equation)
            source_pairing = pairings[(name, transition.source.name)]
            target_pairing = pairings[(name, transition.target.name)]
            quotient = _pairing_hypersurface_quotient(
                source_relation,
                transition,
            )
            factorization = factorization and (
                _matrix_difference(plucker_pairing(adjusted), source_pairing)
                == _matrix_scale(quotient, equation)
            )
            covariance = covariance and (
                transition.transition.compose(target_relation) == adjusted
                and _transpose(transition.transition)
                .compose(plucker_pairing(adjusted))
                .compose(transition.transition)
                == target_pairing
            )
    audit = DeterminantPairingAudit(
        tuple(names),
        tuple(middle_ranks),
        tuple(relation_ranks),
        len(pairings),
        overlap_count,
        alternating,
        annihilation,
        factorization,
        covariance,
        tuple(_matrix_digest(pairing) for pairing in pairings.values()),
    )
    if not audit.exact:
        raise ValueError("the local determinant-pairing audit failed")
    return audit


def write_mixed_schoen_determinant_pairing(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed determinant-pairing certificate."""

    audit = mixed_schoen_determinant_pairing_audit()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-determinant-pairing-v1",
        "coefficient_field": "Q(omega)",
        "pairing": audit.as_record(),
        "local_determinant_pairings_available": True,
        "grouped_chain_contraction_available": False,
        "cyclic_trace_evaluated": False,
        "holomorphic_yukawa_matrix_available": False,
        "next_required_object": (
            "the Alexander-Whitney-compatible lift of the certified local "
            "pairings to the grouped Cech-Koszul chain complex"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact local determinant-pairing artifact."""

    payload = write_mixed_schoen_determinant_pairing()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "local_determinant_pairings_available: "
        f"{payload['local_determinant_pairings_available']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DeterminantPairingAudit",
    "OUTPUT",
    "mixed_schoen_determinant_pairing_audit",
    "plucker_pairing",
    "write_mixed_schoen_determinant_pairing",
]
