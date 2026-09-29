"""Certify the declared scalar trace on the free Schoen quotient.

Owns:
    An actual closed generator of cover H3(O), full deck-boundary
    witnesses, and the finite-etale trace factor in a stated volume frame.

Depends on:
    The published free quotient, exact ordered scalar contraction,
    declared deck actions, and Serre-duality trace compatibility.

Must not:
    Normalize matter metrics, assign an unfinished Yukawa coefficient,
    average a physical product, or conceal a holomorphic volume choice.

Phase 0:
    Research-only trace certificate; no matrix entry is assigned here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from .alternate_up_mixed_scalar_trace import _scalar_context
from .alternate_up_pairing_exchange import direct_ordered_scalar_residue
from .mixed_schoen_common_dga import perturbed_homotopy
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import (
    _full_action,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_quotient_trace.json"


@dataclass(frozen=True, slots=True)
class ScalarTraceGenerator:
    """The declared harmonic coordinate and its complete closed inclusion."""

    harmonic_seed: SparseOuterCechCochain
    full_cochain: SparseOuterCechCochain
    inclusion_depth: int


@cache
def scalar_trace_generator() -> ScalarTraceGenerator:
    """Construct a genuine full cycle, not the unclosed top Koszul term."""

    context = _scalar_context()
    entries = _reduced_basis(context.left_skeleton, context.right_skeleton, 3)
    if len(entries) != 1:
        raise ValueError("the scalar trace needs a one-dimensional cover H3")
    harmonic = _reduced_cochain(entries, {0: Eisenstein(1)})
    full, depth = _perturbed_inclusion(harmonic, context)
    if not context.differential(full).is_zero():
        raise ValueError("the full scalar trace generator is not closed")
    if direct_ordered_scalar_residue(full) != Eisenstein(1):
        raise ValueError("the declared cover trace generator has a different residue")
    projected, _ = _perturbed_projection(full, context, 3)
    if projected != {0: Eisenstein(1)}:
        raise ValueError("the full scalar trace generator has a different reduced class")
    return ScalarTraceGenerator(harmonic, full, depth)


@dataclass(frozen=True, slots=True)
class ScalarTraceDeckWitness:
    """A complete image and a primitive of its difference from the generator."""

    generator: str
    image: SparseOuterCechCochain
    difference: SparseOuterCechCochain
    primitive: SparseOuterCechCochain
    projection_depth: int
    homotopy_depth: int

    def as_record(self) -> dict[str, object]:
        """Record exact cochain checks without confusing strictness with descent."""

        return {
            "generator": self.generator,
            **{f"{name}_term_count": len(value.terms) for name, value in (
                ("image", self.image), ("difference", self.difference),
                ("primitive", self.primitive),
            )},
            **{f"{name}_digest": _cochain_digest((value,)) for name, value in (
                ("image", self.image), ("difference", self.difference),
                ("primitive", self.primitive),
            )},
            "full_image_closed_exact": True,
            "cohomology_eigenvalue": "1",
            "difference_boundary_exact": True,
            "strictly_fixed": self.difference.is_zero(),
            "projection_depth": self.projection_depth,
            "homotopy_depth": self.homotopy_depth,
        }


def scalar_trace_deck_witnesses() -> tuple[ScalarTraceDeckWitness, ...]:
    """Verify actual full actions and boundary equations for both generators."""

    context = _scalar_context()
    full = scalar_trace_generator().full_cochain
    witnesses = []
    for action in schoen_sparse_deck_actions():
        image = _full_action(full, context.left, context.right, action)
        if not context.differential(image).is_zero():
            raise ValueError("the deck action did not preserve the full scalar cycle")
        projected, projection_depth = _perturbed_projection(image, context, 3)
        if projected != {0: Eisenstein(1)}:
            raise ValueError("the scalar trace class is not deck invariant")
        if direct_ordered_scalar_residue(image) != Eisenstein(1):
            raise ValueError("the direct scalar trace is not deck invariant")
        difference = image + full.scale(-1)
        primitive, homotopy_depth = perturbed_homotopy(difference, context)
        if context.differential(primitive) != difference:
            raise ValueError("the scalar deck difference is not the declared full boundary")
        witnesses.append(ScalarTraceDeckWitness(
            action.name, image, difference, primitive, projection_depth, homotopy_depth,
        ))
    if {witness.generator for witness in witnesses} != {"P", "T"}:
        raise ValueError("the scalar descent needs both declared deck generators")
    return tuple(witnesses)


def write_alternate_up_quotient_trace(path: Path = OUTPUT) -> dict[str, object]:
    """Record finite-cover normalization only in the explicitly descended volume frame.

    Deck invariance of H3(O) implies dual invariance of H0(K), so the
    volume form dual to the unit cover residue descends uniquely. With
    pi*Omega_quotient=Omega_cover, Serre trace commutes with finite pushforward
    and Tr_pi(pi*alpha)=degree*alpha. Hence the quotient trace of the class
    pulling back to this generator is 1/degree. This is a holomorphic trace
    convention, not canonical normalization of matter or Higgs states.
    """

    geometry = schoen_geometry()
    quotient = geometry.quotient
    if (
        not quotient.acts_freely or quotient.order != 9
        or quotient.group_name != "Z3 x Z3"
        or quotient.space.cover_degree != quotient.order
    ):
        raise ValueError("the declared free Schoen quotient or covering degree changed")
    generator = scalar_trace_generator()
    witnesses = scalar_trace_deck_witnesses()
    context = _scalar_context()
    dimensions = [len(_reduced_basis(
        context.left_skeleton, context.right_skeleton, degree,
    )) for degree in range(4)]
    if dimensions != [1, 0, 0, 1]:
        raise ValueError("the declared scalar cover cohomology changed")
    payload: dict[str, object] = {
        "schema": "alternate-up-quotient-trace-v1",
        "coefficient_field": "Q(omega)",
        "cover_scalar_h0_to_h3": dimensions,
        "harmonic_seed_term_count": len(generator.harmonic_seed.terms),
        "harmonic_seed_digest": _cochain_digest((generator.harmonic_seed,)),
        "full_generator_term_count": len(generator.full_cochain.terms),
        "full_generator_digest": _cochain_digest((generator.full_cochain,)),
        "full_generator_closed_exact": True,
        "inclusion_depth": generator.inclusion_depth,
        "cover_trace_of_generator": "1",
        "trace_coordinate": {
            "koszul_summand": "k2", "object_indices": [0, 0],
            "x_monomial": [-1, -1, -1], "u_monomial": [-1, -1, -1],
            "p_monomial": [-1, -1], "cell": [[0, 1, 2], [0, 1, 2], [0, 1]],
        },
        "deck_checks": [witness.as_record() for witness in witnesses],
        "cover_h3_deck_character": [0, 0],
        "scalar_class_descent_certified": True,
        "free_quotient_group": quotient.group_name,
        "covering_degree": quotient.order,
        "geometry_input_identifier": quotient.space.input_record.identifier,
        "volume_form_convention": {
            "cover": "dual to the fixed cover H3(O) generator with trace one",
            "quotient": "the unique form whose pullback is that cover form",
            "relation": "pi*Omega_quotient=Omega_cover",
        },
        "finite_etale_trace_identity": "trace_cover(pi*alpha)=degree*trace_quotient(alpha)",
        "cover_to_quotient_trace_factor": str(Rational(1, quotient.order)),
        "quotient_trace_of_pullback_generator_class": str(Rational(1, quotient.order)),
        "quotient_trace_normalization_constructed": True,
        "holomorphic_trace_not_canonical_matter_normalization": True,
        "physical_null_coefficient_assigned": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "published_input_sha256": hashlib.sha256((
            ROOT / "data/published/visible_carrier/source_manifest.json"
        ).read_bytes()).hexdigest(),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_quotient_trace()
    print(f"quotient trace artifact: {record['artifact_digest']}")
