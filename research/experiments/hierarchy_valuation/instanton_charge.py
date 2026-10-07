"""Anomalous-U(1) flux through the exceptional-section instanton curves.

Owns:
    The ambient class of the 81 exceptional sections (fixed base points of both
    cubic pencils times P1), their exact containment in the Schoen cover,
    their Kähler area, and the wall U(1) flux c1(V1).C that sets the
    Green--Schwarz charge of a worldsheet instanton wrapping them.

Depends on:
    The frozen cubic pencils and the cover Chow ring of P2 x P2 x P1.

Must not:
    Compute a Pfaffian, assign an instanton coefficient, choose a Kähler class,
    or use observations.

Phase 0:
    Research charge audit; instanton amplitudes remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .wall_valuation import FIRST_CONSTITUENT_C1

# A curve {x = x*, u = u*} x P1 has ambient class x^2 u^2; its intersection
# numbers with the divisor basis (tau1, tau2, phi) = (x, u, p) are read off
# from x^3 = u^3 = 0 and x^2 u^2 p = 1.
EXCEPTIONAL_CURVE_DEGREES = (0, 0, 1)


def pencil_base_points_are_common_zeros() -> bool:
    """Both Schoen equations vanish identically along {x*} x {u*} x P1.

    p1 = mu F(x) + nu G(x) and p2 = 2 nu F(u) + mu G(u) vanish for every
    (mu:nu) exactly when F(x*) = G(x*) = 0 and F(u*) = G(u*) = 0, i.e. at base
    points of the two cubic pencils; each pencil has nine of them.
    """

    cox = schoen_geometry().cover.cox
    return cox.equations == ("p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)")


@dataclass(frozen=True)
class InstantonChargeAudit:
    curve_count_on_cover: int
    curve_degrees: tuple[int, int, int]
    kahler_area: str
    wall_u1_flux: int
    neutral_under_wall_u1: bool


def audit() -> InstantonChargeAudit:
    if not pencil_base_points_are_common_zeros():
        raise ValueError("the Schoen equations changed")
    flux = sum(c * d for c, d in zip(FIRST_CONSTITUENT_C1, EXCEPTIONAL_CURVE_DEGREES, strict=True))
    return InstantonChargeAudit(81, EXCEPTIONAL_CURVE_DEGREES, "j3", flux, flux == 0)


if __name__ == "__main__":
    print(audit())
