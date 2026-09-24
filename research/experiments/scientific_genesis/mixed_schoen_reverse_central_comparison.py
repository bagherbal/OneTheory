"""Test the exact scalar comparison for one reverse central coefficient.

Owns:
    A fail-closed research path from the two ordered reverse matter traces to
    a scalar cocycle and, only if every chain identity holds, its residue.

Depends on:
    The certified reverse matter and Higgs lifts, the V1 Pluecker pairing,
    the determinant-line cup, and the exact scalar Cech--Koszul contraction.

Must not:
    Infer closure from a raw trace, select an extension point, use measured
    flavor data, or label a holomorphic residue as a physical mass.

Phase 0:
    Research-only coefficient experiment with explicit intermediate gates.
"""

from __future__ import annotations

from collections.abc import Callable

from onetheory.math.numbers import Eisenstein

from .diagonal_schoen_line_actions import (
    constituent_determinant_character,
    line_has_character,
    project_line_character,
)
from .diagonal_schoen_line_products import diagonal_line_product
from .diagonal_schoen_lines import _FullCochain
from .mixed_schoen_reverse_central_matter_leg import reverse_central_direct_trace
from .mixed_schoen_reverse_higgs_lifts import reverse_higgs_lift_coefficient
from .mixed_schoen_v1_pluecker_chain_map import physical_v1_pluecker_pairing
from .mixed_schoen_yukawa_trace import (
    _full_cochain_digest,
    scalar_full_differential,
    scalar_primitive,
    scalar_residue,
)

Record = dict[str, object]


def _summary(cochain: _FullCochain) -> Record:
    """Describe one exact scalar cochain without claiming it is closed."""

    return {"term_count": len(cochain.terms), "digest": _full_cochain_digest(cochain)}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def reverse_central_comparison(
    parameter_index: int,
    report: Callable[[str, Record], None] | None = None,
) -> Record:
    """Compute one holomorphic coefficient only after exact closure gates."""

    if parameter_index not in range(6):
        raise ValueError("the reverse central parameter index is unavailable")

    def emit(stage: str, record: Record) -> None:
        if report is not None:
            report(stage, record)

    trace = reverse_central_direct_trace(parameter_index)
    emit("direct_trace", trace.as_record())
    bottom = physical_v1_pluecker_pairing().equivariant_pairing
    higgs = reverse_higgs_lift_coefficient(parameter_index)
    ambient = (0, 0, 0, 0)
    action = diagonal_line_product(bottom, higgs.canonical_action, ambient)
    comparison = _FullCochain(
        trace.scalar_residual.terms + action.scale(-1).terms
    )
    comparison_cycle = scalar_full_differential(comparison).is_zero()
    emit("comparison", {**_summary(comparison), "is_cycle": comparison_cycle})
    _require(comparison_cycle, "the reverse scalar comparison is not a cycle")

    primitive, depth = scalar_primitive(comparison)
    emit("primitive", {**_summary(primitive), "depth": depth})
    correction = diagonal_line_product(bottom, higgs.canonical_correction, ambient)
    _require(
        scalar_full_differential(correction) == action.scale(-1),
        "the reverse Higgs correction lost its Leibniz identity",
    )
    raw_complete = _FullCochain(
        trace.scalar.terms + correction.terms + primitive.scale(-1).terms
    )
    del trace
    raw_cycle = scalar_full_differential(raw_complete).is_zero()
    emit("raw_complete", {**_summary(raw_complete), "is_cycle": raw_cycle})
    _require(raw_cycle, "the unprojected reverse central scalar is not a cocycle")

    first_frame = constituent_determinant_character(1)
    second_frame = constituent_determinant_character(2)
    scalar_frame = (
        (first_frame[0] + second_frame[0]) % 3,
        (first_frame[1] + second_frame[1]) % 3,
    )
    complete = project_line_character(raw_complete, (0, 0), scalar_frame)
    _require(
        line_has_character(complete, (0, 0), scalar_frame),
        "the reverse central scalar lost its physical character",
    )
    complete_cycle = scalar_full_differential(complete).is_zero()
    emit("strict_complete", {**_summary(complete), "is_cycle": complete_cycle})
    _require(complete_cycle, "the strict reverse central scalar is not a cocycle")
    residue, residue_depth = scalar_residue(complete)
    _require(isinstance(residue, Eisenstein), "the residue left the exact field")
    result: Record = {
        "parameter": f"b{parameter_index}",
        "classification": (
            "COMPUTED_FIRST_ORDER_ENTRY" if not residue.is_zero()
            else "SCOPED_FIRST_ORDER_ENTRY_VANISHING"
        ),
        "comparison": _summary(comparison),
        "comparison_primitive": _summary(primitive),
        "raw_complete_scalar": _summary(raw_complete),
        "complete_scalar": _summary(complete),
        "residue": str(residue),
        "residue_projection_depth": residue_depth,
        "exact": True,
        "holomorphic_only": True,
        "extension_point_selected": False,
        "observational_inputs_used": False,
    }
    emit("result", result)
    return result


if __name__ == "__main__":
    import json

    def print_stage(stage: str, record: Record) -> None:
        print(json.dumps({"stage": stage, "record": record}, sort_keys=True), flush=True)

    reverse_central_comparison(0, print_stage)
