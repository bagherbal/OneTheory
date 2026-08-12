"""Compute exact constituent automorphisms and their outer-Ext actions.

Owns:
    Invariant self-Hom degree-zero algebras, exact unit-locus determinants,
    and induced left/right actions on explicit invariant outer Ext-one bases.

Depends on:
    The exact sparse Schoen Hom totalizations, invariant cocycle bases, and
    ambient Kunneth multiplication maps.

Must not:
    Assume constituent simplicity, identify all nonzero extensions, select a
    canonical orbit without classification, or construct a rank-four bundle.

Phase 0:
    Research-only automorphism algebra and action certificates are executable;
    scalar projective orbits can be classified, while exhaustive screening and
    rank-four construction remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, polynomial_determinant

from .schoen_linebundles import _ambient_space
from .schoen_outer import SchoenPresentation
from .schoen_sparse_outer import (
    SparseMap,
    SparseOuterHom,
    _freeze_rows,
    _sparse_factor_map,
    sparse_outer_hom,
)
from .schoen_sparse_outer_actions import (
    SparseInvariantBasis,
    SparseInvariantCocycleBasis,
    SparseOuterInvariantAudit,
    _columns,
    _total_basis_coordinates,
    sparse_outer_invariant_audit,
    sparse_outer_invariant_cocycles,
)
from .tier_b_serre_extensions import TierBSerreExtensionRay

StructuralCoordinate = tuple[
    int,
    int,
    int,
    tuple[int, int, int],
    str,
    tuple[int, int, int],
    tuple[int, int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...]],
]
SparseColumn = dict[int, Eisenstein]


def _sum_degrees(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Add two Schoen multidegrees exactly."""

    return tuple(a + b for a, b in zip(left, right, strict=True))


def _component(
    presentation_left: SchoenPresentation,
    presentation_right: SchoenPresentation,
    parent_degree: int,
    index: int,
) -> tuple[int, int, int, int]:
    """Decode one Hom-term index as target/source degree and index data."""

    left_target = len(presentation_left.target_line_degrees)
    left_source = len(presentation_left.source_line_degrees)
    right_target = len(presentation_right.target_line_degrees)
    right_source = len(presentation_right.source_line_degrees)
    if parent_degree == -1:
        if index < 0 or index >= left_source * right_target:
            raise IndexError("degree-minus-one Hom component is out of range")
        return -1, index // right_target, 0, index % right_target
    if parent_degree == 0:
        target_block = left_target * right_target
        if 0 <= index < target_block:
            return 0, index // right_target, 0, index % right_target
        source_index = index - target_block
        if source_index < 0 or source_index >= left_source * right_source:
            raise IndexError("degree-zero Hom component is out of range")
        return (
            -1,
            source_index // right_source,
            -1,
            source_index % right_source,
        )
    if parent_degree == 1:
        if index < 0 or index >= left_target * right_source:
            raise IndexError("degree-one Hom component is out of range")
        return 0, index // right_source, -1, index % right_source
    raise ValueError("two-term presentation Hom degrees are -1, 0, and 1")


def _component_index(
    presentation_left: SchoenPresentation,
    presentation_right: SchoenPresentation,
    parent_degree: int,
    target_degree: int,
    target_index: int,
    source_degree: int,
    source_index: int,
) -> int:
    """Encode one compatible target/source component in Hom basis order."""

    left_target = len(presentation_left.target_line_degrees)
    right_target = len(presentation_right.target_line_degrees)
    right_source = len(presentation_right.source_line_degrees)
    if parent_degree == -1:
        if (target_degree, source_degree) != (-1, 0):
            raise ValueError("degree-minus-one Hom component has incompatible degrees")
        return target_index * right_target + source_index
    if parent_degree == 0:
        target_count = left_target * right_target
        if (target_degree, source_degree) == (0, 0):
            return target_index * right_target + source_index
        if (target_degree, source_degree) == (-1, -1):
            return target_count + target_index * right_source + source_index
        raise ValueError("degree-zero Hom component has incompatible degrees")
    if parent_degree == 1:
        if (target_degree, source_degree) != (0, -1):
            raise ValueError("degree-one Hom component has incompatible degrees")
        return target_index * right_source + source_index
    raise ValueError("two-term presentation Hom degrees are -1, 0, and 1")


def _composed_component_index(
    endomorphism: SparseOuterHom,
    outer: SparseOuterHom,
    side: str,
    endomorphism_index: int,
    outer_degree: int,
    outer_index: int,
) -> int | None:
    """Return the Hom index obtained by left or right ordinary composition."""

    endo_target_degree, endo_target, endo_source_degree, endo_source = _component(
        endomorphism.left,
        endomorphism.right,
        0,
        endomorphism_index,
    )
    outer_target_degree, outer_target, outer_source_degree, outer_source = _component(
        outer.left,
        outer.right,
        outer_degree,
        outer_index,
    )
    if side == "left":
        if endomorphism.left != outer.left or endomorphism.right != outer.left:
            raise ValueError("left endomorphisms must act on the outer target")
        if (
            endo_source_degree != outer_target_degree
            or endo_source != outer_target
        ):
            return None
        return _component_index(
            outer.left,
            outer.right,
            outer_degree,
            endo_target_degree,
            endo_target,
            outer_source_degree,
            outer_source,
        )
    if side == "right":
        if endomorphism.left != outer.right or endomorphism.right != outer.right:
            raise ValueError("right endomorphisms must act on the outer source")
        if (
            outer_source_degree != endo_target_degree
            or outer_source != endo_target
        ):
            return None
        return _component_index(
            outer.left,
            outer.right,
            outer_degree,
            outer_target_degree,
            outer_target,
            endo_source_degree,
            endo_source,
        )
    raise ValueError("automorphism action side must be left or right")


def _monomial(
    exponents: tuple[int, ...],
) -> Polynomial:
    """Return one coefficient-one Eisenstein monomial."""

    return Polynomial.monomial(exponents, scalar_type=Eisenstein)


@cache
def _section_multiplication(
    source_degrees: tuple[int, int, int],
    cohomology_degree: int,
    x_monomial: tuple[int, ...],
    u_monomial: tuple[int, ...],
    p_monomial: tuple[int, ...],
) -> SparseMap:
    """Multiply one ambient Kunneth space by a decomposable global section."""

    source = _ambient_space(source_degrees, cohomology_degree)
    after_x_degrees = (
        source_degrees[0] + sum(x_monomial),
        source_degrees[1],
        source_degrees[2],
    )
    after_u_degrees = (
        after_x_degrees[0],
        after_x_degrees[1] + sum(u_monomial),
        after_x_degrees[2],
    )
    target_degrees = (
        after_u_degrees[0],
        after_u_degrees[1],
        after_u_degrees[2] + sum(p_monomial),
    )
    after_x = _ambient_space(after_x_degrees, cohomology_degree)
    after_u = _ambient_space(after_u_degrees, cohomology_degree)
    target = _ambient_space(target_degrees, cohomology_degree)
    x_map = _sparse_factor_map(source, after_x, _monomial(x_monomial), "x")
    u_map = _sparse_factor_map(after_x, after_u, _monomial(u_monomial), "u")
    p_map = _sparse_factor_map(after_u, target, _monomial(p_monomial), "p")
    return p_map.compose(u_map).compose(x_map)


def _ordinary_endomorphism_gate(
    endomorphism: SparseOuterHom,
    cocycles: SparseInvariantCocycleBasis,
) -> bool:
    """Return whether every H0 representative is an ordinary global chain map."""

    coordinates = _total_basis_coordinates(endomorphism, 0)
    for row_index, row in enumerate(cocycles.cover_representatives.rows):
        if not row:
            continue
        coordinate = coordinates[row_index]
        parent_degree, sheaf_degree, _, line_degree, summand, ambient, label = (
            coordinate
        )
        if (
            parent_degree != 0
            or sheaf_degree != 0
            or summand != "k0"
            or ambient != line_degree
            or label[:3] != (0, 0, 0)
        ):
            return False
    return True


def _compose_columns(
    endomorphism: SparseOuterHom,
    outer: SparseOuterHom,
    side: str,
    endomorphism_column: SparseColumn,
    outer_column: SparseColumn,
    total_degree: int,
) -> SparseColumn:
    """Compose one ordinary endomorphism column with one outer cochain column."""

    endomorphism_coordinates = _total_basis_coordinates(endomorphism, 0)
    outer_coordinates = _total_basis_coordinates(outer, total_degree)
    outer_indices = {
        coordinate: index for index, coordinate in enumerate(outer_coordinates)
    }
    result: SparseColumn = {}
    for endomorphism_row, endomorphism_coefficient in endomorphism_column.items():
        endomorphism_coordinate = endomorphism_coordinates[endomorphism_row]
        (
            endomorphism_parent,
            endomorphism_sheaf,
            endomorphism_index,
            endomorphism_line,
            endomorphism_summand,
            endomorphism_ambient,
            endomorphism_label,
        ) = endomorphism_coordinate
        if (
            endomorphism_parent != 0
            or endomorphism_sheaf != 0
            or endomorphism_summand != "k0"
            or endomorphism_ambient != endomorphism_line
            or endomorphism_label[:3] != (0, 0, 0)
        ):
            raise ValueError("endomorphism representative is not an ordinary chain map")
        _, _, _, x_section, u_section, p_section = endomorphism_label
        for outer_row, outer_coefficient in outer_column.items():
            outer_coordinate = outer_coordinates[outer_row]
            (
                outer_parent,
                outer_sheaf,
                outer_index,
                outer_line,
                outer_summand,
                outer_ambient,
                outer_label,
            ) = outer_coordinate
            result_index = _composed_component_index(
                endomorphism,
                outer,
                side,
                endomorphism_index,
                outer_parent,
                outer_index,
            )
            if result_index is None:
                continue
            x_h, u_h, p_h, *_ = outer_label
            multiplication = _section_multiplication(
                outer_ambient,
                x_h + u_h + p_h,
                x_section,
                u_section,
                p_section,
            )
            source_space = _ambient_space(outer_ambient, x_h + u_h + p_h)
            source_local = source_space.labels.index(outer_label)
            target_space = _ambient_space(
                _sum_degrees(outer_ambient, endomorphism_line),
                x_h + u_h + p_h,
            )
            for target_local, row in enumerate(multiplication.rows):
                for source_column, multiplication_coefficient in row:
                    if source_column != source_local:
                        continue
                    target_coordinate: StructuralCoordinate = (
                        outer_parent,
                        outer_sheaf,
                        result_index,
                        _sum_degrees(outer_line, endomorphism_line),
                        outer_summand,
                        target_space.degrees,
                        target_space.labels[target_local],
                    )
                    target_index = outer_indices.get(target_coordinate)
                    if target_index is None:
                        raise ValueError("endomorphism product escaped the outer basis")
                    value = (
                        endomorphism_coefficient
                        * outer_coefficient
                        * multiplication_coefficient
                    )
                    updated = result.get(target_index, Eisenstein(0)) + value
                    if updated.is_zero():
                        result.pop(target_index, None)
                    else:
                        result[target_index] = updated
    return result


def _map_from_columns(
    domain: VectorSpace,
    codomain: VectorSpace,
    columns: tuple[SparseColumn, ...],
) -> SparseMap:
    """Build one immutable sparse map from explicit mutable columns."""

    rows: list[dict[int, Eisenstein]] = [{} for _ in range(codomain.dimension)]
    for column_index, column in enumerate(columns):
        for row_index, coefficient in column.items():
            rows[row_index][column_index] = coefficient
    return SparseMap(domain, codomain, _freeze_rows(rows))


def _cover_to_invariant(
    map_: SparseMap,
    basis: SparseInvariantBasis,
) -> SparseMap:
    """Restrict known invariant cover vectors to a root-normalized basis."""

    if map_.codomain != basis.ambient:
        raise ValueError("cover vectors and invariant basis use different spaces")
    restricted = SparseMap(
        map_.domain,
        basis.invariant,
        tuple(map_.rows[root] for root in basis.orbit_roots),
    )
    if basis.inclusion.compose(restricted) != map_:
        raise ValueError("composed cocycle escaped the invariant cochain subspace")
    return restricted


def _quotient_coordinates(
    boundaries: SparseMap,
    representatives: SparseMap,
    vectors: SparseMap,
) -> SparseMap:
    """Reduce cycle vectors modulo boundaries into the declared H basis."""

    if not (
        boundaries.codomain == representatives.codomain == vectors.codomain
    ):
        raise ValueError("quotient reduction requires one common cochain space")
    pivots: dict[int, tuple[SparseColumn, SparseColumn]] = {}

    def insert(column: SparseColumn, quotient: SparseColumn) -> None:
        vector = dict(column)
        coordinates = dict(quotient)
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            existing = pivots.get(pivot)
            if existing is None:
                inverse = Eisenstein(1) / coefficient
                pivots[pivot] = (
                    {row: value * inverse for row, value in vector.items()},
                    {row: value * inverse for row, value in coordinates.items()},
                )
                return
            pivot_vector, pivot_coordinates = existing
            for row, value in pivot_vector.items():
                updated = vector.get(row, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    vector.pop(row, None)
                else:
                    vector[row] = updated
            for row, value in pivot_coordinates.items():
                updated = coordinates.get(row, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    coordinates.pop(row, None)
                else:
                    coordinates[row] = updated
        if coordinates:
            raise ValueError("declared quotient representatives are dependent")

    for column in sorted(_columns(boundaries), key=len):
        insert(column, {})
    for index, column in enumerate(_columns(representatives)):
        insert(column, {index: Eisenstein(1)})

    reduced_columns = []
    for column in _columns(vectors):
        vector = dict(column)
        quotient: SparseColumn = {}
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            existing = pivots.get(pivot)
            if existing is None:
                raise ValueError("composed cocycle escaped boundaries plus H basis")
            pivot_vector, pivot_coordinates = existing
            for row, value in pivot_vector.items():
                updated = vector.get(row, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    vector.pop(row, None)
                else:
                    vector[row] = updated
            for row, value in pivot_coordinates.items():
                updated = quotient.get(row, Eisenstein(0)) + coefficient * value
                if updated.is_zero():
                    quotient.pop(row, None)
                else:
                    quotient[row] = updated
        reduced_columns.append(quotient)
    return _map_from_columns(
        vectors.domain,
        representatives.domain,
        tuple(reduced_columns),
    )


def _cohomology_action(
    endomorphism: SparseInvariantCocycleBasis,
    outer: SparseInvariantCocycleBasis,
    side: str,
) -> tuple[SparseMap, ...]:
    """Return each H0 basis generator's exact action on one H basis."""

    if endomorphism.degree != 0:
        raise ValueError("automorphism generators must be degree-zero classes")
    endomorphism_outer = endomorphism.invariant_audit.outer
    outer_hom = outer.invariant_audit.outer
    if not _ordinary_endomorphism_gate(endomorphism_outer, endomorphism):
        raise ValueError("higher endomorphism representatives need a DGA product")
    invariant_bases = dict(outer.invariant_audit.bases)
    if outer.degree not in invariant_bases:
        raise ValueError("outer cohomology degree is absent")
    endomorphism_columns = _columns(endomorphism.cover_representatives)
    outer_columns = _columns(outer.cover_representatives)
    outgoing = dict(outer_hom.total_differentials).get(outer.degree)
    actions = []
    for endomorphism_column in endomorphism_columns:
        product_columns = tuple(
            _compose_columns(
                endomorphism_outer,
                outer_hom,
                side,
                endomorphism_column,
                outer_column,
                outer.degree,
            )
            for outer_column in outer_columns
        )
        cover_product = _map_from_columns(
            outer.representatives.domain,
            outer.cover_representatives.codomain,
            product_columns,
        )
        if outgoing is not None and not outgoing.compose(cover_product).is_zero():
            raise ValueError("endomorphism action did not preserve outer cocycles")
        invariant_product = _cover_to_invariant(
            cover_product,
            invariant_bases[outer.degree],
        )
        actions.append(
            _quotient_coordinates(
                outer.boundaries,
                outer.representatives,
                invariant_product,
            )
        )
    return tuple(actions)


def _linear_combination(
    maps: tuple[SparseMap, ...],
    coefficients: tuple[Eisenstein, ...],
) -> SparseMap:
    """Return one exact linear combination of compatible sparse maps."""

    if not maps or len(maps) != len(coefficients):
        raise ValueError("linear combination data are empty or incompatible")
    if any(
        map_.domain != maps[0].domain or map_.codomain != maps[0].codomain
        for map_ in maps
    ):
        raise ValueError("linear combination maps require common spaces")
    rows = []
    for row_index in range(maps[0].codomain.dimension):
        row: dict[int, Eisenstein] = {}
        for map_, coefficient in zip(maps, coefficients, strict=True):
            for column, value in map_.rows[row_index]:
                updated = row.get(column, Eisenstein(0)) + coefficient * value
                if updated.is_zero():
                    row.pop(column, None)
                else:
                    row[column] = updated
        rows.append(row)
    return SparseMap(maps[0].domain, maps[0].codomain, _freeze_rows(rows))


def _identity(space: VectorSpace) -> SparseMap:
    """Return one exact sparse identity map."""

    return SparseMap(
        space,
        space,
        tuple(((index, Eisenstein(1)),) for index in range(space.dimension)),
    )


def _identity_cover_column(outer: SparseOuterHom) -> SparseMap:
    """Return the ordinary identity chain map in total degree zero."""

    coordinates = _total_basis_coordinates(outer, 0)
    indices = {coordinate: index for index, coordinate in enumerate(coordinates)}
    constant_label = (0, 0, 0, (0, 0, 0), (0, 0, 0), (0, 0))
    zero_degree = (0, 0, 0)
    column: SparseColumn = {}
    for complex_degree, rank in (
        (0, len(outer.left.target_line_degrees)),
        (-1, len(outer.left.source_line_degrees)),
    ):
        for index in range(rank):
            hom_index = _component_index(
                outer.left,
                outer.right,
                0,
                complex_degree,
                index,
                complex_degree,
                index,
            )
            coordinate: StructuralCoordinate = (
                0,
                0,
                hom_index,
                zero_degree,
                "k0",
                zero_degree,
                constant_label,
            )
            column[indices[coordinate]] = Eisenstein(1)
    domain = VectorSpace("identity-chain-map", ("identity",), Eisenstein)
    return _map_from_columns(domain, outer.total[0], (column,))


def _unit_polynomial(multiplications: tuple[SparseMap, ...]) -> Polynomial:
    """Return the determinant cutting out nonunits in endomorphism coordinates."""

    dimension = len(multiplications)
    rows = []
    for row in range(dimension):
        polynomial_row = []
        for column in range(dimension):
            terms = []
            for generator, multiplication in enumerate(multiplications):
                coefficient = dict(multiplication.rows[row]).get(
                    column,
                    Eisenstein(0),
                )
                if coefficient.is_zero():
                    continue
                exponent = tuple(
                    1 if index == generator else 0 for index in range(dimension)
                )
                terms.append((exponent, coefficient))
            polynomial_row.append(
                Polynomial(terms, variable_count=dimension, scalar_type=Eisenstein)
            )
        rows.append(tuple(polynomial_row))
    return polynomial_determinant(tuple(rows))


def _map_record(map_: SparseMap) -> list[list[list[object]]]:
    """Serialize one exact sparse matrix by rows."""

    return [
        [[column, str(coefficient)] for column, coefficient in row]
        for row in map_.rows
    ]


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize one exact polynomial without hiding coefficients."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


@dataclass(frozen=True, slots=True)
class SparseEndomorphismAlgebraAudit:
    """One exact invariant endomorphism algebra for a constituent presentation."""

    invariant: SparseOuterInvariantAudit
    cocycles: SparseInvariantCocycleBasis
    multiplications: tuple[SparseMap, ...]
    identity_coordinates: tuple[Eisenstein, ...]
    unit_polynomial: Polynomial
    ordinary_chain_maps: bool
    associative: bool
    identity_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether the endomorphism algebra gates all close."""

        return (
            self.invariant.exact
            and self.cocycles.exact
            and self.ordinary_chain_maps
            and self.associative
            and self.identity_exact
            and not self.unit_polynomial.is_zero()
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact algebra without classifying its unit orbits."""

        return {
            "scheme": self.invariant.outer.left.candidate.scheme.name,
            "factor": self.invariant.outer.left.factor,
            "twist": list(self.invariant.outer.left.twist),
            "character_pair": [
                str(value) for value in self.invariant.outer.left.ray.character_pair
            ],
            "invariant_h0_dimension": self.cocycles.representatives.domain.dimension,
            "h0_cocycles": self.cocycles.as_record(),
            "left_multiplication_matrices": [
                _map_record(map_) for map_ in self.multiplications
            ],
            "identity_coordinates": [str(value) for value in self.identity_coordinates],
            "unit_locus_determinant": _polynomial_record(self.unit_polynomial),
            "ordinary_chain_maps": self.ordinary_chain_maps,
            "associative": self.associative,
            "identity_exact": self.identity_exact,
            "exact": self.exact,
            "status": (
                "exact invariant endomorphism algebra and unit locus; outer "
                "extension orbit classification remains unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class SparseOuterAutomorphismActionAudit:
    """Exact left/right constituent endomorphism actions on one outer Ext basis."""

    outer: SparseInvariantCocycleBasis
    left_algebra: SparseEndomorphismAlgebraAudit
    right_algebra: SparseEndomorphismAlgebraAudit
    left_actions: tuple[SparseMap, ...]
    right_actions: tuple[SparseMap, ...]
    module_laws_exact: bool
    actions_commute: bool

    @property
    def exact(self) -> bool:
        """Return whether both algebras act exactly on the outer Ext basis."""

        return (
            self.outer.exact
            and self.left_algebra.exact
            and self.right_algebra.exact
            and self.module_laws_exact
            and self.actions_commute
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact action matrices without claiming canonical orbits."""

        return {
            "outer_ext_one_dimension": self.outer.representatives.domain.dimension,
            "left_endomorphism_algebra": self.left_algebra.as_record(),
            "right_endomorphism_algebra": self.right_algebra.as_record(),
            "left_action_matrices": [_map_record(map_) for map_ in self.left_actions],
            "right_action_matrices": [_map_record(map_) for map_ in self.right_actions],
            "module_laws_exact": self.module_laws_exact,
            "actions_commute": self.actions_commute,
            "automorphism_action_computed": self.exact,
            "canonical_orbits_computed": False,
            "outer_extension_constructed": False,
            "exact": self.exact,
            "status": (
                "exact constituent automorphism action on invariant Ext-one; "
                "canonical orbits and rank-four construction remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class SparseOuterCoverScalarActionAudit:
    """Exact scalar actions proved on explicit invariant cover cocycles."""

    outer_representatives: SparseMap
    left_algebra: SparseEndomorphismAlgebraAudit
    right_algebra: SparseEndomorphismAlgebraAudit
    left_character: tuple[Eisenstein, ...]
    right_character: tuple[Eisenstein, ...]
    left_cover_equalities: bool
    right_cover_equalities: bool
    unit_characters_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether the cover proof induces exact projective Ext orbits."""

        return (
            self.outer_representatives.domain.dimension > 0
            and self.left_algebra.exact
            and self.right_algebra.exact
            and self.left_cover_equalities
            and self.right_cover_equalities
            and self.unit_characters_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the scalar representation and canonical orbit charts."""

        dimension = self.outer_representatives.domain.dimension
        return {
            "extension_dimension": dimension,
            "action_basis": [str(value) for value in self.outer_representatives.domain.basis],
            "left_scalar_character": [str(value) for value in self.left_character],
            "right_scalar_character": [str(value) for value in self.right_character],
            "left_cover_equalities": self.left_cover_equalities,
            "right_cover_equalities": self.right_cover_equalities,
            "unit_characters_exact": self.unit_characters_exact,
            "zero_orbit": {
                "representative": ["0"] * dimension,
                "split_extension": True,
            },
            "nonzero_orbit_space": f"P^{dimension - 1}(Q(omega))",
            "canonical_normal_form_charts": [
                {
                    "pivot_index": pivot,
                    "zero_coordinates": list(range(pivot)),
                    "normalized_coordinate": pivot,
                    "normalized_value": "1",
                    "free_coordinates": list(range(pivot + 1, dimension)),
                }
                for pivot in range(dimension)
            ],
            "canonical_orbits_computed": self.exact,
            "outer_extension_constructed": False,
            "exact": self.exact,
            "status": (
                "scalar automorphism action proved on explicit cover cocycles; "
                "no extension point is selected"
            ),
        }


@dataclass(frozen=True, slots=True)
class SparseOuterOrbitClassification:
    """Canonical projective normal forms for a scalar automorphism action."""

    action: SparseOuterAutomorphismActionAudit
    left_character: tuple[Eisenstein, ...]
    right_character: tuple[Eisenstein, ...]
    scalar_actions: bool
    unit_characters_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether all nonzero orbits are certified projective points."""

        return (
            self.action.exact
            and self.action.outer.representatives.domain.dimension > 0
            and self.scalar_actions
            and self.unit_characters_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the zero orbit and canonical first-nonzero projective charts."""

        dimension = self.action.outer.representatives.domain.dimension
        return {
            "extension_dimension": dimension,
            "left_scalar_character": [str(value) for value in self.left_character],
            "right_scalar_character": [str(value) for value in self.right_character],
            "scalar_actions": self.scalar_actions,
            "unit_characters_exact": self.unit_characters_exact,
            "zero_orbit": {
                "representative": ["0"] * dimension,
                "split_extension": True,
            },
            "nonzero_orbit_space": f"P^{dimension - 1}(Q(omega))",
            "canonical_normal_form_charts": [
                {
                    "pivot_index": pivot,
                    "zero_coordinates": list(range(pivot)),
                    "normalized_coordinate": pivot,
                    "normalized_value": "1",
                    "free_coordinates": list(range(pivot + 1, dimension)),
                }
                for pivot in range(dimension)
            ],
            "canonical_orbits_computed": self.exact,
            "outer_extension_constructed": False,
            "exact": self.exact,
            "status": (
                "exact projective orbit normal forms; no extension point is "
                "selected and rank-four construction remains unresolved"
            ),
        }


def _scalar_character(actions: tuple[SparseMap, ...]) -> tuple[Eisenstein, ...] | None:
    """Return scalar coefficients when every action generator is scalar."""

    if not actions:
        return None
    identity = _identity(actions[0].domain)
    coefficients = []
    for action in actions:
        if action.domain.dimension == 0:
            return None
        coefficient = dict(action.rows[0]).get(0, Eisenstein(0))
        if action != identity.scale(coefficient):
            return None
        coefficients.append(coefficient)
    return tuple(coefficients)


def _cover_scalar_character(
    endomorphism: SparseInvariantCocycleBasis,
    outer: SparseOuterHom,
    representatives: SparseMap,
    side: str,
) -> tuple[Eisenstein, ...] | None:
    """Prove scalar action directly on a declared cover-cocycle basis."""

    if representatives.codomain != outer.total[1]:
        raise ValueError("outer representatives use another total cochain space")
    if representatives.domain.dimension == 0:
        raise ValueError("scalar cover actions require positive-dimensional Ext")
    characters = []
    for endomorphism_column in _columns(endomorphism.cover_representatives):
        product = _map_from_columns(
            representatives.domain,
            representatives.codomain,
            tuple(
                _compose_columns(
                    endomorphism.invariant_audit.outer,
                    outer,
                    side,
                    endomorphism_column,
                    outer_column,
                    1,
                )
                for outer_column in _columns(representatives)
            ),
        )
        coefficient: Eisenstein | None = None
        for row_index, row in enumerate(representatives.rows):
            for column_index, value in row:
                product_value = dict(product.rows[row_index]).get(
                    column_index,
                    Eisenstein(0),
                )
                coefficient = product_value / value
                break
            if coefficient is not None:
                break
        if coefficient is None:
            raise ValueError("outer cover representative basis contains only zero")
        if product != representatives.scale(coefficient):
            return None
        characters.append(coefficient)
    return tuple(characters)


def _character_polynomial(character: tuple[Eisenstein, ...]) -> Polynomial:
    """Return one linear coordinate character as an exact polynomial."""

    dimension = len(character)
    return Polynomial(
        (
            (
                tuple(1 if index == generator else 0 for index in range(dimension)),
                coefficient,
            )
            for generator, coefficient in enumerate(character)
            if not coefficient.is_zero()
        ),
        variable_count=dimension,
        scalar_type=Eisenstein,
    )


def classify_sparse_outer_automorphism_orbits(
    action: SparseOuterAutomorphismActionAudit,
) -> SparseOuterOrbitClassification:
    """Classify all extension orbits when both unit groups act by scalars."""

    left_character = _scalar_character(action.left_actions)
    right_character = _scalar_character(action.right_actions)
    scalar_actions = left_character is not None and right_character is not None
    if left_character is None:
        left_character = ()
    if right_character is None:
        right_character = ()
    unit_characters_exact = scalar_actions and (
        action.left_algebra.unit_polynomial
        == _character_polynomial(left_character)
        ** action.left_algebra.cocycles.representatives.domain.dimension
        and action.right_algebra.unit_polynomial
        == _character_polynomial(right_character)
        ** action.right_algebra.cocycles.representatives.domain.dimension
    )
    return SparseOuterOrbitClassification(
        action,
        left_character,
        right_character,
        scalar_actions,
        unit_characters_exact,
    )


def sparse_outer_cover_scalar_action(
    outer: SparseOuterHom,
    representatives: SparseMap,
    left_algebra: SparseEndomorphismAlgebraAudit,
    right_algebra: SparseEndomorphismAlgebraAudit,
) -> SparseOuterCoverScalarActionAudit:
    """Certify scalar automorphism actions before passing to cohomology."""

    outgoing = dict(outer.total_differentials).get(1)
    if outgoing is not None and not outgoing.compose(representatives).is_zero():
        raise ValueError("declared outer representatives are not cover cocycles")
    left_character = _cover_scalar_character(
        left_algebra.cocycles,
        outer,
        representatives,
        "left",
    )
    right_character = _cover_scalar_character(
        right_algebra.cocycles,
        outer,
        representatives,
        "right",
    )
    left_exact = left_character is not None
    right_exact = right_character is not None
    if left_character is None:
        left_character = ()
    if right_character is None:
        right_character = ()
    unit_characters_exact = left_exact and right_exact and (
        left_algebra.unit_polynomial
        == _character_polynomial(left_character)
        ** left_algebra.cocycles.representatives.domain.dimension
        and right_algebra.unit_polynomial
        == _character_polynomial(right_character)
        ** right_algebra.cocycles.representatives.domain.dimension
    )
    return SparseOuterCoverScalarActionAudit(
        representatives,
        left_algebra,
        right_algebra,
        left_character,
        right_character,
        left_exact,
        right_exact,
        unit_characters_exact,
    )


def sparse_constituent_endomorphism_algebra(
    ray: TierBSerreExtensionRay,
    factor: int,
    twist: tuple[int, int, int],
) -> SparseEndomorphismAlgebraAudit:
    """Construct one exact invariant constituent endomorphism algebra."""

    outer = sparse_outer_hom(ray, ray, factor, twist, factor, twist)
    invariant = sparse_outer_invariant_audit(outer)
    cocycles = sparse_outer_invariant_cocycles(invariant, degree=0)
    ordinary = _ordinary_endomorphism_gate(outer, cocycles)
    if not ordinary:
        raise ValueError("constituent H0 requires an unavailable higher DGA product")
    multiplications = _cohomology_action(cocycles, cocycles, "left")
    identity_cover = _identity_cover_column(outer)
    invariant_identity = _cover_to_invariant(identity_cover, dict(invariant.bases)[0])
    identity_coordinates_map = _quotient_coordinates(
        cocycles.boundaries,
        cocycles.representatives,
        invariant_identity,
    )
    identity_coordinates = tuple(
        dict(identity_coordinates_map.rows[row]).get(0, Eisenstein(0))
        for row in range(cocycles.representatives.domain.dimension)
    )
    identity_map = _identity(cocycles.representatives.domain)
    identity_exact = (
        _linear_combination(multiplications, identity_coordinates) == identity_map
    )
    associative = True
    multiplication_columns = [_columns(map_) for map_ in multiplications]
    for left_index, left_map in enumerate(multiplications):
        for right_index, right_map in enumerate(multiplications):
            product_coordinates = tuple(
                multiplication_columns[left_index][right_index].get(
                    index,
                    Eisenstein(0),
                )
                for index in range(len(multiplications))
            )
            if left_map.compose(right_map) != _linear_combination(
                multiplications,
                product_coordinates,
            ):
                associative = False
    return SparseEndomorphismAlgebraAudit(
        invariant,
        cocycles,
        multiplications,
        identity_coordinates,
        _unit_polynomial(multiplications),
        ordinary,
        associative,
        identity_exact,
    )


def sparse_outer_automorphism_action(
    outer: SparseInvariantCocycleBasis,
    left_algebra: SparseEndomorphismAlgebraAudit,
    right_algebra: SparseEndomorphismAlgebraAudit,
) -> SparseOuterAutomorphismActionAudit:
    """Compute both exact endomorphism-algebra actions on one outer Ext basis."""

    left_actions = _cohomology_action(left_algebra.cocycles, outer, "left")
    right_actions = _cohomology_action(right_algebra.cocycles, outer, "right")
    module_laws_exact = True
    for side, algebra, actions in (
        ("left", left_algebra, left_actions),
        ("right", right_algebra, right_actions),
    ):
        multiplication_columns = [_columns(map_) for map_ in algebra.multiplications]
        for left_index, left_action in enumerate(actions):
            for right_index, right_action in enumerate(actions):
                product_left, product_right = (
                    (left_index, right_index)
                    if side == "left"
                    else (right_index, left_index)
                )
                product_coordinates = tuple(
                    multiplication_columns[product_left][product_right].get(
                        index,
                        Eisenstein(0),
                    )
                    for index in range(len(actions))
                )
                if left_action.compose(right_action) != _linear_combination(
                    actions,
                    product_coordinates,
                ):
                    module_laws_exact = False
    actions_commute = all(
        left.compose(right) == right.compose(left)
        for left in left_actions
        for right in right_actions
    )
    return SparseOuterAutomorphismActionAudit(
        outer,
        left_algebra,
        right_algebra,
        left_actions,
        right_actions,
        module_laws_exact,
        actions_commute,
    )


__all__ = [
    "SparseEndomorphismAlgebraAudit",
    "SparseOuterAutomorphismActionAudit",
    "SparseOuterCoverScalarActionAudit",
    "SparseOuterOrbitClassification",
    "classify_sparse_outer_automorphism_orbits",
    "sparse_constituent_endomorphism_algebra",
    "sparse_outer_automorphism_action",
    "sparse_outer_cover_scalar_action",
]
