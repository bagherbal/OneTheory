"""Compute projective-presentation hypercohomology for Tier A Hom data.

Owns:
    Exact H0 and H2 monomial bases for projective-plane line bundles, the
    induced maps of the three-term polynomial Hom presentation, and explicit
    cohomology representatives in the resulting finite complexes.

Depends on:
    The exact presentation-level Hom complex and generic Eisenstein linear
    algebra. The calculation uses only the projective-plane line-bundle
    cohomology formula.

Must not:
    Call projective-presentation hypercohomology the final dP9 Ext group,
    infer a quotient invariant class, or omit the comparison with the
    six-chart blow-up sheafification.

Phase 0:
    The projective pullback calculation is exact and finite; the dP9
    sheafification, deck action, and quotient descent remain open gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.math.homological import (
    CochainComplex,
    CoordinateVector,
    GradedVectorSpace,
    LinearMap,
    VectorSpace,
)

from .polynomial_hom import PolynomialHomComplex, tier_a_polynomial_hom_complex

Monomial = tuple[int, ...]
BasisLabel = tuple[int, Monomial]


def _vector_record(vector: CoordinateVector) -> dict[str, object]:
    """Serialize one based exact vector without losing zero coordinates."""

    return {
        "space": vector.space.name,
        "dimension": vector.space.dimension,
        "coordinates": [
            {
                "index": index,
                "basis": vector.space.basis[index],
                "coefficient": str(value),
            }
            for index, value in enumerate(vector.coordinates)
            if not value.is_zero()
        ],
    }


def _sparse_matrix_record(
    rows: tuple[tuple[object, ...], ...],
    column_count: int,
) -> dict[str, object]:
    """Serialize an exact matrix by shape and nonzero entries."""

    return {
        "shape": [len(rows), column_count],
        "entries": [
            {
                "row": row,
                "column": column,
                "coefficient": str(value),
            }
            for row, values in enumerate(rows)
            for column, value in enumerate(values)
            if not value.is_zero()
        ],
    }


def _complex_record(complex_: CochainComplex) -> dict[str, object]:
    """Serialize spaces, differentials, cycles, boundaries, and representatives."""

    return {
        "direction": complex_.direction,
        "degrees": list(complex_.degrees),
        "spaces": [
            {
                "degree": degree,
                "name": complex_.spaces.space(degree).name,
                "basis": list(complex_.spaces.space(degree).basis),
            }
            for degree in complex_.degrees
        ],
        "differentials": [
            {
                "degree": degree,
                "domain": list(differential.domain.basis),
                "codomain": list(differential.codomain.basis),
                "matrix": _sparse_matrix_record(
                    differential.rows,
                    differential.domain.dimension,
                ),
            }
            for degree, differential in complex_.differentials
        ],
        "squared_zero": all(
            complex_.differential(degree + 1).compose(
                complex_.differential(degree)
            ).is_zero()
            for degree in complex_.degrees
        ),
        "cohomology": [
            {
                "degree": degree,
                "dimension": complex_.cohomology_dimension(degree),
                "cycles": [_vector_record(vector) for vector in complex_.cycles(degree)],
                "boundaries": [
                    _vector_record(vector) for vector in complex_.boundaries(degree)
                ],
                "representatives": [
                    _vector_record(vector)
                    for vector in complex_.cohomology_representatives(degree)
                ],
            }
            for degree in complex_.degrees
        ],
    }


def _h0_basis(degree: int, variable_count: int) -> tuple[Monomial, ...]:
    """Return the monomial basis of H0(P^2,O(degree))."""

    if degree < 0:
        return ()
    return tuple(
        exponents
        for exponents in product(range(degree + 1), repeat=variable_count)
        if sum(exponents) == degree
    )


def _h2_basis(degree: int, variable_count: int) -> tuple[Monomial, ...]:
    """Return the Serre-dual monomial basis of H2(P^2,O(degree))."""

    if degree > -variable_count:
        return ()
    return tuple(
        exponents
        for exponents in product(range(degree, 0), repeat=variable_count)
        if sum(exponents) == degree
    )


def _line_basis(degree: int, cohomology_degree: int, variable_count: int) -> tuple[Monomial, ...]:
    """Return the exact nonzero H^i basis of one projective line bundle."""

    if cohomology_degree == 0:
        return _h0_basis(degree, variable_count)
    if cohomology_degree == 2:
        return _h2_basis(degree, variable_count)
    raise ValueError("projective-plane line bundles have only H0 and H2 here")


def _component_basis(
    module,
    cohomology_degree: int,
) -> tuple[BasisLabel, ...]:
    """Expand shifted free generators into their line-cohomology bases."""

    return tuple(
        (generator, monomial)
        for generator, shift in enumerate(module.shifts)
        for monomial in _line_basis(-shift[0], cohomology_degree, module.variable_count)
    )


def _cohomology_map(
    source_basis: tuple[BasisLabel, ...],
    target_basis: tuple[BasisLabel, ...],
    source_space: VectorSpace,
    target_space: VectorSpace,
    polynomial_map,
    cohomology_degree: int,
) -> LinearMap:
    """Evaluate one polynomial map on H0 or H2 monomial representatives."""

    target_index = {label: index for index, label in enumerate(target_basis)}
    target_monomials = {
        generator: tuple(
            monomial
            for basis_generator, monomial in target_basis
            if basis_generator == generator
        )
        for generator in range(polynomial_map.codomain.rank)
    }
    zero = polynomial_map.domain.scalar_type(0)
    rows = [[zero for _ in source_basis] for _ in target_basis]
    for source_position, (source_generator, source_monomial) in enumerate(source_basis):
        for target_generator in range(polynomial_map.codomain.rank):
            entry = polynomial_map.matrix.rows[target_generator][source_generator]
            for exponent, coefficient in entry.terms:
                image = tuple(
                    source_value + entry_value
                    for source_value, entry_value in zip(
                        source_monomial,
                        exponent,
                        strict=True,
                    )
                )
                if cohomology_degree == 2 and any(value >= 0 for value in image):
                    continue
                if image not in target_monomials[target_generator]:
                    continue
                rows[target_index[(target_generator, image)]][source_position] += coefficient
    return LinearMap(source_space, target_space, rows)


@dataclass(frozen=True, slots=True)
class ProjectiveHomCohomology:
    """One exact projective-plane cohomology complex of the presentation Hom."""

    parent: PolynomialHomComplex
    sheaf_cohomology_degree: int
    complex: CochainComplex
    bases: tuple[tuple[int, tuple[BasisLabel, ...]], ...]

    def __post_init__(self) -> None:
        if self.sheaf_cohomology_degree not in (0, 2):
            raise ValueError("projective Hom cohomology degrees must be 0 or 2")

    def basis(self, cochain_degree: int) -> tuple[BasisLabel, ...]:
        """Return the exact basis in one derived-Hom degree."""

        return dict(self.bases)[cochain_degree]

    def representatives(self, cochain_degree: int) -> tuple[CoordinateVector, ...]:
        """Return exact representatives for one derived-Hom cohomology."""

        return self.complex.cohomology_representatives(cochain_degree)

    def as_record(self) -> dict[str, object]:
        """Serialize the full finite projective cochain complex."""

        return {
            "sheaf_cohomology_degree": self.sheaf_cohomology_degree,
            "bases": [
                {
                    "degree": degree,
                    "basis": [
                        {
                            "generator": generator,
                            "monomial": list(monomial),
                        }
                        for generator, monomial in basis
                    ],
                }
                for degree, basis in self.bases
            ],
            "complex": _complex_record(self.complex),
        }


@dataclass(frozen=True, slots=True)
class ProjectiveHomHypercohomology:
    """The finite projective hypercohomology audit of one Hom presentation."""

    parent: PolynomialHomComplex
    h0: ProjectiveHomCohomology
    h2: ProjectiveHomCohomology

    @property
    def ext_one_dimension(self) -> int:
        """Return the projective hypercohomology degree-one dimension."""

        return (
            self.h0.complex.cohomology_dimension(1)
            + self.h2.complex.cohomology_dimension(-1)
        )

    @property
    def ext_one_representatives(self) -> tuple[tuple[str, CoordinateVector], ...]:
        """Return explicit representatives contributing to hypercohomology one."""

        return tuple(
            ("H0", representative)
            for representative in self.h0.representatives(1)
        ) + tuple(
            ("H2", representative)
            for representative in self.h2.representatives(-1)
        )

    @staticmethod
    def _sparse_record(
        label: str,
        vector: CoordinateVector,
    ) -> dict[str, object]:
        """Serialize only nonzero coordinates of one exact representative."""

        return {
            "sheaf_cohomology": label,
            "coordinates": [
                {"basis": str(basis), "coefficient": str(coefficient)}
                for basis, coefficient in zip(
                    vector.space.basis,
                    vector.coordinates,
                    strict=True,
                )
                if not coefficient.is_zero()
            ],
        }

    def as_record(self) -> dict[str, object]:
        """Serialize dimensions, exact maps, and sparse representatives."""

        return {
            "left_scheme": self.parent.left.scheme.name,
            "right_scheme": self.parent.right.scheme.name,
            "h0_derived_dimensions": [
                [degree, self.h0.complex.cohomology_dimension(degree)]
                for degree in self.h0.complex.degrees
            ],
            "h2_derived_dimensions": [
                [degree, self.h2.complex.cohomology_dimension(degree)]
                for degree in self.h2.complex.degrees
            ],
            "ext1_dimension": self.ext_one_dimension,
            "ext1_representative_count": len(self.ext_one_representatives),
            "ext1_representatives": [
                self._sparse_record(label, representative)
                for label, representative in self.ext_one_representatives
            ],
            "h0": self.h0.as_record(),
            "h2": self.h2.as_record(),
            "squared_zero": all(
                complex_.differential(degree + 1).compose(
                    complex_.differential(degree)
                ).is_zero()
                for complex_ in (self.h0.complex, self.h2.complex)
                for degree in (-1, 0)
            ),
            "status": (
                "exact projective-presentation hypercohomology; comparison with "
                "the dP9 sheafification, deck action, and quotient descent remains unresolved"
            ),
        }


def _build_projective_complex(
    parent: PolynomialHomComplex,
    cohomology_degree: int,
) -> ProjectiveHomCohomology:
    """Build one H0 or H2 derived-Hom complex exactly."""

    bases = {
        degree: _component_basis(module, cohomology_degree)
        for degree, module in parent.terms
    }
    spaces = {
        degree: VectorSpace(
            f"projective Hom H^{cohomology_degree}^{degree}",
            tuple(str(label) for label in basis),
            parent.term(degree).scalar_type,
        )
        for degree, basis in bases.items()
    }
    graded = GradedVectorSpace(
        f"projective Hom H^{cohomology_degree}",
        spaces,
    )
    differentials = {
        degree: _cohomology_map(
            bases[degree],
            bases[degree + 1],
            spaces[degree],
            spaces[degree + 1],
            polynomial_map,
            cohomology_degree,
        )
        for degree, polynomial_map in parent.differentials
    }
    return ProjectiveHomCohomology(
        parent,
        cohomology_degree,
        CochainComplex(graded, differentials),
        tuple(sorted(bases.items())),
    )


def projective_hom_hypercohomology(
    parent: PolynomialHomComplex,
) -> ProjectiveHomHypercohomology:
    """Compute both line-cohomology components of the Hom hypercomplex."""

    return ProjectiveHomHypercohomology(
        parent,
        _build_projective_complex(parent, 0),
        _build_projective_complex(parent, 2),
    )


def tier_a_projective_hom_hypercohomology() -> ProjectiveHomHypercohomology:
    """Build the Tier A projective-presentation hypercohomology audit."""

    return projective_hom_hypercohomology(tier_a_polynomial_hom_complex())


__all__ = [
    "ProjectiveHomCohomology",
    "ProjectiveHomHypercohomology",
    "projective_hom_hypercohomology",
    "tier_a_projective_hom_hypercohomology",
]
