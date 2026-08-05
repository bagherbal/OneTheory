"""Compute raw deck actions on the atlas-local Serre Cech classes.

Owns:
    Exact P/T point permutations, local coordinate characters, Laurent Cech
    cocycle multipliers, and the raw invariant subspaces of the I3/I6 local
    extension directions.

Depends on:
    The atlas-local Serre cocycles and exact Eisenstein linear algebra. These
    actions are computed before line-character compensation or global gluing.

Must not:
    Call raw local invariance a global linearization, infer an equivariant
    constituent from a character count, or replace the missing global Cech
    complement and extension map.

Phase 0:
    Raw local deck action records are exact; global Serre descent remains an
    unresolved construction gate.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

from .pencil import TierAPencilModel, tier_a_pencil_model
from .serre_atlas import AtlasSerreLocal, tier_a_atlas_serre_locals

POINTS = ("p_a", "p_b", "p_c")
PERMUTATION_P = ("p_c", "p_a", "p_b")


@dataclass(frozen=True, slots=True)
class LocalCechDeckAction:
    """One raw P/T action on the three local point classes."""

    scheme: str
    generator: str
    point_images: tuple[str, ...]
    coordinate_weights: tuple[Eisenstein, Eisenstein]
    cocycle_multiplier: Eisenstein
    action_matrix: Matrix
    order_three: bool
    commutes_with_other_generator: bool
    raw_invariant_dimension: int
    status: str

    def as_record(self) -> dict[str, object]:
        """Serialize the exact raw action and its status boundary."""

        return {
            "scheme": self.scheme,
            "generator": self.generator,
            "point_images": list(self.point_images),
            "coordinate_weights": [str(value) for value in self.coordinate_weights],
            "cocycle_multiplier": str(self.cocycle_multiplier),
            "action_matrix": {
                "shape": list(self.action_matrix.shape),
                "rows": [[str(value) for value in row] for row in self.action_matrix.rows],
            },
            "order_three": self.order_three,
            "commutes_with_other_generator": self.commutes_with_other_generator,
            "raw_invariant_dimension": self.raw_invariant_dimension,
            "status": self.status,
        }


def _permutation_matrix(multiplier: Eisenstein) -> Matrix:
    """Return the exact point-cycle action with one scalar multiplier."""

    return Matrix(
        (
            (0, multiplier, 0),
            (0, 0, multiplier),
            (multiplier, 0, 0),
        ),
        scalar_type=Eisenstein,
    )


def _diagonal_matrix(multiplier: Eisenstein) -> Matrix:
    """Return the exact fixed-point action with one scalar multiplier."""

    return Matrix(
        (
            (multiplier, 0, 0),
            (0, multiplier, 0),
            (0, 0, multiplier),
        ),
        scalar_type=Eisenstein,
    )


def _raw_invariant_dimension(actions: tuple[Matrix, Matrix]) -> int:
    """Return the common fixed-space dimension of two exact actions."""

    size = actions[0].shape[0]
    identity = Matrix.identity(size, scalar_type=Eisenstein)
    equations = Matrix(
        (*((actions[0] - identity).rows), *((actions[1] - identity).rows)),
        scalar_type=Eisenstein,
    )
    return len(equations.nullspace())


def _action_records(
    scheme: str,
    multiplier: Eisenstein,
    p_matrix: Matrix,
    t_matrix: Matrix,
) -> tuple[LocalCechDeckAction, ...]:
    """Create exact P/T records for one scheme."""

    identity = Matrix.identity(3, scalar_type=Eisenstein)
    invariant_dimension = _raw_invariant_dimension((p_matrix, t_matrix))
    records = (
        LocalCechDeckAction(
            scheme,
            "P",
            PERMUTATION_P,
            (OMEGA, OMEGA2),
            multiplier,
            p_matrix,
            p_matrix**3 == identity,
            p_matrix @ t_matrix == t_matrix @ p_matrix,
            invariant_dimension,
            "raw local action; line-character compensation and global gluing pending",
        ),
        LocalCechDeckAction(
            scheme,
            "T",
            POINTS,
            (OMEGA, OMEGA2),
            multiplier,
            t_matrix,
            t_matrix**3 == identity,
            p_matrix @ t_matrix == t_matrix @ p_matrix,
            invariant_dimension,
            "raw local action; line-character compensation and global gluing pending",
        ),
    )
    return records


def tier_a_local_cech_deck_actions(
    model: TierAPencilModel | None = None,
    locals_: tuple[AtlasSerreLocal, ...] | None = None,
) -> tuple[LocalCechDeckAction, ...]:
    """Return exact raw deck actions on both local Serre directions."""

    current = tier_a_pencil_model() if model is None else model
    local_records = tier_a_atlas_serre_locals(current) if locals_ is None else locals_
    if not all(item.local_cocycle_exact for item in local_records):
        raise ValueError("raw deck actions require exact local Cech cocycles")
    result: list[LocalCechDeckAction] = []
    for scheme, multiplicity in (("I3", 1), ("I6", 2)):
        multiplier = OMEGA ** (multiplicity + 2)
        p_matrix = _permutation_matrix(multiplier)
        t_matrix = _diagonal_matrix(multiplier)
        result.extend(_action_records(scheme, multiplier, p_matrix, t_matrix))
    return tuple(result)


__all__ = ["LocalCechDeckAction", "tier_a_local_cech_deck_actions"]
