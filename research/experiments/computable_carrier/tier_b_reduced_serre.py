"""Audit local Serre prerequisites on reduced special orbit schemes.

Owns:
    Exact functions on the four reduced length-three orbit supports, their
    induced P/T permutation actions, simultaneous character spaces, and local
    unit tests for a possible Serre extension class.

Depends on:
    Exact Eisenstein linear algebra, the fixed projective deck action, and the
    reduced orbit Hilbert--Burch presentations.

Must not:
    Call support functions a global Ext group, fabricate a rank-two bundle or
    transition cocycle, infer quotient descent, or claim a physical carrier.

Phase 0:
    Local reduced-support Serre prerequisites are exact; global extension
    construction, dP9 patching, linearization, and descent remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

from .tier_b_orbits import ProjectivePoint, _deck_generators
from .tier_b_reduced_schemes import ReducedOrbitScheme, tier_b_reduced_orbit_schemes

CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)


def _permutation_action(points: tuple[ProjectivePoint, ...], generator) -> Matrix:
    """Build the exact pullback action on functions over a reduced support."""

    index = {point: position for position, point in enumerate(points)}
    rows = [[Eisenstein(0) for _ in points] for _ in points]
    for source, point in enumerate(points):
        image = _normalize_point(generator, point)
        rows[source][index[image]] = Eisenstein(1)
    return Matrix(rows, scalar_type=Eisenstein)


def _normalize_point(generator, point: ProjectivePoint) -> ProjectivePoint:
    """Apply one exact lift and normalize its projective representative."""

    image = generator.matvec(Vector(point, scalar_type=Eisenstein))
    pivot = next((value for value in image if not value.is_zero()), None)
    if pivot is None:
        raise ValueError("a deck lift cannot map a projective point to zero")
    return tuple(value / pivot for value in image)


@dataclass(frozen=True, slots=True)
class ReducedSerreCharacter:
    """One exact support-function character space and local-unit witness."""

    p_character: Eisenstein
    t_character: Eisenstein
    vectors: tuple[tuple[Eisenstein, ...], ...]

    @property
    def dimension(self) -> int:
        """Return the exact simultaneous-character dimension."""

        return len(self.vectors)

    @property
    def contains_local_unit(self) -> bool:
        """Return whether a character vector is nonzero at every support point."""

        return any(all(not value.is_zero() for value in vector) for vector in self.vectors)

    def as_record(self) -> dict[str, object]:
        """Serialize the exact character space and its local-unit gate."""

        return {
            "p_character": str(self.p_character),
            "t_character": str(self.t_character),
            "dimension": self.dimension,
            "vectors": [[str(value) for value in vector] for vector in self.vectors],
            "contains_local_unit": self.contains_local_unit,
        }


@dataclass(frozen=True, slots=True)
class ReducedSerrePrerequisite:
    """Exact local-support data required before a reduced Serre construction."""

    scheme: ReducedOrbitScheme
    p_action: Matrix
    t_action: Matrix
    characters: tuple[ReducedSerreCharacter, ...]
    local_lci: bool
    global_serre_constructed: bool = False

    def __post_init__(self) -> None:
        if self.p_action.shape != (3, 3) or self.t_action.shape != (3, 3):
            raise ValueError("reduced support actions must be three-dimensional")
        if self.global_serre_constructed:
            raise ValueError("this diagnostic cannot claim a global Serre construction")

    @property
    def extension_space_dimension(self) -> int:
        """Return the exact dimension of functions on the reduced support."""

        return 3

    @property
    def local_unit_character_count(self) -> int:
        """Return the number of character spaces containing a local unit."""

        return sum(character.contains_local_unit for character in self.characters)

    @property
    def exact(self) -> bool:
        """Return the local-support prerequisite certificate."""

        identity = Matrix.identity(3, scalar_type=Eisenstein)
        return (
            self.scheme.exact
            and self.local_lci
            and self.p_action**3 == identity
            and self.t_action**3 == identity
            and self.p_action @ self.t_action == self.t_action @ self.p_action
            and self.extension_space_dimension == 3
            and len(self.characters) == 3
            and self.local_unit_character_count == 3
        )

    def as_record(self) -> dict[str, object]:
        """Serialize local prerequisite data with its global boundary."""

        return {
            "scheme": self.scheme.orbit.identifier,
            "extension_space_dimension": self.extension_space_dimension,
            "p_action": [[str(value) for value in row] for row in self.p_action.rows],
            "t_action": [[str(value) for value in row] for row in self.t_action.rows],
            "characters": [character.as_record() for character in self.characters],
            "local_lci": self.local_lci,
            "local_unit_character_count": self.local_unit_character_count,
            "global_serre_constructed": self.global_serre_constructed,
            "exact": self.exact,
            "status": (
                "exact reduced-support Serre prerequisite only; global Ext, "
                "patching, linearization, and quotient descent remain unresolved"
            ),
        }


def _characters(
    p_action: Matrix,
    t_action: Matrix,
) -> tuple[ReducedSerreCharacter, ...]:
    """Compute every nonzero simultaneous character space exactly."""

    identity = Matrix.identity(3, scalar_type=Eisenstein)
    result = []
    for p_character in CHARACTERS:
        for t_character in CHARACTERS:
            equations = Matrix(
                (*((p_action - identity.scale(p_character)).rows),
                 *((t_action - identity.scale(t_character)).rows)),
                scalar_type=Eisenstein,
            )
            vectors = tuple(vector.values for vector in equations.nullspace())
            if vectors:
                result.append(ReducedSerreCharacter(p_character, t_character, vectors))
    return tuple(result)


def _audit(scheme: ReducedOrbitScheme) -> ReducedSerrePrerequisite:
    """Construct one exact reduced-support Serre prerequisite audit."""

    generators = _deck_generators()
    p_action = _permutation_action(scheme.orbit.points, generators[0])
    t_action = _permutation_action(scheme.orbit.points, generators[1])
    result = ReducedSerrePrerequisite(
        scheme,
        p_action,
        t_action,
        _characters(p_action, t_action),
        True,
    )
    if not result.exact:
        raise ValueError("reduced-support Serre prerequisite failed exact gates")
    return result


@cache
def tier_b_reduced_serre_prerequisites() -> tuple[ReducedSerrePrerequisite, ...]:
    """Audit local Serre prerequisites for all four reduced orbit schemes."""

    return tuple(_audit(scheme) for scheme in tier_b_reduced_orbit_schemes())


__all__ = [
    "ReducedSerreCharacter",
    "ReducedSerrePrerequisite",
    "tier_b_reduced_serre_prerequisites",
]
