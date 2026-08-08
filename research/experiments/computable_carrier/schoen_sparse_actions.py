"""Audit deck actions on sparse Schoen line-bundle complexes.

Owns:
    Exact monomial actions on the three ambient factors, their equation-unit
    corrections on Koszul terms, and order/chain-map checks for the published
    Schoen deck generators.

Depends on:
    The production Heisenberg lifts and cubic characters, plus sparse exact
    Schoen line-bundle complexes. It does not consume observations.

Must not:
    Infer quotient-invariant Ext from a chain action, select a linearization
    without recording its scalar, or promote cover actions to physics.

Phase 0:
    Sparse line-bundle deck actions are exact cover-level diagnostics;
    presentation equivariance and quotient-invariant outer Ext remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.numbers import Eisenstein

from .dp9_actions import published_coordinate_images
from .dp9_deck_atlas import _cubic_characters
from .schoen_sparse_outer import (
    SparseLineBundle,
    SparseMap,
    _freeze_rows,
    sparse_line_bundle,
)

CoordinateImage = tuple[tuple[Eisenstein, tuple[int, ...]], ...]


def _inverse_images(images: CoordinateImage) -> CoordinateImage:
    """Invert one monomial coordinate substitution exactly."""

    inverse: list[tuple[Eisenstein, tuple[int, ...]] | None] = [None] * len(images)
    for source, (scalar, image) in enumerate(images):
        target = image.index(1)
        inverse[target] = (
            Eisenstein(1) / scalar,
            tuple(1 if index == source else 0 for index in range(len(images))),
        )
    if any(item is None for item in inverse):
        raise ValueError("deck image is not an invertible monomial map")
    return tuple(item for item in inverse if item is not None)


def _compose_images(first: CoordinateImage, second: CoordinateImage) -> CoordinateImage:
    """Compose two exact monomial substitutions."""

    result = []
    for second_scalar, second_exponents in second:
        scalar = second_scalar
        exponents = [0] * len(first)
        for power, (first_scalar, first_exponents) in zip(
            second_exponents,
            first,
            strict=True,
        ):
            scalar *= first_scalar**power
            for index, exponent in enumerate(first_exponents):
                exponents[index] += power * exponent
        result.append((scalar, tuple(exponents)))
    return tuple(result)


def _identity_images(variable_count: int) -> CoordinateImage:
    """Return an exact identity monomial map."""

    return tuple(
        (
            Eisenstein(1),
            tuple(1 if row == column else 0 for column in range(variable_count)),
        )
        for row in range(variable_count)
    )


def _monomial_action(
    source: tuple[int, ...],
    images: CoordinateImage,
) -> tuple[Eisenstein, tuple[int, ...]]:
    """Transform one possibly negative monomial."""

    scalar = Eisenstein(1)
    exponents = [0] * len(source)
    for power, (image_scalar, image_exponents) in zip(source, images, strict=True):
        scalar *= image_scalar**power
        for index, exponent in enumerate(image_exponents):
            exponents[index] += power * exponent
    return scalar, tuple(exponents)


def _ambient_action(
    space,
    x_images: CoordinateImage,
    u_images: CoordinateImage,
    p_images: CoordinateImage,
) -> SparseMap:
    """Build one sparse monomial action on an ambient Künneth basis."""

    indices = {label: index for index, label in enumerate(space.labels)}
    rows: list[dict[int, Eisenstein]] = [{} for _ in space.labels]
    for source_index, label in enumerate(space.labels):
        x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
        x_scalar, x_target = _monomial_action(x_monomial, x_images)
        u_scalar, u_target = _monomial_action(u_monomial, u_images)
        p_scalar, p_target = _monomial_action(p_monomial, p_images)
        target_label = (x_h, u_h, p_h, x_target, u_target, p_target)
        target_index = indices.get(target_label)
        if target_index is None:
            raise ValueError("deck action escaped the exact ambient Künneth basis")
        rows[target_index][source_index] = x_scalar * u_scalar * p_scalar
    return SparseMap(space.vector_space, space.vector_space, _freeze_rows(rows))


@dataclass(frozen=True, slots=True)
class SchoenSparseDeckAction:
    """One published deck generator with its exact equation units."""

    name: str
    x_images: CoordinateImage
    u_images: CoordinateImage
    p_images: CoordinateImage
    first_equation_unit: Eisenstein
    second_equation_unit: Eisenstein

    @property
    def order_three_coordinates(self) -> bool:
        """Return whether all three ambient coordinate maps have order three."""

        return all(
            _compose_images(
                _compose_images(images, images),
                images,
            )
            == _identity_images(len(images))
            for images in (self.x_images, self.u_images, self.p_images)
        )

    def line_component(self, line: SparseLineBundle, degree: int) -> SparseMap:
        """Build the corrected action on one Koszul cochain space."""

        blocks = (
            _ambient_action(
                line.ambient_k0.space(degree),
                self.x_images,
                self.u_images,
                self.p_images,
            ),
            _ambient_action(
                line.ambient_k1_x.space(degree + 1),
                self.x_images,
                self.u_images,
                self.p_images,
            ).scale(self.first_equation_unit),
            _ambient_action(
                line.ambient_k1_u.space(degree + 1),
                self.x_images,
                self.u_images,
                self.p_images,
            ).scale(self.second_equation_unit),
            _ambient_action(
                line.ambient_k2.space(degree + 2),
                self.x_images,
                self.u_images,
                self.p_images,
            ).scale(self.first_equation_unit * self.second_equation_unit),
        )
        return SparseMap.block(
            tuple(
                tuple(
                    block
                    if row == column
                    else SparseMap.zero(
                        blocks[column].domain,
                        blocks[row].codomain,
                    )
                    for column, block in enumerate(blocks)
                )
                for row in range(4)
            )
        )

    def line_chain_map(self, line: SparseLineBundle) -> tuple[tuple[int, SparseMap], ...]:
        """Return and validate the corrected line-complex action."""

        components = tuple(
            (degree, self.line_component(line, degree))
            for degree in range(4)
        )
        for degree, differential in line.differentials:
            left = dict(components)[degree + 1].compose(differential)
            right = differential.compose(dict(components)[degree])
            if left != right:
                raise ValueError("Schoen deck action does not commute with Koszul d")
        return components


def _action(name: str) -> SchoenSparseDeckAction:
    """Derive one deck action from the frozen cubic characters."""

    x_images = published_coordinate_images(name)
    u_images = _inverse_images(x_images)
    f_x, g_x = _cubic_characters(name)
    p_images = (
        (g_x, (1, 0)),
        (f_x, (0, 1)),
    )
    f_u, g_u = _cubic_characters(name)
    if name in ("P", "T"):
        f_u = Eisenstein(1) / f_u
        g_u = Eisenstein(1) / g_u
    first_unit = f_x * g_x
    second_unit_f = f_x * f_u
    second_unit_g = g_x * g_u
    if second_unit_f != second_unit_g:
        raise ValueError("the shared P1 action does not preserve the second equation")
    return SchoenSparseDeckAction(
        name,
        x_images,
        u_images,
        p_images,
        first_unit,
        second_unit_f,
    )


@cache
def schoen_sparse_deck_actions() -> tuple[SchoenSparseDeckAction, ...]:
    """Return and validate the two exact sparse deck generators."""

    actions = tuple(_action(name) for name in ("P", "T"))
    if not all(action.order_three_coordinates for action in actions):
        raise ValueError("Schoen sparse deck coordinates failed order three")
    return actions


def schoen_sparse_line_action_audit(
    degrees: tuple[int, int, int] = (0, 0, 0),
) -> dict[str, object]:
    """Certify chain actions on one exact sparse line-bundle complex."""

    line = sparse_line_bundle(*degrees)
    actions = schoen_sparse_deck_actions()
    records = []
    for action in actions:
        components = action.line_chain_map(line)
        order_three = all(
            dict(components)[degree]
            .compose(dict(components)[degree])
            .compose(dict(components)[degree])
            == _identity_sparse_map(line.space(degree))
            for degree in range(4)
        )
        records.append(
            {
                "name": action.name,
                "first_equation_unit": str(action.first_equation_unit),
                "second_equation_unit": str(action.second_equation_unit),
                "chain_map": True,
                "order_three": order_three,
            }
        )
    return {
        "line_degrees": list(degrees),
        "actions": records,
        "exact": all(
            item["chain_map"] and item["order_three"] for item in records
        ),
    }


def _identity_sparse_map(space) -> SparseMap:
    """Build an exact sparse identity map."""

    rows = tuple(
        ((index, Eisenstein(1)),)
        for index in range(space.dimension)
    )
    return SparseMap(space, space, rows)


__all__ = [
    "SchoenSparseDeckAction",
    "schoen_sparse_deck_actions",
    "schoen_sparse_line_action_audit",
]
