"""Formula engine for the Genesis film: every drawn shape comes from here.

Owns:
    Pure NumPy evaluations of the physical and mathematical objects the film
    draws: the E8 root system and its Coxeter-plane projection with the
    SU(4) x Spin(10) and Standard Model subsets, the Spin(10) spinor weights
    of one family, real slices of the Hesse cubic pencil, closed-string mode
    shapes, Gaussian random fields with a measured spectral tilt, the
    Zel'dovich displacement, the LambdaCDM expansion history, horizons and
    growth factor, the Higgs potential, the thermal clock, and a spiral galaxy.

Depends on:
    NumPy only, so it is testable without Manim.

Must not:
    Import Manim, fit any parameter to make a picture look right, or hide an
    approximation; approximations are named in their docstrings.

Phase 0:
    Visualization engine; it supplies no new physical result.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np

# ---------------------------------------------------------------------------
# Measured constants (terminal comparison values; used only to draw)
# ---------------------------------------------------------------------------
HBAR_GEV_S = 6.582119569e-25
MPL_GEV = 1.220890e19          # non-reduced Planck mass
H0_KM_S_MPC = 67.4             # Planck 2018
OMEGA_M, OMEGA_L, OMEGA_R = 0.315, 0.685, 9.15e-5
N_S = 0.9649                   # Planck 2018 scalar tilt
HIGGS_V_GEV, HIGGS_MASS_GEV = 246.21965, 125.20
GYR_S = 3.15576e16
MPC_KM = 3.0857e19
C_KM_S = 299792.458
GLY_PER_MPC = 3.26156e-3


# ---------------------------------------------------------------------------
# E8: roots, Coxeter plane, subgroups, one family
# ---------------------------------------------------------------------------
def e8_roots() -> np.ndarray:
    """All 240 roots of E8 in the even coordinate system (Bourbaki)."""

    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((1, -1), repeat=2):
            v = np.zeros(8)
            v[i], v[j] = si, sj
            roots.append(v)
    for signs in itertools.product((0.5, -0.5), repeat=8):
        if sum(s < 0 for s in signs) % 2 == 0:
            roots.append(np.array(signs))
    return np.array(roots)


def e8_simple_roots() -> np.ndarray:
    """Bourbaki simple roots alpha_1..alpha_8 in the same coordinates."""

    e = np.eye(8)
    return np.array([
        0.5 * np.array([1, -1, -1, -1, -1, -1, -1, 1]),
        e[0] + e[1], e[1] - e[0], e[2] - e[1], e[3] - e[2],
        e[4] - e[3], e[5] - e[4], e[6] - e[5],
    ])


def coxeter_plane() -> np.ndarray:
    """Orthonormal 2x8 basis of the Petrie (Coxeter) plane of E8.

    The Coxeter element c = s_1 ... s_8 has order h = 30; the plane is spanned
    by the real and imaginary parts of its eigenvector for exp(2 pi i / 30).
    """

    c = np.eye(8)
    for a in e8_simple_roots():
        c = c @ (np.eye(8) - 2 * np.outer(a, a) / (a @ a))
    values, vectors = np.linalg.eig(c)
    k = int(np.argmin(np.abs(values - np.exp(2j * np.pi / 30))))
    u, w = vectors[:, k].real, vectors[:, k].imag
    u /= np.linalg.norm(u)
    w -= (w @ u) * u
    w /= np.linalg.norm(w)
    return np.vstack([u, w])


def project(vectors: np.ndarray) -> np.ndarray:
    return vectors @ coxeter_plane().T


def root_subsets(roots: np.ndarray) -> dict[str, np.ndarray]:
    """Boolean masks for E8 ⊃ SU(4)×Spin(10) ⊃ SU(4)×SU(3)×SU(2).

    SO(16) ⊃ SO(6)×SO(10): integer roots ±e_i±e_j with both indices in the
    first three coordinates (SO(6) = SU(4), 12 roots) or in the last five
    (Spin(10), 40 roots). Inside Spin(10) ⊃ SU(5): e_i − e_j (20 roots);
    SU(3) on coordinates 4–6 (6 roots) and SU(2) on 7–8 (2 roots).
    """

    integer = np.all(np.abs(roots - np.round(roots)) < 1e-9, axis=1)
    support = np.abs(roots) > 1e-9
    first, last = support[:, :3], support[:, 3:]
    su4 = integer & ~last.any(axis=1)
    spin10 = integer & ~first.any(axis=1)
    positive_negative = np.isclose(roots.sum(axis=1), 0)
    su5 = spin10 & positive_negative
    su3 = su5 & ~support[:, 6:].any(axis=1)
    su2 = su5 & ~support[:, 3:6].any(axis=1)
    return {"su4": su4, "spin10": spin10, "su5": su5, "su3": su3, "su2": su2}


@dataclass(frozen=True)
class SpinorWeight:
    vector: np.ndarray
    field: str


def one_family() -> list[SpinorWeight]:
    """The 16 of Spin(10) inside E8's (4,16): fixed SU(4) weight (+½,+½,+½).

    Fields follow the SU(5) decomposition by the minus signs among the last
    five coordinates: none → ν^c; two in colour → u^c; two in isospin → e^c;
    one of each → Q; four with the plus in colour → d^c; plus in isospin → L.
    """

    family = []
    for signs in itertools.product((0.5, -0.5), repeat=5):
        if sum(s < 0 for s in signs) % 2:
            continue
        vector = np.array((0.5, 0.5, 0.5, *signs))
        if sum(vector < 0) % 2:
            continue
        colour = [s < 0 for s in signs[:3]]
        isospin = [s < 0 for s in signs[3:]]
        minus = sum(colour) + sum(isospin)
        if minus == 0:
            field = "ν^c"
        elif minus == 2:
            field = "u^c" if sum(colour) == 2 else ("e^c" if sum(isospin) == 2 else "Q")
        else:
            field = "d^c" if sum(colour) == 2 else "L"
        family.append(SpinorWeight(vector, field))
    return family


def hypercharge(vector: np.ndarray) -> float:
    """Y = (s1+s2+s3)/3 − (s4+s5)/2 on the last five coordinates (SU(5) ⊂ Spin(10))."""

    s = vector[3:]
    return float((s[0] + s[1] + s[2]) / 3 - (s[3] + s[4]) / 2)


def isospin(vector: np.ndarray) -> float:
    """Weak isospin T₃ = (s4 − s5)/2."""

    s = vector[3:]
    return float((s[3] - s[4]) / 2)


# ---------------------------------------------------------------------------
# Quantum vacuum and the closed string
# ---------------------------------------------------------------------------
def wigner_vacuum_level(level: float) -> float:
    """Radius of the Wigner-function contour W = level·W(0) of the ground state.

    W(x,p) ∝ exp(−x² − p²) in units ħ = 1, ω = 1; contour radius sqrt(−ln level).
    """

    return math.sqrt(-math.log(level))


def string_loop(sigma: np.ndarray, tau: float, left: tuple[float, ...],
                right: tuple[float, ...], radius: float = 1.0) -> np.ndarray:
    """Closed-string profile r(σ,τ) = R + Σ_n [a_n cos n(σ−τ) + b_n cos n(σ+τ)]/n.

    Left-movers depend on σ+τ and right-movers on σ−τ, the general solution of
    the free wave equation on the closed string (radial projection to 2D).
    """

    r = np.full_like(sigma, radius, dtype=float)
    for n, amplitude in enumerate(right, start=1):
        r += amplitude * np.cos(n * (sigma - tau)) / n
    for n, amplitude in enumerate(left, start=1):
        r += amplitude * np.cos(n * (sigma + tau) + 0.7 * n) / n
    return np.stack([r * np.cos(sigma), r * np.sin(sigma)], axis=1)


def graviton_loop(sigma: np.ndarray, phase: float, amplitude: float = 0.22) -> np.ndarray:
    """Plus-polarized spin-2 (quadrupole) deformation of a ring: the graviton mode."""

    x = (1 + amplitude * np.cos(phase)) * np.cos(sigma)
    y = (1 - amplitude * np.cos(phase)) * np.sin(sigma)
    return np.stack([x, y], axis=1)


# ---------------------------------------------------------------------------
# Geometry: the Hesse cubic pencil (real slices of the elliptic fibres)
# ---------------------------------------------------------------------------
def hesse(x: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    """Affine Hesse cubic x³ + y³ + 1 − 3λxy (the z = 1 chart of x³+y³+z³ = 3λxyz).

    λ = 1 is the singular 'triangle' fibre (x+y+1)(x+ωy+ω²)(x+ω²y+ω): its real
    slice is the line x + y + 1 = 0 and the isolated point (1, 1).
    """

    return x**3 + y**3 + 1 - 3 * lam * x * y


def marching_squares(field: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> list[np.ndarray]:
    """Zero-level segments of a sampled field, as an (n, 2, 2) array list."""

    segments = []
    f = field
    for i in range(len(ys) - 1):
        for j in range(len(xs) - 1):
            corners = [(xs[j], ys[i], f[i, j]), (xs[j + 1], ys[i], f[i, j + 1]),
                       (xs[j + 1], ys[i + 1], f[i + 1, j + 1]), (xs[j], ys[i + 1], f[i + 1, j])]
            points = []
            for k in range(4):
                (x1, y1, v1), (x2, y2, v2) = corners[k], corners[(k + 1) % 4]
                if (v1 < 0) != (v2 < 0):
                    t = v1 / (v1 - v2)
                    points.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
            if len(points) >= 2:
                segments.append(np.array(points[:2]))
            if len(points) == 4:
                segments.append(np.array(points[2:]))
    return segments


def hesse_segments(lam: float, extent: float = 3.0, n: int = 160) -> list[np.ndarray]:
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    grid_x, grid_y = np.meshgrid(xs, ys)
    return marching_squares(hesse(grid_x, grid_y, lam), xs, ys)


def hesse_base_points() -> np.ndarray:
    """The real affine base points shared by every Hesse cubic: (−1,0), (0,−1)."""

    return np.array([[-1.0, 0.0], [0.0, -1.0]])


def torus_point(u: float, v: float, big: float = 1.0, small: float = 0.42) -> np.ndarray:
    """Embedded torus: a real picture of a complex elliptic curve C/(Z+τZ)."""

    return np.array([(big + small * math.cos(v)) * math.cos(u),
                     (big + small * math.cos(v)) * math.sin(u),
                     small * math.sin(v)])


# ---------------------------------------------------------------------------
# Random fields: inflation, CMB, cosmic web
# ---------------------------------------------------------------------------
def gaussian_field(n: int, seed: int, tilt: float = N_S, damping: float = 0.0,
                   acoustic: float = 0.0, scale: float = 0.0) -> np.ndarray:
    """2D Gaussian random field with P(k) ∝ k^(n_s − 3), optional damping/oscillation.

    The k^(n_s−3) slope is the nearly scale-invariant primordial spectrum as seen
    in a 2D slice. The acoustic factor (1 + A cos(k·s)) and Gaussian damping are
    an approximation to the CMB transfer function, not a Boltzmann solution.
    """

    rng = np.random.default_rng(seed)
    kx = np.fft.fftfreq(n)[:, None]
    ky = np.fft.fftfreq(n)[None, :]
    k = np.sqrt(kx**2 + ky**2)
    k[0, 0] = 1.0
    power = k ** (tilt - 3.0)
    if acoustic:
        power *= 1 + acoustic * np.cos(2 * np.pi * k * scale)
    if damping:
        power *= np.exp(-((k / damping) ** 2))
    power[0, 0] = 0.0
    noise = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    field = np.fft.ifft2(noise * np.sqrt(power)).real
    return (field - field.mean()) / field.std()


def zeldovich_displacement(delta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """ψ = −∇φ with ∇²φ = δ, solved spectrally on the periodic grid."""

    n = delta.shape[0]
    k = 2 * np.pi * np.fft.fftfreq(n)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    k2 = kx**2 + ky**2
    k2[0, 0] = 1.0
    phi_k = -np.fft.fft2(delta) / k2
    phi_k[0, 0] = 0
    psi_x = -np.fft.ifft2(1j * kx * phi_k).real
    psi_y = -np.fft.ifft2(1j * ky * phi_k).real
    return psi_x, psi_y


def splat(points: np.ndarray, size: int, weights: np.ndarray | None = None) -> np.ndarray:
    """Histogram points in [0,1)² onto a size×size grid with a soft 3×3 kernel."""

    grid = np.zeros((size, size))
    idx = np.floor((points % 1.0) * size).astype(int) % size
    np.add.at(grid, (idx[:, 1], idx[:, 0]), 1.0 if weights is None else weights)
    soft = grid.copy()
    for dx, dy, w in ((1, 0, .5), (-1, 0, .5), (0, 1, .5), (0, -1, .5)):
        soft += w * np.roll(np.roll(grid, dx, 0), dy, 1)
    return soft


# ---------------------------------------------------------------------------
# Expansion history (flat LambdaCDM, Planck 2018)
# ---------------------------------------------------------------------------
def hubble(a: np.ndarray | float) -> np.ndarray | float:
    """H(a) in 1/Gyr."""

    h0 = H0_KM_S_MPC / MPC_KM * GYR_S
    return h0 * np.sqrt(OMEGA_R / a**4 + OMEGA_M / a**3 + OMEGA_L)


def age_at(a: float, samples: int = 200000) -> float:
    """t(a) = ∫ da'/(a' H(a')) in Gyr (log-spaced trapezoid)."""

    grid = np.logspace(-12, math.log10(a), samples)
    integrand = 1 / (grid * hubble(grid))
    return float(np.trapezoid(integrand, grid))


def comoving_distance_gly(a_from: float, a_to: float = 1.0, samples: int = 200000) -> float:
    """Comoving distance c∫dt/a between two scale factors, in Gly."""

    grid = np.logspace(math.log10(a_from), math.log10(a_to), samples)
    integrand = 1 / (grid**2 * hubble(grid))      # Gyr per unit a / a
    return float(np.trapezoid(integrand, grid))   # light-Gyr = Gly


def horizons_gly() -> dict[str, float]:
    """Particle horizon, Hubble radius and cosmic event horizon today (Gly)."""

    particle = comoving_distance_gly(1e-12, 1.0)
    hubble_radius = C_KM_S / H0_KM_S_MPC * GLY_PER_MPC
    future = np.logspace(0, 6, 400000)
    event = float(np.trapezoid(1 / (future**2 * hubble(future)), future))
    return {"particle": particle, "hubble": hubble_radius, "event": event}


def growth_factor(a: float) -> float:
    """Linear growth D(a) ∝ H(a)∫da/(aH)^3 (matter + Λ), normalized D(1) = 1."""

    def raw(x: float) -> float:
        grid = np.linspace(1e-6, x, 20000)
        return float(hubble(x) * np.trapezoid(1 / (grid * hubble(grid)) ** 3, grid))

    return raw(a) / raw(1.0)


# ---------------------------------------------------------------------------
# Thermal history and the Higgs
# ---------------------------------------------------------------------------
def time_at_temperature(t_gev: float, g_star: float) -> float:
    """Radiation era t = 0.301 g*^(−1/2) M_Pl / T² (seconds)."""

    return 0.301 / math.sqrt(g_star) * MPL_GEV / t_gev**2 * HBAR_GEV_S


def higgs_lambda() -> float:
    """Tree-level quartic λ = m_H² / (2 v²) from the measured mass and vev."""

    return HIGGS_MASS_GEV**2 / (2 * HIGGS_V_GEV**2)


def higgs_potential(phi: np.ndarray, temperature: float = 0.0,
                    critical: float = 159.5) -> np.ndarray:
    """V(φ,T) = λ/4 (φ² − v²)² + λ v² T²/(2 T_c²) φ²  (mean-field sketch).

    At T = 0 it is the measured Standard Model potential. The thermal mass term
    restores the symmetric minimum above T_c ≈ 159.5 GeV (lattice crossover);
    the mean-field form is a qualitative approximation.
    """

    lam, v = higgs_lambda(), HIGGS_V_GEV
    return lam / 4 * (phi**2 - v**2) ** 2 + lam * v**2 * temperature**2 / (2 * critical**2) * phi**2


# ---------------------------------------------------------------------------
# Galaxies
# ---------------------------------------------------------------------------
def spiral_galaxy(n: int, seed: int, arms: int = 2, pitch_deg: float = 12.0,
                  scale: float = 0.33) -> np.ndarray:
    """Stars on logarithmic spiral arms r = r0 exp(θ tan p) in an exponential disk."""

    rng = np.random.default_rng(seed)
    r = rng.exponential(scale, n)
    r = r[r < 1.6][:n]
    theta0 = np.log(np.maximum(r, 1e-3) / 0.05) / math.tan(math.radians(pitch_deg))
    arm = rng.integers(0, arms, r.size) * 2 * math.pi / arms
    spread = rng.normal(0, 0.28, r.size)
    theta = theta0 + arm + spread
    return np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)


def flat_rotation_speed(r_kpc: np.ndarray) -> np.ndarray:
    """Observed-like flat curve v ≈ 220(1 − e^(−r/2.5)) km/s (Milky Way scale)."""

    return 220 * (1 - np.exp(-r_kpc / 2.5))


def keplerian_speed(r_kpc: np.ndarray, peak_r: float = 6.0) -> np.ndarray:
    """What visible mass alone would give beyond the disk: v ∝ r^(−1/2)."""

    v = 220 * (1 - np.exp(-r_kpc / 2.5))
    outer = r_kpc > peak_r
    v[outer] = 220 * (1 - math.exp(-peak_r / 2.5)) * np.sqrt(peak_r / r_kpc[outer])
    return v
