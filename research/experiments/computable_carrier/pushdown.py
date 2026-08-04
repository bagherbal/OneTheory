"""Serialize exact dP9 pushdown constraints for Tier A constituents.

Owns:
    Basis-aware projective-line line-bundle cohomology, character-labelled
    direct and higher direct-image summands, and the source-backed W1/W2
    Leray boundary used to constrain the new construction.

Depends on:
    Exact Eisenstein characters and the generic named vector-space engine.
    The formulas are research inputs from the published dP9 architecture.

Must not:
    Treat pushdown dimensions as global bundle construction, invent a
    coboundary map, infer an extension cocycle, or identify this constraint
    with the published carrier.

Phase 0:
    Pushdown constraints and cohomology representatives are serialized; the
    global dP9 atlas, Serre patching, and outer hypercohomology remain open.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from onetheory.math.homological import CoordinateVector, VectorSpace
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

Character = tuple[Eisenstein, Eisenstein]


@dataclass(frozen=True, slots=True)
class P1Summand:
    """One character-labelled line or skyscraper summand on the base."""

    label: str
    character: Character
    degree: int | None = None
    point: str | None = None

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("P1 summands require names")
        if (self.degree is None) == (self.point is None):
            raise ValueError("a summand must be either a line or a skyscraper")

    @property
    def is_skyscraper(self) -> bool:
        """Return whether this summand is supported at a point."""

        return self.point is not None

    def dimension(self, cohomological_degree: int) -> int:
        """Return the exact H^i dimension of the summand on P1."""

        if cohomological_degree not in (0, 1):
            raise ValueError("P1 summands have only H0 and H1")
        if self.is_skyscraper:
            return 1 if cohomological_degree == 0 else 0
        assert self.degree is not None
        if cohomological_degree == 0:
            return self.degree + 1 if self.degree >= 0 else 0
        return -self.degree - 1 if self.degree <= -2 else 0

    def basis(self, cohomological_degree: int) -> tuple[str, ...]:
        """Return deterministic monomial or Serre-dual basis labels."""

        dimension = self.dimension(cohomological_degree)
        if self.is_skyscraper:
            return (f"{self.label}:delta",) if dimension else ()
        assert self.degree is not None
        if cohomological_degree == 0:
            return tuple(
                f"{self.label}:s^{index}t^{self.degree - index}"
                for index in range(self.degree + 1)
            ) if dimension else ()
        return tuple(f"{self.label}:h1:{index}" for index in range(dimension))


@dataclass(frozen=True, slots=True)
class P1PushdownConstraint:
    """Direct-image data with exact Leray cohomology spaces."""

    name: str
    direct_terms: tuple[P1Summand, ...]
    higher_terms: tuple[P1Summand, ...]
    coboundary_status: str
    source_equations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.source_equations:
            raise ValueError("pushdown constraints require a name and provenance")
        if self.coboundary_status not in {"isomorphism", "zero"}:
            raise ValueError("pushdown coboundary status must be explicit")

    def basis(self, degree: int) -> tuple[str, ...]:
        """Return the exact Leray basis in one total cohomological degree."""

        if degree not in (0, 1, 2):
            raise ValueError("pushdown cohomology degrees are 0, 1, and 2")
        labels: list[str] = []
        if degree in (0, 1):
            labels.extend(
                label
                for summand in self.direct_terms
                for label in summand.basis(degree)
            )
        if degree in (1, 2):
            labels.extend(
                label
                for summand in self.higher_terms
                for label in summand.basis(degree - 1)
            )
        return tuple(labels)

    def space(self, degree: int) -> VectorSpace:
        """Return the named exact cohomology space in one degree."""

        return VectorSpace(f"{self.name}:H^{degree}", self.basis(degree), Eisenstein)

    def representatives(self, degree: int) -> tuple[CoordinateVector, ...]:
        """Return standard exact representatives for the displayed basis."""

        space = self.space(degree)
        return tuple(
            CoordinateVector(
                space,
                tuple(
                    Eisenstein(1) if index == basis_index else Eisenstein(0)
                    for index in range(space.dimension)
                ),
            )
            for basis_index in range(space.dimension)
        )

    def dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact total cohomology dimensions."""

        return tuple((degree, self.space(degree).dimension) for degree in range(3))

    def character_multiplicities(self, degree: int) -> tuple[tuple[Character, int], ...]:
        """Return character multiplicities in one exact Leray degree."""

        terms: list[Character] = []
        if degree in (0, 1):
            terms.extend(
                summand.character
                for summand in self.direct_terms
                for _ in summand.basis(degree)
            )
        if degree in (1, 2):
            terms.extend(
                summand.character
                for summand in self.higher_terms
                for _ in summand.basis(degree - 1)
            )
        counts = Counter(terms)
        return tuple(sorted(counts.items(), key=lambda item: str(item[0])))

    def as_record(self) -> dict[str, object]:
        """Serialize the source-backed constraint without a bundle claim."""

        def summand_record(summand: P1Summand) -> dict[str, object]:
            return {
                "label": summand.label,
                "character": [str(value) for value in summand.character],
                "degree": summand.degree,
                "point": summand.point,
            }

        return {
            "name": self.name,
            "direct_terms": [summand_record(item) for item in self.direct_terms],
            "higher_terms": [summand_record(item) for item in self.higher_terms],
            "coboundary_status": self.coboundary_status,
            "cohomology_dimensions": [list(item) for item in self.dimensions()],
            "cohomology_bases": [
                [degree, list(self.basis(degree))]
                for degree in range(3)
            ],
            "character_multiplicities": [
                [
                    degree,
                    [
                        [
                            [str(value) for value in character],
                            multiplicity,
                        ]
                        for character, multiplicity in self.character_multiplicities(degree)
                    ],
                ]
                for degree in range(3)
            ],
            "source_equations": list(self.source_equations),
            "status": "source-backed pushdown constraint; global bundle pending",
        }


def tier_a_pushdown_constraints() -> tuple[P1PushdownConstraint, ...]:
    """Return the exact source-backed W1/W2 pushdown constraints."""

    one = Eisenstein(1)
    return (
        P1PushdownConstraint(
            "W1 pushdown constraint",
            (P1Summand("chi1 O(-1)", (OMEGA, one), degree=-1),),
            (P1Summand("O", (one, one), degree=0),),
            "isomorphism",
            ("hep-th/0602073 eq. (60)", "hep-th/0602073 eq. (62)"),
        ),
        P1PushdownConstraint(
            "W2 pushdown constraint",
            (
                P1Summand("chi2^2 O(-1)", (one, OMEGA2), degree=-1),
                P1Summand("chi2 O(-2)", (one, OMEGA), degree=-2),
            ),
            (
                P1Summand("chi2^2 O(1)", (one, OMEGA2), degree=1),
                P1Summand("chi2 O", (one, OMEGA), degree=0),
            ),
            "zero",
            ("hep-th/0602073 eq. (63)",),
        ),
    )


__all__ = ["P1PushdownConstraint", "P1Summand", "tier_a_pushdown_constraints"]
