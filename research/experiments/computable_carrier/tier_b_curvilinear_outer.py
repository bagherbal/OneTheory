"""Audit presentation-level outer Hom data for curvilinear witnesses.

Owns:
    Exact polynomial Hom complexes and projective-plane hypercohomology for
    the eight diagonal pairs of the declared curvilinear Serre presentations.

Depends on:
    The exact curvilinear Serre witnesses, the reusable polynomial Hom engine,
    projective line-bundle cohomology, and exact polynomial matrix arithmetic.

Must not:
    Call these presentation calculations global Schoen Ext groups, invent a
    constituent linearization, infer an invariant outer class, or promote a
    non-equivariant witness to a descended bundle.

Phase 0:
    The diagonal presentation-pair frontier is exact; exhaustive off-diagonal
    pair enumeration remains a later bounded computation. dP9 sheafification
    comparison, honest equivariant outer classes, stability, and physical
    carrier promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme

from .dp9_homology import DPSurfaceDerivedHom, dp9_derived_hom
from .polynomial_hom import (
    PolynomialHomComplex,
    PresentationCandidate,
    polynomial_hom_complex,
)
from .projective_hyperhom import (
    ProjectiveHomHypercohomology,
    projective_hom_hypercohomology,
)
from .serre_pushout import _quotient_row, _relation_matrix
from .tier_b_curvilinear_serre import (
    TierBCurvilinearSerreAudit,
    tier_b_curvilinear_serre_audits,
)


@dataclass(frozen=True, slots=True)
class CurvilinearPresentationCandidate(PresentationCandidate):
    """One exact research-only presentation extracted from a Serre witness."""

    source_audit: TierBCurvilinearSerreAudit
    scheme: PointScheme
    relation: PolynomialMatrix
    source_shifts: tuple[int, ...]
    target_shifts: tuple[int, ...]
    relation_composes_to_zero: bool

    @classmethod
    def from_audit(
        cls,
        audit: TierBCurvilinearSerreAudit,
    ) -> CurvilinearPresentationCandidate:
        """Build the exact polynomial presentation without assigning physics."""

        scheme = audit.specialization.point_scheme
        relation = _relation_matrix(scheme, audit.extension_map)
        quotient = _quotient_row(scheme)
        quotient_column = PolynomialMatrix(tuple((entry,) for entry in quotient.rows[0]))
        return cls(
            source_audit=audit,
            scheme=scheme,
            relation=relation,
            source_shifts=audit.source_shifts,
            target_shifts=audit.target_shifts,
            relation_composes_to_zero=relation.compose(quotient_column).is_zero(),
        )

    @property
    def exact(self) -> bool:
        """Return the exact presentation gates inherited by this witness."""

        return (
            self.source_audit.exact
            and self.relation_composes_to_zero
            and self.source_audit.graded_relation
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the adapter while preserving its nonphysical scope."""

        return {
            "scheme": self.source_audit.specialization.name,
            "witness_mask": self.source_audit.witness_mask,
            "relation_shape": list(self.relation.shape),
            "source_shifts": list(self.source_shifts),
            "target_shifts": list(self.target_shifts),
            "relation_composes_to_zero": self.relation_composes_to_zero,
            "exact": self.exact,
            "status": (
                "research-only curvilinear presentation adapter; no sheaf-level "
                "linearization or quotient descent is supplied"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearOuterPairAudit:
    """One exact ordered projective Hom audit for two curvilinear witnesses."""

    left: CurvilinearPresentationCandidate
    right: CurvilinearPresentationCandidate
    parent: PolynomialHomComplex
    projective: ProjectiveHomHypercohomology | None
    dp9: DPSurfaceDerivedHom
    parent_squared_zero: bool
    parent_homogeneous: bool
    projective_h0_dimensions: tuple[tuple[int, int], ...]
    projective_h2_dimensions: tuple[tuple[int, int], ...]
    projective_ext1_dimension: int | None
    dp9_h1_dimension: int

    @property
    def exact(self) -> bool:
        """Return all exact presentation and projective square-zero gates."""

        return (
            self.left.exact
            and self.right.exact
            and self.parent_squared_zero
            and self.parent_homogeneous
            and self.dp9.squared_zero
            and self.dp9.all_line_bundles_squared_zero
        )

    @property
    def raw_projective_ext_one_dimension(self) -> int | None:
        """Return the exact projective-presentation degree-one dimension."""

        return self.projective_ext1_dimension

    def as_record(self) -> dict[str, object]:
        """Serialize exact presentation shapes and the unresolved boundary."""

        projective_record = None
        if self.projective is not None:
            projective_record = {
                "h0_derived_dimensions": [
                    list(item) for item in self.projective_h0_dimensions
                ],
                "h2_derived_dimensions": [
                    list(item) for item in self.projective_h2_dimensions
                ],
                "ext1_dimension": self.projective_ext1_dimension,
                "squared_zero": True,
                "status": (
                    "exact projective-presentation hypercohomology summary; full "
                    "cochain objects remain available on the returned audit"
                ),
            }
        parent_record = {
            "left_scheme": self.parent.left.scheme.name,
            "right_scheme": self.parent.right.scheme.name,
            "term_ranks": [[degree, term.rank] for degree, term in self.parent.terms],
            "differential_shapes": [
                [degree, list(map_.matrix.shape)]
                for degree, map_ in self.parent.differentials
            ],
            "squared_zero": self.parent_squared_zero,
            "homogeneous": self.parent_homogeneous,
        }
        return {
            "left": self.left.as_record(),
            "right": self.right.as_record(),
            "parent": parent_record,
            "projective_hypercohomology": projective_record,
            "dP9_totalization": {
                "fiber_degree": self.dp9.fiber_degree,
                "total_degrees": list(self.dp9.total.degrees),
                "total_dimensions": [
                    [degree, self.dp9.total.spaces.space(degree).dimension]
                    for degree in self.dp9.total.degrees
                ],
                "total_h1_dimension": self.dp9_h1_dimension,
                "squared_zero": True,
                "all_line_bundles_squared_zero": True,
                "status": (
                    "exact presentation-level dP9 totalization; global "
                    "sheafification and quotient descent remain unresolved"
                ),
            },
            "raw_projective_ext1_dimension": self.raw_projective_ext_one_dimension,
            "dP9_total_h1_dimension": self.dp9_h1_dimension,
            "exact": self.exact,
            "status": (
                "exact projective-presentation outer audit; dP9 sheafification, "
                "deck-linearized Ext, and quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearOuterFrontier:
    """The exact diagonal-pair frontier for the declared eight witnesses."""

    pair_audits: tuple[TierBCurvilinearOuterPairAudit, ...]
    candidate_count: int
    category: str

    @property
    def complete_for_declared_category(self) -> bool:
        """Return whether every declared diagonal pair was constructed exactly."""

        return len(self.pair_audits) == self.candidate_count

    @property
    def exact(self) -> bool:
        """Return whether every declared diagonal pair passes exact gates."""

        return self.complete_for_declared_category and all(
            audit.exact for audit in self.pair_audits
        )

    @property
    def raw_projective_ext1_total(self) -> int:
        """Return the sum of raw projective degree-one dimensions."""

        return sum(
            dimension
            for audit in self.pair_audits
            if (dimension := audit.raw_projective_ext_one_dimension) is not None
        )

    @property
    def projective_pair_count(self) -> int:
        """Return the number of pairs with materialized hypercohomology."""

        return sum(audit.projective is not None for audit in self.pair_audits)

    @property
    def no_equivariant_candidate_selected(self) -> bool:
        """Return the explicit scope wall inherited from all eight witnesses."""

        return self.exact and all(
            audit.left.source_audit.finite_lift_no_pair
            and audit.right.source_audit.finite_lift_no_pair
            for audit in self.pair_audits
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the full frontier without promoting a candidate."""

        return {
            "category": self.category,
            "candidate_count": self.candidate_count,
            "diagonal_pair_count": len(self.pair_audits),
            "complete_for_declared_category": self.complete_for_declared_category,
            "exact": self.exact,
            "raw_projective_ext1_total": self.raw_projective_ext1_total,
            "projective_pair_count": self.projective_pair_count,
            "no_equivariant_candidate_selected": self.no_equivariant_candidate_selected,
            "pair_audits": [audit.as_record() for audit in self.pair_audits],
            "status": (
                "complete diagonal curvilinear presentation-pair audit only; no "
                "global Ext, invariant projector, or physical carrier is selected"
            ),
        }


@cache
def _cached_frontier(parameter: Eisenstein) -> TierBCurvilinearOuterFrontier:
    """Construct all diagonal pairs for one exact declared specialization."""

    candidates = tuple(
        CurvilinearPresentationCandidate.from_audit(audit)
        for audit in tier_b_curvilinear_serre_audits(parameter)
    )
    audits = []
    for left in candidates:
        parent = polynomial_hom_complex(left, left)
        projective = projective_hom_hypercohomology(parent)
        dp9 = dp9_derived_hom(parent)
        parent_squared_zero = parent.squared_zero
        parent_homogeneous = parent.homogeneous
        h0_dimensions = tuple(
            (degree, projective.h0.complex.cohomology_dimension(degree))
            for degree in projective.h0.complex.degrees
        )
        h2_dimensions = tuple(
            (degree, projective.h2.complex.cohomology_dimension(degree))
            for degree in projective.h2.complex.degrees
        )
        ext_one_dimension = (
            dict(h0_dimensions).get(1, 0)
            + dict(h2_dimensions).get(-1, 0)
        )
        audit = TierBCurvilinearOuterPairAudit(
            left,
            left,
            parent,
            projective,
            dp9,
            parent_squared_zero,
            parent_homogeneous,
            h0_dimensions,
            h2_dimensions,
            ext_one_dimension,
            dp9.total_h1_dimension,
        )
        if not audit.exact:
            raise ValueError("curvilinear outer presentation failed an exact gate")
        audits.append(audit)
    return TierBCurvilinearOuterFrontier(
        tuple(audits),
        len(candidates),
        "all eight diagonal presentation pairs with projective hypercohomology",
    )


def tier_b_curvilinear_outer_frontier(
    parameter: object = Eisenstein(1),
) -> TierBCurvilinearOuterFrontier:
    """Audit every diagonal curvilinear presentation pair exactly once."""

    return _cached_frontier(Eisenstein.coerce(parameter))


__all__ = [
    "CurvilinearPresentationCandidate",
    "TierBCurvilinearOuterFrontier",
    "TierBCurvilinearOuterPairAudit",
    "tier_b_curvilinear_outer_frontier",
]
