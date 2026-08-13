"""Lift pair 73 from ambient cohomology into the full Čech-resolution Hom complex.

Owns:
    Exact recursive descent of all four pair-73 invariant Ext classes through
    the projective-product Čech, Schoen Koszul, and presentation-Hom directions.

Depends on:
    The certified pair-73 universal family, exact standard-projective Čech
    contractions, the published Schoen equations, and exact presentation data.

Must not:
    Treat ambient cohomology coordinates as transition matrices, select an
    extension point, or claim local freeness, quotient descent, or stability.

Phase 0:
    The chain-level lift is a research construction; physical carrier gates
    remain unavailable until its exact total-cycle certificate closes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.cech import (
    ProductProjectiveMonomialCechComplex,
    product_projective_monomial_cech_complex,
    projective_monomial_cech_complex,
)
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.polynomial_hom import (
    PolynomialHomComplex,
    polynomial_hom_complex,
)
from research.experiments.computable_carrier.schoen_outer import (
    _factor_matrix,
    _hom_term_lines,
    schoen_presentation,
)
from research.experiments.computable_carrier.tier_b_monomial import (
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _eisenstein_text,
)
from research.experiments.computable_carrier.tier_b_serre_extensions import (
    TierBSerreExtensionRay,
    tier_b_serre_eigenrays,
)

from .pair_73_universal import PAIR_INDEX, PARAMETERS

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/pair_73_cech_lift.json"
SOURCE = ROOT / "data/generated/scientific_genesis/pair_73_source.json"
PARTIAL = ROOT / "data/generated/scientific_genesis/pair_73_cech_lift.partial.json"
KOSZUL_DEGREES = {"k0": 0, "k1_x": -1, "k1_u": -1, "k2": -2}
KOSZUL_SHIFTS = {
    "k0": (0, 0, 0),
    "k1_x": (-3, 0, -1),
    "k1_u": (0, -3, -1),
    "k2": (-3, -3, -2),
}


@dataclass(frozen=True, slots=True, order=True)
class StructuralComponent:
    """One presentation/Koszul summand of the sheaf-resolution Hom complex."""

    parent_degree: int
    hom_term_index: int
    line_degree: tuple[int, int, int]
    koszul_summand: str

    def __post_init__(self) -> None:
        if self.parent_degree not in (-1, 0, 1):
            raise ValueError("presentation Hom degrees must be -1, 0, or 1")
        if self.hom_term_index < 0:
            raise ValueError("Hom term indices must be nonnegative")
        if self.koszul_summand not in KOSZUL_DEGREES:
            raise ValueError("unknown Schoen Koszul summand")

    @property
    def structural_degree(self) -> int:
        """Return presentation plus Koszul cochain degree."""

        return self.parent_degree + KOSZUL_DEGREES[self.koszul_summand]

    @property
    def ambient_degree(self) -> tuple[int, int, int]:
        """Return the ambient line degree of this Koszul summand."""

        shift = KOSZUL_SHIFTS[self.koszul_summand]
        return tuple(left + right for left, right in zip(self.line_degree, shift, strict=True))


@dataclass(frozen=True, slots=True, order=True)
class CechBasisTerm:
    """One exact Laurent monomial on one projective-product intersection."""

    component: StructuralComponent
    x_monomial: tuple[int, int, int]
    u_monomial: tuple[int, int, int]
    p_monomial: tuple[int, int]
    cell: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]

    def __post_init__(self) -> None:
        degrees = (
            sum(self.x_monomial),
            sum(self.u_monomial),
            sum(self.p_monomial),
        )
        if degrees != self.component.ambient_degree:
            raise ValueError("Čech Laurent monomial has the wrong ambient line degree")
        monomials = (self.x_monomial, self.u_monomial, self.p_monomial)
        if any(
            any(index not in simplex for index, exponent in enumerate(monomial) if exponent < 0)
            for monomial, simplex in zip(monomials, self.cell, strict=True)
        ):
            raise ValueError("Čech Laurent monomial is not regular on its declared cell")

    @property
    def cech_degree(self) -> int:
        """Return the total projective-product Čech degree."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def total_degree(self) -> int:
        """Return the total Hom-resolution degree."""

        return self.component.structural_degree + self.cech_degree


@dataclass(frozen=True, slots=True)
class SparseCechCochain:
    """An immutable normalized sparse Čech-resolution Hom cochain."""

    terms: tuple[tuple[CechBasisTerm, Eisenstein], ...]

    def __init__(self, terms: tuple[tuple[CechBasisTerm, Eisenstein], ...] = ()) -> None:
        combined: dict[CechBasisTerm, Eisenstein] = {}
        for basis, coefficient in terms:
            combined[basis] = combined.get(basis, Eisenstein(0)) + coefficient
        normalized = tuple(
            sorted(
                (
                    (basis, coefficient)
                    for basis, coefficient in combined.items()
                    if not coefficient.is_zero()
                ),
                key=lambda item: item[0],
            )
        )
        object.__setattr__(self, "terms", normalized)

    def __add__(self, other: SparseCechCochain) -> SparseCechCochain:
        return SparseCechCochain(self.terms + other.terms)

    def scale(self, scalar: Eisenstein | int) -> SparseCechCochain:
        """Scale every exact cochain coefficient."""

        value = Eisenstein.coerce(scalar)
        return SparseCechCochain(
            tuple((basis, coefficient * value) for basis, coefficient in self.terms)
        )

    def is_zero(self) -> bool:
        """Return whether this normalized cochain has no support."""

        return not self.terms

    @property
    def total_degrees(self) -> tuple[int, ...]:
        """Return all occupied total degrees."""

        return tuple(sorted({basis.total_degree for basis, _ in self.terms}))


@dataclass(frozen=True, slots=True)
class Pair73CechLift:
    """The four exact pair-73 hypercocycles in the full Čech resolution."""

    lifted_term_counts: tuple[tuple[int, ...], ...]
    lifted_term_digests: tuple[str, ...]
    source_cycle_exact: bool
    total_cycles_exact: bool
    universal_linearity_exact: bool
    invariant_certificate_digest: str

    def __post_init__(self) -> None:
        if len(self.lifted_term_counts) != len(PARAMETERS):
            raise ValueError("pair 73 requires four lifted Ext classes")
        if any(len(counts) != 4 for counts in self.lifted_term_counts):
            raise ValueError("pair 73 descent must span Čech degrees three through zero")
        if len(self.lifted_term_digests) != len(PARAMETERS) or any(
            len(digest) != 64 for digest in self.lifted_term_digests
        ):
            raise ValueError("pair 73 requires one SHA-256 lift digest per class")
        if not (
            self.source_cycle_exact and self.total_cycles_exact and self.universal_linearity_exact
        ):
            raise ValueError("pair 73 chain-level lift failed an exact gate")

    def as_record(self) -> dict[str, object]:
        """Serialize the lift and preserve all unresolved carrier gates."""

        return {
            "schema": "pair-73-cech-hypercocycle-lift-v1",
            "global_pair_index": PAIR_INDEX,
            "coefficient_field": "Q(omega)",
            "basis_names": [f"class:{index}" for index in range(4)],
            "descent_cech_degrees": [3, 2, 1, 0],
            "lifted_term_counts": [list(counts) for counts in self.lifted_term_counts],
            "lifted_term_digests": list(self.lifted_term_digests),
            "source_cycle_exact": self.source_cycle_exact,
            "total_cycles_exact": self.total_cycles_exact,
            "universal_linearity_exact": self.universal_linearity_exact,
            "universal_parameters": list(PARAMETERS),
            "invariant_certificate_digest": self.invariant_certificate_digest,
            "chain_level_lift_constructed": True,
            "derived_mapping_cone_available": True,
            "mapping_cone_constructed": True,
            "mapping_cone_differential": "D_E=[[D_left,E(a)],[0,D_right]]",
            "mapping_cone_squared_zero": self.total_cycles_exact,
            "arbitrary_extension_point_selected": False,
            "local_freeness_locus_computed": False,
            "quotient_descent_computed": False,
            "structure_group_locus_computed": False,
            "status": (
                "exact universal chain-level hypercocycle and derived mapping-cone input; "
                "local freeness, quotient descent, Chern gates, and SU(4) locus remain open"
            ),
        }


@dataclass(frozen=True, slots=True)
class Pair73StructuralData:
    """The lightweight exact presentation data needed by the Čech lift."""

    parent: PolynomialHomComplex
    lines: tuple[tuple[int, tuple[tuple[int, int, int], ...]], ...]
    factors: tuple[tuple[int, tuple[tuple[str, ...], ...]], ...]


@cache
def _pair_structure() -> Pair73StructuralData:
    """Reconstruct pair 73 without its memory-heavy sparse cohomology maps."""

    scheme = tier_b_invariant_monomial_schemes(6)[1]
    actions = tier_b_monomial_resolution_actions((scheme,))

    def ray(target_shift: int) -> TierBSerreExtensionRay:
        """Return the exact pair-73 character ray at one target shift."""

        return next(
            selected
            for selected in tier_b_serre_eigenrays(
                (scheme,),
                actions,
                target_shift,
            )
            if tuple(str(value) for value in selected.character_pair) == ("-1-omega", "-1-omega")
        )

    left = schoen_presentation(ray(-6), 1, (-2, -1, 0))
    right = schoen_presentation(ray(0), 1, (-1, 1, 0))
    parent = polynomial_hom_complex(left.candidate, right.candidate)
    return Pair73StructuralData(
        parent,
        _hom_term_lines(left, right),
        tuple(
            (
                degree,
                _factor_matrix(
                    parent,
                    degree,
                    1,
                    1,
                ),
            )
            for degree, _ in parent.differentials
        ),
    )


@cache
def _product_cech_support(
    x_support: tuple[int, ...],
    u_support: tuple[int, ...],
    p_support: tuple[int, ...],
) -> ProductProjectiveMonomialCechComplex:
    """Return one cached projective-product complex per negative support."""

    return product_projective_monomial_cech_complex(
        (
            projective_monomial_cech_complex(
                ("x0", "x1", "x2"),
                tuple(-1 if index in x_support else 0 for index in range(3)),
                scalar_type=Eisenstein,
            ),
            projective_monomial_cech_complex(
                ("u0", "u1", "u2"),
                tuple(-1 if index in u_support else 0 for index in range(3)),
                scalar_type=Eisenstein,
            ),
            projective_monomial_cech_complex(
                ("p0", "p1"),
                tuple(-1 if index in p_support else 0 for index in range(2)),
                scalar_type=Eisenstein,
            ),
        )
    )


def _product_cech(
    x_monomial: tuple[int, int, int],
    u_monomial: tuple[int, int, int],
    p_monomial: tuple[int, int],
) -> ProductProjectiveMonomialCechComplex:
    """Return the exact product complex determined by negative supports."""

    return _product_cech_support(
        tuple(index for index, exponent in enumerate(x_monomial) if exponent < 0),
        tuple(index for index, exponent in enumerate(u_monomial) if exponent < 0),
        tuple(index for index, exponent in enumerate(p_monomial) if exponent < 0),
    )


def _monomial_product(source: tuple[int, ...], multiplier: tuple[int, ...]) -> tuple[int, ...]:
    """Add exact Laurent and polynomial exponents."""

    return tuple(left + right for left, right in zip(source, multiplier, strict=True))


def _multiply_basis(
    basis: CechBasisTerm,
    target: StructuralComponent,
    factor: str,
    exponents: tuple[int, ...],
) -> CechBasisTerm:
    """Multiply one Čech basis term by one homogeneous polynomial monomial."""

    x_monomial = basis.x_monomial
    u_monomial = basis.u_monomial
    p_monomial = basis.p_monomial
    if factor == "x":
        x_monomial = cast(tuple[int, int, int], _monomial_product(x_monomial, exponents))
    elif factor == "u":
        u_monomial = cast(tuple[int, int, int], _monomial_product(u_monomial, exponents))
    elif factor == "p":
        p_monomial = cast(tuple[int, int], _monomial_product(p_monomial, exponents))
    else:
        raise ValueError("Schoen multiplication requires x, u, or p")
    return CechBasisTerm(target, x_monomial, u_monomial, p_monomial, basis.cell)


def _polynomial_images(
    basis: CechBasisTerm,
    target: StructuralComponent,
    polynomial: Polynomial,
    factor: str,
    coefficient: Eisenstein,
) -> tuple[tuple[CechBasisTerm, Eisenstein], ...]:
    """Expand one exact factor-polynomial multiplication sparsely."""

    return tuple(
        (
            _multiply_basis(basis, target, factor, exponents),
            coefficient * cast(Eisenstein, scalar),
        )
        for exponents, scalar in polynomial.terms
    )


def _equation_images(
    basis: CechBasisTerm,
    target: StructuralComponent,
    equation: int,
    coefficient: Eisenstein,
) -> tuple[tuple[CechBasisTerm, Eisenstein], ...]:
    """Expand one of the two exact Schoen complete-intersection equations."""

    cox = schoen_geometry().cover.cox
    if equation == 1:
        records = (
            (cox.cubic_f, "x", (1, 0), Eisenstein(1)),
            (cox.cubic_g, "x", (0, 1), Eisenstein(1)),
        )
    elif equation == 2:
        records = (
            (cox.cubic_f, "u", (0, 1), Eisenstein(2)),
            (cox.cubic_g, "u", (1, 0), Eisenstein(1)),
        )
    else:
        raise ValueError("Schoen Koszul equations are numbered one and two")
    images: list[tuple[CechBasisTerm, Eisenstein]] = []
    for polynomial, factor, p_exponents, prefactor in records:
        for exponents, scalar in polynomial.terms:
            x_monomial = basis.x_monomial
            u_monomial = basis.u_monomial
            if factor == "x":
                x_monomial = cast(
                    tuple[int, int, int],
                    _monomial_product(x_monomial, exponents),
                )
            elif factor == "u":
                u_monomial = cast(
                    tuple[int, int, int],
                    _monomial_product(u_monomial, exponents),
                )
            else:
                raise ValueError("Schoen cubics require an x or u factor")
            p_monomial = cast(
                tuple[int, int],
                _monomial_product(basis.p_monomial, p_exponents),
            )
            images.append(
                (
                    CechBasisTerm(
                        target,
                        x_monomial,
                        u_monomial,
                        p_monomial,
                        basis.cell,
                    ),
                    coefficient * prefactor * cast(Eisenstein, scalar),
                )
            )
    return tuple(images)


def _structural_differential(
    cochain: SparseCechCochain,
    structure: Pair73StructuralData,
) -> SparseCechCochain:
    """Apply presentation plus signed Koszul differential exactly."""

    lines = dict(structure.lines)
    parent = structure.parent
    factors = dict(structure.factors)
    result: list[tuple[CechBasisTerm, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        parent_map = dict(parent.differentials).get(component.parent_degree)
        if parent_map is not None:
            factor_matrix = factors[component.parent_degree]
            for target_index in range(parent_map.codomain.rank):
                polynomial = parent_map.matrix.rows[target_index][component.hom_term_index]
                if polynomial.is_zero():
                    continue
                target = StructuralComponent(
                    component.parent_degree + 1,
                    target_index,
                    lines[component.parent_degree + 1][target_index],
                    component.koszul_summand,
                )
                result.extend(
                    _polynomial_images(
                        basis,
                        target,
                        polynomial,
                        factor_matrix[target_index][component.hom_term_index],
                        coefficient,
                    )
                )
        outer_sign = Eisenstein(-1 if component.parent_degree % 2 else 1)
        if component.koszul_summand == "k2":
            target_x = StructuralComponent(
                component.parent_degree,
                component.hom_term_index,
                component.line_degree,
                "k1_x",
            )
            target_u = StructuralComponent(
                component.parent_degree,
                component.hom_term_index,
                component.line_degree,
                "k1_u",
            )
            result.extend(_equation_images(basis, target_x, 2, coefficient * outer_sign * -1))
            result.extend(_equation_images(basis, target_u, 1, coefficient * outer_sign))
        elif component.koszul_summand == "k1_x":
            target = StructuralComponent(
                component.parent_degree,
                component.hom_term_index,
                component.line_degree,
                "k0",
            )
            result.extend(_equation_images(basis, target, 1, coefficient * outer_sign))
        elif component.koszul_summand == "k1_u":
            target = StructuralComponent(
                component.parent_degree,
                component.hom_term_index,
                component.line_degree,
                "k0",
            )
            result.extend(_equation_images(basis, target, 2, coefficient * outer_sign))
    return SparseCechCochain(tuple(result))


def _cech_differential(cochain: SparseCechCochain) -> SparseCechCochain:
    """Apply the raw signed projective-product Čech differential."""

    result: list[tuple[CechBasisTerm, Eisenstein]] = []
    factor_sizes = (3, 3, 2)
    for basis, coefficient in cochain.terms:
        preceding_degree = 0
        for factor_index, (simplex, size) in enumerate(zip(basis.cell, factor_sizes, strict=True)):
            for vertex in range(size):
                if vertex in simplex:
                    continue
                target_simplex = tuple(sorted((*simplex, vertex)))
                local_sign = -1 if target_simplex.index(vertex) % 2 else 1
                tensor_sign = -1 if preceding_degree % 2 else 1
                target_cell = list(basis.cell)
                target_cell[factor_index] = target_simplex
                result.append(
                    (
                        CechBasisTerm(
                            basis.component,
                            basis.x_monomial,
                            basis.u_monomial,
                            basis.p_monomial,
                            cast(
                                tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
                                tuple(target_cell),
                            ),
                        ),
                        coefficient * local_sign * tensor_sign,
                    )
                )
            preceding_degree += len(simplex) - 1
    return SparseCechCochain(tuple(result))


def _total_differential(
    cochain: SparseCechCochain,
    structure: Pair73StructuralData,
) -> SparseCechCochain:
    """Apply the exact total presentation/Koszul/Čech differential."""

    cech_terms = tuple(
        (basis, coefficient * (-1 if basis.component.structural_degree % 2 else 1))
        for basis, coefficient in _cech_differential(cochain).terms
    )
    return _structural_differential(cochain, structure) + SparseCechCochain(cech_terms)


def _primitive(cochain: SparseCechCochain) -> SparseCechCochain:
    """Contract every independent Laurent-monomial Čech coboundary exactly."""

    groups: dict[
        tuple[
            StructuralComponent,
            tuple[int, int, int],
            tuple[int, int, int],
            tuple[int, int],
        ],
        dict[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]], Eisenstein],
    ] = {}
    for basis, coefficient in cochain.terms:
        key = (
            basis.component,
            basis.x_monomial,
            basis.u_monomial,
            basis.p_monomial,
        )
        groups.setdefault(key, {})[basis.cell] = coefficient
    result: list[tuple[CechBasisTerm, Eisenstein]] = []
    for (component, x_monomial, u_monomial, p_monomial), coefficients in groups.items():
        cech = _product_cech(x_monomial, u_monomial, p_monomial)
        degrees = {sum(len(simplex) - 1 for simplex in cell) for cell in coefficients}
        if len(degrees) != 1:
            raise ValueError("one Laurent monomial group spans multiple Čech degrees")
        degree = next(iter(degrees))
        source = cech.primitive(cech.cochain(degree, coefficients))
        for cell, coefficient in zip(cech.cells_at(degree - 1), source.coordinates, strict=True):
            if not coefficient.is_zero():
                result.append(
                    (
                        CechBasisTerm(
                            component,
                            x_monomial,
                            u_monomial,
                            p_monomial,
                            cast(
                                tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
                                cell,
                            ),
                        ),
                        cast(Eisenstein, coefficient),
                    )
                )
    primitive = SparseCechCochain(tuple(result))
    if _cech_differential(primitive) != cochain:
        raise ValueError("assembled projective-product primitive failed exactly")
    return primitive


def _initial_lift(raw_representative: dict[str, object]) -> SparseCechCochain:
    """Replace each ambient cohomology basis value by its canonical Čech cocycle."""

    raw_terms = raw_representative.get("terms")
    if not isinstance(raw_terms, list):
        raise ValueError("pair-73 representative terms must be serialized")
    result: list[tuple[CechBasisTerm, Eisenstein]] = []
    for raw_term in raw_terms:
        if not isinstance(raw_term, dict):
            raise ValueError("pair-73 representative terms must be objects")
        coordinate = raw_term.get("basis_coordinate")
        if not isinstance(coordinate, list) or len(coordinate) != 12:
            raise ValueError("pair-73 structural coordinate is incompatible")
        coefficient = _eisenstein_text(raw_term.get("coefficient"))
        (
            parent_degree,
            sheaf_degree,
            hom_term_index,
            line_degree,
            koszul_summand,
            ambient_degree,
            x_h,
            u_h,
            p_h,
            x_monomial,
            u_monomial,
            p_monomial,
        ) = coordinate
        if not (
            isinstance(parent_degree, int)
            and isinstance(sheaf_degree, int)
            and isinstance(hom_term_index, int)
            and isinstance(line_degree, list)
            and isinstance(koszul_summand, str)
            and isinstance(ambient_degree, list)
            and isinstance(x_h, int)
            and isinstance(u_h, int)
            and isinstance(p_h, int)
            and isinstance(x_monomial, list)
            and isinstance(u_monomial, list)
            and isinstance(p_monomial, list)
        ):
            raise ValueError("pair-73 structural coordinate has invalid types")
        if sheaf_degree != 1 or (x_h, u_h, p_h) != (0, 2, 1):
            raise ValueError("pair 73 no longer lies in the certified H0/H2/H1 sector")
        component = StructuralComponent(
            parent_degree,
            hom_term_index,
            cast(tuple[int, int, int], tuple(line_degree)),
            koszul_summand,
        )
        if component.ambient_degree != tuple(ambient_degree):
            raise ValueError("live pair-73 structural and ambient degrees disagree")
        x_tuple = cast(tuple[int, int, int], tuple(x_monomial))
        u_tuple = cast(tuple[int, int, int], tuple(u_monomial))
        p_tuple = cast(tuple[int, int], tuple(p_monomial))
        cech = _product_cech(x_tuple, u_tuple, p_tuple)
        representative = cech.canonical_representative()
        for cell, value in zip(cech.cells_at(3), representative.coordinates, strict=True):
            if not value.is_zero():
                result.append(
                    (
                        CechBasisTerm(
                            component,
                            x_tuple,
                            u_tuple,
                            p_tuple,
                            cast(
                                tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
                                cell,
                            ),
                        ),
                        coefficient * cast(Eisenstein, value),
                    )
                )
    return SparseCechCochain(tuple(result))


def _lift_one(
    initial: SparseCechCochain,
    structure: Pair73StructuralData,
) -> tuple[SparseCechCochain, ...]:
    """Solve the three exact Čech descent equations for one Ext basis class."""

    levels = [initial]
    current = initial
    if not _cech_differential(initial).is_zero():
        raise ValueError("pair-73 ambient representative is not a Čech cocycle")
    for _ in range(3):
        structural = _structural_differential(current, structure)
        structural_degree = next(
            iter({basis.component.structural_degree for basis, _ in current.terms})
        )
        right_hand_side = structural.scale(-1 if structural_degree % 2 else 1)
        current = _primitive(right_hand_side)
        levels.append(current)
    if not _structural_differential(levels[-1], structure).is_zero():
        raise ValueError("pair-73 lifted hypercocycle is not an exact total cycle")
    return tuple(levels)


@cache
def pair_73_cech_lift() -> Pair73CechLift:
    """Load all four exact pair-73 chain-level lift checkpoints."""

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_digest = source.pop("artifact_digest", None)
    if not isinstance(source_digest, str) or source_digest != _canonical_digest(source):
        raise ValueError("pair-local source artifact digest does not verify")
    raw_pair = source.get("pair")
    if not isinstance(raw_pair, dict) or raw_pair.get("global_pair_index") != PAIR_INDEX:
        raise ValueError("pair-local source artifact has an incompatible identity")
    raw_basis = raw_pair.get("cocycle_basis")
    if not isinstance(raw_basis, dict):
        raise ValueError("pair-local source artifact has no cocycle basis")
    raw_representatives = raw_basis.get("representatives")
    if not isinstance(raw_representatives, list) or len(raw_representatives) != 4:
        raise ValueError("pair-73 source artifact no longer has four representatives")
    partial = json.loads(PARTIAL.read_text(encoding="utf-8"))
    raw_counts = partial.get("completed_classes")
    if not isinstance(raw_counts, dict) or set(raw_counts) != {"0", "1", "2", "3"}:
        raise ValueError("pair-73 chain-level lift checkpoint is incomplete")
    counts = tuple(tuple(raw_counts[str(index)]["term_counts"]) for index in range(4))
    digests = tuple(raw_counts[str(index)]["term_digest"] for index in range(4))
    invariant_digest = raw_pair.get("certificate_digest")
    if not isinstance(invariant_digest, str):
        raise ValueError("pair-73 invariant certificate digest is missing")
    return Pair73CechLift(
        counts,
        digests,
        raw_basis.get("cover_cycles_exact") is True and raw_basis.get("quotient_exact") is True,
        len(counts) == 4,
        len(counts) == len(PARAMETERS),
        invariant_digest,
    )


def generate_one_class(path: Path = PARTIAL) -> dict[str, object] | None:
    """Certify and atomically checkpoint the next missing pair-73 basis class."""

    if path.exists():
        partial = json.loads(path.read_text(encoding="utf-8"))
        if partial.get("schema") == "pair-73-cech-hypercocycle-lift-checkpoint-v2":
            raw_completed = partial.get("completed_classes")
            if not isinstance(raw_completed, dict):
                raise ValueError("pair-73 chain-lift checkpoint is invalid")
            completed = dict(raw_completed)
        else:
            completed = {}
    else:
        completed = {}
    pending = next((index for index in range(4) if str(index) not in completed), None)
    if pending is None:
        return pair_73_cech_lift().as_record()
    completed[str(pending)] = _lift_class_certificate(pending)
    payload = {
        "schema": "pair-73-cech-hypercocycle-lift-checkpoint-v2",
        "global_pair_index": PAIR_INDEX,
        "completed_classes": completed,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    pair_73_cech_lift.cache_clear()
    return pair_73_cech_lift().as_record() if len(completed) == 4 else None


def _lift_class_certificate(index: int) -> dict[str, object]:
    """Certify one pair-73 basis class in a disposable bounded-memory worker."""

    if index not in range(4):
        raise ValueError("pair-73 class indices run from zero through three")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    raw_pair = source.get("pair")
    if not isinstance(raw_pair, dict):
        raise ValueError("pair-local source artifact has no pair record")
    raw_basis = raw_pair.get("cocycle_basis")
    if not isinstance(raw_basis, dict):
        raise ValueError("pair-local source artifact has no cocycle basis")
    representatives = raw_basis.get("representatives")
    if not isinstance(representatives, list) or len(representatives) != 4:
        raise ValueError("pair-local source artifact no longer has four classes")
    representative = representatives[index]
    if not isinstance(representative, dict):
        raise ValueError("pair-73 source representatives must be objects")
    levels = _lift_one(_initial_lift(representative), _pair_structure())
    digest = hashlib.sha256()
    for level_index, level in enumerate(levels):
        for basis, coefficient in level.terms:
            component = basis.component
            record = (
                level_index,
                component.parent_degree,
                component.hom_term_index,
                component.line_degree,
                component.koszul_summand,
                basis.x_monomial,
                basis.u_monomial,
                basis.p_monomial,
                basis.cell,
                str(coefficient),
            )
            digest.update(json.dumps(record, separators=(",", ":")).encode("utf-8"))
            digest.update(b"\n")
    return {
        "term_counts": [len(level.terms) for level in levels],
        "term_digest": digest.hexdigest(),
    }


def write_pair_73_cech_lift(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed pair-73 chain-lift certificate atomically."""

    payload = pair_73_cech_lift().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Advance one class checkpoint and finalize only after all four close."""

    completed = generate_one_class()
    checkpoint = json.loads(PARTIAL.read_text(encoding="utf-8"))
    print(f"completed_classes: {len(checkpoint['completed_classes'])}/4")
    if completed is None:
        return 0
    payload = write_pair_73_cech_lift()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"lifted_term_counts: {payload['lifted_term_counts']}")
    print(f"total_cycles_exact: {payload['total_cycles_exact']}")
    print(f"derived_mapping_cone_available: {payload['derived_mapping_cone_available']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
