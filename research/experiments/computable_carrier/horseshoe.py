"""Construct exact Tier A polynomial horseshoe presentations.

Owns:
    Rank-four two-term polynomial presentations assembled from explicit
    degree-zero projective Hom cocycles, their short exact free-term maps,
    graded shifts, non-boundary checks, and six-chart Fitting diagnostics.

Depends on:
    Tier A projective Hom hypercohomology, exact pushout presentations,
    polynomial free modules and maps, the explicit dP9 chart atlas, and
    deterministic Fitting-unit certificates.

Must not:
    Call a horseshoe presentation a descended bundle, infer equivariance from
    a raw extension class, claim SU(4) Chern data on the Schoen quotient, or
    hide failed local-freeness and invariant-class gates.

Phase 0:
    Exact presentation-level rank-four horseshoes are generated for the
    declared projective ray pairs; quotient descent, stability, spectrum,
    and physical carrier promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import CoordinateVector
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import (
    Polynomial,
    PolynomialChainComplex,
    PolynomialChainMap,
    PolynomialFreeModule,
    PolynomialMap,
    PolynomialMatrix,
)

from .global_serre import (
    FittingUnitCertificate,
    _constant_unit_combination,
)
from .pencil import TierAPencilModel, tier_a_pencil_model
from .polynomial_hom import _presentation_map
from .projective_hom_search import (
    TierAProjectiveHomPairAudit,
    tier_a_projective_hom_pair_audits,
)
from .serre_pushout import SerrePushoutCandidate, _chart_matrix


def _polynomial_record(polynomial: Polynomial) -> dict[str, object]:
    """Serialize one exact polynomial without reducing its basis data."""

    return {
        "terms": [
            {
                "exponents": list(exponents),
                "coefficient": str(coefficient),
            }
            for exponents, coefficient in polynomial.terms
        ]
    }


def _matrix_record(matrix: PolynomialMatrix) -> list[list[dict[str, object]]]:
    """Serialize an exact polynomial matrix entry by entry."""

    return [
        [_polynomial_record(entry) for entry in row]
        for row in matrix.rows
    ]


def _rank_of_vectors(vectors: tuple[CoordinateVector, ...], dimension: int) -> int:
    """Return the exact rank of vectors in one ordered finite basis."""

    if not vectors or dimension == 0:
        return 0
    return Matrix(
        tuple(
            tuple(vector.coordinates[index] for vector in vectors)
            for index in range(dimension)
        ),
        scalar_type=Eisenstein,
    ).rank()


def _presentation_complex(
    candidate: SerrePushoutCandidate,
    prefix: str,
) -> tuple[PolynomialChainComplex, PolynomialMap]:
    """Build the two-term polynomial complex behind one pushout presentation."""

    map_ = _presentation_map(candidate, prefix)
    complex_ = PolynomialChainComplex(
        {0: map_.codomain, 1: map_.domain},
        {1: map_},
    )
    return complex_, map_


def _extension_map(
    audit: TierAProjectiveHomPairAudit,
    representative: CoordinateVector,
) -> PolynomialMatrix:
    """Convert one degree-zero Hom representative into a polynomial map."""

    parent = audit.hypercohomology.parent
    basis = audit.hypercohomology.h0.basis(1)
    if representative.space != audit.hypercohomology.h0.complex.spaces.space(1):
        raise ValueError("horseshoe representatives require projective Hom degree one")
    left_candidate = audit.hypercohomology.parent.left
    right_candidate = audit.hypercohomology.parent.right
    left_target_rank = len(left_candidate.target_shifts)
    right_source_rank = len(right_candidate.source_shifts)
    terms: list[list[list[tuple[tuple[int, ...], Eisenstein]]]] = [
        [[] for _ in range(right_source_rank)]
        for _ in range(left_target_rank)
    ]
    for (generator, monomial), coefficient in zip(
        basis,
        representative.coordinates,
        strict=True,
    ):
        if generator < 0 or generator >= left_target_rank * right_source_rank:
            raise ValueError("Hom representative generator escaped the target basis")
        target = generator // right_source_rank
        source = generator % right_source_rank
        if not coefficient.is_zero():
            terms[target][source].append((monomial, coefficient))
    matrix = PolynomialMatrix(
        tuple(
            tuple(
                Polynomial(
                    entries,
                    variable_count=parent.term(1).variable_count,
                    scalar_type=Eisenstein,
                )
                for entries in row
            )
            for row in terms
        )
    )
    return matrix


def _block_presentation_map(
    left_map: PolynomialMap,
    right_map: PolynomialMap,
    extension_map: PolynomialMatrix,
) -> tuple[PolynomialFreeModule, PolynomialFreeModule, PolynomialMap]:
    """Assemble the horseshoe differential with the extension block."""

    if extension_map.shape != (left_map.codomain.rank, right_map.domain.rank):
        raise ValueError("the extension block has incompatible presentation ranks")
    source = left_map.domain.direct_sum(right_map.domain, "horseshoe F1")
    target = left_map.codomain.direct_sum(right_map.codomain, "horseshoe F0")
    zero = Polynomial.zero(
        left_map.domain.variable_count,
        scalar_type=left_map.domain.scalar_type,
    )
    rows = tuple(
        tuple(left_map.matrix.rows[row]) + tuple(extension_map.rows[row])
        for row in range(left_map.codomain.rank)
    ) + tuple(
        tuple(zero for _ in left_map.domain.basis)
        + tuple(right_map.matrix.rows[row])
        for row in range(right_map.codomain.rank)
    )
    return source, target, PolynomialMap(source, target, PolynomialMatrix(rows))


def _selector_map(
    domain: PolynomialFreeModule,
    codomain: PolynomialFreeModule,
    offset: int,
) -> PolynomialMap:
    """Build an exact inclusion or projection selector between direct sums."""

    if offset < 0 or offset + domain.rank > codomain.rank:
        raise ValueError("selector block lies outside its direct-sum codomain")
    one = Polynomial.one(domain.variable_count, scalar_type=domain.scalar_type)
    zero = Polynomial.zero(domain.variable_count, scalar_type=domain.scalar_type)
    rows = tuple(
        tuple(
            one if row == offset + column else zero
            for column in range(domain.rank)
        )
        for row in range(codomain.rank)
    )
    return PolynomialMap(domain, codomain, PolynomialMatrix(rows))


def _retraction_map(
    domain: PolynomialFreeModule,
    codomain: PolynomialFreeModule,
    offset: int,
) -> PolynomialMap:
    """Build the complementary projection selector between direct sums."""

    if offset < 0 or offset + codomain.rank > domain.rank:
        raise ValueError("retraction block lies outside its direct-sum domain")
    one = Polynomial.one(domain.variable_count, scalar_type=domain.scalar_type)
    zero = Polynomial.zero(domain.variable_count, scalar_type=domain.scalar_type)
    rows = tuple(
        tuple(
            one if column == offset + row else zero
            for column in range(domain.rank)
        )
        for row in range(codomain.rank)
    )
    return PolynomialMap(domain, codomain, PolynomialMatrix(rows))


def _homogeneous(map_: PolynomialMap) -> bool:
    """Check the exact degree condition for every nonzero map entry."""

    return all(
        entry.is_zero()
        or entry.degree == map_.domain.shifts[column][0] - map_.codomain.shifts[row][0]
        for row, row_values in enumerate(map_.matrix.rows)
        for column, entry in enumerate(row_values)
    )


def _horseshoe_fitting_certificate(
    relation: PolynomialMatrix,
    chart,
) -> FittingUnitCertificate:
    """Build a unit certificate from the maximal column-rank minors."""

    local_relation = _chart_matrix(relation, chart)
    minor_size = min(local_relation.shape)
    minors = local_relation.minors(minor_size)
    coefficients = _constant_unit_combination(minors)
    identity = Polynomial.zero(3, scalar_type=Eisenstein)
    for index, coefficient in coefficients:
        identity = identity + coefficient * minors[index]
    return FittingUnitCertificate(chart.name, len(minors), coefficients, identity)


@dataclass(frozen=True, slots=True)
class TierAHorseshoePresentation:
    """One exact rank-four horseshoe presentation for a projective Hom class."""

    audit: TierAProjectiveHomPairAudit
    representative_index: int
    representative: CoordinateVector
    extension_map: PolynomialMatrix
    differential: PolynomialMap
    complex: PolynomialChainComplex
    left_injection: PolynomialChainMap
    right_projection: PolynomialChainMap
    left_retractions: tuple[tuple[int, PolynomialMap], ...]
    right_sections: tuple[tuple[int, PolynomialMap], ...]
    fitting_certificates: tuple[FittingUnitCertificate, ...]
    fitting_failures: tuple[tuple[str, str], ...]

    @property
    def rank(self) -> int:
        """Return the generic rank of the presented cokernel."""

        return self.differential.codomain.rank - self.differential.domain.rank

    @property
    def representative_is_cocycle(self) -> bool:
        """Return whether the source representative is an exact cocycle."""

        image = self.audit.hypercohomology.h0.complex.differential(1)(
            self.representative
        )
        return all(value.is_zero() for value in image.coordinates)

    @property
    def representative_is_nonboundary(self) -> bool:
        """Return whether the representative increases the exact boundary rank."""

        space = self.audit.hypercohomology.h0.complex.spaces.space(1)
        boundaries = self.audit.hypercohomology.h0.complex.boundaries(1)
        return _rank_of_vectors((*boundaries, self.representative), space.dimension) > (
            _rank_of_vectors(boundaries, space.dimension)
        )

    @property
    def short_exact_free_terms(self) -> bool:
        """Return the split exactness identities on both free terms."""

        left_retractions = dict(self.left_retractions)
        right_sections = dict(self.right_sections)
        left_identity = left_retractions[0].compose(
            self.left_injection.component(0)
        )
        left_identity_one = left_retractions[1].compose(
            self.left_injection.component(1)
        )
        right_identity = self.right_projection.component(0).compose(
            right_sections[0]
        )
        right_identity_one = self.right_projection.component(1).compose(
            right_sections[1]
        )
        zero_zero = self.right_projection.component(0).compose(
            self.left_injection.component(0)
        )
        zero_one = self.right_projection.component(1).compose(
            self.left_injection.component(1)
        )
        return (
            left_identity.matrix == PolynomialMap.identity(
                left_identity.domain
            ).matrix
            and left_identity_one.matrix == PolynomialMap.identity(
                left_identity_one.domain
            ).matrix
            and right_identity.matrix == PolynomialMap.identity(
                right_identity.domain
            ).matrix
            and right_identity_one.matrix == PolynomialMap.identity(
                right_identity_one.domain
            ).matrix
            and zero_zero.is_zero()
            and zero_one.is_zero()
        )

    @property
    def homogeneous(self) -> bool:
        """Return whether the horseshoe differential is shift-preserving."""

        return _homogeneous(self.differential)

    @property
    def local_freeness_on_atlas(self) -> bool:
        """Return whether every declared dP9 chart has a unit Fitting cover."""

        return not self.fitting_failures and all(
            certificate.verified for certificate in self.fitting_certificates
        )

    @property
    def determinant_degree(self) -> Rational:
        """Return the exact base-projective determinant degree of the presentation."""

        return Rational(
            sum(shift[0] for shift in self.differential.domain.shifts)
            - sum(shift[0] for shift in self.differential.codomain.shifts)
        )

    @property
    def c2_degree(self) -> Rational:
        """Return the exact base-projective second-Chern degree."""

        ch2 = Rational(
            sum(shift[0] * shift[0] for shift in self.differential.codomain.shifts)
            - sum(shift[0] * shift[0] for shift in self.differential.domain.shifts),
            2,
        )
        return self.determinant_degree * self.determinant_degree / 2 - ch2

    @property
    def presentation_gate(self) -> bool:
        """Return all exact presentation-level gates for this horseshoe."""

        return (
            self.rank == 4
            and self.complex.squared_zero
            and self.homogeneous
            and self.representative_is_cocycle
            and self.representative_is_nonboundary
            and self.short_exact_free_terms
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the horseshoe and preserve its quotient boundary."""

        return {
            "left_scheme": self.audit.left.scheme,
            "right_scheme": self.audit.right.scheme,
            "representative_index": self.representative_index,
            "representative_dimension": self.representative.space.dimension,
            "extension_map": _matrix_record(self.extension_map),
            "differential": {
                "shape": list(self.differential.matrix.shape),
                "matrix": _matrix_record(self.differential.matrix),
            },
            "complex_degrees": list(self.complex.degrees),
            "square_zero": self.complex.squared_zero,
            "rank": self.rank,
            "homogeneous": self.homogeneous,
            "representative_is_cocycle": self.representative_is_cocycle,
            "representative_is_nonboundary": self.representative_is_nonboundary,
            "short_exact_free_terms": self.short_exact_free_terms,
            "presentation_gate": self.presentation_gate,
            "determinant_degree": str(self.determinant_degree),
            "c2_degree": str(self.c2_degree),
            "fitting_cover": [
                certificate.as_record()
                for certificate in self.fitting_certificates
            ],
            "fitting_failures": [
                {"chart": chart, "error": error}
                for chart, error in self.fitting_failures
            ],
            "local_freeness_on_atlas": self.local_freeness_on_atlas,
            "equivariant": False,
            "status": (
                "exact presentation-level rank-four horseshoe; quotient "
                "linearization, descent, stability, spectrum, and physical "
                "promotion remain unresolved"
            ),
        }


def _build_horseshoe(
    audit: TierAProjectiveHomPairAudit,
    representative_index: int,
    model: TierAPencilModel,
) -> TierAHorseshoePresentation:
    """Build one exact horseshoe from one degree-zero H¹ representative."""

    representatives = audit.hypercohomology.h0.representatives(1)
    if representative_index < 0 or representative_index >= len(representatives):
        raise IndexError("horseshoe representative index is outside H¹")
    representative = representatives[representative_index]
    left_complex, left_map = _presentation_complex(
        audit.hypercohomology.parent.left,
        "left",
    )
    right_complex, right_map = _presentation_complex(
        audit.hypercohomology.parent.right,
        "right",
    )
    extension_map = _extension_map(audit, representative)
    source, target, differential = _block_presentation_map(
        left_map,
        right_map,
        extension_map,
    )
    horseshoe_complex = PolynomialChainComplex(
        {0: target, 1: source},
        {1: differential},
    )
    left_inclusion = PolynomialChainMap(
        left_complex,
        horseshoe_complex,
        {
            degree: _selector_map(
                left_complex.module(degree),
                horseshoe_complex.module(degree),
                0,
            )
            for degree in (0, 1)
        },
    )
    right_projection = PolynomialChainMap(
        horseshoe_complex,
        right_complex,
        {
            degree: _retraction_map(
                horseshoe_complex.module(degree),
                right_complex.module(degree),
                left_complex.module(degree).rank,
            )
            for degree in (0, 1)
        },
    )
    left_retractions = tuple(
        (
            degree,
            _retraction_map(
                horseshoe_complex.module(degree),
                left_complex.module(degree),
                0,
            ),
        )
        for degree in (0, 1)
    )
    right_sections = tuple(
        (
            degree,
            _selector_map(
                right_complex.module(degree),
                horseshoe_complex.module(degree),
                left_complex.module(degree).rank,
            ),
        )
        for degree in (0, 1)
    )
    certificates = []
    failures = []
    for chart in model.blowup_atlas.charts:
        try:
            certificates.append(
                _horseshoe_fitting_certificate(differential.matrix, chart)
            )
        except ValueError as error:
            failures.append((chart.name, str(error)))
    return TierAHorseshoePresentation(
        audit,
        representative_index,
        representative,
        extension_map,
        differential,
        horseshoe_complex,
        left_inclusion,
        right_projection,
        left_retractions,
        right_sections,
        tuple(certificates),
        tuple(failures),
    )


def tier_a_horseshoe_presentations(
    audits: tuple[TierAProjectiveHomPairAudit, ...] | None = None,
    model: TierAPencilModel | None = None,
) -> tuple[TierAHorseshoePresentation, ...]:
    """Build every degree-zero projective Tier A horseshoe presentation."""

    selected = tier_a_projective_hom_pair_audits() if audits is None else audits
    current = tier_a_pencil_model() if model is None else model
    return tuple(
        _build_horseshoe(audit, index, current)
        for audit in selected
        for index in range(len(audit.hypercohomology.h0.representatives(1)))
    )


__all__ = [
    "TierAHorseshoePresentation",
    "tier_a_horseshoe_presentations",
]
