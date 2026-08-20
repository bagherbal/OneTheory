"""Lift sparse Schoen deck actions to presentation Hom totalizations.

Owns:
    Exact pullback-and-conjugation maps on sparse Hom cells, totalized chain-map
    checks, order-three checks, projective-generator commutator checks, and
    simultaneous invariant subcomplexes for declared monomial Serre ray pairs.

Depends on:
    Sparse Schoen line actions, exact presentation Hom matrices, and the
    certified monomial resolution actions.

Must not:
    Call an invariant cover class a descended extension, hide a failed
    linearization, or promote a finite action audit to physical selection.

Phase 0:
    Hom-level cover equivariance, invariant Ext dimensions, and explicit
    invariant cocycles are executable; rank-four construction remains open.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein

from .projective_hom_action import _presentation_term_actions
from .resolution_actions import ResolutionActionPair
from .schoen_linebundles import _KOSZUL_TOTAL_DEGREES
from .schoen_outer import _hom_term_lines
from .schoen_sparse_actions import (
    SchoenSparseDeckAction,
    _inverse_images,
    schoen_sparse_deck_actions,
)
from .schoen_sparse_outer import (
    SparseMap,
    SparseOuterHom,
    _freeze_rows,
    _sparse_line_sum_space,
    sparse_line_bundle,
)
from .tier_b_monomial import tier_b_monomial_resolution_actions


def _resolution_pairs() -> dict[str, ResolutionActionPair]:
    """Return exact resolution actions keyed by invariant scheme name."""

    return {
        audit.scheme.name: audit.actions
        for audit in tier_b_monomial_resolution_actions()
    }


def _factor_resolution_data(presentation):
    """Return the resolution lift and characters for one Schoen factor."""

    pairs = _resolution_pairs()
    pair = pairs[presentation.candidate.scheme.name]
    characters = presentation.ray.character_pair
    if presentation.factor == 1:
        return pair, characters
    def inverse_action(name: str):
        """Invert one exact resolution action for the second factor."""

        original = pair.action(name)
        return type(original)(
            original.scheme,
            name,
            _inverse_images(original.coordinate_images),
            original.target_action.inverse(),
            original.source_action.inverse(),
            original.generator_permutation,
            original.generator_scalars,
        )

    inverse_p = inverse_action("P")
    inverse_t = inverse_action("T")
    return (
        ResolutionActionPair(pair.scheme, (inverse_p, inverse_t)),
        (
            Eisenstein(1) / characters[0],
            Eisenstein(1) / characters[1],
        ),
    )


def _identity(space) -> SparseMap:
    """Build one exact sparse identity map."""

    rows = tuple(
        ((index, Eisenstein(1)),)
        for index in range(space.dimension)
    )
    return SparseMap(space, space, rows)


def _term_action(
    outer: SparseOuterHom,
    action: SchoenSparseDeckAction,
    term_degree: int,
    sheaf_degree: int,
    bundles,
    matrix,
) -> SparseMap:
    """Combine presentation conjugation with line-bundle pullback."""

    selected = bundles[term_degree]
    blocks = []
    for target_index, target_bundle in enumerate(selected):
        row = []
        for source_index, source_bundle in enumerate(selected):
            coefficient = matrix[target_index][source_index]
            source_space = source_bundle.space(sheaf_degree)
            target_space = target_bundle.space(sheaf_degree)
            if coefficient.is_zero():
                row.append(SparseMap.zero(source_space, target_space))
                continue
            if source_bundle.degrees != target_bundle.degrees:
                raise ValueError(
                    "Hom presentation action mixes incompatible multigraded line terms"
                )
            row.append(
                action.line_component(target_bundle, sheaf_degree).scale(coefficient)
            )
        blocks.append(tuple(row))
    del outer
    return SparseMap.block(tuple(blocks))


def _total_cells(outer: SparseOuterHom) -> tuple[tuple[int, int], ...]:
    """Return all totalization cells in deterministic order."""

    return tuple(
        (parent_degree, sheaf_degree)
        for parent_degree, _ in _hom_term_lines(outer.left, outer.right)
        for sheaf_degree in _KOSZUL_TOTAL_DEGREES
    )


def _bundle_terms(outer: SparseOuterHom):
    """Rebuild sparse line bundles for one Hom term basis."""

    return {
        degree: tuple(sparse_line_bundle(*line) for line in line_degrees)
        for degree, line_degrees in _hom_term_lines(outer.left, outer.right)
    }


@dataclass(frozen=True, slots=True)
class SparseOuterDeckAudit:
    """Exact totalized P/T action audit for one cover Hom pair."""

    outer: SparseOuterHom
    p_components: tuple[tuple[int, SparseMap], ...]
    t_components: tuple[tuple[int, SparseMap], ...]
    p_chain_map: bool
    t_chain_map: bool
    p_order_three: bool
    t_order_three: bool
    commute: bool

    @property
    def exact(self) -> bool:
        """Return whether every declared Hom-level action identity holds."""

        return (
            self.p_chain_map
            and self.t_chain_map
            and self.p_order_three
            and self.t_order_three
            and self.commute
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the action gate without quotient promotion."""

        return {
            "cover_ext_one_dimension": self.outer.cover_ext_one_dimension,
            "p_chain_map": self.p_chain_map,
            "t_chain_map": self.t_chain_map,
            "p_order_three": self.p_order_three,
            "t_order_three": self.t_order_three,
            "commute": self.commute,
            "exact": self.exact,
            "status": "exact cover Hom action; quotient invariants remain unresolved",
        }


@dataclass(frozen=True, slots=True)
class SparseInvariantBasis:
    """One root-normalized simultaneous P/T invariant cochain basis."""

    degree: int
    ambient: VectorSpace
    invariant: VectorSpace
    inclusion: SparseMap
    orbit_roots: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SparseOuterInvariantAudit:
    """Exact invariant subcomplex and its degree-one cohomology dimension."""

    outer: SparseOuterHom
    deck: SparseOuterDeckAudit
    bases: tuple[tuple[int, SparseInvariantBasis], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    cover_ext_one_dimension: int
    invariant_ext_one_dimension: int
    restrictions_exact: bool
    squared_zero: bool

    @property
    def exact(self) -> bool:
        """Return whether action, restriction, and complex gates all close."""

        return self.deck.exact and self.restrictions_exact and self.squared_zero

    def as_record(self) -> dict[str, object]:
        """Serialize the invariant dimension without claiming a cocycle basis."""

        return {
            "cover_ext_one_dimension": self.cover_ext_one_dimension,
            "invariant_cochain_dimensions": [
                [degree, basis.invariant.dimension]
                for degree, basis in self.bases
            ],
            "invariant_ext_one_dimension": self.invariant_ext_one_dimension,
            "deck_action_exact": self.deck.exact,
            "restrictions_exact": self.restrictions_exact,
            "squared_zero": self.squared_zero,
            "exact": self.exact,
            "explicit_invariant_cocycles_computed": False,
            "outer_extension_constructed": False,
            "status": (
                "exact invariant Ext dimension; cocycle representatives and "
                "rank-four construction remain unresolved"
            ),
        }


def _invariant_cohomology_dimension(
    bases: dict[int, SparseInvariantBasis],
    differentials: dict[int, SparseMap],
    degree: int,
) -> int:
    """Return one exact cohomology dimension from invariant complex data."""

    if isinstance(degree, bool) or not isinstance(degree, int):
        raise TypeError("invariant cohomology degrees must be integers")
    if degree not in bases:
        raise ValueError("requested cohomology degree is absent")
    cochains = bases[degree].invariant
    outgoing = differentials.get(
        degree,
        SparseMap.zero(
            cochains,
            VectorSpace(f"zero:{degree + 1}", (), Eisenstein),
        ),
    )
    incoming = differentials.get(
        degree - 1,
        SparseMap.zero(
            VectorSpace(f"zero:{degree - 1}", (), Eisenstein),
            cochains,
        ),
    )
    dimension = cochains.dimension - outgoing.rank() - incoming.rank()
    if dimension < 0:
        raise ValueError("invariant cochain ranks violate cohomology dimensions")
    return dimension


def sparse_invariant_cohomology_dimension(
    invariant_audit: SparseOuterInvariantAudit,
    degree: int,
) -> int:
    """Return one exact cohomology dimension of the invariant subcomplex."""

    return _invariant_cohomology_dimension(
        dict(invariant_audit.bases),
        dict(invariant_audit.differentials),
        degree,
    )


@dataclass(frozen=True, slots=True)
class SparseInvariantCocycleBasis:
    """Explicit invariant cohomology representatives in cover cochains."""

    invariant_audit: SparseOuterInvariantAudit
    degree: int
    cycles: SparseMap
    boundaries: SparseMap
    representatives: SparseMap
    cover_representatives: SparseMap
    cycles_exact: bool
    quotient_exact: bool
    cover_cycles_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether cycle, quotient, and ambient-cover gates close."""

        return (
            self.invariant_audit.exact
            and self.cycles_exact
            and self.quotient_exact
            and self.cover_cycles_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize root-normalized cocycles in compact structural coordinates."""

        basis_coordinates = _total_basis_coordinates(
            self.invariant_audit.outer,
            self.degree,
        )
        representatives = []
        for column in range(self.cover_representatives.domain.dimension):
            terms = []
            for row_index, row in enumerate(self.cover_representatives.rows):
                for source_column, coefficient in row:
                    if source_column == column:
                        terms.append(
                            {
                                "basis_index": row_index,
                                "basis_coordinate": _basis_coordinate_record(
                                    basis_coordinates[row_index]
                                ),
                                "coefficient": str(coefficient),
                            }
                        )
            representatives.append(
                {
                    "name": self.cover_representatives.domain.basis[column],
                    "terms": terms,
                }
            )
        return {
            "degree": self.degree,
            "dimension": self.representatives.domain.dimension,
            "ambient_basis": {
                "dimension": self.cover_representatives.codomain.dimension,
                "coordinate_schema": [
                    "parent_degree",
                    "sheaf_degree",
                    "hom_term_index",
                    "line_degree",
                    "koszul_summand",
                    "ambient_degree",
                    "x_h",
                    "u_h",
                    "p_h",
                    "x_monomial",
                    "u_monomial",
                    "p_monomial",
                ],
            },
            "representatives": representatives,
            "cycles_exact": self.cycles_exact,
            "quotient_exact": self.quotient_exact,
            "cover_cycles_exact": self.cover_cycles_exact,
            "exact": self.exact,
            "outer_extension_constructed": False,
            "status": (
                "explicit invariant cover cocycles; automorphism orbits and "
                "rank-four construction remain unresolved"
            ),
        }


def _total_basis_coordinates(
    outer: SparseOuterHom,
    total_degree: int,
) -> tuple[
    tuple[
        int,
        int,
        int,
        tuple[int, int, int],
        str,
        tuple[int, int, int],
        tuple[int, int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    ],
    ...,
]:
    """Return compact structural coordinates for one total cochain basis."""

    bundles = _bundle_terms(outer)
    coordinates = []
    cells = sorted(
        cell for cell in _total_cells(outer) if sum(cell) == total_degree
    )
    for parent_degree, sheaf_degree in cells:
        for hom_term_index, bundle in enumerate(bundles[parent_degree]):
            ambient_blocks = (
                ("k0", bundle.ambient_k0.space(sheaf_degree)),
                ("k1_x", bundle.ambient_k1_x.space(sheaf_degree + 1)),
                ("k1_u", bundle.ambient_k1_u.space(sheaf_degree + 1)),
                ("k2", bundle.ambient_k2.space(sheaf_degree + 2)),
            )
            for summand, ambient in ambient_blocks:
                coordinates.extend(
                    (
                        parent_degree,
                        sheaf_degree,
                        hom_term_index,
                        bundle.degrees,
                        summand,
                        ambient.degrees,
                        label,
                    )
                    for label in ambient.labels
                )
    expected = outer.total[total_degree].dimension
    if len(coordinates) != expected:
        raise ValueError("structural coordinates do not span the total basis")
    return tuple(coordinates)


def _basis_coordinate_record(
    coordinate: tuple[
        int,
        int,
        int,
        tuple[int, int, int],
        str,
        tuple[int, int, int],
        tuple[int, int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    ],
) -> list[object]:
    """Convert one immutable structural basis coordinate to compact JSON."""

    (
        parent_degree,
        sheaf_degree,
        hom_term_index,
        line_degree,
        koszul_summand,
        ambient_degree,
        ambient_label,
    ) = coordinate
    x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = ambient_label
    return [
        parent_degree,
        sheaf_degree,
        hom_term_index,
        list(line_degree),
        koszul_summand,
        list(ambient_degree),
        x_h,
        u_h,
        p_h,
        list(x_monomial),
        list(u_monomial),
        list(p_monomial),
    ]


def _monomial_images(action: SparseMap) -> tuple[tuple[int, Eisenstein], ...]:
    """Extract target indices and scalars from one exact monomial action."""

    if action.domain != action.codomain:
        raise ValueError("a monomial action must be an endomorphism")
    images: list[tuple[int, Eisenstein] | None] = [
        None for _ in range(action.domain.dimension)
    ]
    for row_index, row in enumerate(action.rows):
        if len(row) != 1:
            raise ValueError("a monomial action must have one entry per row")
        column, coefficient = row[0]
        if coefficient.is_zero() or images[column] is not None:
            raise ValueError("a monomial action must permute basis lines")
        images[column] = (row_index, coefficient)
    if any(image is None for image in images):
        raise ValueError("a monomial action must have one entry per column")
    return tuple(image for image in images if image is not None)


def _simultaneous_invariant_basis(
    degree: int,
    p_action: SparseMap,
    t_action: SparseMap,
) -> SparseInvariantBasis:
    """Construct exact root-normalized common fixed vectors orbit by orbit."""

    if p_action.domain != t_action.domain or p_action.codomain != t_action.codomain:
        raise ValueError("simultaneous actions require one common cochain space")
    ambient = p_action.domain
    p_images = _monomial_images(p_action)
    t_images = _monomial_images(t_action)
    visited = [False for _ in range(ambient.dimension)]
    invariant_orbits: list[tuple[int, dict[int, Eisenstein]]] = []
    for root in range(ambient.dimension):
        if visited[root]:
            continue
        coefficients = {root: Eisenstein(1)}
        stack = [root]
        consistent = True
        while stack:
            source = stack.pop()
            source_coefficient = coefficients[source]
            for images in (p_images, t_images):
                target, action_coefficient = images[source]
                expected = action_coefficient * source_coefficient
                existing = coefficients.get(target)
                if existing is None:
                    coefficients[target] = expected
                    stack.append(target)
                elif existing != expected:
                    consistent = False
        for index in coefficients:
            if visited[index]:
                raise ValueError("monomial action orbits overlap inconsistently")
            visited[index] = True
        if consistent:
            invariant_orbits.append((root, coefficients))
    invariant = VectorSpace(
        f"{ambient.name}:P,T-invariant",
        tuple(f"orbit:{root}" for root, _ in invariant_orbits),
        Eisenstein,
    )
    rows: list[dict[int, Eisenstein]] = [
        {} for _ in range(ambient.dimension)
    ]
    for column, (_, coefficients) in enumerate(invariant_orbits):
        for row, coefficient in coefficients.items():
            rows[row][column] = coefficient
    inclusion = SparseMap(invariant, ambient, _freeze_rows(rows))
    return SparseInvariantBasis(
        degree,
        ambient,
        invariant,
        inclusion,
        tuple(root for root, _ in invariant_orbits),
    )


def _restrict_to_invariants(
    differential: SparseMap,
    source: SparseInvariantBasis,
    target: SparseInvariantBasis,
) -> SparseMap:
    """Restrict one equivariant differential to root-normalized fixed bases."""

    image = differential.compose(source.inclusion)
    restricted = SparseMap(
        source.invariant,
        target.invariant,
        tuple(image.rows[root] for root in target.orbit_roots),
    )
    if target.inclusion.compose(restricted) != image:
        raise ValueError("equivariant differential escaped the invariant subspace")
    return restricted


def _columns(map_: SparseMap) -> list[dict[int, Eisenstein]]:
    """Return mutable sparse columns for one immutable sparse map."""

    columns: list[dict[int, Eisenstein]] = [
        {} for _ in range(map_.domain.dimension)
    ]
    for row_index, row in enumerate(map_.rows):
        for column, coefficient in row:
            columns[column][row_index] = coefficient
    return columns


def _insert_independent_column(
    column: dict[int, Eisenstein],
    pivots: dict[int, dict[int, Eisenstein]],
) -> bool:
    """Insert one column into an exact sparse span when independent."""

    vector = dict(column)
    while vector:
        pivot = min(vector)
        coefficient = vector[pivot]
        existing = pivots.get(pivot)
        if existing is None:
            inverse = Eisenstein(1) / coefficient
            pivots[pivot] = {
                row: value * inverse for row, value in vector.items()
            }
            return True
        for row, value in existing.items():
            updated = vector.get(row, Eisenstein(0)) - coefficient * value
            if updated.is_zero():
                vector.pop(row, None)
            else:
                vector[row] = updated
    return False


def _cohomology_complement_columns(
    boundaries: SparseMap,
    cycles: SparseMap,
) -> tuple[int, ...]:
    """Select cycle columns extending the exact boundary image basis."""

    if boundaries.codomain != cycles.codomain:
        raise ValueError("cycles and boundaries require one common cochain space")
    pivots: dict[int, dict[int, Eisenstein]] = {}
    boundary_columns = _columns(boundaries)
    for column in sorted(boundary_columns, key=len):
        _insert_independent_column(column, pivots)
    selected = []
    for index, column in enumerate(_columns(cycles)):
        if _insert_independent_column(column, pivots):
            selected.append(index)
    return tuple(selected)


def _select_columns(
    map_: SparseMap,
    selected: tuple[int, ...],
    name: str,
) -> SparseMap:
    """Return one exact sparse map containing selected source columns."""

    selected_indices = {column: index for index, column in enumerate(selected)}
    domain = VectorSpace(
        name,
        tuple(f"class:{index}" for index in range(len(selected))),
        Eisenstein,
    )
    return SparseMap(
        domain,
        map_.codomain,
        _freeze_rows(
            {
                selected_indices[column]: coefficient
                for column, coefficient in row
                if column in selected_indices
            }
            for row in map_.rows
        ),
    )


def _chain_map_gate(
    outer: SparseOuterHom,
    components: dict[int, SparseMap],
) -> bool:
    """Check that one total action commutes with every total differential."""

    for degree, differential in outer.total_differentials:
        if degree + 1 not in components:
            continue
        left = components[degree + 1].compose(differential)
        right = differential.compose(components[degree])
        if left != right:
            return False
    return True


def _order_three(components: dict[int, SparseMap]) -> bool:
    """Check one action's exact order-three identity on every total degree."""

    return all(
        components[degree].compose(components[degree]).compose(
            components[degree]
        )
        == _identity(components[degree].domain)
        for degree in components
    )


def _components(
    outer: SparseOuterHom,
    action: SchoenSparseDeckAction,
    name: str,
) -> dict[int, SparseMap]:
    """Build one totalized action from exact presentation matrices."""

    bundles = _bundle_terms(outer)
    left_pair, left_characters = _factor_resolution_data(outer.left)
    right_pair, right_characters = _factor_resolution_data(outer.right)
    term_matrices = _presentation_term_actions(
        name,
        left_pair,
        right_pair,
        left_characters,
        right_characters,
    )
    cells = _total_cells(outer)
    by_degree: dict[int, list[tuple[int, int]]] = {}
    for cell in cells:
        by_degree.setdefault(sum(cell), []).append(cell)
    components = {}
    for degree, selected_cells in by_degree.items():
        blocks = tuple(
            tuple(
                _term_action(
                    outer,
                    action,
                    target_cell[0],
                    target_cell[1],
                    bundles,
                    term_matrices[target_cell[0]],
                )
                if target_cell == source_cell
                else SparseMap.zero(
                    _sparse_line_sum_space(
                        bundles[source_cell[0]],
                        source_cell[1],
                    ),
                    _sparse_line_sum_space(
                        bundles[target_cell[0]],
                        target_cell[1],
                    ),
                )
                for source_cell in selected_cells
            )
            for target_cell in selected_cells
        )
        components[degree] = SparseMap.block(blocks)
    return components


def sparse_outer_deck_audit(outer: SparseOuterHom) -> SparseOuterDeckAudit:
    """Build and certify P/T actions on one sparse cover Hom totalization."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    p = _components(outer, actions["P"], "P")
    t = _components(outer, actions["T"], "T")
    p_chain = _chain_map_gate(outer, p)
    t_chain = _chain_map_gate(outer, t)
    commute = all(
        p[degree].compose(t[degree]) == t[degree].compose(p[degree])
        for degree in p
    )
    result = SparseOuterDeckAudit(
        outer,
        tuple(sorted(p.items())),
        tuple(sorted(t.items())),
        p_chain,
        t_chain,
        _order_three(p),
        _order_three(t),
        commute,
    )
    return result


def sparse_outer_invariant_audit(
    outer: SparseOuterHom,
    certified_cover_ext_one_dimension: int | None = None,
) -> SparseOuterInvariantAudit:
    """Build the exact common-fixed subcomplex and its invariant Ext-one."""

    if (
        certified_cover_ext_one_dimension is not None
        and (
            isinstance(certified_cover_ext_one_dimension, bool)
            or not isinstance(certified_cover_ext_one_dimension, int)
            or certified_cover_ext_one_dimension < 0
        )
    ):
        raise ValueError("a certified cover Ext dimension must be nonnegative")

    deck = sparse_outer_deck_audit(outer)
    if not deck.exact:
        raise ValueError("invariant cohomology requires exact commuting deck actions")
    p_components = dict(deck.p_components)
    t_components = dict(deck.t_components)
    bases = {
        degree: _simultaneous_invariant_basis(
            degree,
            p_components[degree],
            t_components[degree],
        )
        for degree in sorted(p_components)
    }
    for degree, basis in bases.items():
        if (
            p_components[degree].compose(basis.inclusion) != basis.inclusion
            or t_components[degree].compose(basis.inclusion) != basis.inclusion
        ):
            raise ValueError("constructed invariant basis is not pointwise fixed")
    differentials = {
        degree: _restrict_to_invariants(
            differential,
            bases[degree],
            bases[degree + 1],
        )
        for degree, differential in outer.total_differentials
        if degree + 1 in bases
    }
    squared_zero = all(
        differentials[degree + 1].compose(differential).is_zero()
        for degree, differential in differentials.items()
        if degree + 1 in differentials
    )
    invariant_ext_one_dimension = _invariant_cohomology_dimension(
        bases,
        differentials,
        1,
    )
    cover_ext_one_dimension = (
        outer.cover_ext_one_dimension
        if certified_cover_ext_one_dimension is None
        else certified_cover_ext_one_dimension
    )
    return SparseOuterInvariantAudit(
        outer,
        deck,
        tuple(sorted(bases.items())),
        tuple(sorted(differentials.items())),
        cover_ext_one_dimension,
        invariant_ext_one_dimension,
        True,
        squared_zero,
    )


def sparse_outer_invariant_cocycles(
    invariant_audit: SparseOuterInvariantAudit,
    degree: int = 1,
) -> SparseInvariantCocycleBasis:
    """Construct explicit invariant cocycles modulo exact boundaries."""

    if not invariant_audit.exact:
        raise ValueError("explicit cocycles require an exact invariant subcomplex")
    bases = dict(invariant_audit.bases)
    if degree not in bases:
        raise ValueError("requested cohomology degree is absent")
    differentials = dict(invariant_audit.differentials)
    cochains = bases[degree].invariant
    outgoing = differentials.get(
        degree,
        SparseMap.zero(
            cochains,
            VectorSpace(f"zero:{degree + 1}", (), Eisenstein),
        ),
    )
    boundaries = differentials.get(
        degree - 1,
        SparseMap.zero(
            VectorSpace(f"zero:{degree - 1}", (), Eisenstein),
            cochains,
        ),
    )
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(boundaries, cycles)
    representatives = _select_columns(
        cycles,
        selected,
        f"H^{degree}:P,T-invariant",
    )
    cover_representatives = bases[degree].inclusion.compose(representatives)
    expected_dimension = sparse_invariant_cohomology_dimension(
        invariant_audit,
        degree,
    )
    combined = SparseMap.block(((boundaries, representatives),))
    cycles_exact = outgoing.compose(cycles).is_zero()
    quotient_exact = (
        representatives.domain.dimension == expected_dimension
        and combined.rank()
        == boundaries.rank() + representatives.domain.dimension
    )
    outer_differentials = dict(invariant_audit.outer.total_differentials)
    cover_cycles_exact = (
        degree not in outer_differentials
        or outer_differentials[degree].compose(cover_representatives).is_zero()
    )
    return SparseInvariantCocycleBasis(
        invariant_audit,
        degree,
        cycles,
        boundaries,
        representatives,
        cover_representatives,
        cycles_exact,
        quotient_exact,
        cover_cycles_exact,
    )


__all__ = [
    "SparseInvariantBasis",
    "SparseInvariantCocycleBasis",
    "SparseOuterDeckAudit",
    "SparseOuterInvariantAudit",
    "sparse_invariant_cohomology_dimension",
    "sparse_outer_deck_audit",
    "sparse_outer_invariant_audit",
    "sparse_outer_invariant_cocycles",
]
