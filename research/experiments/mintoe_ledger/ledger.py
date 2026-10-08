"""Evidence ledger for the MinTOE hierarchy formulas.

Owns:
    A faithful port of the MinTOE calculation (calc_04 to calc_07), checked
    against MinTOE's own build outputs; pulls against recorded observations;
    the measured Koide ratio and Brannen phase; the coarse "core" of each
    precision formula with its accuracy and nominal look-elsewhere
    probability; and a content-addressed, dated set of falsifiable
    predictions registered before the corresponding measurements.

Depends on:
    Only the standard library and the observation manifest.

Must not:
    Retune any formula, add observations to a formula, treat post-hoc menus as
    pre-declared, or present a pull table as a derivation.

Phase 0:
    Research ledger; every formula remains a hypothesis.
"""

from __future__ import annotations

import cmath
import hashlib
import json
import math
from math import comb, cos, exp, pi, sin, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OBSERVATIONS = ROOT / "data/observations/terminal_comparison_2024.json"
OUTPUT = ROOT / "data/generated/mintoe_ledger/ledger.json"
REGISTERED_ON = "2026-10-08"

# MinTOE commit bc3df9f, build/05..07 JSON (Decimal outputs, rounded here).
MINTOE_BUILD = {
    "v_GeV": 246.2196673, "mH_GeV": 125.2915298, "mtau_MeV": 1776.860127,
    "me_MeV": 0.5109630501, "mmu_MeV": 105.6519913, "dm21_eV2": 7.45325514e-05,
    "dm31_eV2": 0.002517030232, "Lambda_m2": 1.089195302e-52, "sum_mnu_eV": 0.05880323698,
}


def mintoe() -> dict[str, float]:
    """Port of the user's Julia calculation; constants exactly as written there."""

    mp = 2.435e18
    lphase = 1 / (8 * pi)
    s = lphase * (2 * 7) / (6 * 8 * 9 - 1)
    eps = ((9 / 5) * s) ** 0.25
    dq, thl = 3 * pi / 8, 2 / 9
    b_ew = 9 * (4 * pi / 3) - sqrt(3) / 2 - 2 * s - (2 * 72 + 4) * s**2
    a_tau = 4 * pi / 3 + 0.5 * (3 / 5) + 7 / 72 - s + ((72 + 27) / 2) * s**2
    a_t = lphase - 5 * s + 2 * 69 * s**2
    a_b = 4 * pi / 3 - comb(8, 3) * s + 2 * (comb(8, 3) - 3) * s**2
    v = mp * exp(-b_ew)
    lam = (3 / 8) * (1 + lphase) * (1 / 3 - s)
    mtau = 1000 * v / sqrt(2) * exp(-a_tau)
    s12, s23, s13 = eps * sqrt(1 + eps**2), sqrt(3) / 2 * eps**2, eps**3 / (2 * sqrt(2))
    c12, c23, c13 = (sqrt(1 - x * x) for x in (s12, s23, s13))
    phase = cmath.exp(1j * dq)
    vud, vub = c12 * c13, s13 / phase
    vcd = -s12 * c23 - c12 * s23 * s13 * phase
    vcb = s23 * c13
    vtd = s12 * s23 - c12 * c23 * s13 * phase
    vtb = c23 * c13
    gamma = cmath.phase(-vud * vub.conjugate() / (vcd * vcb.conjugate())) % (2 * pi)
    beta = cmath.phase(-vcd * vcb.conjugate() / (vtd * vtb.conjugate())) % (2 * pi)
    cone = sqrt(mtau) / (1 + sqrt(2) * cos(thl))
    me = (cone * (1 + sqrt(2) * cos(thl + 2 * pi / 3))) ** 2
    mmu = (cone * (1 + sqrt(2) * cos(thl + 4 * pi / 3))) ** 2
    th12, th13 = pi / 6 + 48 * s, 4 * lphase - 7 * s + 4 * s**2
    th23 = (pi / 4 - 48 * s, pi / 4 + 48 * s)
    mr3 = (sqrt(2 * pi) + 49 * s + 90 * s**2) * sqrt(v * mp)
    m3 = v**2 * exp(-2 * a_tau) / (2 * mr3) * 1e9
    m2 = (4 * lphase + 10 * s) * m3
    a, b = m2 * sin(th12) ** 2 * cos(th13) ** 2, m3 * sin(th13) ** 2
    mee = sqrt(a * a + b * b - a * b)
    lam_cc = (mee**4 / (mp * 1e9) ** 2) / (1.973269804e-7) ** 2
    return {
        "S_star": s, "epsilon": eps, "v_GeV": v, "mH_GeV": v * sqrt(2 * lam), "mtau_MeV": mtau,
        "me_MeV": me, "mmu_MeV": mmu, "y_t": exp(-a_t), "y_b": exp(-a_b),
        "V_us": s12 * c13, "V_cb": s23 * c13, "V_ub": s13,
        "J": c12 * c23 * c13**2 * s12 * s23 * s13 * sin(dq),
        "gamma_deg": math.degrees(gamma), "beta_deg": math.degrees(beta),
        "sin2_theta12": sin(th12) ** 2, "sin2_theta13": sin(th13) ** 2,
        "sin2_theta23_lower": sin(th23[0]) ** 2, "sin2_theta23_upper": sin(th23[1]) ** 2,
        "delta_CP_PMNS_deg": math.degrees(4 * dq), "m1_eV": 0.0, "m2_eV": m2, "m3_eV": m3,
        "dm21_eV2": m2**2, "dm31_eV2": m3**2, "sum_mnu_eV": m2 + m3,
        "m_betabeta_meV": 1000 * mee, "Lambda_m2": lam_cc,
    }


def observations() -> dict[str, dict[str, object]]:
    return json.loads(OBSERVATIONS.read_text())["observations"]


def pulls() -> dict[str, dict[str, float]]:
    """(prediction - measurement)/sigma for every comparable two-sided entry."""

    pred, obs = mintoe(), observations()
    pairs = {
        "mH_GeV": "m_H_GeV", "mtau_MeV": "m_tau_MeV", "V_us": "V_us", "V_cb": "V_cb",
        "V_ub": "V_ub", "sin2_theta12": "sin2_theta12", "sin2_theta13": "sin2_theta13",
        "sin2_theta23_upper": "sin2_theta23", "dm21_eV2": "dm21_eV2", "dm31_eV2": "dm31_eV2",
        "delta_CP_PMNS_deg": "delta_CP_PMNS_deg", "Lambda_m2": "Lambda_m2",
    }
    result = {}
    for key, name in pairs.items():
        entry = obs[name]
        value, sigma = float(entry["value"]), float(entry["sigma"])  # type: ignore[arg-type]
        result[key] = {"prediction": pred[key], "measured": value,
                       "pull": (pred[key] - value) / sigma}
    # The delta_CP likelihood is strongly non-Gaussian; the pull is indicative only.
    result["delta_CP_PMNS_deg"]["gaussian_pull_unreliable"] = True
    alt = 212.0
    result["delta_CP_PMNS_deg"]["difference_from_alternative_fit_212_deg"] = (
        pred["delta_CP_PMNS_deg"] - alt
    )
    for key, name in (("me_MeV", "m_e_MeV"), ("mmu_MeV", "m_mu_MeV"), ("v_GeV", "v_GeV")):
        value = float(obs[name]["value"])  # type: ignore[arg-type]
        result[key] = {"prediction": pred[key], "measured": value,
                       "relative_difference": pred[key] / value - 1}
    old = float(obs["m_tau_MeV_superseded"]["value"])  # type: ignore[arg-type]
    result["mtau_vs_superseded_average"] = {"relative_difference": pred["mtau_MeV"] / old - 1}
    return result


def koide() -> dict[str, float]:
    """Measured Koide ratio Q and Brannen phase delta (tau k=0, e k=1, mu k=2)."""

    obs = observations()
    masses = {k: float(obs[n]["value"]) for k, n in  # type: ignore[arg-type]
              (("tau", "m_tau_MeV"), ("e", "m_e_MeV"), ("mu", "m_mu_MeV"))}
    roots = {k: sqrt(m) for k, m in masses.items()}
    q = sum(masses.values()) / sum(roots.values()) ** 2
    fourier = sum(roots[k] * cmath.exp(-2j * pi * i / 3) for i, k in enumerate(("tau", "e", "mu")))
    delta = cmath.phase(fourier)
    sigma_tau = float(obs["m_tau_MeV"]["sigma"])  # type: ignore[arg-type]
    shifted = dict(masses, tau=masses["tau"] + sigma_tau)
    q_up = sum(shifted.values()) / sum(sqrt(m) for m in shifted.values()) ** 2
    shifted_root = sum(sqrt(m) for m in shifted.values())
    delta_up = cmath.phase(sum(sqrt(shifted[k]) * cmath.exp(-2j * pi * i / 3)
                               for i, k in enumerate(("tau", "e", "mu"))))
    # Koide-Brannen with delta = 2/9 exactly, anchored on the measured tau mass only.
    cone = roots["tau"] / (1 + sqrt(2) * cos(2 / 9))
    me = (cone * (1 + sqrt(2) * cos(2 / 9 + 2 * pi / 3))) ** 2
    mmu = (cone * (1 + sqrt(2) * cos(2 / 9 + 4 * pi / 3))) ** 2
    del shifted_root
    return {"Q": q, "Q_minus_two_thirds": q - 2 / 3, "Q_sigma_from_tau": abs(q_up - q),
            "brannen_delta": delta, "delta_minus_two_ninths": delta - 2 / 9,
            "delta_sigma_from_tau": abs(delta_up - delta),
            "me_from_measured_tau_relative_difference": me / masses["e"] - 1,
            "mmu_from_measured_tau_relative_difference": mmu / masses["mu"] - 1}


def cores() -> dict[str, dict[str, object]]:
    """Coarse parts of the precision formulas, without S or S^2 corrections."""

    obs = observations()
    v = float(obs["v_GeV"]["value"])  # type: ignore[arg-type]
    mp = float(obs["MbarP_GeV"]["value"])  # type: ignore[arg-type]
    mtau = float(obs["m_tau_MeV"]["value"])  # type: ignore[arg-type]
    mh = float(obs["m_H_GeV"]["value"])  # type: ignore[arg-type]
    lphase = 1 / (8 * pi)
    rows = {
        "ln(MbarP/v) = 12 pi - sqrt3/2": (12 * pi - sqrt(3) / 2, math.log(mp / v)),
        "ln(v/(sqrt2 m_tau)) = 4pi/3 + 3/10 + 7/72": (
            4 * pi / 3 + 3 / 10 + 7 / 72, math.log(v / sqrt(2) * 1000 / mtau)),
        "lambda_h = (1 + 1/(8 pi))/8": ((1 + lphase) / 8, mh**2 / (2 * v * v)),
    }
    simple = (0, 0.5, -0.5, sqrt(3) / 2, -sqrt(3) / 2, 1, -1, sqrt(2) / 2, -sqrt(2) / 2,
              pi / 6, -pi / 6)
    tau_menu = tuple(j * 0.3 + k / 72 for j in range(3) for k in range(13))
    menus = {"ln(MbarP/v) = 12 pi - sqrt3/2": simple,
             "ln(v/(sqrt2 m_tau)) = 4pi/3 + 3/10 + 7/72": tau_menu}
    result: dict[str, dict[str, object]] = {}
    for name, (core, needed) in rows.items():
        gap = core - needed
        row: dict[str, object] = {"core": core, "needed": needed, "absolute_gap": gap,
                                  "relative_gap": core / needed - 1}
        if name in menus:
            # Post-hoc menu: offsets r, modulo the 4pi/3 step; window |gap|.
            row["nominal_post_hoc_probability"] = _coverage(menus[name], 4 * pi / 3, abs(gap))
        result[name] = row
    return result


def _coverage(offsets: tuple[float, ...], period: float, half_width: float) -> float:
    """Fraction of a period covered by windows of the given half-width around offsets."""

    segments = sorted(((r % period) - half_width, (r % period) + half_width) for r in offsets)
    covered, low, high = 0.0, None, None
    for start, end in segments:
        if high is None or start > high:
            if high is not None and low is not None:
                covered += high - low
            low, high = start, end
        else:
            high = max(high, end)
    if high is not None and low is not None:
        covered += high - low
    return min(1.0, covered / period)


def registered_predictions() -> dict[str, object]:
    """Falsifiable MinTOE outputs, frozen and hashed on REGISTERED_ON."""

    pred = mintoe()
    keys = ("delta_CP_PMNS_deg", "m1_eV", "sum_mnu_eV", "m_betabeta_meV", "sin2_theta12",
            "sin2_theta13", "sin2_theta23_lower", "sin2_theta23_upper", "dm21_eV2",
            "dm31_eV2", "mH_GeV", "mtau_MeV", "gamma_deg", "beta_deg", "V_ub", "J")
    frozen = {key: float(f"{pred[key]:.10g}") for key in keys}
    payload = json.dumps(frozen, sort_keys=True, separators=(",", ":")).encode()
    return {"registered_on": REGISTERED_ON, "values": frozen,
            "ordering": "normal, lightest neutrino massless",
            "sha256": hashlib.sha256(payload).hexdigest()}


def write_artifact(path: Path = OUTPUT) -> dict[str, object]:
    record: dict[str, object] = {
        "schema": "mintoe-evidence-ledger-v1",
        "port_matches_mintoe_build": {k: mintoe()[k] / v - 1 for k, v in MINTOE_BUILD.items()},
        "pulls": pulls(), "koide": koide(), "cores": cores(),
        "registered_predictions": registered_predictions(),
        "knob_accounting": {
            "adjustable_integers_on_S_and_S2": {
                "B_EW": [2, 148], "A_tau": [1, 49.5], "A_t": [5, 138], "A_b": [56, 106],
                "theta12": [48], "theta13": [7, 4], "M_R3": [49, 90], "m2": [10]},
            "base_of_S_expansion": 1 / mintoe()["S_star"],
            "note": "integer coefficients up to ~1/S make the S-expansion a positional number "
                    "system; digits beyond the cores carry no evidence without a derivation",
        },
        "observations_used_as_inputs": False,
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), default=float).encode()
    record["artifact_digest"] = hashlib.sha256(payload).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
