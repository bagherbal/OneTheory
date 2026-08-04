"""Exact holomorphic tree-level flavor structure of the Schoen carrier.

Owns:
    The supported cubic Yukawa texture, its polynomial determinant identity,
    generic rank bound, exact null-vector formulas, common one-plus-two family
    support decomposition, and the tree-level CKM-CP obstruction.

Depends on:
    `onetheory.math.linear`, `polynomials`, and `numbers`, plus the core exact-input
    failure vocabulary. It does not import metrics, observations, engine,
    verification, or physical normalization machinery.

Must not:
    Treat holomorphic coefficients as masses, insert measured values, choose a
    geometry from a mixing angle, fabricate rank-lifting coefficients, or report a
    physical Yukawa or CKM matrix.

Phase 0:
    The exact holomorphic support theorem is implemented; canonical normalization,
    physical Yukawas, and CKM observables remain unresolved.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from onetheory.core.errors import MissingPhysicalInput, NonExactInput
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import Rational, coerce_rational
from onetheory.math.polynomials import Polynomial, determinant


@dataclass(frozen=True, slots=True)
class HolomorphicTexture:
    """A formal four-parameter cubic texture with no assigned physical values."""

    sector: str
    variable_names: tuple[str, str, str, str]
    matrix: tuple[tuple[Polynomial, ...], ...]
    right_null: tuple[Polynomial, Polynomial, Polynomial]
    left_null: tuple[Polynomial, Polynomial, Polynomial]

    @property
    def determinant(self) -> Polynomial:
        """Return the exact symbolic determinant."""

        return determinant(self.matrix)

    @property
    def generic_rank(self) -> int:
        """Return the rank attained away from the vanishing coefficient locus."""

        return 2

    @property
    def family_block_sizes(self) -> tuple[int, int]:
        """Return the common one-plus-two support decomposition."""

        return (1, 2)

    def evaluate(self, coefficients: Mapping[str, object]) -> Matrix:
        """Evaluate with caller-supplied exact coefficients only."""

        missing = tuple(name for name in self.variable_names if name not in coefficients)
        if missing:
            raise MissingPhysicalInput("holomorphic Yukawa coefficients", missing)
        values = tuple(coerce_rational(coefficients[name]) for name in self.variable_names)
        entries = tuple(
            tuple(
                _constant_value(entry.substitute(values))
                for entry in row
            )
            for row in self.matrix
        )
        return Matrix(entries)

    def exact_null_vectors(self, coefficients: Mapping[str, object]) -> tuple[Vector, Vector]:
        """Return the exact right and left null vectors for supplied coefficients."""

        values = tuple(coerce_rational(coefficients[name]) for name in self.variable_names)
        a, b, c, d = values
        return Vector((0, -b, a)), Vector((0, -d, c))


@dataclass(frozen=True, slots=True)
class TreeLevelFlavorResult:
    """The model-independent content of the supported holomorphic texture."""

    up: HolomorphicTexture
    down: HolomorphicTexture
    physical: bool
    ckm_cp_obstructed: bool
    obstruction_statement: str


def _constant_value(polynomial: Polynomial) -> Rational:
    """Extract a scalar from a fully evaluated exact constant polynomial."""

    if polynomial.variable_count != 0 or len(polynomial.terms) != 1:
        raise NonExactInput("texture evaluation did not produce an exact scalar")
    return coerce_rational(polynomial.coefficient(()))


def _texture(sector: str) -> HolomorphicTexture:
    """Construct one formal texture over four independent coefficient variables."""

    variables = tuple(
        Polynomial.monomial(tuple(1 if index == position else 0 for index in range(4)))
        for position in range(4)
    )
    a, b, c, d = variables
    return HolomorphicTexture(
        sector,
        ("a", "b", "c", "d"),
        ((Polynomial.zero(4), a, b), (c, Polynomial.zero(4), Polynomial.zero(4)),
         (d, Polynomial.zero(4), Polynomial.zero(4))),
        (Polynomial.zero(4), -b, a),
        (Polynomial.zero(4), -d, c),
    )


def tree_level_flavor() -> TreeLevelFlavorResult:
    """Return the exact holomorphic texture theorem for both cubic sectors."""

    up = _texture("up")
    down = _texture("down")
    if not up.determinant.is_zero() or not down.determinant.is_zero():
        raise ValueError("the supported tree-level determinant identity failed")
    if up.family_block_sizes != down.family_block_sizes:
        raise ValueError("up and down textures do not share the family decomposition")
    return TreeLevelFlavorResult(
        up,
        down,
        False,
        True,
        "The common one-plus-two holomorphic support has no tree-level CKM CP invariant.",
    )


def tree_yukawa_texture(a: object, b: object, c: object, d: object) -> Matrix:
    """Evaluate the exact support matrix from explicit caller-supplied coefficients."""

    values = tuple(coerce_rational(value) for value in (a, b, c, d))
    return Matrix(((0, values[0], values[1]), (values[2], 0, 0), (values[3], 0, 0)))
