"""Attack the ordered null pairing by exchange and direct Laurent residue.

Owns:
    The reversed three-term scalar with the same actual Higgs primitive,
    a direct top-Laurent trace, and full exchange-boundary witnesses.

Depends on:
    The pinned complete forward scalars, actual null matter corrections,
    full exterior primitives, and the standard Schoen scalar differential.

Must not:
    Symmetrize away a failed comparison, change a primitive sign to fit a
    residue, or identify exchange consistency alone with physical Higgs data.

Phase 0:
    Research-only necessary test of the physical pairing identification.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .alternate_up_dual_higgs_inputs import _quotient, alternate_up_dual_higgs_inputs
from .alternate_up_exterior_higgs_action import OUTPUT as EXTERIOR_WITNESSES
from .alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
    alternate_up_exterior_primitive,
)
from .alternate_up_first_order_scalar import OUTPUT as FORWARD_SCALARS
from .alternate_up_first_order_scalar import (
    OrderedFirstOrderScalar,
    alternate_null_matter,
    alternate_up_first_order_scalar,
    even_vector_line_product,
)
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE
from .alternate_up_mixed_scalar_trace import _scalar_context
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup, perturbed_homotopy
from .mixed_schoen_exterior_square import resolution_vector_wedge
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import (
    _basis_record,
    _MixedContraction,
    _perturbed_projection,
)
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_pairing_exchange.json"


def direct_ordered_scalar_residue(cochain: SparseOuterCechCochain) -> Eisenstein:
    """Extract the ordered top Laurent coefficient only from a full cycle.

    On P2_x times P2_u times P1_p, H3(O_X) is the k2 ambient H5
    generator with every exponent minus one and the ordered full cell.
    The scalar Koszul perturbation strictly lowers the Koszul subset;
    its Cech homotopy preserves it. Every positive-order projection
    correction therefore misses k2. This calculation does not call a
    transferred projection or sum its perturbation series. The declared
    cover generator has trace one; no quotient or physical normalization
    is introduced here.
    """

    if any(
        basis.total_degree != 3
        or basis.component.left_index != 0
        or basis.component.right_index != 0
        or basis.component.object_degree != 0
        or basis.component.line_degree != (0, 0, 0)
        for basis, _ in cochain.terms
    ):
        raise ValueError("the direct residue needs a degree-three ordered O_X scalar")
    if not _scalar_context().differential(cochain).is_zero():
        raise ValueError("the direct residue cannot trace a nonclosed scalar")
    result = Eisenstein(0)
    for basis, coefficient in cochain.terms:
        if (
            basis.component.koszul_summand == "k2"
            and basis.x_monomial == (-1, -1, -1)
            and basis.u_monomial == (-1, -1, -1)
            and basis.p_monomial == (-1, -1)
            and basis.cell == ((0, 1, 2), (0, 1, 2), (0, 1))
        ):
            result += coefficient
    return result


@dataclass(frozen=True, slots=True)
class PairingExchangeCoefficient:
    """A necessary comparison test, including any actual exchange obstruction."""

    parameter_index: int
    forward: OrderedFirstOrderScalar
    reverse_scalar: SparseOuterCechCochain
    reverse_defect: SparseOuterCechCochain
    reverse_residue: Eisenstein | None
    reverse_projection_depth: int | None
    difference: SparseOuterCechCochain
    difference_primitive: SparseOuterCechCochain | None
    homotopy_depth: int | None

    def __post_init__(self) -> None:
        if (
            self.parameter_index != self.forward.parameter_index
            or not self.forward.defect.is_zero()
            or self.forward.residue is None
        ):
            raise ValueError("the exchange screen needs its closed matching forward coefficient")
        if self.difference != self.reverse_scalar + self.forward.scalar.scale(-1):
            raise ValueError("the exchange screen has a different declared scalar difference")
        if not self.reverse_defect.is_zero() and (
            self.reverse_residue is not None
            or self.reverse_projection_depth is not None
            or self.difference_primitive is not None
        ):
            raise ValueError(
                "a nonclosed reverse scalar cannot carry a residue or exchange boundary"
            )
        if self.reverse_defect.is_zero() and self.reverse_residue is None:
            raise ValueError("a closed reverse scalar needs its actual residue")
        if self.difference_primitive is not None and (
            self.reverse_residue != self.forward.residue or self.homotopy_depth is None
        ):
            raise ValueError("the exchange boundary assignment has a nonzero cohomology difference")

    def as_record(self) -> dict[str, object]:
        """Record failed symmetry without averaging or assigning a coupling."""

        forward_residue = self.forward.residue
        if forward_residue is None:
            raise ValueError("an exchange screen requires a closed forward scalar")
        direct_forward = direct_ordered_scalar_residue(self.forward.scalar)
        if direct_forward != forward_residue:
            raise ValueError("the direct forward residue differs from the declared projection")
        direct_reverse = None
        if self.reverse_defect.is_zero():
            direct_reverse = direct_ordered_scalar_residue(self.reverse_scalar)
            if direct_reverse != self.reverse_residue:
                raise ValueError("the direct reverse residue differs from the declared projection")
        return {
            "parameter": f"a{self.parameter_index}",
            "forward_scalar_digest": _cochain_digest((self.forward.scalar,)),
            "forward_direct_laurent_residue": str(direct_forward),
            "forward_direct_and_transferred_residues_equal": direct_forward == forward_residue,
            "reverse_scalar_term_count": len(self.reverse_scalar.terms),
            "reverse_scalar_digest": _cochain_digest((self.reverse_scalar,)),
            "reverse_defect_term_count": len(self.reverse_defect.terms),
            "reverse_defect_digest": _cochain_digest((self.reverse_defect,)),
            "reverse_scalar_closed_exact": self.reverse_defect.is_zero(),
            "reverse_cover_residue": (
                None if self.reverse_residue is None else str(self.reverse_residue)
            ),
            "reverse_direct_and_transferred_residues_equal": (
                direct_reverse is not None and direct_reverse == self.reverse_residue
            ),
            "reverse_projection_depth": self.reverse_projection_depth,
            "exchange_difference_term_count": len(self.difference.terms),
            "exchange_difference_digest": _cochain_digest((self.difference,)),
            "exchange_residue_difference": (
                None if self.reverse_residue is None
                else str(self.reverse_residue - forward_residue)
            ),
            "exchange_difference_boundary_exact": self.difference_primitive is not None,
            "exchange_primitive_term_count": (
                None if self.difference_primitive is None else len(self.difference_primitive.terms)
            ),
            "exchange_primitive_digest": (
                None if self.difference_primitive is None
                else _cochain_digest((self.difference_primitive,))
            ),
            "exchange_homotopy_depth": self.homotopy_depth,
            "physical_higgs_identification_certified": False,
        }


@cache
def alternate_up_pairing_exchange(parameter_index: int) -> PairingExchangeCoefficient:
    """Exchange the actual matter inputs without changing h or its primitive."""

    if parameter_index not in (0, 1):
        raise ValueError("the alternate exchange parameter index is unavailable")
    forward = alternate_up_first_order_scalar(parameter_index)
    _, pinned_forward = _verified_payload(FORWARD_SCALARS)
    pinned_coefficients = cast(list[dict[str, object]], pinned_forward["parameter_coefficients"])
    if forward.as_record() != pinned_coefficients[parameter_index]:
        raise ValueError("the reconstructed forward scalar differs from its pinned record")
    if direct_ordered_scalar_residue(forward.scalar) != forward.residue:
        raise ValueError("the direct forward residue disagrees with the transferred projection")
    exterior, _ = alternate_up_exterior_context()
    unit = mixed_schoen_unit()
    left, right = alternate_null_matter()
    wedge = resolution_vector_wedge(
        right, left, exterior, _MixedContraction(exterior, unit), 1, 1,
    )
    if not _MixedContraction(exterior, unit).differential(wedge).is_zero():
        raise ValueError("the actual reversed null wedge is not a full cycle")
    line = MixedSchoenUnit(
        "B1", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B1", 0, QUOTIENT_LINE),),
    )
    quotient_context = _MixedContraction(line, unit)
    quotient_left = _quotient(forward.left_correction, quotient_context)
    quotient_right = _quotient(forward.right_correction, quotient_context)
    cross = even_vector_line_product(
        quotient_right, left,
    ) + even_vector_line_product(quotient_left, right, reverse=True).scale(-1)
    h = alternate_up_dual_higgs_inputs().higgs_covector
    reverse_scalar = mixed_outer_cup(h, cross) + mixed_outer_cup(
        alternate_up_exterior_primitive(parameter_index).primitive, wedge,
    )
    context = _scalar_context()
    reverse_defect = context.differential(reverse_scalar)
    residue, projection_depth = None, None
    difference = reverse_scalar + forward.scalar.scale(-1)
    primitive, homotopy_depth = None, None
    if reverse_defect.is_zero():
        coordinates, projection_depth = _perturbed_projection(reverse_scalar, context, 3)
        if set(coordinates) - {0}:
            raise ValueError("the reverse scalar has an undeclared trace coordinate")
        residue = coordinates.get(0, Eisenstein(0))
        if direct_ordered_scalar_residue(reverse_scalar) != residue:
            raise ValueError("the direct reverse residue disagrees with the transferred projection")
        if residue == forward.residue:
            primitive, homotopy_depth = perturbed_homotopy(difference, context)
            if context.differential(primitive) != difference:
                raise ValueError("the exchange homotopy failed its full differential identity")
    return PairingExchangeCoefficient(
        parameter_index, forward, reverse_scalar, reverse_defect, residue,
        projection_depth, difference, primitive, homotopy_depth,
    )


def _cochain_record(cochain: SparseOuterCechCochain) -> dict[str, object]:
    """Retain exact terms for independent verification, not a hidden fallback."""

    return {
        "term_count": len(cochain.terms),
        "cochain_digest": _cochain_digest((cochain,)),
        "terms": [
            {"basis": _basis_record(basis), "coefficient": str(value)}
            for basis, value in cochain.terms
        ],
    }


def load_alternate_up_pairing_cochains(
    parameter_index: int,
    path: Path = OUTPUT,
) -> tuple[
    SparseOuterCechCochain, SparseOuterCechCochain,
    SparseOuterCechCochain, SparseOuterCechCochain | None,
]:
    """Verify declared full witnesses without an automatic solver fallback.

    The compressed artifact is an explicit, content-addressed prerequisite.
    Missing or inconsistent data fail. Scalar closure and the complete
    exterior primitive identity are rechecked after decoding, so a cache
    cannot manufacture an input or conceal a failed scientific calculation.
    """

    if parameter_index not in (0, 1):
        raise ValueError("the alternate exchange parameter index is unavailable")
    _, record = _verified_payload(path)
    forward_digest, forward_reference = _verified_payload(FORWARD_SCALARS)
    exterior_digest, exterior_reference = _verified_payload(EXTERIOR_WITNESSES)
    prerequisites = {"forward_scalars": forward_digest, "full_exterior_primitives": exterior_digest}
    archive_path = path.with_suffix(".cochains.json.gz")
    if (
        record.get("schema") != "alternate-up-pairing-exchange-v1"
        or record.get("prerequisite_artifact_digests") != prerequisites
        or record.get("full_cochain_archive_name") != archive_path.name
        or any(record.get(field) is not False for field in (
            "symmetrizing_average_used", "primitive_sign_changed",
            "physical_higgs_identification_certified",
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the declared pairing-exchange prerequisite changed")
    archive = archive_path.read_bytes()
    if hashlib.sha256(archive).hexdigest() != record.get("full_cochain_archive_sha256"):
        raise ValueError("the full pairing-exchange archive does not match its declared digest")
    full = json.loads(gzip.decompress(archive))
    digest = full.pop("artifact_digest", None)
    if (
        digest != _canonical_digest(full)
        or digest != record.get("full_cochain_payload_digest")
        or full.get("schema") != "alternate-up-pairing-exchange-cochains-v1"
        or full.get("prerequisite_artifact_digests") != prerequisites
        or [item.get("parameter") for item in full.get("parameter_coefficients", [])]
        != ["a0", "a1"]
    ):
        raise ValueError("the full pairing-exchange cochains changed their content or source")

    def decode(raw: object) -> SparseOuterCechCochain:
        if not isinstance(raw, dict):
            raise ValueError("a pairing-exchange cochain requires its exact term record")
        if raw.get("term_count") == 0 and raw.get("terms") == []:
            cochain = SparseOuterCechCochain()
        else:
            cochain = _representative(raw)
        if (
            len(cochain.terms) != raw.get("term_count")
            or _cochain_digest((cochain,)) != raw.get("cochain_digest")
        ):
            raise ValueError("a pairing-exchange cochain changed its exact normalized terms")
        return cochain

    coefficient = full["parameter_coefficients"][parameter_index]
    summary = cast(list[dict[str, object]], record["parameter_coefficients"])[parameter_index]
    forward = decode(coefficient["forward_scalar"])
    reverse = decode(coefficient["reverse_scalar"])
    primitive = decode(coefficient["exterior_primitive"])
    raw_exchange = coefficient["exchange_primitive"]
    exchange = None if raw_exchange is None else decode(raw_exchange)
    reference = cast(list[dict[str, object]], forward_reference["parameter_coefficients"])[
        parameter_index
    ]
    exterior_witness = cast(list[dict[str, object]], exterior_reference["witnesses"])[
        parameter_index
    ]
    _, exterior_context = alternate_up_exterior_context()
    if (
        summary.get("parameter") != f"a{parameter_index}"
        or summary.get("forward_scalar_digest") != reference["scalar_digest"]
        or summary.get("forward_direct_laurent_residue") != reference["ordered_cover_residue"]
        or len(forward.terms) != reference["scalar_term_count"]
        or len(reverse.terms) != summary["reverse_scalar_term_count"]
        or len(primitive.terms) != exterior_witness["primitive_term_count"]
        or _cochain_digest((forward,)) != reference["scalar_digest"]
        or _cochain_digest((reverse,)) != summary["reverse_scalar_digest"]
        or _cochain_digest((primitive,)) != exterior_witness["primitive_digest"]
        or _cochain_digest((exterior_context.differential(primitive),))
        != exterior_witness["product_digest"]
        or str(direct_ordered_scalar_residue(forward)) != reference["ordered_cover_residue"]
    ):
        raise ValueError("the archived actual cochains do not satisfy their full pinned identities")
    scalar_context = _scalar_context()
    reverse_defect = scalar_context.differential(reverse)
    if (
        _cochain_digest((reverse_defect,)) != summary["reverse_defect_digest"]
        or reverse_defect.is_zero() != summary["reverse_scalar_closed_exact"]
    ):
        raise ValueError("the archived reverse scalar has a different full closure defect")
    if reverse_defect.is_zero() and (
        str(direct_ordered_scalar_residue(reverse)) != summary["reverse_cover_residue"]
    ):
        raise ValueError("the archived reverse scalar has a different literal residue")
    if (exchange is not None) != summary["exchange_difference_boundary_exact"]:
        raise ValueError("the archived exchange boundary assignment changed")
    if exchange is not None and (
        len(exchange.terms) != summary["exchange_primitive_term_count"]
        or _cochain_digest((exchange,)) != summary["exchange_primitive_digest"]
        or scalar_context.differential(exchange) != reverse + forward.scale(-1)
    ):
        raise ValueError("the archived exchange homotopy failed its full identity")
    return forward, reverse, primitive, exchange


def write_alternate_up_pairing_exchange(path: Path = OUTPUT) -> dict[str, object]:
    """Persist either verified exchange boundaries or explicit obstructions."""

    forward_digest, _ = _verified_payload(FORWARD_SCALARS)
    exterior_digest, exterior_reference = _verified_payload(EXTERIOR_WITNESSES)
    exterior_records = cast(list[dict[str, object]], exterior_reference["witnesses"])
    screens = []
    full_records = []
    for index in range(2):
        print(f"checking actual ordered pairing exchange a{index}", flush=True)
        screen = alternate_up_pairing_exchange(index)
        primitive_witness = alternate_up_exterior_primitive(index)
        if primitive_witness.as_record() != exterior_records[index]:
            raise ValueError("the exchange used a different full exterior primitive")
        screens.append(screen.as_record())
        full_records.append({
            "parameter": f"a{index}",
            "forward_scalar": _cochain_record(screen.forward.scalar),
            "reverse_scalar": _cochain_record(screen.reverse_scalar),
            "exterior_primitive": _cochain_record(primitive_witness.primitive),
            "exchange_primitive": (
                None if screen.difference_primitive is None
                else _cochain_record(screen.difference_primitive)
            ),
        })
        print(json.dumps(screen.as_record(), sort_keys=True), flush=True)
    full_payload: dict[str, object] = {
        "schema": "alternate-up-pairing-exchange-cochains-v1",
        "prerequisite_artifact_digests": {
            "forward_scalars": forward_digest, "full_exterior_primitives": exterior_digest,
        },
        "parameter_coefficients": full_records,
    }
    full_digest = _canonical_digest(full_payload)
    full_payload["artifact_digest"] = full_digest
    archive = gzip.compress(
        json.dumps(full_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        mtime=0,
    )
    archive_path = path.with_suffix(".cochains.json.gz")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_temporary = archive_path.with_name(f".{archive_path.name}.tmp")
    archive_temporary.write_bytes(archive)
    archive_temporary.replace(archive_path)
    payload: dict[str, object] = {
        "schema": "alternate-up-pairing-exchange-v1",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "parameter_coefficients": screens,
        "exchange_expected_sign": "positive: two cohomological degrees and two exterior slots",
        "primitive_sign_changed": False,
        "symmetrizing_average_used": False,
        "physical_higgs_identification_certified": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "full_cochain_archive_name": archive_path.name,
        "full_cochain_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "full_cochain_payload_digest": full_digest,
        "prerequisite_artifact_digests": {
            "forward_scalars": forward_digest, "full_exterior_primitives": exterior_digest,
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_pairing_exchange()
    print(f"artifact_digest: {record['artifact_digest']}")
