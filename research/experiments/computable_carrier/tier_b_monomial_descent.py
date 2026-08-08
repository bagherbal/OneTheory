"""Certify the surviving length-six monomial constituent sheaves.

Owns:
    Exact affine Fitting-unit identities, graded projective cocycles, Chern
    data, and conditional free-quotient descent for every surviving length-six
    Serre eigenray in the invariant monomial Tier B frontier.

Depends on:
    Exact monomial Hilbert--Burch resolutions, their graded Serre eigenrays,
    the published dP9 deck atlas, Schoen quotient data, and the topology-first
    twist screen.

Must not:
    Select a physical constituent, construct the rank-four outer extension,
    infer stability or spectrum, generalize beyond the declared monomial
    schemes, or replace independent external verification.

Phase 0:
    Internal exact constituent descent is certified; outer Ext, stability,
    spectrum, and physical promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import PointScheme

from .dp9_deck_atlas import DP9DeckAtlasAudit, dp9_deck_atlas_audit
from .pencil import _pivot_images
from .pushout_linearization import _middle_action
from .serre_pushout import _relation_matrix
from .tier_b_curvilinear_projective_cocycles import (
    _central_relation_equation,
    _coordinate_matrix,
    _degree_central_action,
)
from .tier_b_linearization import _relation_compatible
from .tier_b_monomial import (
    MonomialResolutionActionAudit,
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)
from .tier_b_monomial_topology import tier_b_monomial_topology_screen
from .tier_b_serre_extensions import (
    TierBSerreExtensionRay,
    tier_b_serre_eigenrays,
)

ExactCombination = tuple[tuple[int, Polynomial], ...]


def _polynomial_record(polynomial: Polynomial) -> dict[str, object]:
    """Serialize one exact sparse polynomial without numerical conversion."""

    return {
        "terms": [
            {
                "exponents": list(exponents),
                "coefficient": str(coefficient),
            }
            for exponents, coefficient in polynomial.terms
        ]
    }


def _monomial_quotient(
    dividend: Polynomial,
    divisor: Polynomial,
) -> Polynomial | None:
    """Divide exactly by one monomial, returning no result on a remainder."""

    if len(divisor.terms) != 1:
        return None
    divisor_exponents, divisor_coefficient = divisor.terms[0]
    quotient_terms = []
    for exponents, coefficient in dividend.terms:
        quotient_exponents = tuple(
            left - right
            for left, right in zip(exponents, divisor_exponents, strict=True)
        )
        if min(quotient_exponents) < 0:
            return None
        quotient_terms.append(
            (quotient_exponents, coefficient / divisor_coefficient)
        )
    return Polynomial(
        quotient_terms,
        variable_count=dividend.variable_count,
        scalar_type=Eisenstein,
    )


def _two_minor_unit_combination(
    generators: tuple[Polynomial, ...],
) -> ExactCombination:
    """Find the smallest exact constant-plus-monomial unit identity."""

    if not generators:
        raise ValueError("a Fitting certificate requires maximal minors")
    variable_count = generators[0].variable_count
    if any(
        generator.variable_count != variable_count
        or generator.scalar_type is not Eisenstein
        for generator in generators
    ):
        raise ValueError("Fitting minors must share one Eisenstein ring")
    zero_exponents = (0,) * variable_count
    zero = Polynomial.zero(variable_count, scalar_type=Eisenstein)
    one = Polynomial.one(variable_count, scalar_type=Eisenstein)
    candidates: list[ExactCombination] = []
    for constant_index, generator in enumerate(generators):
        constant = generator.coefficient(zero_exponents)
        if constant.is_zero():
            continue
        inverse = Eisenstein(1) / constant
        remainder = generator - Polynomial.constant(
            constant,
            variable_count,
            scalar_type=Eisenstein,
        )
        if remainder.is_zero():
            candidates.append(
                (
                    (
                        constant_index,
                        Polynomial.constant(
                            inverse,
                            variable_count,
                            scalar_type=Eisenstein,
                        ),
                    ),
                )
            )
            continue
        for monomial_index, monomial in enumerate(generators):
            if monomial_index == constant_index or monomial.is_zero():
                continue
            quotient = _monomial_quotient(remainder, monomial)
            if quotient is None:
                continue
            combination = (
                (
                    constant_index,
                    Polynomial.constant(
                        inverse,
                        variable_count,
                        scalar_type=Eisenstein,
                    ),
                ),
                (monomial_index, quotient.scale(-inverse)),
            )
            identity = zero
            for index, coefficient in combination:
                identity += coefficient * generators[index]
            if identity == one:
                candidates.append(combination)
    if not candidates:
        raise ValueError(
            "maximal minors have no constant-plus-monomial unit certificate"
        )
    return min(
        candidates,
        key=lambda combination: (
            max(coefficient.degree for _, coefficient in combination),
            len(combination),
            tuple(index for index, _ in combination),
        ),
    )


@dataclass(frozen=True, slots=True)
class MonomialFittingCertificate:
    """One displayed affine unit identity among the maximal minors."""

    base_pivot: int
    minor_count: int
    nonzero_minor_count: int
    coefficients: ExactCombination
    identity: Polynomial

    @property
    def coefficient_degree_bound(self) -> int:
        """Return the largest total degree used by the displayed coefficients."""

        return max(coefficient.degree for _, coefficient in self.coefficients)

    @property
    def exact(self) -> bool:
        """Return whether the displayed combination is exactly one."""

        return self.identity == Polynomial.one(2, scalar_type=Eisenstein)

    def as_record(self) -> dict[str, object]:
        """Serialize the exact affine identity and its six-chart coverage."""

        return {
            "base_pivot": self.base_pivot,
            "dp9_charts": [
                f"U_{self.base_pivot}_mu",
                f"U_{self.base_pivot}_nu",
            ],
            "minor_count": self.minor_count,
            "nonzero_minor_count": self.nonzero_minor_count,
            "coefficient_degree_bound": self.coefficient_degree_bound,
            "coefficients": [
                {
                    "minor_index": index,
                    "coefficient": _polynomial_record(coefficient),
                }
                for index, coefficient in self.coefficients
            ],
            "identity": _polynomial_record(self.identity),
            "exact": self.exact,
        }


def _fitting_certificates(
    relation: PolynomialMatrix,
) -> tuple[MonomialFittingCertificate, ...]:
    """Prove that maximal minors generate one on every projective chart."""

    minors = relation.minors(relation.shape[0])
    result = []
    for pivot in range(3):
        affine_minors = tuple(
            minor.substitute(_pivot_images(pivot)) for minor in minors
        )
        coefficients = _two_minor_unit_combination(affine_minors)
        identity = Polynomial.zero(2, scalar_type=Eisenstein)
        for index, coefficient in coefficients:
            identity += coefficient * affine_minors[index]
        result.append(
            MonomialFittingCertificate(
                pivot,
                len(affine_minors),
                sum(not minor.is_zero() for minor in affine_minors),
                coefficients,
                identity,
            )
        )
    return tuple(result)


@dataclass(frozen=True, slots=True)
class MonomialProjectiveCocycleAudit:
    """Exact graded presentation cocycle for one length-six eigenray."""

    relation_equations: tuple[bool, bool]
    relation_order_three: tuple[bool, bool]
    middle_order_three: tuple[bool, bool]
    central_relation_equation: bool
    central_grading_preserved: bool
    source_cocycle: bool
    target_cocycle: bool
    middle_cocycle: bool
    coordinate_lift_commutator: bool

    @property
    def exact(self) -> bool:
        """Return whether every graded projective-cocycle identity holds."""

        return (
            all(self.relation_equations)
            and all(self.relation_order_three)
            and all(self.middle_order_three)
            and self.central_relation_equation
            and self.central_grading_preserved
            and self.source_cocycle
            and self.target_cocycle
            and self.middle_cocycle
            and self.coordinate_lift_commutator
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact cocycle without claiming physical selection."""

        return {
            "relation_equations": list(self.relation_equations),
            "relation_order_three": list(self.relation_order_three),
            "middle_order_three": list(self.middle_order_three),
            "central_relation_equation": self.central_relation_equation,
            "central_grading_preserved": self.central_grading_preserved,
            "source_cocycle": self.source_cocycle,
            "target_cocycle": self.target_cocycle,
            "middle_cocycle": self.middle_cocycle,
            "coordinate_lift_commutator": self.coordinate_lift_commutator,
            "exact": self.exact,
        }


def _projective_cocycle(
    relation: PolynomialMatrix,
    ray: TierBSerreExtensionRay,
    resolution_audit: MonomialResolutionActionAudit,
) -> MonomialProjectiveCocycleAudit:
    """Check the degree-dependent central cocycle for one exact ray."""

    actions = tuple(
        resolution_audit.actions.action(name) for name in ("P", "T")
    )
    middle_actions = tuple(
        _middle_action(action, character)
        for action, character in zip(actions, ray.character_pair, strict=True)
    )
    relation_actions = tuple(
        action.source_action.transpose() for action in actions
    )
    source_identity = Matrix.identity(
        relation_actions[0].row_count,
        scalar_type=Eisenstein,
    )
    middle_identity = Matrix.identity(
        middle_actions[0].row_count,
        scalar_type=Eisenstein,
    )
    source_central = _degree_central_action(ray.cokernel.syzygy_degrees)
    target_central = _degree_central_action(ray.cokernel.generator_degrees)
    middle_central = _degree_central_action(
        (
            *ray.cokernel.generator_degrees,
            ray.cokernel.target_line_shift,
        )
    )
    p_action, t_action = actions
    p_middle, t_middle = middle_actions
    p_coordinates = _coordinate_matrix("P")
    t_coordinates = _coordinate_matrix("T")
    return MonomialProjectiveCocycleAudit(
        tuple(
            _relation_compatible(relation, action, character)
            for action, character in zip(
                actions,
                ray.character_pair,
                strict=True,
            )
        ),
        tuple(action**3 == source_identity for action in relation_actions),
        tuple(action**3 == middle_identity for action in middle_actions),
        _central_relation_equation(
            relation,
            ray.cokernel.syzygy_degrees,
            (
                *ray.cokernel.generator_degrees,
                ray.cokernel.target_line_shift,
            ),
        ),
        all(
            action @ middle_central == middle_central @ action
            for action in middle_actions
        ),
        p_action.source_action @ t_action.source_action
        == source_central.inverse()
        @ (t_action.source_action @ p_action.source_action),
        p_action.target_action @ t_action.target_action
        == target_central.inverse()
        @ (t_action.target_action @ p_action.target_action),
        p_middle @ t_middle == middle_central @ (t_middle @ p_middle),
        p_coordinates @ t_coordinates
        == (t_coordinates @ p_coordinates).scale(OMEGA),
    )


def _chern_data(
    source_shifts: tuple[int, ...],
    target_shifts: tuple[int, ...],
) -> tuple[int, int, Rational]:
    """Return exact rank, first Chern degree, and second Chern degree."""

    rank = len(target_shifts) - len(source_shifts)
    first_chern = sum(source_shifts) - sum(target_shifts)
    ch_two = Rational(
        sum(shift * shift for shift in target_shifts)
        - sum(shift * shift for shift in source_shifts),
        2,
    )
    second_chern = Rational(first_chern * first_chern, 2) - ch_two
    return rank, first_chern, second_chern


@dataclass(frozen=True, slots=True)
class MonomialConstituentDescentLine:
    """Internal descent certificate for one surviving rank-two eigenray."""

    scheme: str
    target_line_shift: int
    character_pair: tuple[Eisenstein, Eisenstein]
    source_shifts: tuple[int, ...]
    target_shifts: tuple[int, ...]
    rank: int
    first_chern_hyperplane: int
    second_chern_hyperplane_squared: Rational
    fitting_certificates: tuple[MonomialFittingCertificate, ...]
    projective_cocycle: MonomialProjectiveCocycleAudit
    dp9_deck_atlas_verified: bool
    determinant_linearizable: bool
    schoen_action_free: bool
    quotient_order: int

    @property
    def locally_free_sheaf_verified(self) -> bool:
        """Return whether the full maximal-minor cover has rank two."""

        return (
            self.rank == 2
            and len(self.fitting_certificates) == 3
            and all(
                certificate.minor_count == 10
                and certificate.nonzero_minor_count == 10
                and certificate.exact
                for certificate in self.fitting_certificates
            )
        )

    @property
    def equivariant_dp9_pullback_verified(self) -> bool:
        """Return whether equivariant pullback to the dP9 atlas is certified."""

        return (
            self.locally_free_sheaf_verified
            and self.projective_cocycle.exact
            and self.dp9_deck_atlas_verified
            and self.determinant_linearizable
        )

    @property
    def internal_descent_certificate(self) -> bool:
        """Apply equivariant descent along the published free finite quotient."""

        return (
            self.equivariant_dp9_pullback_verified
            and self.schoen_action_free
            and self.quotient_order == 9
        )

    @property
    def exact(self) -> bool:
        """Return whether every internal constituent gate is exact."""

        return (
            self.second_chern_hyperplane_squared == Rational(6)
            and self.internal_descent_certificate
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one descended candidate without physical promotion."""

        return {
            "scheme": self.scheme,
            "target_line_shift": self.target_line_shift,
            "character_pair": [str(value) for value in self.character_pair],
            "source_shifts": list(self.source_shifts),
            "target_shifts": list(self.target_shifts),
            "rank": self.rank,
            "chern_character": {
                "c1_hyperplane": self.first_chern_hyperplane,
                "c2_hyperplane_squared": str(
                    self.second_chern_hyperplane_squared
                ),
            },
            "fitting_certificates": [
                certificate.as_record()
                for certificate in self.fitting_certificates
            ],
            "locally_free_sheaf_verified": self.locally_free_sheaf_verified,
            "projective_cocycle": self.projective_cocycle.as_record(),
            "dp9_deck_atlas_verified": self.dp9_deck_atlas_verified,
            "determinant_linearizable": self.determinant_linearizable,
            "equivariant_dp9_pullback_verified": (
                self.equivariant_dp9_pullback_verified
            ),
            "schoen_action_free": self.schoen_action_free,
            "quotient_order": self.quotient_order,
            "internal_descent_certificate": self.internal_descent_certificate,
            "descent_theorem": (
                "equivariant locally free sheaves descend along a free finite "
                "group quotient"
            ),
            "independent_external_constituent_certificate": False,
            "selected_as_physics": False,
            "promotion_ready": False,
            "exact": self.exact,
            "status": (
                "internally certified rank-two constituent; independent result "
                "is tracked by the external artifact, while outer extension "
                "and physical selection remain unresolved"
            ),
        }


def _point_scheme(ray: TierBSerreExtensionRay) -> PointScheme:
    """Return the production point-scheme wrapper for one research ray."""

    scheme = ray.cokernel.scheme
    return PointScheme(
        scheme.name,
        tuple(scheme.ideal.generators),
        scheme.resolution,
    )


def _line_audit(
    ray: TierBSerreExtensionRay,
    resolution_audit: MonomialResolutionActionAudit,
    deck_atlas: DP9DeckAtlasAudit,
) -> MonomialConstituentDescentLine:
    """Build every exact sheaf and descent gate for one eigenray."""

    relation = _relation_matrix(_point_scheme(ray), ray.extension_map)
    source_shifts = ray.cokernel.syzygy_degrees
    target_shifts = (
        *ray.cokernel.generator_degrees,
        ray.cokernel.target_line_shift,
    )
    rank, first_chern, second_chern = _chern_data(
        source_shifts,
        target_shifts,
    )
    geometry = schoen_geometry()
    return MonomialConstituentDescentLine(
        ray.cokernel.scheme.name,
        ray.cokernel.target_line_shift,
        ray.character_pair,
        source_shifts,
        target_shifts,
        rank,
        first_chern,
        second_chern,
        _fitting_certificates(relation),
        _projective_cocycle(relation, ray, resolution_audit),
        deck_atlas.exact,
        first_chern % geometry.descent_modulus == 0,
        geometry.quotient.acts_freely,
        geometry.quotient.order,
    )


@dataclass(frozen=True, slots=True)
class TierBMonomialConstituentDescentFrontier:
    """Complete descended-constituent frontier for surviving monomial rays."""

    lines: tuple[MonomialConstituentDescentLine, ...]
    surviving_topology_candidate_count: int
    surviving_presentation_pair_count: int
    all_surviving_line_twists_descend: bool

    @property
    def descended_constituent_count(self) -> int:
        """Count individual eigenrays passing every descent gate."""

        return sum(line.internal_descent_certificate for line in self.lines)

    @property
    def descended_presentation_pair_count(self) -> int:
        """Count topology/ray pairs whose two constituents descend."""

        if (
            self.descended_constituent_count != len(self.lines)
            or not self.all_surviving_line_twists_descend
        ):
            return 0
        return self.surviving_presentation_pair_count

    @property
    def exact(self) -> bool:
        """Return whether the declared constituent frontier is complete."""

        return (
            len(self.lines) == 12
            and self.descended_constituent_count == 12
            and self.surviving_topology_candidate_count == 40
            and self.surviving_presentation_pair_count == 1440
            and self.descended_presentation_pair_count == 1440
            and all(line.exact for line in self.lines)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the constituent gate and preserve the outer-Ext wall."""

        return {
            "category": (
                "surviving length-six invariant coordinate-supported monomial "
                "Serre eigenrays"
            ),
            "constituent_count": len(self.lines),
            "descended_constituent_count": self.descended_constituent_count,
            "lines": [line.as_record() for line in self.lines],
            "surviving_topology_candidate_count": (
                self.surviving_topology_candidate_count
            ),
            "surviving_presentation_pair_count": (
                self.surviving_presentation_pair_count
            ),
            "all_surviving_line_twists_descend": (
                self.all_surviving_line_twists_descend
            ),
            "descended_presentation_pair_count": (
                self.descended_presentation_pair_count
            ),
            "outer_ext_computation_available": self.exact,
            "outer_extension_constructed": False,
            "selected_as_physics": False,
            "promotion_ready": False,
            "exact": self.exact,
            "status": (
                "exact descended rank-two constituent frontier; rank-four "
                "outer extension and all physical gates remain unresolved"
            ),
        }


@cache
def tier_b_monomial_constituent_descent_frontier(
) -> TierBMonomialConstituentDescentFrontier:
    """Return all exact length-six constituent descent certificates."""

    schemes = tuple(
        scheme
        for scheme in tier_b_invariant_monomial_schemes()
        if int(scheme.length) == 6
    )
    resolution_audits = tier_b_monomial_resolution_actions(schemes)
    actions_by_scheme = {
        audit.scheme.name: audit for audit in resolution_audits
    }
    deck_atlas = dp9_deck_atlas_audit()
    lines = tuple(
        _line_audit(ray, actions_by_scheme[ray.cokernel.scheme.name], deck_atlas)
        for shift in (-6, 0)
        for ray in tier_b_serre_eigenrays(
            schemes,
            resolution_audits,
            shift,
        )
    )
    topology = tier_b_monomial_topology_screen()
    result = TierBMonomialConstituentDescentFrontier(
        lines,
        len(topology.surviving_topology_candidates),
        topology.surviving_presentation_count,
        all(
            candidate.individual_line_twists_descend
            for candidate in topology.surviving_topology_candidates
        ),
    )
    if not result.exact:
        raise ValueError("monomial constituent descent failed exact gates")
    return result


__all__ = [
    "MonomialConstituentDescentLine",
    "MonomialFittingCertificate",
    "MonomialProjectiveCocycleAudit",
    "TierBMonomialConstituentDescentFrontier",
    "tier_b_monomial_constituent_descent_frontier",
]
