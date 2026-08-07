"""Certify sheafification and free-quotient descent of curvilinear candidates.

Owns:
    Exact internal certificates that corrected curvilinear presentations define
    rank-two locally free sheaves, carry honest projective deck cocycles, pull
    back equivariantly to the Schoen cover, and descend through its free
    order-nine quotient.

Depends on:
    Exact Fitting-cover frame audits, projective presentation cocycles, the
    six-chart dP9 deck action, published free Schoen quotient data, and graded
    presentation shifts.

Must not:
    Select one descended sheaf as physical, call it the rank-four observable
    bundle, infer stability or spectrum, claim an external certificate, or
    bypass the remaining constituent twists and outer-extension gates.

Phase 0:
    Internal exact descent certificates are available for the six corrected
    rank-two candidates; independent verification and promotion remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.numbers import Eisenstein, Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .dp9_deck_atlas import DP9DeckAtlasAudit, dp9_deck_atlas_audit
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_corrections import (
    TierBCurvilinearCorrectionAudit,
    tier_b_curvilinear_correction_audits,
)
from .tier_b_curvilinear_eigenclasses import (
    TierBCurvilinearEigenclassAudit,
    tier_b_curvilinear_eigenclass_audits,
)
from .tier_b_curvilinear_frame_actions import (
    CurvilinearFrameLinearizationLine,
    TierBCurvilinearFrameActionAudit,
    tier_b_curvilinear_frame_action_audits,
)
from .tier_b_curvilinear_projective_cocycles import (
    CurvilinearProjectiveCocycleLine,
    TierBCurvilinearProjectiveCocycleAudit,
    tier_b_curvilinear_projective_cocycle_audits,
)
from .tier_b_curvilinear_serre import _dual_presentation


def _chern_data(
    source_shifts: tuple[int, ...],
    target_shifts: tuple[int, ...],
) -> tuple[int, int, Rational]:
    """Return rank, first Chern coefficient, and second Chern coefficient."""

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
class CurvilinearSheafDescentLine:
    """Internal descent certificate for one rank-two curvilinear eigenline."""

    scheme: str
    eigenline_index: int
    source_shifts: tuple[int, ...]
    target_shifts: tuple[int, ...]
    rank: int
    first_chern_hyperplane: int
    second_chern_hyperplane_squared: Rational
    fitting_cover_verified: bool
    projective_cocycle_verified: bool
    dp9_deck_atlas_verified: bool
    determinant_linearizable: bool
    schoen_action_free: bool
    quotient_order: int

    @property
    def locally_free_sheaf_verified(self) -> bool:
        """Return whether presentation sheafification is rank-two locally free."""

        return self.rank == 2 and self.fitting_cover_verified

    @property
    def equivariant_sheaf_verified(self) -> bool:
        """Return whether the locally free sheaf has an honest deck cocycle."""

        return (
            self.locally_free_sheaf_verified
            and self.projective_cocycle_verified
            and self.dp9_deck_atlas_verified
            and self.determinant_linearizable
        )

    @property
    def internal_descent_certificate(self) -> bool:
        """Apply finite equivariant descent over the free Schoen quotient."""

        return (
            self.equivariant_sheaf_verified
            and self.schoen_action_free
            and self.quotient_order == 9
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the descent theorem inputs without physical promotion."""

        return {
            "scheme": self.scheme,
            "eigenline_index": self.eigenline_index,
            "source_shifts": list(self.source_shifts),
            "target_shifts": list(self.target_shifts),
            "rank": self.rank,
            "chern_character": {
                "c1_hyperplane": self.first_chern_hyperplane,
                "c2_hyperplane_squared": str(
                    self.second_chern_hyperplane_squared
                ),
            },
            "fitting_cover_verified": self.fitting_cover_verified,
            "locally_free_sheaf_verified": self.locally_free_sheaf_verified,
            "projective_cocycle_verified": self.projective_cocycle_verified,
            "dp9_deck_atlas_verified": self.dp9_deck_atlas_verified,
            "determinant_linearizable": self.determinant_linearizable,
            "equivariant_sheaf_verified": self.equivariant_sheaf_verified,
            "schoen_action_free": self.schoen_action_free,
            "quotient_order": self.quotient_order,
            "internal_descent_certificate": self.internal_descent_certificate,
            "descent_theorem": (
                "equivariant locally free sheaves descend along a free finite "
                "group quotient"
            ),
            "independent_external_descent_certificate": False,
            "selected_as_physics": False,
            "promotion_ready": False,
            "status": (
                "internally certified descended rank-two sheaf candidate; "
                "external verification, twists, outer extension, stability, "
                "spectrum, and physical selection remain open"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearDescentAudit:
    """Complete internal descent frontier for one curvilinear specialization."""

    scheme: str
    support_free_eigenline_count: int
    scoped_no_correction_eigenline_count: int
    lines: tuple[CurvilinearSheafDescentLine, ...]

    @property
    def internally_descended_eigenline_count(self) -> int:
        """Return lines passing every internal free-quotient descent gate."""

        return sum(line.internal_descent_certificate for line in self.lines)

    @property
    def exact(self) -> bool:
        """Return whether the declared internal descent frontier is complete."""

        return (
            len(self.lines) + self.scoped_no_correction_eigenline_count
            == self.support_free_eigenline_count
            and all(line.internal_descent_certificate for line in self.lines)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize all internally descended candidates and promotion walls."""

        return {
            "scheme": self.scheme,
            "support_free_eigenline_count": self.support_free_eigenline_count,
            "scoped_no_correction_eigenline_count": (
                self.scoped_no_correction_eigenline_count
            ),
            "internally_descended_eigenline_count": (
                self.internally_descended_eigenline_count
            ),
            "lines": [line.as_record() for line in self.lines],
            "exact": self.exact,
            "independent_external_descent_certificate": False,
            "promotion_ready": False,
            "status": (
                "complete internal descent frontier for the declared corrected "
                "lines; independent verification and physical selection remain "
                "mandatory"
            ),
        }


def _line_audit(
    scheme: str,
    frame_line: CurvilinearFrameLinearizationLine,
    projective_line: CurvilinearProjectiveCocycleLine,
    source_shifts: tuple[int, ...],
    target_shifts: tuple[int, ...],
    deck_atlas: DP9DeckAtlasAudit,
) -> CurvilinearSheafDescentLine:
    """Apply exact sheafification and free finite descent to one line."""

    if frame_line.eigenline_index != projective_line.eigenline_index:
        raise ValueError("frame and projective descent lines do not match")
    rank, first_chern, second_chern = _chern_data(
        source_shifts,
        target_shifts,
    )
    geometry = schoen_geometry()
    fitting_cover = (
        frame_line.exact
        and len(frame_line.fitting_frames) == 10
        and len(frame_line.fitting_cover_certificates) == 3
        and all(
            certificate.exact
            for certificate in frame_line.fitting_cover_certificates
        )
    )
    return CurvilinearSheafDescentLine(
        scheme,
        frame_line.eigenline_index,
        source_shifts,
        target_shifts,
        rank,
        first_chern,
        second_chern,
        fitting_cover,
        projective_line.exact,
        deck_atlas.exact,
        first_chern % geometry.descent_modulus == 0,
        geometry.quotient.acts_freely,
        geometry.quotient.order,
    )


def _audit_one(
    action_audit: TierBCurvilinearResolutionActionAudit,
    eigen_audit: TierBCurvilinearEigenclassAudit,
    correction_audit: TierBCurvilinearCorrectionAudit,
    projective_audit: TierBCurvilinearProjectiveCocycleAudit,
    frame_audit: TierBCurvilinearFrameActionAudit,
    deck_atlas: DP9DeckAtlasAudit,
    target_line_shift: int,
) -> TierBCurvilinearDescentAudit:
    """Build one specialization's exact internal descent frontier."""

    if not (
        action_audit.specialization.name
        == eigen_audit.scheme
        == correction_audit.scheme
        == projective_audit.scheme
        == frame_audit.scheme
    ):
        raise ValueError("curvilinear descent inputs describe different schemes")
    generator_degrees, syzygy_degrees, _, _, _ = _dual_presentation(
        action_audit.specialization,
        target_line_shift,
    )
    target_shifts = (*generator_degrees, target_line_shift)
    projective_lines = {
        line.eigenline_index: line for line in projective_audit.lines
    }
    lines = tuple(
        _line_audit(
            eigen_audit.scheme,
            frame_line,
            projective_lines[frame_line.eigenline_index],
            syzygy_degrees,
            target_shifts,
            deck_atlas,
        )
        for frame_line in frame_audit.lines
    )
    return TierBCurvilinearDescentAudit(
        eigen_audit.scheme,
        eigen_audit.support_locally_free_eigenclass_count,
        correction_audit.scoped_no_correction_eigenline_count,
        lines,
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
    target_line_shift: int,
) -> tuple[TierBCurvilinearDescentAudit, ...]:
    """Cache all exact internal curvilinear descent certificates."""

    actions = tier_b_curvilinear_resolution_actions(parameter)
    eigenclasses = tier_b_curvilinear_eigenclass_audits(
        parameter,
        target_line_shift,
        actions,
    )
    corrections = tier_b_curvilinear_correction_audits(
        parameter,
        target_line_shift,
        actions,
        eigenclasses,
    )
    projective = tier_b_curvilinear_projective_cocycle_audits(
        parameter,
        target_line_shift,
        actions,
        eigenclasses,
        corrections,
    )
    frames = tier_b_curvilinear_frame_action_audits(
        parameter,
        target_line_shift,
        actions,
        eigenclasses,
        corrections,
        projective,
    )
    deck_atlas = dp9_deck_atlas_audit()
    return tuple(
        _audit_one(
            action,
            eigen,
            correction,
            cocycle,
            frame,
            deck_atlas,
            target_line_shift,
        )
        for action, eigen, correction, cocycle, frame in zip(
            actions,
            eigenclasses,
            corrections,
            projective,
            frames,
            strict=True,
        )
    )


def tier_b_curvilinear_descent_audits(
    parameter: object = Eisenstein(1),
    target_line_shift: int = 3,
    action_audits: tuple[TierBCurvilinearResolutionActionAudit, ...] | None = None,
    eigenclass_audits: tuple[TierBCurvilinearEigenclassAudit, ...] | None = None,
    correction_audits: tuple[TierBCurvilinearCorrectionAudit, ...] | None = None,
    projective_audits: tuple[TierBCurvilinearProjectiveCocycleAudit, ...]
    | None = None,
    frame_audits: tuple[TierBCurvilinearFrameActionAudit, ...] | None = None,
    deck_atlas: DP9DeckAtlasAudit | None = None,
) -> tuple[TierBCurvilinearDescentAudit, ...]:
    """Return internal exact descent certificates for all corrected lines."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    supplied = (
        action_audits,
        eigenclass_audits,
        correction_audits,
        projective_audits,
        frame_audits,
        deck_atlas,
    )
    if all(item is None for item in supplied):
        audits = _cached_audits(value, target_line_shift)
    else:
        actions = (
            tier_b_curvilinear_resolution_actions(value)
            if action_audits is None
            else action_audits
        )
        eigenclasses = (
            tier_b_curvilinear_eigenclass_audits(value, target_line_shift, actions)
            if eigenclass_audits is None
            else eigenclass_audits
        )
        corrections = (
            tier_b_curvilinear_correction_audits(
                value,
                target_line_shift,
                actions,
                eigenclasses,
            )
            if correction_audits is None
            else correction_audits
        )
        projective = (
            tier_b_curvilinear_projective_cocycle_audits(
                value,
                target_line_shift,
                actions,
                eigenclasses,
                corrections,
            )
            if projective_audits is None
            else projective_audits
        )
        frames = (
            tier_b_curvilinear_frame_action_audits(
                value,
                target_line_shift,
                actions,
                eigenclasses,
                corrections,
                projective,
            )
            if frame_audits is None
            else frame_audits
        )
        atlas = dp9_deck_atlas_audit() if deck_atlas is None else deck_atlas
        if not (
            len(actions)
            == len(eigenclasses)
            == len(corrections)
            == len(projective)
            == len(frames)
        ):
            raise ValueError("curvilinear descent inputs require matching counts")
        audits = tuple(
            _audit_one(
                action,
                eigen,
                correction,
                cocycle,
                frame,
                atlas,
                target_line_shift,
            )
            for action, eigen, correction, cocycle, frame in zip(
                actions,
                eigenclasses,
                corrections,
                projective,
                frames,
                strict=True,
            )
        )
    if len(audits) != 8 or not all(audit.exact for audit in audits):
        raise ValueError("curvilinear internal descent audit failed exact gates")
    return audits


__all__ = [
    "CurvilinearSheafDescentLine",
    "TierBCurvilinearDescentAudit",
    "tier_b_curvilinear_descent_audits",
]
