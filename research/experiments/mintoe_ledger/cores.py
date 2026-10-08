"""Test whether the MinTOE cores survive scheme changes and renormalization running.

Owns:
    The convention table for the two cores, `ln(MbarP/v) ≈ 12π − √3/2` and
    `ln(v/(√2 m_τ)) ≈ 4π/3 + 3/10 + 7/72`. It also owns two one-loop checks of
    candidate physical readings: a GUT-coupling reading of 12π, using
    one-loop MSSM gauge unification, and a GUT-scale tau-Yukawa reading of
    4π/3, using one-loop SM and MSSM Yukawa running with tan β scanned.

Depends on:
    The Python standard library only. Inputs are rounded PDG/CODATA values,
    used for terminal comparison only.

Must not:
    Tune a convention, threshold or tan β to make a core fit, or present a
    one-loop scan as a derivation.

Phase 0:
    Research audit; no derivation of either core is claimed.
"""

from __future__ import annotations

import json
import math

MBARP = 2.43532e18                      # reduced Planck mass (GeV)
V_GF = 246.21965                        # (√2 G_F)^(−1/2)
V_MSBAR_MZ = 248.4                      # approximate MS-bar vev at M_Z (scheme dependent)
MTAU_POLE, MTAU_MZ = 1.77693, 1.7462    # pole and approximate MS-bar m_τ(M_Z)
MZ = 91.1876
ALPHA_EM_INV, SIN2W, ALPHA_S = 127.951, 0.23122, 0.1180
CORE_V = 12 * math.pi - math.sqrt(3) / 2
CORE_TAU = 4 * math.pi / 3 + 3 / 10 + 7 / 72


def conventions() -> dict[str, dict[str, float]]:
    """Each core's gap under common, equally legitimate conventions."""

    mp = MBARP * math.sqrt(8 * math.pi)
    v_rows = {
        "MbarP / v_GF (MinTOE)": math.log(MBARP / V_GF),
        "M_P / v_GF (non-reduced Planck)": math.log(mp / V_GF),
        "MbarP / (v_GF/√2) (v = 174 GeV)": math.log(MBARP / (V_GF / math.sqrt(2))),
        "MbarP / v_MSbar(M_Z)": math.log(MBARP / V_MSBAR_MZ),
    }
    tau_rows = {
        "v_GF / (√2 m_τ pole) (MinTOE)": math.log(V_GF / (math.sqrt(2) * MTAU_POLE)),
        "v_GF / (√2 m_τ(M_Z) MS-bar)": math.log(V_GF / (math.sqrt(2) * MTAU_MZ)),
        "v_MSbar / (√2 m_τ(M_Z))": math.log(V_MSBAR_MZ / (math.sqrt(2) * MTAU_MZ)),
    }
    return {"v": {k: CORE_V - x for k, x in v_rows.items()},
            "tau": {k: CORE_TAU - x for k, x in tau_rows.items()}}


def _couplings() -> tuple[float, float, float]:
    alpha_y = 1 / (ALPHA_EM_INV * (1 - SIN2W))
    return (5 / 3) * alpha_y, 1 / (ALPHA_EM_INV * SIN2W), ALPHA_S


def mssm_unification(m_susy: float) -> dict[str, float]:
    """One-loop α1 = α2 crossing with SM running below m_susy and MSSM above."""

    a1, a2, a3 = _couplings()
    inverse = [1 / a1, 1 / a2, 1 / a3]
    sm, mssm = (41 / 10, -19 / 6, -7), (33 / 5, 1, -3)
    t1 = math.log(m_susy / MZ)
    inverse = [x - b / (2 * math.pi) * t1 for x, b in zip(inverse, sm, strict=True)]
    t = 2 * math.pi * (inverse[0] - inverse[1]) / (mssm[0] - mssm[1])
    alpha_gut_inv = inverse[0] - mssm[0] / (2 * math.pi) * t
    return {"m_susy": m_susy, "m_gut": m_susy * math.exp(t), "alpha_gut_inv": alpha_gut_inv,
            "reading_ln_MbarP_over_v": (math.pi / 2) * alpha_gut_inv - math.sqrt(3) / 2}


def _rge(y, g, k, model):
    yt, yb, ytau = y
    g1, g2, g3 = g
    if model == "sm":
        trace = 3 * yt**2 + 3 * yb**2 + ytau**2
        return (k * yt * (1.5 * yt**2 - 1.5 * yb**2 + trace - 17 / 20 * g1**2
                          - 9 / 4 * g2**2 - 8 * g3**2),
                k * yb * (1.5 * yb**2 - 1.5 * yt**2 + trace - 1 / 4 * g1**2
                          - 9 / 4 * g2**2 - 8 * g3**2),
                k * ytau * (1.5 * ytau**2 + trace - 9 / 4 * g1**2 - 9 / 4 * g2**2))
    return (k * yt * (6 * yt**2 + yb**2 - 13 / 15 * g1**2 - 3 * g2**2 - 16 / 3 * g3**2),
            k * yb * (6 * yb**2 + yt**2 + ytau**2 - 7 / 15 * g1**2 - 3 * g2**2
                      - 16 / 3 * g3**2),
            k * ytau * (4 * ytau**2 + 3 * yb**2 - 9 / 5 * g1**2 - 3 * g2**2))


def tau_yukawa_at_unification(tan_beta: float | None, m_susy: float = 1000.0,
                              steps: int = 20000) -> dict[str, float]:
    """−ln y_τ at the α1 = α2 crossing: SM only (tan β None) or SM then MSSM."""

    a1, a2, a3 = _couplings()
    g = [math.sqrt(4 * math.pi * a) for a in (a1, a2, a3)]
    y = [math.sqrt(2) * m / V_GF for m in (169.0, 2.86, MTAU_MZ)]
    k = 1 / (16 * math.pi**2)
    model, beta = "sm", (41 / 10, -19 / 6, -7)
    switch = math.log(m_susy / MZ) if tan_beta is not None else math.inf
    dt = math.log(2e16 / MZ) / steps
    t = 0.0
    for _ in range(6 * steps):
        if model == "sm" and t >= switch:
            b = math.atan(tan_beta)
            y = [y[0] / math.sin(b), y[1] / math.cos(b), y[2] / math.cos(b)]
            model, beta = "mssm", (33 / 5, 1, -3)
        if g[0] >= g[1] or (tan_beta is None and t >= math.log(2e16 / MZ)):
            break
        if max(y) > 4 * math.pi:
            return {"tan_beta": tan_beta, "A_tau": math.nan, "y_top": math.inf,
                    "four_pi_over_three": 4 * math.pi / 3, "landau_pole_below_gut": True,
                    "pole_scale_gev": MZ * math.exp(t)}
        dy = _rge(y, g, k, model)
        y = [yi + d * dt for yi, d in zip(y, dy, strict=True)]
        g = [gi + k * bi * gi**3 * dt for gi, bi in zip(g, beta, strict=True)]
        t += dt
    return {"tan_beta": tan_beta, "A_tau": -math.log(y[2]), "y_top": y[0],
            "four_pi_over_three": 4 * math.pi / 3, "landau_pole_below_gut": False,
            "unification_scale_gev": MZ * math.exp(t)}


def tan_beta_for_core(low: float = 1.5, high: float = 3.0, steps: int = 30) -> float:
    """tan β at which the one-loop MSSM gives −ln y_τ(M_GUT) = 4π/3 (bisection)."""

    target = 4 * math.pi / 3
    for _ in range(steps):
        mid = 0.5 * (low + high)
        if tau_yukawa_at_unification(mid, steps=8000)["A_tau"] > target:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


def run() -> dict[str, object]:
    return {
        "core_v": CORE_V, "core_tau": CORE_TAU,
        "convention_gaps": conventions(),
        "mssm_unification": [mssm_unification(m) for m in (MZ, 1000.0, 3000.0)],
        "sm_tau_yukawa": tau_yukawa_at_unification(None),
        "mssm_tau_yukawa": [tau_yukawa_at_unification(tb) for tb in (1.0, 1.5, 2.0, 3.0, 5.0,
                                                                      10.0, 30.0, 50.0)],
        "tan_beta_for_tau_core": tan_beta_for_core(),
        "derivation_claimed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
