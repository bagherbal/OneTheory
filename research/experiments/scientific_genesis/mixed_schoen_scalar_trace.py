"""Certify the scalar residue target for the lawful mixed-Schoen pairing.

Owns:
    Exact virtual determinant degrees, their cancellation, adjunction, and the
    unique reduced degree-three coordinate residue of the diagonal Schoen model.

Depends on:
    The lawful constituent resolutions and exact diagonal complete-intersection
    line-cohomology transfer over the Eisenstein field.

Must not:
    Construct the missing alternating determinant contraction, identify a
    product with a scalar, or report a holomorphic Yukawa coefficient.

Phase 0:
    Research-only certificate for the scalar target of a future lawful trace.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .diagonal_schoen_lines import (
    _EQUATION_DEGREES,
    LineDegree4,
    _reduced_entries,
    diagonal_schoen_line_bundle,
)
from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    mixed_schoen_constituents,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_scalar_trace.json"


def _virtual_rank(constituent: MixedSchoenConstituent) -> int:
    """Return the alternating rank of one two-term line resolution."""

    return sum(1 if item.position == 0 else -1 for item in constituent.objects)


def _virtual_determinant_degree(
    constituent: MixedSchoenConstituent,
) -> tuple[int, int, int]:
    """Return the alternating sum of constituent line degrees."""

    return cast(
        tuple[int, int, int],
        tuple(
            sum(
                (1 if item.position == 0 else -1) * item.line_degree[index]
                for item in constituent.objects
            )
            for index in range(3)
        ),
    )


@dataclass(frozen=True, slots=True)
class ScalarTraceTarget:
    """The exact one-dimensional target preceding determinant contraction."""

    constituent_ranks: tuple[int, int]
    determinant_degrees: tuple[tuple[int, int, int], tuple[int, int, int]]
    determinant_product_degree: tuple[int, int, int]
    equation_degree_sum: LineDegree4
    ambient_canonical_degree: LineDegree4
    structure_sheaf_cohomology: tuple[int, int, int, int]
    top_subset: tuple[int, ...]
    top_ambient_degree: LineDegree4
    top_monomials: tuple[tuple[int, ...], ...]

    @property
    def exact(self) -> bool:
        """Return every determinant, adjunction, and uniqueness gate."""

        return (
            self.constituent_ranks == (2, 2)
            and self.determinant_degrees == ((-2, 2, 0), (2, -2, 0))
            and self.determinant_product_degree == (0, 0, 0)
            and tuple(
                left + right
                for left, right in zip(
                    self.equation_degree_sum,
                    self.ambient_canonical_degree,
                    strict=True,
                )
            )
            == (0, 0, 0, 0)
            and self.structure_sheaf_cohomology == (1, 0, 0, 1)
            and self.top_subset == (0, 1, 2)
            and self.top_ambient_degree == self.ambient_canonical_degree
            and self.top_monomials
            == ((-1, -1, -1), (-1, -1), (-1, -1, -1), (-1, -1))
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact scalar-target gates without a fabricated pairing."""

        return {
            "constituent_virtual_ranks": list(self.constituent_ranks),
            "constituent_determinant_degrees": [
                list(item) for item in self.determinant_degrees
            ],
            "determinant_product_degree": list(self.determinant_product_degree),
            "equation_degree_sum": list(self.equation_degree_sum),
            "ambient_canonical_degree": list(self.ambient_canonical_degree),
            "structure_sheaf_cohomology_h0_to_h3": list(
                self.structure_sheaf_cohomology
            ),
            "top_koszul_subset": list(self.top_subset),
            "top_ambient_degree": list(self.top_ambient_degree),
            "top_laurent_monomials": [list(item) for item in self.top_monomials],
            "top_reduced_dimension": 1,
            "coordinate_residue_normalization": (
                "the displayed ordered top Laurent generator has trace one"
            ),
            "exact": self.exact,
        }


def mixed_schoen_scalar_trace_target() -> ScalarTraceTarget:
    """Construct the exact reduced scalar target of determinant tracing."""

    constituents = mixed_schoen_constituents()
    line = diagonal_schoen_line_bundle(0, 0, 0)
    entries = _reduced_entries((0, 0, 0, 0), 3)
    if len(entries) != 1:
        raise ValueError("the diagonal Schoen scalar trace target is not unique")
    entry = entries[0]
    equation_sum = cast(
        LineDegree4,
        tuple(sum(item[index] for item in _EQUATION_DEGREES) for index in range(4)),
    )
    target = ScalarTraceTarget(
        tuple(_virtual_rank(item) for item in constituents),
        tuple(_virtual_determinant_degree(item) for item in constituents),
        cast(
            tuple[int, int, int],
            tuple(
                sum(_virtual_determinant_degree(item)[index] for item in constituents)
                for index in range(3)
            ),
        ),
        equation_sum,
        (-3, -2, -3, -2),
        line.geometric_dimensions,
        entry.subset,
        entry.ambient_degrees,
        entry.monomials,
    )
    if not line.squared_zero or not target.exact:
        raise ValueError("the exact scalar trace target failed")
    return target


def write_mixed_schoen_scalar_trace(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed scalar trace-target certificate."""

    target = mixed_schoen_scalar_trace_target()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-scalar-trace-target-v1",
        "coefficient_field": "Q(omega)",
        "target": target.as_record(),
        "coordinate_residue_target_available": True,
        "alternating_determinant_contraction_available": False,
        "holomorphic_yukawa_matrix_available": False,
        "next_required_object": (
            "an exact alternating chain contraction from two grouped "
            "V1-tensor-V2 representatives to the certified scalar complex"
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
    """Regenerate the exact scalar trace-target artifact."""

    payload = write_mixed_schoen_scalar_trace()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "coordinate_residue_target_available: "
        f"{payload['coordinate_residue_target_available']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "OUTPUT",
    "ScalarTraceTarget",
    "mixed_schoen_scalar_trace_target",
    "write_mixed_schoen_scalar_trace",
]
