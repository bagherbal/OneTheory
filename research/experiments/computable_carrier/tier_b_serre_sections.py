"""Compute projective monomial Serre-section diagnostics.

Owns:
    Stabilized graded quotient bases for the six bounded monomial point
    schemes, exact P/T actions on those bases, simultaneous character spaces,
    and explicit local-unit representatives for the projective Serre section
    test.

Depends on:
    Exact finite-dimensional Eisenstein linear algebra, published projective
    deck substitutions, and the bounded monomial scheme certificates. It does
    not consume observations or numerical parameters.

Must not:
    Identify a projective quotient section with a dP9 Ext class, infer a
    global Serre cocycle, hide a fiber character, or claim quotient descent or
    a physical constituent from a local-unit vector.

Phase 0:
    The projective monomial section spaces and their character/unit tests are
    exact; dP9 comparison, global patching, linearization, and promotion remain
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

from .dp9_actions import published_coordinate_images
from .tier_b_monomial import InvariantMonomialScheme, tier_b_invariant_monomial_schemes

Monomial = tuple[int, int, int]
ExactVector = tuple[Eisenstein, ...]
_UNITS = (
    Eisenstein(1),
    OMEGA,
    OMEGA2,
    -Eisenstein(1),
    -OMEGA,
    -OMEGA2,
)


def _divisible(generator: Monomial, exponent: Monomial) -> bool:
    """Return whether one monomial is divisible by another."""

    return all(left <= right for left, right in zip(generator, exponent, strict=True))


def _quotient_basis(scheme: InvariantMonomialScheme, degree: int) -> tuple[Monomial, ...]:
    """Return the exact degree slice of the projective monomial quotient."""

    if degree < 0:
        raise ValueError("graded quotient degrees must be nonnegative")
    return tuple(
        exponent
        for exponent in product(range(degree + 1), repeat=3)
        if sum(exponent) == degree
        and not any(_divisible(generator, exponent) for generator in scheme.ideal.monomials)
    )


def _stabilized_degree(scheme: InvariantMonomialScheme) -> int:
    """Find the first two consecutive quotient slices of scheme length."""

    for degree in range(2 * len(scheme.local_standard_monomials) + 3):
        if len(_quotient_basis(scheme, degree)) != scheme.length:
            continue
        if len(_quotient_basis(scheme, degree + 1)) == scheme.length:
            return degree
    raise ValueError("monomial quotient did not stabilize within the exact bound")


def _action_matrix(
    basis: tuple[Monomial, ...],
    images: tuple[tuple[Eisenstein, tuple[int, ...]], ...],
) -> Matrix:
    """Build one exact monomial substitution matrix on a quotient basis."""

    index = {monomial: position for position, monomial in enumerate(basis)}
    rows = [[Eisenstein(0) for _ in basis] for _ in basis]
    for source_position, monomial in enumerate(basis):
        target = [0, 0, 0]
        scalar = Eisenstein(1)
        for power, (image_scalar, image_exponents) in zip(monomial, images, strict=True):
            scalar *= image_scalar**power
            target = [
                current + power * exponent
                for current, exponent in zip(target, image_exponents, strict=True)
            ]
        target_position = index.get(tuple(target))
        if target_position is None:
            raise ValueError("published deck action escaped the stabilized quotient basis")
        rows[target_position][source_position] = scalar
    return Matrix(rows, scalar_type=Eisenstein)


def _commutator_scalar(left: Matrix, right: Matrix) -> Eisenstein | None:
    """Return an exact scalar for a projective commutator, when one exists."""

    left_right = left @ right
    right_left = right @ left
    return next(
        (scalar for scalar in _UNITS if left_right == right_left.scale(scalar)),
        None,
    )


def _is_local_unit(vector: ExactVector, basis: tuple[Monomial, ...], degree: int) -> bool:
    """Check nonzero constant residues at all three coordinate points."""

    vertex_monomials = ((degree, 0, 0), (0, degree, 0), (0, 0, degree))
    positions = tuple(basis.index(monomial) for monomial in vertex_monomials)
    return all(not vector[position].is_zero() for position in positions)


@dataclass(frozen=True, slots=True)
class ProjectiveCharacterSection:
    """One simultaneous P/T character subspace and its unit representative."""

    p_character: Eisenstein
    t_character: Eisenstein
    vectors: tuple[ExactVector, ...]
    unit_representative: ExactVector | None

    @property
    def dimension(self) -> int:
        """Return the exact simultaneous-character dimension."""

        return len(self.vectors)

    @property
    def contains_local_unit(self) -> bool:
        """Return whether an explicit representative is a local unit."""

        return self.unit_representative is not None

    def as_record(self) -> dict[str, object]:
        """Serialize the exact character vectors and unit witness."""

        return {
            "p_character": str(self.p_character),
            "t_character": str(self.t_character),
            "dimension": self.dimension,
            "vectors": [[str(value) for value in vector] for vector in self.vectors],
            "unit_representative": (
                None
                if self.unit_representative is None
                else [str(value) for value in self.unit_representative]
            ),
            "contains_local_unit": self.contains_local_unit,
        }


@dataclass(frozen=True, slots=True)
class ProjectiveSerreSectionAudit:
    """Exact projective quotient-section data for one monomial scheme."""

    scheme: InvariantMonomialScheme
    degree: int
    basis: tuple[Monomial, ...]
    p_action: Matrix
    t_action: Matrix
    commutator_scalar: Eisenstein | None
    character_sections: tuple[ProjectiveCharacterSection, ...]

    @property
    def extension_space_dimension(self) -> int:
        """Return the stabilized projective quotient dimension."""

        return len(self.basis)

    @property
    def unit_character_sections(self) -> tuple[ProjectiveCharacterSection, ...]:
        """Return character spaces containing explicit local-unit sections."""

        return tuple(item for item in self.character_sections if item.contains_local_unit)

    @property
    def projective_serre_candidate(self) -> bool:
        """Return whether the projective section test has an explicit unit class."""

        return bool(self.unit_character_sections)

    def as_record(self) -> dict[str, object]:
        """Serialize exact projective section data and its scope boundary."""

        return {
            "scheme": self.scheme.name,
            "degree": self.degree,
            "basis": [list(item) for item in self.basis],
            "extension_space_dimension": self.extension_space_dimension,
            "p_action": [[str(value) for value in row] for row in self.p_action.rows],
            "t_action": [[str(value) for value in row] for row in self.t_action.rows],
            "commutator_scalar": (
                None if self.commutator_scalar is None else str(self.commutator_scalar)
            ),
            "character_sections": [item.as_record() for item in self.character_sections],
            "unit_character_count": len(self.unit_character_sections),
            "projective_serre_candidate": self.projective_serre_candidate,
            "status": (
                "projective monomial quotient-section diagnostic only; dP9 Ext, "
                "global Serre gluing, and quotient descent remain unresolved"
            ),
        }


def _character_sections(
    basis: tuple[Monomial, ...],
    p_action: Matrix,
    t_action: Matrix,
    degree: int,
) -> tuple[ProjectiveCharacterSection, ...]:
    """Compute every exact simultaneous character space."""

    identity = Matrix.identity(len(basis), scalar_type=Eisenstein)
    sections = []
    for p_character in (Eisenstein(1), OMEGA, OMEGA2):
        for t_character in (Eisenstein(1), OMEGA, OMEGA2):
            equations = Matrix(
                (*((p_action - identity.scale(p_character)).rows),
                 *((t_action - identity.scale(t_character)).rows)),
                scalar_type=Eisenstein,
            )
            vectors = tuple(vector.values for vector in equations.nullspace())
            if not vectors:
                continue
            unit_representative = (
                vectors[0] if len(vectors) == 1 and _is_local_unit(vectors[0], basis, degree)
                else None
            )
            sections.append(
                ProjectiveCharacterSection(
                    p_character,
                    t_character,
                    vectors,
                    unit_representative,
                )
            )
    return tuple(sections)


def projective_serre_section_audit(
    scheme: InvariantMonomialScheme,
) -> ProjectiveSerreSectionAudit:
    """Construct the exact stabilized projective section audit for one scheme."""

    degree = _stabilized_degree(scheme)
    basis = _quotient_basis(scheme, degree)
    p_action = _action_matrix(basis, published_coordinate_images("P"))
    t_action = _action_matrix(basis, published_coordinate_images("T"))
    return ProjectiveSerreSectionAudit(
        scheme,
        degree,
        basis,
        p_action,
        t_action,
        _commutator_scalar(p_action, t_action),
        _character_sections(basis, p_action, t_action, degree),
    )


def tier_b_projective_serre_section_audits(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
) -> tuple[ProjectiveSerreSectionAudit, ...]:
    """Audit projective quotient sections for the bounded monomial family."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    return tuple(projective_serre_section_audit(scheme) for scheme in selected)


__all__ = [
    "ProjectiveCharacterSection",
    "ProjectiveSerreSectionAudit",
    "projective_serre_section_audit",
    "tier_b_projective_serre_section_audits",
]
