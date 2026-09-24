"""Construct the first-order matter leg of the reverse central down entry.

Owns:
    Both ordered V1-V2 correction products, their exact diagonal transfer,
    strict physical-character projection, and partial scalar contraction.

Depends on:
    Certified reverse universal matter lifts, the independent-factor tensor,
    common-to-diagonal transfer, and the strict physical down-Higgs cocycle.

Must not:
    Treat a nonclosed leg as a Yukawa coefficient, omit the complementary
    Higgs correction, select an extension point, or use observational data.

Phase 0:
    Research-only scoped first-order matter-leg computation.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from functools import cache

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .diagonal_schoen_lines import _FullCochain
from .mixed_schoen_chain_actions import (
    _perturbed_inclusion,
    load_certified_higgs_representative,
)
from .mixed_schoen_chain_diagonal import chain_diagonal_objects, full_chain_diagonal_differential
from .mixed_schoen_matter_comparison import (
    _character_project,
    _cochain_digest,
    _has_character,
    _perturbed_projection_inclusion,
)
from .mixed_schoen_matter_representatives import (
    _cochain_digest as outer_cochain_digest,
)
from .mixed_schoen_matter_representatives import mixed_schoen_matter_representatives
from .mixed_schoen_matter_tensor import (
    IndependentMatterCochain,
    external_lifted_matter_tensor,
    lift_matter_cochain,
)
from .mixed_schoen_outer_universal_cone import (
    _load_orientation_basis,
    _representative,
)
from .mixed_schoen_reverse_diagonal_chain_map import (
    reverse_diagonal_compare_common_matter,
)
from .mixed_schoen_reverse_down_matter_lifts import (
    FORWARD_MATTER_CHARACTERS,
    _cache_input_digest,
    _cache_path,
    _lift_v1_coefficient,
    _write_cache,
)
from .mixed_schoen_reverse_down_matter_lifts import (
    OUTPUT as REVERSE_MATTER_ARTIFACT,
)
from .mixed_schoen_universal_matter_lifts import _verified_digest
from .mixed_schoen_yukawa_trace import (
    _full_cochain_digest,
    _pairing_terms,
    contract_with_strict_higgs,
    scalar_full_differential,
)

PRODUCT_CHARACTER = (0, 2)


def _selected_correction(
    character: tuple[int, int],
    representative: SparseOuterCechCochain,
    parameter_index: int,
    extensions: tuple[SparseOuterCechCochain, ...],
) -> SparseOuterCechCochain:
    """Consume one previously certified cache by exact source fingerprints."""

    artifact = json.loads(REVERSE_MATTER_ARTIFACT.read_text(encoding="utf-8"))
    artifact_digest = artifact.pop("artifact_digest", None)
    if (
        not isinstance(artifact_digest, str)
        or artifact_digest != _canonical_digest(artifact)
        or artifact.get("exact") is not True
    ):
        raise ValueError("the reverse matter artifact is not certified")
    lift_record = next(
        (
            item
            for item in artifact["v1_parameter_linear_lifts"]
            if item["forward_character_exponents"] == list(character)
        ),
        None,
    )
    if (
        not isinstance(lift_record, dict)
        or lift_record.get("exact") is not True
        or lift_record.get("product_cycles_exact") is not True
        or lift_record.get("correction_identities_exact") is not True
        or lift_record.get("strict_characters_exact") is not True
    ):
        raise ValueError("the selected reverse character has no certified lift")
    coefficient_record = next(
        (
            item
            for item in lift_record["parameter_coefficients"]
            if item["parameter"] == f"b{parameter_index}"
        ),
        None,
    )
    if not isinstance(coefficient_record, dict):
        raise ValueError("the selected parameter has no certified correction")

    path = _cache_path(character, parameter_index)
    if path.is_file():
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            cached = json.load(stream)
        cache_digest = cached.pop("cache_digest", None)
        if (
            not isinstance(cache_digest, str)
            or cache_digest != _canonical_digest(cached)
            or cached.get("schema")
            != "mixed-schoen-reverse-down-lift-cache-v1"
            or cached.get("character_exponents") != list(character)
            or cached.get("parameter_index") != parameter_index
            or cached.get("input_digest")
            != _cache_input_digest(
                character,
                parameter_index,
                representative,
                extensions[parameter_index],
            )
            or cached.get("product_cycle_exact") is not True
            or cached.get("correction_identity_exact") is not True
            or cached.get("strict_character_exact") is not True
            or cached.get("product_digest")
            != coefficient_record["product_digest"]
            or cached.get("correction_digest")
            != coefficient_record["correction_digest"]
        ):
            raise ValueError("the selected reverse matter cache failed provenance")
        product = _representative(cached.get("product"))
        correction = _representative(cached.get("correction"))
        if (
            outer_cochain_digest((product,)) != cached["product_digest"]
            or outer_cochain_digest((correction,)) != cached["correction_digest"]
            or len(product.terms) != coefficient_record["product_term_count"]
            or len(correction.terms)
            != coefficient_record["correction_term_count"]
        ):
            raise ValueError("the selected reverse matter cochains changed")
        return correction

    product, correction, cycle, identity, strict = _lift_v1_coefficient(
        character, representative, extensions[parameter_index]
    )
    if (
        not (cycle and identity and strict)
        or outer_cochain_digest((product,))
        != coefficient_record["product_digest"]
        or outer_cochain_digest((correction,))
        != coefficient_record["correction_digest"]
    ):
        raise ValueError("the selected reverse matter coefficient failed")
    selected = (
        character,
        parameter_index,
        product,
        correction,
        cycle,
        identity,
        strict,
    )
    _write_cache(selected, representative, extensions[parameter_index])
    return correction


@dataclass(frozen=True, slots=True)
class ReverseCentralMatterLeg:
    """One incomplete first-order central coefficient before Higgs comparison."""

    parameter: str
    raw_term_count: int
    raw_digest: str
    projection_depth: int
    projected_term_count: int
    inclusion_depth: int
    strict_term_count: int
    equivariant_term_count: int
    equivariant_digest: str
    equivariant_character_exact: bool
    equivariant_residual_term_count: int
    equivariant_residual_digest: str
    scalar: _FullCochain
    scalar_residual: _FullCochain

    @property
    def scoped_exact(self) -> bool:
        """Require source-derived transfer without claiming a closed result."""

        return (
            self.parameter in {f"b{index}" for index in range(6)}
            and self.raw_term_count > 0
            and self.equivariant_character_exact
        )

    def as_record(self) -> dict[str, object]:
        """Record exact partial-leg diagnostics with an explicit open gate."""

        return {
            "parameter": self.parameter,
            "raw_term_count": self.raw_term_count,
            "raw_digest": self.raw_digest,
            "projection_depth": self.projection_depth,
            "projected_term_count": self.projected_term_count,
            "inclusion_depth": self.inclusion_depth,
            "strict_term_count": self.strict_term_count,
            "equivariant_term_count": self.equivariant_term_count,
            "equivariant_digest": self.equivariant_digest,
            "equivariant_character_exact": self.equivariant_character_exact,
            "equivariant_residual_term_count": (
                self.equivariant_residual_term_count
            ),
            "equivariant_residual_digest": self.equivariant_residual_digest,
            "scalar_term_count": len(self.scalar.terms),
            "scalar_digest": _full_cochain_digest(self.scalar),
            "scalar_residual_term_count": len(self.scalar_residual.terms),
            "scalar_residual_digest": _full_cochain_digest(self.scalar_residual),
            "scalar_is_cycle": self.scalar_residual.is_zero(),
            "scoped_exact": self.scoped_exact,
            "central_yukawa_coefficient_available": False,
        }


def _physical_lifts(
    parameter_index: int,
) -> tuple[
    str,
    IndependentMatterCochain,
    IndependentMatterCochain,
    IndependentMatterCochain,
    IndependentMatterCochain,
]:
    """Load exactly one strict V1 pair and its certified V2 corrections."""

    if not 0 <= parameter_index < 6:
        raise ValueError("the reverse central parameter index is unavailable")
    _verified_digest(REVERSE_MATTER_ARTIFACT, "exact", True)
    _first, parameters, extensions = _load_orientation_basis("V2", "V1", "b")
    if parameters != tuple(f"b{index}" for index in range(6)):
        raise ValueError("the reverse extension parameter basis changed")
    first_constituent, _second_constituent = mixed_schoen_matter_representatives()
    sectors = {sector.character: sector for sector in first_constituent.sectors}
    row_character, column_character = FORWARD_MATTER_CHARACTERS
    row_representatives = sectors[row_character].full_representatives
    column_representatives = sectors[column_character].full_representatives
    if len(row_representatives) != 1 or len(column_representatives) != 1:
        raise ValueError("the physical V1 character multiplicities changed")
    row_representative = row_representatives[0]
    column_representative = column_representatives[0]
    row_correction = _selected_correction(
        row_character, row_representative, parameter_index, extensions
    )
    column_correction = _selected_correction(
        column_character, column_representative, parameter_index, extensions
    )
    row_v1 = lift_matter_cochain(row_representative, 1)
    column_v1 = lift_matter_cochain(column_representative, 1)
    return (
        parameters[parameter_index],
        row_v1,
        column_v1,
        reverse_diagonal_compare_common_matter(row_correction),
        reverse_diagonal_compare_common_matter(column_correction),
    )


@dataclass(frozen=True, slots=True)
class ReverseCentralDirectTrace:
    """Unprojected exact scalar trace with closure explicitly unresolved."""

    parameter: str
    ordered_matter_terms: int
    scalar: _FullCochain
    scalar_residual: _FullCochain

    def as_record(self) -> dict[str, object]:
        """Expose exact direct-trace diagnostics without a Yukawa claim."""

        return {
            "parameter": self.parameter,
            "ordered_matter_terms_before_cross_order_cancellation": (
                self.ordered_matter_terms
            ),
            "scalar_term_count": len(self.scalar.terms),
            "scalar_digest": _full_cochain_digest(self.scalar),
            "scalar_residual_term_count": len(self.scalar_residual.terms),
            "scalar_residual_digest": _full_cochain_digest(self.scalar_residual),
            "scalar_is_cycle": self.scalar_residual.is_zero(),
            "central_yukawa_coefficient_available": False,
        }


def reverse_central_direct_trace(parameter_index: int) -> ReverseCentralDirectTrace:
    """Trace supported ordered products separately, then add their scalars."""

    parameter, row_v1, column_v1, row_v2, column_v2 = _physical_lifts(
        parameter_index
    )
    allowed_pairs = frozenset(
        (item.first_index, item.second_index)
        for item in chain_diagonal_objects()
        if _pairing_terms(item.first_index, item.second_index)
    )
    higgs = load_certified_higgs_representative()
    first = external_lifted_matter_tensor(row_v1, column_v2, allowed_pairs)
    first_count = len(first.terms)
    first_scalar = contract_with_strict_higgs(first, higgs)
    del first
    second = external_lifted_matter_tensor(column_v1, row_v2, allowed_pairs)
    second_count = len(second.terms)
    second_scalar = contract_with_strict_higgs(second, higgs)
    del second
    scalar = _FullCochain(first_scalar.terms + second_scalar.terms)
    del first_scalar, second_scalar
    return ReverseCentralDirectTrace(
        parameter,
        first_count + second_count,
        scalar,
        scalar_full_differential(scalar),
    )


@cache
def reverse_central_matter_leg(parameter_index: int) -> ReverseCentralMatterLeg:
    """Compute one exact first-order matter leg over the reverse P5 basis."""

    parameter, row_v1, column_v1, row_v2, column_v2 = _physical_lifts(
        parameter_index
    )
    first = external_lifted_matter_tensor(
        row_v1,
        column_v2,
    )
    second = external_lifted_matter_tensor(
        column_v1,
        row_v2,
    )
    raw = first + second
    del first, second
    raw_term_count = len(raw.terms)
    raw_digest = _cochain_digest(raw)
    projected, projection_depth = _perturbed_projection_inclusion(raw, 2)
    del raw
    projected_term_count = len(projected.terms)
    strict, inclusion_depth = _perturbed_inclusion(projected)
    del projected
    strict_term_count = len(strict.terms)
    equivariant = _character_project(strict, PRODUCT_CHARACTER)
    del strict
    equivariant_residual = full_chain_diagonal_differential(equivariant)
    higgs = load_certified_higgs_representative()
    scalar = contract_with_strict_higgs(equivariant, higgs)
    scalar_residual = scalar_full_differential(scalar)
    result = ReverseCentralMatterLeg(
        parameter,
        raw_term_count,
        raw_digest,
        projection_depth,
        projected_term_count,
        inclusion_depth,
        strict_term_count,
        len(equivariant.terms),
        _cochain_digest(equivariant),
        _has_character(equivariant, PRODUCT_CHARACTER),
        len(equivariant_residual.terms),
        _cochain_digest(equivariant_residual),
        scalar,
        scalar_residual,
    )
    if not result.scoped_exact:
        raise ValueError("the reverse central matter-leg transfer failed")
    return result


if __name__ == "__main__":
    result = reverse_central_matter_leg(0)
    record = result.as_record()
    print(f"b0_record_digest: {_canonical_digest(record)}")
    print(f"raw_term_count: {record['raw_term_count']}")
    print(f"scalar_term_count: {record['scalar_term_count']}")
    print(f"scalar_residual_term_count: {record['scalar_residual_term_count']}")


__all__ = [
    "ReverseCentralDirectTrace",
    "ReverseCentralMatterLeg",
    "reverse_central_direct_trace",
    "reverse_central_matter_leg",
]
