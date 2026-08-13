"""Derive deck actions on the fiber-sensitive dP9 Serre complexes.

Owns:
    Monomial pullback on ambient ``P2 x P1`` cohomology, its compatible action
    on dP9 Koszul cones, dual Hilbert--Burch frame actions, and induced exact
    actions on constituent Ext-one representatives.

Depends on:
    Published coordinate lifts, derived Hilbert--Burch resolution lifts, exact
    dP9 Serre total complexes, and basis-aware homological algebra.

Must not:
    Import published Serre matrices as chain maps, choose a character twist to
    force an invariant ray, or infer quotient descent before the action gates
    pass exactly.

Phase 0:
    Research-only derivation of constituent deck actions and their induced
    Ext-one representations.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import ChainMap, LinearMap
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein

from .dp9_actions import CoordinateImage, published_coordinate_images
from .dp9_linebundles import DPSurfaceLineBundle, _kunneth_space
from .dp9_serre_ext import DPSurfaceSerreExt, published_constituent_serre_exts
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions
from .tier_b_dp9_actions import _induced_action

FiberImage = tuple[tuple[Eisenstein, tuple[int, ...]], ...]


def _fiber_coordinate_images(generator: str, surface_factor: int) -> FiberImage:
    """Return the homogeneous fiber action making one dP9 equation invariant."""

    if surface_factor not in (1, 2):
        raise ValueError("dP9 surface factors are indexed by one and two")
    if generator == "T":
        return (
            (Eisenstein(1), (1, 0)),
            (Eisenstein(1), (0, 1)),
        )
    if generator == "P" and surface_factor == 1:
        return (
            (OMEGA, (1, 0)),
            (Eisenstein(1), (0, 1)),
        )
    if generator == "P" and surface_factor == 2:
        return (
            (Eisenstein(1), (1, 0)),
            (OMEGA, (0, 1)),
        )
    raise KeyError(generator)


def _monomial_image(
    monomial: tuple[int, ...],
    images: tuple[tuple[Eisenstein, tuple[int, ...]], ...],
) -> tuple[Eisenstein, tuple[int, ...]]:
    """Apply a monomial substitution to positive or Serre-dual exponents."""

    coefficient = Eisenstein(1)
    exponents = [0 for _ in monomial]
    for power, (image_coefficient, image_exponents) in zip(
        monomial,
        images,
        strict=True,
    ):
        coefficient *= image_coefficient**power
        for index, exponent in enumerate(image_exponents):
            exponents[index] += power * exponent
    return coefficient, tuple(exponents)


def _ambient_action(
    base_degree: int,
    fiber_degree: int,
    total_degree: int,
    base_images: CoordinateImage,
    fiber_images: FiberImage,
) -> LinearMap:
    """Return exact pullback on one ambient Kunneth cohomology space."""

    space, records = _kunneth_space(base_degree, fiber_degree, total_degree)
    labels = tuple(
        (base_cohomology, fiber_cohomology, base, fiber)
        for base_cohomology, fiber_cohomology, base_basis, fiber_basis in records
        for base in base_basis
        for fiber in fiber_basis
    )
    indices = {label: index for index, label in enumerate(labels)}
    rows = [
        [Eisenstein(0) for _ in labels]
        for _ in labels
    ]
    for source_index, (base_cohomology, fiber_cohomology, base, fiber) in enumerate(
        labels
    ):
        base_coefficient, target_base = _monomial_image(base, base_images)
        fiber_coefficient, target_fiber = _monomial_image(fiber, fiber_images)
        target = (
            base_cohomology,
            fiber_cohomology,
            target_base,
            target_fiber,
        )
        target_index = indices.get(target)
        if target_index is None:
            raise ValueError("deck pullback escaped an ambient Kunneth basis")
        rows[target_index][source_index] = base_coefficient * fiber_coefficient
    return LinearMap(space, space, rows)


def _line_bundle_action(
    bundle: DPSurfaceLineBundle,
    generator: str,
) -> ChainMap:
    """Lift one equation-preserving pullback to a dP9 Koszul cone."""

    base_images = published_coordinate_images(generator)
    fiber_images = _fiber_coordinate_images(generator, bundle.surface_factor)
    components = {}
    for degree in bundle.complex.degrees:
        target_action = _ambient_action(
            bundle.base_degree,
            bundle.fiber_degree,
            degree,
            base_images,
            fiber_images,
        )
        source_action = _ambient_action(
            bundle.base_degree - 3,
            bundle.fiber_degree - 1,
            degree + 1,
            base_images,
            fiber_images,
        )
        components[degree] = LinearMap.block(
            (
                (
                    target_action,
                    LinearMap.zero(
                        bundle.ambient_source.space(degree + 1),
                        bundle.ambient_target.space(degree),
                    ),
                ),
                (
                    LinearMap.zero(
                        bundle.ambient_target.space(degree),
                        bundle.ambient_source.space(degree + 1),
                    ),
                    source_action,
                ),
            )
        )
    return ChainMap(bundle.complex, bundle.complex, components)


def _term_action(
    bundles: tuple[DPSurfaceLineBundle, ...],
    frame_action: Matrix,
    generator: str,
    sheaf_degree: int,
) -> LinearMap:
    """Tensor a dual resolution-frame action with geometric pullback."""

    if frame_action.shape != (len(bundles), len(bundles)):
        raise ValueError("dual resolution action has the wrong term rank")
    line_actions = tuple(_line_bundle_action(bundle, generator) for bundle in bundles)
    blocks: list[list[LinearMap]] = []
    for target_index, target_bundle in enumerate(bundles):
        row: list[LinearMap] = []
        for source_index, source_bundle in enumerate(bundles):
            coefficient = frame_action[target_index][source_index]
            source_space = source_bundle.complex.spaces.space(sheaf_degree)
            target_space = target_bundle.complex.spaces.space(sheaf_degree)
            if coefficient.is_zero():
                row.append(LinearMap.zero(source_space, target_space))
            else:
                if (
                    source_bundle.base_degree != target_bundle.base_degree
                    or source_bundle.fiber_degree != target_bundle.fiber_degree
                    or source_bundle.surface_factor != target_bundle.surface_factor
                ):
                    raise ValueError("frame action mixes incompatible dP9 line bundles")
                row.append(
                    line_actions[target_index].component(sheaf_degree).scale(
                        coefficient
                    )
                )
        blocks.append(row)
    return LinearMap.block(blocks)


def _total_cells(extension: DPSurfaceSerreExt) -> tuple[tuple[int, int], ...]:
    """Return totalization cells in the exact ordering used by Bicomplex."""

    cells = {cell for cell, _ in extension.bicomplex.components}
    cells.update(cell for cell, _ in extension.bicomplex.horizontal)
    cells.update(cell for cell, _ in extension.bicomplex.vertical)
    return tuple(sorted(cells))


def _dual_frame_actions(
    pair: ResolutionActionPair,
    generator: str,
) -> dict[int, Matrix]:
    """Dualize the two semilinear Hilbert--Burch frame actions."""

    action = pair.action(generator)
    return {
        0: action.target_action.inverse().transpose(),
        1: action.source_action.inverse().transpose(),
    }


def _total_action(
    extension: DPSurfaceSerreExt,
    pair: ResolutionActionPair,
    generator: str,
) -> ChainMap:
    """Build one exact deck action on the Serre total complex."""

    frames = _dual_frame_actions(pair, generator)
    bundles = {
        0: extension.generator_bundles,
        1: extension.syzygy_bundles,
    }
    degree_cells: dict[int, tuple[tuple[int, int], ...]] = {}
    for cell in _total_cells(extension):
        degree = sum(cell)
        degree_cells[degree] = tuple(sorted((*degree_cells.get(degree, ()), cell)))
    components = {}
    for degree in extension.total.degrees:
        maps = tuple(
            _term_action(
                bundles[parent_degree],
                frames[parent_degree],
                generator,
                sheaf_degree,
            )
            for parent_degree, sheaf_degree in degree_cells.get(degree, ())
        )
        if not maps:
            components[degree] = LinearMap.zero(
                extension.total.spaces.space(degree),
                extension.total.spaces.space(degree),
            )
            continue
        combined = maps[0]
        for map_ in maps[1:]:
            combined = LinearMap.direct_sum(combined, map_)
        components[degree] = combined
    return ChainMap(extension.total, extension.total, components)


def _matrix_record(matrix: Matrix) -> list[list[str]]:
    """Serialize an exact induced action matrix."""

    return [[str(value) for value in row] for row in matrix.rows]


@dataclass(frozen=True, slots=True)
class DPSurfaceSerreDeckAction:
    """Derived chain actions and induced Ext-one representation."""

    extension: DPSurfaceSerreExt
    p_action: ChainMap
    t_action: ChainMap
    p_induced: Matrix
    t_induced: Matrix

    @property
    def actions_commute(self) -> bool:
        """Return whether P and T commute on the total complex."""

        return self.p_action.compose(self.t_action) == self.t_action.compose(
            self.p_action
        )

    @property
    def actions_order_three(self) -> bool:
        """Return whether each total chain action has order three."""

        identity = ChainMap.identity(self.extension.total)
        return (
            self.p_action.compose(self.p_action).compose(self.p_action) == identity
            and self.t_action.compose(self.t_action).compose(self.t_action) == identity
        )

    @property
    def induced_actions_commute(self) -> bool:
        """Return whether the two induced Ext-one matrices commute."""

        return self.p_induced @ self.t_induced == self.t_induced @ self.p_induced

    def as_record(self) -> dict[str, object]:
        """Serialize chain gates and induced matrices without selecting a ray."""

        return {
            "scheme": self.extension.scheme.name,
            "surface_factor": self.extension.surface_factor,
            "ext_one_dimension": self.extension.ext_one_dimension,
            "p_induced": _matrix_record(self.p_induced),
            "t_induced": _matrix_record(self.t_induced),
            "actions_commute": self.actions_commute,
            "actions_order_three": self.actions_order_three,
            "induced_actions_commute": self.induced_actions_commute,
            "status": (
                "derived action in the natural equation-preserving dP9 "
                "linearization; character comparison remains pending"
            ),
        }


def dp9_serre_deck_action(
    extension: DPSurfaceSerreExt,
    pair: ResolutionActionPair,
) -> DPSurfaceSerreDeckAction:
    """Derive both deck generators and their Ext-one actions."""

    if extension.scheme != pair.scheme:
        raise ValueError("Serre complex and resolution action use different schemes")
    p_action = _total_action(extension, pair, "P")
    t_action = _total_action(extension, pair, "T")
    representatives = extension.ext_one_representatives
    p_induced = _induced_action(p_action, extension.total, 1, representatives)
    t_induced = _induced_action(t_action, extension.total, 1, representatives)
    if p_induced is None or t_induced is None:
        raise ValueError("published constituent Ext-one spaces must be nonzero")
    return DPSurfaceSerreDeckAction(
        extension,
        p_action,
        t_action,
        p_induced,
        t_induced,
    )


def published_constituent_serre_actions() -> tuple[DPSurfaceSerreDeckAction, ...]:
    """Derive W1/W2 constituent actions in published factor order."""

    return tuple(
        dp9_serre_deck_action(extension, pair)
        for extension, pair in zip(
            published_constituent_serre_exts(),
            tier_a_resolution_actions(),
            strict=True,
        )
    )


__all__ = [
    "DPSurfaceSerreDeckAction",
    "dp9_serre_deck_action",
    "published_constituent_serre_actions",
]
