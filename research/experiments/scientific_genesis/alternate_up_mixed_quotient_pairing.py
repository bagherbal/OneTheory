"""Evaluate the constant mixed entries through the canonical Higgs quotient.

Owns:
    Four actual ordered mixed scalars in the fixed one-plus-two family
    bases, exchanged-input boundaries, and explicit holomorphic quotient traces.

Depends on:
    The global signed-minor map, actual matter representatives, quotient
    Higgs covector, graded exterior signs, and the certified scalar trace frame.

Must not:
    Fill the missing F-F block with zeros, choose a Higgs phase to fit
    an old screen, select an extension point, or assert canonical matter metrics.

Phase 0:
    Research-only partial holomorphic pairing; no complete matrix is returned.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .alternate_constituent_up_cone_matter_lifts import _first_representatives
from .alternate_constituent_up_matter_representatives import (
    CARRIER,
    alternate_constituent_up_matter_representatives,
)
from .alternate_constituent_up_matter_representatives import OUTPUT as MATTER
from .alternate_up_coupled_tensor_comparison import OUTPUT as COMPARISON
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_first_order_scalar import even_vector_line_product
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE
from .alternate_up_higgs_quotient_cone import OUTPUT as HIGGS_CONE
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_covector,
    alternate_higgs_quotient_models,
)
from .alternate_up_mixed_scalar_trace import OUTPUT as OLD_MIXED
from .alternate_up_mixed_scalar_trace import _scalar_context
from .alternate_up_pairing_exchange import direct_ordered_scalar_residue
from .alternate_up_quotient_trace import OUTPUT as TRACE
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup, perturbed_homotopy
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_mixed_quotient_pairing.json"


@cache
def first_matter_quotient(character: tuple[int, int]) -> SparseOuterCechCochain:
    """Push an actual E class through q_E(e)=e wedge A_E, with its fixed sign."""

    selected = [item for item in _first_representatives() if item.character == character]
    if len(selected) != 1:
        raise ValueError("the first matter quotient needs its unique declared character class")
    line = MixedSchoenUnit(
        "actual B1 quotient", 0, QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 quotient", 0, QUOTIENT_LINE),),
    )
    context = _MixedContraction(line, mixed_schoen_unit())
    result = _quotient(selected[0].full_cochain, context)
    if result.is_zero() or any(basis.total_degree != 1 for basis, _ in result.terms):
        raise ValueError("the first matter quotient is not a nonzero degree-one cochain")
    if not context.differential(result).is_zero():
        raise ValueError("the actual global quotient did not preserve the matter cycle")
    return result


def quotient_mixed_product(
    line: SparseOuterCechCochain, vector: SparseOuterCechCochain, *, line_first: bool,
) -> SparseOuterCechCochain:
    """Use the literal B-F exterior product in Q and its actual A_F quotient.

    Every coupled correction on a B-supported input lands in B wedge B
    or the killed B wedge A_F relation, or its row leaves B and is zero.
    Thus the canonical product here is the structural wedge itself.
    Reversing the two even bundle slots contributes a minus sign; their
    degree-one cochain coefficients are not silently commuted.
    """

    _, quotient = alternate_higgs_quotient_models()
    context = _MixedContraction(quotient, mixed_schoen_unit())
    raw = even_vector_line_product(line, vector, reverse=not line_first)
    terms = []
    for basis, value in raw.terms:
        old = basis.component
        if old.left_index == 0:
            # This is the entire declared B tensor A_F quotient relation,
            # not an ad hoc omission of a scalar contribution.
            continue
        component = context.components[(old.left_index - 1, 0, old.koszul_summand)]
        if (component.object_degree, component.line_degree) != (
            old.object_degree, old.line_degree,
        ):
            raise ValueError("the actual A_F quotient changed a mixed product's grading")
        terms.append((replace(basis, component=component), value if line_first else -value))
    result = SparseOuterCechCochain(tuple(terms))
    if any(basis.total_degree != 2 for basis, _ in result.terms):
        raise ValueError("the mixed quotient product changed its total degree")
    if not context.differential(result).is_zero():
        raise ValueError("the actual mixed quotient product is not fully closed")
    return result


@dataclass(frozen=True, slots=True)
class MixedQuotientEntry:
    """One actually computed entry, with no values for the absent F-F block."""

    row: int
    column: int
    first_character: tuple[int, int]
    second_character: tuple[int, int]
    second_seed_index: int
    scalar: SparseOuterCechCochain
    reverse_scalar: SparseOuterCechCochain
    exchange_primitive: SparseOuterCechCochain
    cover_residue: Eisenstein

    def as_record(self) -> dict[str, object]:
        """Keep the input order, full witnesses, and exact cover trace explicit."""

        return {
            "row": self.row, "column": self.column,
            "first_constituent_character": list(self.first_character),
            "second_constituent_character": list(self.second_character),
            "second_constituent_seed_index": self.second_seed_index,
            **{f"{name}_term_count": len(value.terms) for name, value in (
                ("scalar", self.scalar), ("reverse_scalar", self.reverse_scalar),
                ("exchange_primitive", self.exchange_primitive),
            )},
            **{f"{name}_digest": _cochain_digest((value,)) for name, value in (
                ("scalar", self.scalar), ("reverse_scalar", self.reverse_scalar),
                ("exchange_primitive", self.exchange_primitive),
            )},
            "full_scalar_closed_exact": True,
            "exchanged_scalar_closed_exact": True,
            "exchange_difference_boundary_exact": True,
            "cover_residue": str(self.cover_residue),
        }


@cache
def mixed_quotient_entries() -> tuple[MixedQuotientEntry, ...]:
    """Recompute all four constant entries with H evaluated first in both orders."""

    h = alternate_higgs_quotient_covector()
    matter = alternate_constituent_up_matter_representatives().classes
    entries = []
    # Fixed rows E(0,0), F(0,0):seed0, F(0,0):seed5 and columns
    # E(1,0), F(1,0):seed0, F(1,0):seed5. No family redefinition occurs.
    for first_character, second_character, line_first in (
        ((0, 0), (1, 0), True), ((1, 0), (0, 0), False),
    ):
        line = first_matter_quotient(first_character)
        selected = [item for item in matter if item.character == second_character]
        if [item.seed_index for item in selected] != [0, 5]:
            raise ValueError("the frozen mixed family seed order changed")
        for family_index, item in enumerate(selected, start=1):
            entries.append(evaluate_mixed_entry(
                h, line, item.full_cochain, line_first=line_first, family=family_index,
                first_character=first_character, second_character=second_character,
                second_seed_index=item.seed_index,
            ))
    return tuple(entries)


def evaluate_mixed_entry(
    h: SparseOuterCechCochain, line: SparseOuterCechCochain, vector: SparseOuterCechCochain,
    *, line_first: bool, family: int, first_character: tuple[int, int],
    second_character: tuple[int, int], second_seed_index: int,
) -> MixedQuotientEntry:
    """Evaluate explicitly supplied actual inputs with the existing signed engine."""

    if type(line_first) is not bool or type(family) is not int or family not in (1, 2):
        raise ValueError("an actual mixed entry requires its declared order and family")
    scalar = mixed_outer_cup(h, quotient_mixed_product(line, vector, line_first=line_first))
    reverse = mixed_outer_cup(h, quotient_mixed_product(line, vector, line_first=not line_first))
    if not _scalar_context().differential(scalar).is_zero():
        raise ValueError("the actual mixed scalar is not fully closed")
    direct = direct_ordered_scalar_residue(scalar)
    reduced, _ = _perturbed_projection(scalar, _scalar_context(), 3)
    if (set(reduced) - {0} or reduced.get(0, 0) != direct
        or direct_ordered_scalar_residue(reverse) != direct):
        raise ValueError("the independent actual mixed traces disagree")
    difference = reverse + scalar.scale(-1)
    primitive, _ = perturbed_homotopy(difference, _scalar_context())
    if _scalar_context().differential(primitive) != difference:
        raise ValueError("the actual mixed exchange lacks its full boundary identity")
    return MixedQuotientEntry(
        0 if line_first else family, family if line_first else 0,
        first_character, second_character, second_seed_index, scalar, reverse, primitive, direct,
    )


def write_mixed_quotient_pairing(path: Path = OUTPUT) -> dict[str, object]:
    """Record four evaluated entries rather than constructing an incomplete matrix."""

    trace_digest, trace = _verified_payload(TRACE)
    old_digest, old = _verified_payload(OLD_MIXED)
    source_inputs = {
        "frozen_carrier": _verified_payload(CARRIER),
        "actual_matter": _verified_payload(MATTER),
        "quotient_higgs_cone": _verified_payload(HIGGS_CONE),
        "coupled_product_presentation": _verified_payload(COMPARISON),
    }
    volume = trace.get("volume_form_convention")
    if (
        trace.get("schema") != "alternate-up-quotient-trace-v1"
        or trace.get("cover_to_quotient_trace_factor") != "1/9"
        or trace.get("scalar_class_descent_certified") is not True
        or not isinstance(volume, dict)
        or volume.get("relation") != "pi*Omega_quotient=Omega_cover"
        or old.get("schema") != "alternate-up-mixed-scalar-trace-v1"
    ):
        raise ValueError("the mixed pairing's declared trace or old comparison changed")
    entries = mixed_quotient_entries()
    payload: dict[str, object] = {
        "schema": "alternate-up-mixed-quotient-pairing-v1",
        "coefficient_field": "Q(omega)",
        "basis_order": {
            "rows": ["E(0,0)", "F(0,0):seed0", "F(0,0):seed5"],
            "columns": ["E(1,0)", "F(1,0):seed0", "F(1,0):seed5"],
        },
        "scalar_order": "h_K cup projected ordered B-F exterior product",
        "actual_higgs_covector_digest": _cochain_digest((alternate_higgs_quotient_covector(),)),
        "first_matter_quotient_digests": [
            {"character": list(character), "cochain_digest": _cochain_digest((
                first_matter_quotient(character),
            ))} for character in ((0, 0), (1, 0))
        ],
        "evaluated_entries": [{
            **entry.as_record(),
            "quotient_residue": str(entry.cover_residue * Rational(1, 9)),
        } for entry in entries],
        "constant_mixed_entries_evaluated": True,
        "exterior_filtration_parameter_degree": 0,
        "first_first_entry_zero_by_B_wedge_B": True,
        "second_second_entries_assigned": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "higgs_phase_adjusted": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "explicit_trace_frame": trace_digest, "old_ordered_mixed_comparison": old_digest,
            **{name: digest for name, (digest, _) in source_inputs.items()},
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_mixed_quotient_pairing()
    print(f"mixed quotient pairing artifact: {record['artifact_digest']}")
