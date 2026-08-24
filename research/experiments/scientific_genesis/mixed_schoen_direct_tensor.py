"""Construct the lawful mixed constituent tensor in the common Schoen grading.

Owns:
    The signed total tensor of the two selected mixed constituent complexes,
    including both factor resolutions and full Cech--Koszul extension arrows.

Depends on:
    The exact synchronized constituent complexes and sparse polynomial arithmetic.

Must not:
    Use determinant-twist Hom identifications, retired diagonal cones, select a
    Higgs class, or import expected cohomology dimensions or deck characters.

Phase 0:
    Research-only direct tensor complex for the lawful Higgs calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from functools import cache
from itertools import product
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedExtensionTerm,
    MixedResolutionArrow,
    MixedSchoenConstituent,
    mixed_schoen_constituents,
)

LineDegree = tuple[int, int, int]
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_direct_tensor.json"


def _add_degree(left: LineDegree, right: LineDegree) -> LineDegree:
    """Add two exact common-Schoen line degrees."""

    return cast(
        LineDegree,
        tuple(first + second for first, second in zip(left, right, strict=True)),
    )


@dataclass(frozen=True, slots=True)
class MixedSchoenTensorComplex:
    """A naïve merged-arrow candidate for the lawful constituent tensor."""

    name: str
    factor: int
    twist: LineDegree
    objects: tuple[MixedConstituentObject, ...]
    resolution_arrows: tuple[MixedResolutionArrow, ...]
    extension_terms: tuple[MixedExtensionTerm, ...]
    first_object_count: int
    second_object_count: int

    def object_index(self, first_index: int, second_index: int) -> int:
        """Return the deterministic first-major tensor-object index."""

        if not 0 <= first_index < self.first_object_count:
            raise IndexError(first_index)
        if not 0 <= second_index < self.second_object_count:
            raise IndexError(second_index)
        return first_index * self.second_object_count + second_index

    @property
    def all_terms_total_degree_one(self) -> bool:
        """Return whether every tensor differential term has total degree one."""

        return all(
            self.objects[term.target].position
            - self.objects[term.source].position
            - term.koszul_degree
            + term.cech_degree
            == 1
            for term in self.extension_terms
        )

    @property
    def exact_shape(self) -> bool:
        """Return deterministic object, arrow, and degree gates."""

        return (
            self.factor == 3
            and len(self.objects) == self.first_object_count * self.second_object_count
            and self.all_terms_total_degree_one
            and all(arrow.factor in (1, 2) for arrow in self.resolution_arrows)
        )


def _tensor_resolution_arrows(
    first: MixedSchoenConstituent,
    second: MixedSchoenConstituent,
) -> tuple[MixedResolutionArrow, ...]:
    """Return d_first tensor 1 plus the signed 1 tensor d_second arrows."""

    second_count = len(second.objects)
    result = []
    for arrow in first.resolution_arrows:
        for second_index in range(second_count):
            result.append(
                MixedResolutionArrow(
                    arrow.source * second_count + second_index,
                    arrow.target * second_count + second_index,
                    arrow.polynomial,
                    arrow.factor,
                )
            )
    for first_index, first_object in enumerate(first.objects):
        sign = -1 if first_object.position % 2 else 1
        for arrow in second.resolution_arrows:
            result.append(
                MixedResolutionArrow(
                    first_index * second_count + arrow.source,
                    first_index * second_count + arrow.target,
                    arrow.polynomial.scale(sign),
                    arrow.factor,
                )
            )
    return tuple(result)


def _shift_extension_term(
    term: MixedExtensionTerm,
    source: int,
    target: int,
    sign: int,
) -> MixedExtensionTerm:
    """Embed one constituent extension term in the tensor object indexing."""

    return MixedExtensionTerm(
        source,
        target,
        term.parent_degree,
        term.koszul_equation,
        term.x_monomial,
        term.u_monomial,
        term.p_monomial,
        term.cell,
        term.coefficient * sign,
    )


def _tensor_extension_terms(
    first: MixedSchoenConstituent,
    second: MixedSchoenConstituent,
) -> tuple[MixedExtensionTerm, ...]:
    """Return the signed full-Cech extension part of the tensor differential."""

    second_count = len(second.objects)
    result = []
    for term in first.extension_terms:
        for second_index in range(second_count):
            result.append(
                _shift_extension_term(
                    term,
                    term.source * second_count + second_index,
                    term.target * second_count + second_index,
                    1,
                )
            )
    for first_index, first_object in enumerate(first.objects):
        sign = -1 if first_object.position % 2 else 1
        for term in second.extension_terms:
            result.append(
                _shift_extension_term(
                    term,
                    first_index * second_count + term.source,
                    first_index * second_count + term.target,
                    sign,
                )
            )
    return tuple(result)


@cache
def naive_mixed_schoen_direct_tensor_candidate() -> MixedSchoenTensorComplex:
    """Return the merged-arrow candidate whose full differential is audited."""

    first, second = mixed_schoen_constituents()
    objects = tuple(
        MixedConstituentObject(
            f"{first_object.name}*{second_object.name}",
            first_object.position + second_object.position,
            _add_degree(first_object.line_degree, second_object.line_degree),
        )
        for first_object in first.objects
        for second_object in second.objects
    )
    result = MixedSchoenTensorComplex(
        "V1 tensor V2",
        3,
        _add_degree(first.twist, second.twist),
        objects,
        _tensor_resolution_arrows(first, second),
        _tensor_extension_terms(first, second),
        len(first.objects),
        len(second.objects),
    )
    if not result.exact_shape:
        raise ValueError("the direct mixed tensor complex failed its shape gates")
    return result


@dataclass(frozen=True, slots=True)
class NaiveTensorSquareWitness:
    """A compact exact witness that the merged full differential is invalid."""

    degree: int
    reduced_index: int
    left_object: int
    object_degree: int
    line_degree: LineDegree
    koszul_summand: str
    x_monomial: tuple[int, int, int]
    u_monomial: tuple[int, int, int]
    p_monomial: tuple[int, int]
    seed_term_count: int
    first_image_term_count: int
    square_term_count: int

    @property
    def exact_obstruction(self) -> bool:
        """Return whether the declared witness has a nonzero differential square."""

        return self.square_term_count > 0

    def as_record(self) -> dict[str, object]:
        """Serialize the minimal merged-arrow square witness."""

        return {
            "degree": self.degree,
            "reduced_index": self.reduced_index,
            "component": {
                "left_object": self.left_object,
                "object_degree": self.object_degree,
                "line_degree": list(self.line_degree),
                "koszul_summand": self.koszul_summand,
            },
            "monomials": {
                "x": list(self.x_monomial),
                "u": list(self.u_monomial),
                "p": list(self.p_monomial),
            },
            "seed_term_count": self.seed_term_count,
            "first_image_term_count": self.first_image_term_count,
            "square_term_count": self.square_term_count,
            "differential_square_nonzero": self.exact_obstruction,
        }


@cache
def naive_tensor_square_witness() -> NaiveTensorSquareWitness:
    """Return the first deterministic D-squared witness for merged arrows."""

    from research.experiments.computable_carrier.schoen_serre_outer_transfer import (  # noqa: PLC0415
        _include,
        _reduced_basis,
    )

    from .mixed_schoen_outer_actions import _MixedContraction  # noqa: PLC0415
    from .mixed_schoen_outer_transfer import mixed_schoen_unit  # noqa: PLC0415

    contraction = _MixedContraction(
        naive_mixed_schoen_direct_tensor_candidate(),
        mixed_schoen_unit(),
    )
    degree = 0
    reduced_index = 0
    entry = _reduced_basis(
        contraction.left_skeleton,
        contraction.right_skeleton,
        degree,
    )[reduced_index]
    seed = _include(entry)
    first_image = contraction.differential(seed)
    square = contraction.differential(first_image)
    component = entry.component
    result = NaiveTensorSquareWitness(
        degree,
        reduced_index,
        component.left_index,
        component.object_degree,
        component.line_degree,
        component.koszul_summand,
        entry.x_monomial,
        entry.u_monomial,
        entry.p_monomial,
        len(seed.terms),
        len(first_image.terms),
        len(square.terms),
    )
    if not result.exact_obstruction:
        raise ValueError("the merged-arrow tensor obstruction changed")
    return result


@cache
def ordinary_tensor_skeleton_square_zero() -> bool:
    """Return the exact square-zero gate before full Cech--Koszul arrows."""

    from research.experiments.computable_carrier.schoen_serre_outer import (  # noqa: PLC0415
        schoen_serre_outer_hom,
    )

    from .mixed_schoen_outer_transfer import (  # noqa: PLC0415
        _skeleton,
        mixed_schoen_unit,
    )

    reduced = schoen_serre_outer_hom(
        _skeleton(naive_mixed_schoen_direct_tensor_candidate()),
        _skeleton(mixed_schoen_unit()),
    )
    return reduced.squared_zero


def _parity_law_candidate(
    coefficients: tuple[int, int, int, int, int, int],
) -> MixedSchoenTensorComplex:
    """Build one finite parity-law variant of the merged tensor arrows."""

    first, second = mixed_schoen_constituents()
    second_count = len(second.objects)
    objects = tuple(
        replace(
            first_object,
            name=f"{first_object.name}*{second_object.name}",
            position=first_object.position + second_object.position,
            line_degree=_add_degree(
                first_object.line_degree,
                second_object.line_degree,
            ),
        )
        for first_object in first.objects
        for second_object in second.objects
    )
    terms = []
    for term in first.extension_terms:
        internal = (term.cech_degree - term.koszul_degree) % 2
        for second_index, second_object in enumerate(second.objects):
            opposite = second_object.position % 2
            exponent = (
                coefficients[0] * opposite
                + coefficients[1] * internal
                + coefficients[2] * opposite * internal
            ) % 2
            terms.append(
                replace(
                    _shift_extension_term(
                        term,
                        term.source * second_count + second_index,
                        term.target * second_count + second_index,
                        -1 if exponent else 1,
                    ),
                    parent_degree=term.parent_degree - second_object.position,
                )
            )
    for first_index, first_object in enumerate(first.objects):
        opposite = first_object.position % 2
        for term in second.extension_terms:
            internal = (term.cech_degree - term.koszul_degree) % 2
            exponent = (
                coefficients[3] * opposite
                + coefficients[4] * internal
                + coefficients[5] * opposite * internal
            ) % 2
            terms.append(
                replace(
                    _shift_extension_term(
                        term,
                        first_index * second_count + term.source,
                        first_index * second_count + term.target,
                        -1 if exponent else 1,
                    ),
                    parent_degree=term.parent_degree - first_object.position,
                )
            )
    return MixedSchoenTensorComplex(
        f"parity-law:{''.join(str(value) for value in coefficients)}",
        3,
        _add_degree(first.twist, second.twist),
        objects,
        _tensor_resolution_arrows(first, second),
        tuple(terms),
        len(first.objects),
        second_count,
    )


@cache
def tensor_sign_law_scan() -> dict[str, object]:
    """Falsify all linear parity-only repairs on three exact witnesses."""

    from research.experiments.computable_carrier.schoen_serre_outer_transfer import (  # noqa: PLC0415
        _include,
        _reduced_basis,
    )

    from .mixed_schoen_outer_actions import _MixedContraction  # noqa: PLC0415
    from .mixed_schoen_outer_transfer import mixed_schoen_unit  # noqa: PLC0415

    witnesses = ((0, 0), (1, 1), (1, 10))
    survivors = tuple(product((0, 1), repeat=6))
    survivor_counts = []
    for degree, reduced_index in witnesses:
        selected = []
        for coefficients in survivors:
            contraction = _MixedContraction(
                _parity_law_candidate(coefficients),
                mixed_schoen_unit(),
            )
            entry = _reduced_basis(
                contraction.left_skeleton,
                contraction.right_skeleton,
                degree,
            )[reduced_index]
            seed = _include(entry)
            square = contraction.differential(contraction.differential(seed))
            if square.is_zero():
                selected.append(coefficients)
        survivors = tuple(selected)
        survivor_counts.append(len(survivors))
    result: dict[str, object] = {
        "law_family": (
            "independent linear parity exponents in opposite object degree, "
            "internal Cech-minus-Koszul degree, and their product"
        ),
        "declared_law_count": 64,
        "witnesses": [list(witness) for witness in witnesses],
        "survivor_counts": survivor_counts,
        "surviving_laws": [list(item) for item in survivors],
        "sign_only_repair_exists": bool(survivors),
    }
    if survivor_counts != [4, 2, 0] or survivors:
        raise ValueError("the tensor parity-law classification changed")
    return result


def write_mixed_schoen_direct_tensor_audit(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed direct-tensor boundary certificate."""

    candidate = naive_mixed_schoen_direct_tensor_candidate()
    witness = naive_tensor_square_witness()
    skeleton_square_zero = ordinary_tensor_skeleton_square_zero()
    if not skeleton_square_zero:
        raise ValueError("the ordinary tensor skeleton lost square zero")
    payload: dict[str, object] = {
        "schema": "mixed-schoen-direct-tensor-audit-v2",
        "candidate_shape": {
            "object_count": len(candidate.objects),
            "resolution_arrow_count": len(candidate.resolution_arrows),
            "full_extension_term_count": len(candidate.extension_terms),
            "ordinary_resolution_skeleton_square_zero": skeleton_square_zero,
        },
        "naive_merged_arrow_witness": witness.as_record(),
        "parity_sign_law_scan": tensor_sign_law_scan(),
        "physical_higgs_representative_available": False,
        "retired_diagonal_cones_used": False,
        "first_missing_input": (
            "a chain diagonal with complete Koszul-Cech tensor signs for the "
            "two lawful mixed constituent complexes"
        ),
        "status": (
            "ordinary tensor skeleton exact; naive merging of two full "
            "Koszul-Cech arrow sets has nonzero differential square"
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
    """Regenerate the direct-tensor boundary certificate."""

    payload = write_mixed_schoen_direct_tensor_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenTensorComplex",
    "NaiveTensorSquareWitness",
    "naive_mixed_schoen_direct_tensor_candidate",
    "naive_tensor_square_witness",
    "ordinary_tensor_skeleton_square_zero",
    "tensor_sign_law_scan",
    "write_mixed_schoen_direct_tensor_audit",
]
