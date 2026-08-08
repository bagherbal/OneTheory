"""Lift sparse Schoen deck actions to presentation Hom totalizations.

Owns:
    Exact pullback-and-conjugation maps on sparse Hom cells, totalized chain-map
    checks, order-three checks, and projective-generator commutator checks for
    declared monomial Serre ray pairs.

Depends on:
    Sparse Schoen line actions, exact presentation Hom matrices, and the
    certified monomial resolution actions.

Must not:
    Call an invariant cover class a descended extension, hide a failed
    linearization, or promote a finite action audit to physical selection.

Phase 0:
    Hom-level cover equivariance is executable for declared pairs; quotient
    invariant Ext and rank-four construction remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein

from .projective_hom_action import _presentation_term_actions
from .resolution_actions import ResolutionActionPair
from .schoen_outer import _hom_term_lines
from .schoen_sparse_actions import (
    SchoenSparseDeckAction,
    _inverse_images,
    schoen_sparse_deck_actions,
)
from .schoen_sparse_outer import (
    SparseMap,
    SparseOuterHom,
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
    if presentation.factor == 0:
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
        for sheaf_degree in range(4)
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


__all__ = ["SparseOuterDeckAudit", "sparse_outer_deck_audit"]
