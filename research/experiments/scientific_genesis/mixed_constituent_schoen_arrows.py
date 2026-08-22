"""Embed the selected mixed constituent arrows in the common Schoen grading.

Owns:
    Common-cover object degrees, Hilbert--Burch arrows, mixed extension terms,
    multidegree checks, cover regularity, closure, and deck eigencharacters.

Depends on:
    Selected full constituent Cech cocycles, exact resolution actions, the
    Schoen complete-intersection degrees, and sparse Eisenstein arithmetic.

Must not:
    Replace mixed arrows by pure canonical Cech classes, construct the outer
    rank-four cone, or infer Higgs and matter cohomology from term counts.

Phase 0:
    Research-only common-Schoen constituent arrow data for the next transfer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.dp9_actions import (
    published_coordinate_images,
)
from research.experiments.computable_carrier.dp9_serre_actions import (
    _dual_frame_actions,
    _fiber_coordinate_images,
    _monomial_image,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.resolution_actions import (
    tier_a_resolution_actions,
)

from .published_constituent_full_cech import (
    ConstituentCechBasis,
    ConstituentFullCochain,
    PublishedConstituentFullCech,
    published_constituent_full_cech,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json"
)

LineDegree = tuple[int, int, int]
Monomial3 = tuple[int, int, int]
Monomial2 = tuple[int, int]
Cell = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]


@dataclass(frozen=True, slots=True)
class MixedConstituentObject:
    """One line-bundle object in a selected constituent resolution."""

    name: str
    position: int
    line_degree: LineDegree


@dataclass(frozen=True, slots=True)
class MixedResolutionArrow:
    """One exact Hilbert--Burch polynomial arrow in the common grading."""

    source: int
    target: int
    polynomial: Polynomial
    factor: int


@dataclass(frozen=True, slots=True)
class MixedExtensionTerm:
    """One sparse term of the selected full constituent extension arrow."""

    source: int
    target: int
    parent_degree: int
    koszul_equation: int | None
    x_monomial: Monomial3
    u_monomial: Monomial3
    p_monomial: Monomial2
    cell: Cell
    coefficient: Eisenstein

    @property
    def cech_degree(self) -> int:
        """Return the total degree in the three-factor standard cover."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def koszul_degree(self) -> int:
        """Return zero or one for the selected hypersurface wedge."""

        return int(self.koszul_equation is not None)

    @property
    def monomial_degree(self) -> LineDegree:
        """Return the common Schoen multidegree of this Laurent monomial."""

        return (
            sum(self.x_monomial),
            sum(self.u_monomial),
            sum(self.p_monomial),
        )

    @property
    def regular_on_cell(self) -> bool:
        """Return whether every Laurent pole is inverted on its cover cell."""

        return all(
            all(exponent >= 0 or index in simplex for index, exponent in enumerate(monomial))
            for monomial, simplex in zip(
                (self.x_monomial, self.u_monomial, self.p_monomial),
                self.cell,
                strict=True,
            )
        )


@dataclass(frozen=True, slots=True)
class MixedSchoenConstituent:
    """One selected W1/W2 twisted constituent in the common Schoen cover."""

    name: str
    factor: int
    twist: LineDegree
    full: PublishedConstituentFullCech
    objects: tuple[MixedConstituentObject, ...]
    resolution_arrows: tuple[MixedResolutionArrow, ...]
    extension_terms: tuple[MixedExtensionTerm, ...]

    @property
    def all_terms_total_degree_one(self) -> bool:
        """Return whether every mixed component is a degree-one arrow term."""

        return all(
            self.objects[term.target].position
            - self.objects[term.source].position
            - term.koszul_degree
            + term.cech_degree
            == 1
            for term in self.extension_terms
        )

    @property
    def all_multidegrees_compatible(self) -> bool:
        """Return whether each term has the exact line-bundle map degree."""

        equation_degree = {
            None: (0, 0, 0),
            1: (3, 0, 1),
            2: (0, 3, 1),
        }
        return all(
            term.monomial_degree
            == cast(
                LineDegree,
                tuple(
                    target - source - equation
                    for target, source, equation in zip(
                        self.objects[term.target].line_degree,
                        self.objects[term.source].line_degree,
                        equation_degree[term.koszul_equation],
                        strict=True,
                    )
                ),
            )
            for term in self.extension_terms
        )

    @property
    def exact(self) -> bool:
        """Return all selected-arrow embedding gates."""

        return (
            self.full.exact
            and self.full.alignment.has_syzygy_koszul_component
            and self.all_terms_total_degree_one
            and self.all_multidegrees_compatible
            and all(term.regular_on_cell for term in self.extension_terms)
            and _selected_deck_eigen(self.full)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize common-cover term distributions and exact gates."""

        distributions: dict[str, int] = {}
        for term in self.extension_terms:
            key = (
                f"parent{term.parent_degree}:"
                f"koszul{term.koszul_degree}:cech{term.cech_degree}"
            )
            distributions[key] = distributions.get(key, 0) + 1
        return {
            "name": self.name,
            "factor": self.factor,
            "twist": list(self.twist),
            "object_count": len(self.objects),
            "resolution_arrow_count": len(self.resolution_arrows),
            "extension_term_count": len(self.extension_terms),
            "extension_term_distribution": distributions,
            "all_terms_total_degree_one": self.all_terms_total_degree_one,
            "all_multidegrees_compatible": self.all_multidegrees_compatible,
            "all_terms_regular_on_declared_cells": all(
                term.regular_on_cell for term in self.extension_terms
            ),
            "full_constituent_cocycle_closed": self.full.full_closed,
            "selected_deck_eigencharacters_exact": _selected_deck_eigen(self.full),
            "exact": self.exact,
        }


def _permutation(images: tuple[tuple[Eisenstein, tuple[int, ...]], ...]) -> tuple[int, ...]:
    """Return the coordinate permutation of one monomial action."""

    result = tuple(exponents.index(1) for _scalar, exponents in images)
    if sorted(result) != list(range(len(images))):
        raise ValueError("selected deck action is not a coordinate permutation")
    return result


def _orientation(values: tuple[int, ...]) -> int:
    """Return the sign needed to sort one oriented simplex."""

    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _full_action(
    result: PublishedConstituentFullCech,
    generator: str,
) -> ConstituentFullCochain:
    """Apply the exact aligned deck action to one full constituent cocycle."""

    extension = result.alignment.action.derived.extension
    pair = tier_a_resolution_actions()[extension.surface_factor - 1]
    frames = _dual_frame_actions(pair, generator)
    base_images = published_coordinate_images(generator)
    fiber_images = _fiber_coordinate_images(generator, extension.surface_factor)
    base_permutation = _permutation(base_images)
    fiber_permutation = _permutation(fiber_images)
    twist = (
        result.alignment.action.p_twist
        if generator == "P"
        else result.alignment.action.t_twist
    )
    terms = []
    for basis, coefficient in result.representative.terms:
        base_scalar, base_monomial = _monomial_image(
            basis.base_monomial,
            base_images,
        )
        fiber_scalar, fiber_monomial = _monomial_image(
            basis.fiber_monomial,
            fiber_images,
        )
        base_raw = tuple(base_permutation[index] for index in basis.cell[0])
        fiber_raw = tuple(fiber_permutation[index] for index in basis.cell[1])
        cell_sign = _orientation(base_raw) * _orientation(fiber_raw)
        frame = frames[basis.component.parent_degree]
        for target_index in range(frame.row_count):
            frame_scalar = frame[target_index][basis.component.bundle_index]
            if frame_scalar.is_zero():
                continue
            component = type(basis.component)(
                basis.component.parent_degree,
                target_index,
                basis.component.koszul_degree,
                basis.component.base_degree,
                basis.component.fiber_degree,
            )
            terms.append(
                (
                    ConstituentCechBasis(
                        component,
                        cast(Monomial3, base_monomial),
                        cast(Monomial2, fiber_monomial),
                        (
                            tuple(sorted(base_raw)),
                            tuple(sorted(fiber_raw)),
                        ),
                    ),
                    coefficient
                    * base_scalar
                    * fiber_scalar
                    * frame_scalar
                    * twist
                    * cell_sign,
                )
            )
    return ConstituentFullCochain(tuple(terms))


def _selected_deck_eigen(result: PublishedConstituentFullCech) -> bool:
    """Return both exact full-cover selected-eigenvector identities."""

    return all(
        _full_action(result, generator)
        == result.representative.scale(character)
        for generator, character in zip(
            ("P", "T"),
            result.alignment.source_character,
            strict=True,
        )
    )


def _objects(
    result: PublishedConstituentFullCech,
    factor: int,
    twist: LineDegree,
) -> tuple[MixedConstituentObject, ...]:
    """Build the line objects of one selected constituent resolution."""

    extension = result.alignment.action.derived.extension
    position = factor - 1

    def line(base_shift: int, fiber_shift: int) -> LineDegree:
        values = list(twist)
        values[position] -= base_shift
        values[2] += fiber_shift
        return cast(LineDegree, tuple(values))

    objects = [MixedConstituentObject("A", 0, line(0, -1))]
    objects.extend(
        MixedConstituentObject(f"F0:{index}", 0, line(degree, 1))
        for index, degree in enumerate(extension.generator_degrees)
    )
    objects.extend(
        MixedConstituentObject(f"F1:{index}", -1, line(degree, 1))
        for index, degree in enumerate(extension.syzygy_degrees)
    )
    return tuple(objects)


def _resolution_arrows(
    result: PublishedConstituentFullCech,
    factor: int,
) -> tuple[MixedResolutionArrow, ...]:
    """Embed every nonzero Hilbert--Burch entry in object indices."""

    extension = result.alignment.action.derived.extension
    source_offset = 1 + len(extension.generator_degrees)
    return tuple(
        MixedResolutionArrow(
            source_offset + column,
            1 + row,
            polynomial,
            factor,
        )
        for row, matrix_row in enumerate(extension.scheme.resolution.matrix)
        for column, polynomial in enumerate(matrix_row)
        if not polynomial.is_zero()
    )


def _extension_terms(
    result: PublishedConstituentFullCech,
    factor: int,
) -> tuple[MixedExtensionTerm, ...]:
    """Embed every selected full-Cech extension term in the Schoen cover."""

    extension = result.alignment.action.derived.extension
    source_offsets = (1, 1 + len(extension.generator_degrees))
    zero = (0, 0, 0)
    terms = []
    for basis, coefficient in result.representative.terms:
        parent = basis.component.parent_degree
        source = source_offsets[parent] + basis.component.bundle_index
        if factor == 1:
            x_monomial = basis.base_monomial
            u_monomial = zero
            cell = (basis.cell[0], (0,), basis.cell[1])
        else:
            x_monomial = zero
            u_monomial = basis.base_monomial
            cell = ((0,), basis.cell[0], basis.cell[1])
        terms.append(
            MixedExtensionTerm(
                source,
                0,
                parent,
                factor if basis.component.koszul_degree else None,
                cast(Monomial3, x_monomial),
                cast(Monomial3, u_monomial),
                basis.fiber_monomial,
                cast(Cell, cell),
                coefficient,
            )
        )
    return tuple(terms)


def _constituent(
    result: PublishedConstituentFullCech,
    name: str,
    factor: int,
    twist: LineDegree,
) -> MixedSchoenConstituent:
    """Construct one selected constituent in the synchronized grading."""

    constituent = MixedSchoenConstituent(
        name,
        factor,
        twist,
        result,
        _objects(result, factor, twist),
        _resolution_arrows(result, factor),
        _extension_terms(result, factor),
    )
    if not constituent.exact:
        raise ValueError("a selected mixed Schoen constituent failed")
    return constituent


@cache
def mixed_schoen_constituents(
) -> tuple[MixedSchoenConstituent, MixedSchoenConstituent]:
    """Return the selected V1/V2 arrows in the common Schoen grading."""

    first, second = published_constituent_full_cech()
    return (
        _constituent(first, "V1", 1, (-1, 1, 0)),
        _constituent(second, "V2", 2, (1, -1, 0)),
    )


def write_mixed_schoen_constituents(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed mixed constituent arrow certificate."""

    constituents = mixed_schoen_constituents()
    payload: dict[str, object] = {
        "schema": "mixed-constituent-schoen-arrows-v1",
        "constituents": [item.as_record() for item in constituents],
        "all_common_schoen_arrows_exact": all(item.exact for item in constituents),
        "retired_pure_cech_arrows_used": False,
        "outer_hom_transfer_constructed": False,
        "next_required_object": (
            "Alexander--Whitney convolution of these mixed arrow terms with "
            "the synchronized Schoen outer Hom complex"
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
    """Regenerate the selected common-Schoen constituent arrows."""

    payload = write_mixed_schoen_constituents()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"all_common_schoen_arrows_exact: {payload['all_common_schoen_arrows_exact']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedConstituentObject",
    "MixedExtensionTerm",
    "MixedResolutionArrow",
    "MixedSchoenConstituent",
    "mixed_schoen_constituents",
]
