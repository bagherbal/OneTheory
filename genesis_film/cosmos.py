"""Cosmic textures for the Genesis film: NumPy painters for acts 6 to 14.

Owns:
    One periodic primordial field (n_s = 0.9649) and everything the film grows
    from it: the inflation animation that converges exactly to it, the hot
    particle soup (reheating, electroweak, QCD, nucleosynthesis, recombination)
    on a fixed schedule, the CMB map, the Zel'dovich cosmic web, a spiral
    galaxy and the horizon view. Every painter is a pure function of its
    arguments and returns an RGBA image.

Depends on:
    NumPy, SciPy (ndimage) and the film's `physics` module. No Manim, so it is
    testable on its own.

Must not:
    Use wall-clock time or hidden state, fit anything to look right, or claim
    more than the approximations named in each docstring.

Phase 0:
    Visualization engine; it supplies no new physical result.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import physics
from scipy import ndimage

SIZE = 360  # pixels of every live cosmic image (window = [-1, 1]²)


# ---------------------------------------------------------------------------
# Colour and small helpers
# ---------------------------------------------------------------------------
def hex_rgb(color: str) -> np.ndarray:
    color = color.lstrip("#")
    return np.array([int(color[k:k + 2], 16) for k in (0, 2, 4)], dtype=float) / 255


def colormap(values: np.ndarray, stops) -> np.ndarray:
    positions = np.array([s[0] for s in stops], dtype=float)
    colors = np.array([hex_rgb(s[1]) for s in stops])
    v = np.clip(values, 0, 1)
    out = np.empty((*np.shape(v), 3))
    for c in range(3):
        out[..., c] = np.interp(v, positions, colors[:, c])
    return out


def rgba(rgb: np.ndarray, alpha: np.ndarray | float = 1.0) -> np.ndarray:
    a = np.broadcast_to(np.asarray(alpha, dtype=float), rgb.shape[:2])
    out = np.empty((*rgb.shape[:2], 4), dtype=np.uint8)
    out[..., :3] = np.clip(rgb * 255, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return out


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def ramp(t: float, start: float, end: float) -> float:
    return float(smoothstep((t - start) / (end - start)))


def bump(t: float, center: float, width: float) -> float:
    return math.exp(-(((t - center) / width) ** 2))


CMAP_FIELD = ((0, "#020617"), (0.3, "#172554"), (0.55, "#1d4ed8"), (0.75, "#38bdf8"),
              (0.9, "#e0f2fe"), (1, "#ffffff"))
CMAP_HOT = ((0, "#0c0400"), (0.3, "#7c2d12"), (0.6, "#f97316"), (0.85, "#fde68a"),
            (1, "#ffffff"))
CMAP_CMB = ((0, "#0a1a5c"), (0.22, "#1d4ed8"), (0.42, "#93c5fd"), (0.5, "#f1f5f9"),
            (0.58, "#fde68a"), (0.78, "#f97316"), (1, "#991b1b"))
CMAP_WEB = ((0, "#000000"), (0.18, "#0f0a2a"), (0.42, "#4c1d95"), (0.66, "#be185d"),
            (0.85, "#fdba74"), (1, "#fffbeb"))


def window_coords(size: int = SIZE) -> tuple[np.ndarray, np.ndarray]:
    """Pixel centres in window units, row 0 at the top (y = +1)."""

    c = (np.arange(size) + 0.5) / size * 2 - 1
    return np.meshgrid(c, -c)


def vignette(size: int = SIZE, soft: float = 0.07) -> np.ndarray:
    x, y = window_coords(size)
    edge = np.minimum(1 - np.abs(x), 1 - np.abs(y))
    return smoothstep(edge / soft)


def sample_periodic(field: np.ndarray, x: np.ndarray, y: np.ndarray, order: int = 1):
    """Sample a periodic field on [-1,1)² (row 0 at y = +1) at window coordinates."""

    n = field.shape[0]
    col = (x + 1) / 2 * n - 0.5
    row = (1 - y) / 2 * n - 0.5
    return ndimage.map_coordinates(field, [row, col], order=order, mode="grid-wrap")


# ---------------------------------------------------------------------------
# Raster particles
# ---------------------------------------------------------------------------
class Raster:
    """Additive Gaussian splats onto a square canvas covering [-1,1]²."""

    def __init__(self, size: int = SIZE) -> None:
        self.size = size
        self._kernels: dict[float, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    def _kernel(self, radius_px: float):
        key = round(radius_px, 2)
        if key not in self._kernels:
            half = max(1, int(math.ceil(2.5 * radius_px)))
            dy, dx = np.mgrid[-half:half + 1, -half:half + 1]
            weight = np.exp(-(dx**2 + dy**2) / (2 * radius_px**2))
            self._kernels[key] = (dx.ravel(), dy.ravel(), weight.ravel())
        return self._kernels[key]

    def blank(self) -> np.ndarray:
        return np.zeros((self.size, self.size, 3))

    def splat(self, buffer: np.ndarray, xy: np.ndarray, rgb: np.ndarray,
              radius_px: float, intensity) -> None:
        if len(xy) == 0:
            return
        n = self.size
        ix = np.rint((xy[:, 0] + 1) / 2 * n - 0.5).astype(int)
        iy = np.rint((1 - xy[:, 1]) / 2 * n - 0.5).astype(int)
        inten = np.broadcast_to(np.asarray(intensity, dtype=float), (len(xy),))
        colors = rgb * inten[:, None]
        dx, dy, weight = self._kernel(radius_px)
        x = ix[:, None] + dx[None, :]
        y = iy[:, None] + dy[None, :]
        ok = (x >= 0) & (x < n) & (y >= 0) & (y < n)
        index = (y * n + x)[ok]
        flat = buffer.reshape(-1, 3)
        for c in range(3):
            w = (colors[:, c:c + 1] * weight[None, :])[ok]
            flat[:, c] += np.bincount(index, weights=w, minlength=n * n)

    def line(self, buffer, a, b, rgb, radius_px, intensity, samples: int = 12) -> None:
        t = np.linspace(0, 1, samples)[:, None]
        self.splat(buffer, a[None, :] * (1 - t) + b[None, :] * t,
                   np.broadcast_to(rgb, (samples, 3)), radius_px, intensity / samples * 3)


def expose(light: np.ndarray) -> np.ndarray:
    """Film-like saturation of additive light: 1 − e^(−L)."""

    return 1 - np.exp(-np.maximum(light, 0))


def to_rgba(rgb_light: np.ndarray, mask: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Light on black → straight RGBA whose alpha is the light's brightness."""

    alpha = rgb_light.max(axis=2)
    rgb = np.divide(rgb_light, alpha[..., None], out=np.zeros_like(rgb_light),
                    where=alpha[..., None] > 1e-6)
    return rgba(rgb, alpha * mask * opacity)


# ---------------------------------------------------------------------------
# The primordial field and inflation
# ---------------------------------------------------------------------------
LAMBDA_BORN = 0.35        # window wavelength at which a ripple leaves the horizon
FINE_LAYERS = 6           # octaves finer than P, visible only while zoomed in
N_END = math.log(LAMBDA_BORN / (1.41421356 / 2**12)) + 0.9   # e-folds shown


@dataclass
class Layer:
    """One octave of the primordial field, periodic on [-R, R]², as an analytic signal."""

    values: np.ndarray        # complex; real part is the ripple
    half_width: float         # R in comoving units (P's domain is R = 1)
    wavelength: float         # comoving

    def birth(self) -> float:
        """Inflation time (e-folds) when the ripple's size equals the horizon."""

        return math.log(LAMBDA_BORN / self.wavelength)

    def sample(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        r = self.half_width
        return (sample_periodic(self.values.real, x / r, y / r),
                sample_periodic(self.values.imag, x / r, y / r))


class Universe:
    """One periodic primordial field P and every texture grown from it."""

    def __init__(self, seed: int = 1989, n: int = 512) -> None:
        raw = physics.gaussian_field(n, seed, tilt=physics.N_S)
        freq = np.fft.fftfreq(n) * n                      # cycles per domain
        kx, ky = np.meshgrid(freq, freq)
        k = np.sqrt(kx**2 + ky**2)
        spectrum = np.fft.fft2(raw) * (k <= 128)          # what 360 px can show
        primordial = np.fft.ifft2(spectrum).real
        self.mean, self.std = primordial.mean(), primordial.std()
        self.P = (primordial - self.mean) / self.std
        spectrum = np.fft.fft2(self.P)
        one_sided = np.where(kx > 0, 2.0, np.where(kx == 0, 1.0, 0.0))
        edges = (0.5, 2, 4, 8, 16, 32, 64, 129)
        self.layers: list[Layer] = []
        for low, high in zip(edges[:-1], edges[1:], strict=True):
            mask = (k >= low) & (k < high)
            band = spectrum * mask * one_sided
            if high > 100:
                # The finest band is magnified most while zoomed in: resample it at
                # twice the resolution (exact Fourier interpolation, no content > k 128).
                band = 4 * np.fft.ifftshift(np.pad(np.fft.fftshift(band), n // 2))
            self.layers.append(Layer(np.fft.ifft2(band), 1.0,
                                     2 / math.sqrt(max(low, 1) * high)))
        self.layers += self._finer_layers(seed, self.layers[-1])
        self.n = n
        self.x, self.y = window_coords()
        self.mask = vignette()
        self._cmb = None
        self._web = None

    @staticmethod
    def _finer_layers(seed: int, last: Layer) -> list[Layer]:
        """Octaves below P's resolution, same spectrum: variance ratio 2^(n_s − 1) per octave.

        Each lives on a patch of 48 wavelengths around the centre, which is all a
        zoomed-in view ever shows before the ripple shrinks below a pixel.
        """

        rng = np.random.default_rng(seed + 1)
        m = 768
        freq = np.fft.fftfreq(m) * m
        kx, ky = np.meshgrid(freq, freq)
        k = np.sqrt(kx**2 + ky**2)
        one_sided = np.where(kx > 0, 2.0, np.where(kx == 0, 1.0, 0.0))
        target = float(np.var(last.values.real))
        layers = []
        for j in range(1, FINE_LAYERS + 1):
            wavelength = last.wavelength / 2**j
            half_width = min(1.0, 48 * wavelength)
            cycles = 2 * half_width / wavelength
            mask = (k >= cycles / math.sqrt(2)) & (k < cycles * math.sqrt(2))
            noise = np.fft.fft2(rng.normal(size=(m, m)))
            values = np.fft.ifft2(noise * mask * one_sided)
            values *= math.sqrt(target * 2 ** (j * (physics.N_S - 1)) / np.var(values.real))
            layers.append(Layer(values, half_width, wavelength))
        return layers

    # -- inflation -----------------------------------------------------------
    def view_field(self, width: float, efolds: float | None = None) -> np.ndarray:
        """The field seen in a window of comoving half-width `width`.

        During inflation (`efolds` given, width = e^(−efolds)) each ripple is
        born as a twinkling quantum jitter when its size reaches the horizon,
        then freezes and is stretched. With `efolds` None every ripple is frozen;
        at width = 1 the view is exactly P.
        """

        pixel = 2 / SIZE
        total = np.zeros_like(self.x)
        for layer in self.layers:
            size_px = layer.wavelength / width / pixel
            amplitude = float(smoothstep((size_px - 2.0) / 1.9))
            phase = 0.0
            if efolds is not None:
                age = efolds - layer.birth()
                amplitude *= float(smoothstep((age + 0.5) / 0.5))
                phase = 3.5 * max(0.0, 0.6 - age)
            if amplitude <= 0:
                continue
            if layer.wavelength / width > 200:
                re, im = layer.sample(np.zeros(1), np.zeros(1))
            else:
                re, im = layer.sample(self.x * width, self.y * width)
            total = total + amplitude * (re * math.cos(phase) - im * math.sin(phase))
        return total

    def grid_light(self, width: float) -> np.ndarray:
        """Comoving grid lines at every scale that is currently legible in the window."""

        light = np.zeros((SIZE, SIZE))
        for m in range(0, 16):
            spacing = 0.5 * 2.0**-m / width
            alpha = ramp(spacing, 0.05, 0.16) * (1 - ramp(spacing, 0.9, 1.8))
            if alpha <= 0.01:
                continue
            count = int(1 / spacing)
            for k in range(-count, count + 1):
                pix = int(round((k * spacing + 1) / 2 * SIZE - 0.5))
                if 0 <= pix < SIZE:
                    light[:, pix] += alpha
                    light[SIZE - 1 - pix, :] += alpha
        return np.minimum(light, 1.0)

    def field_rgb(self, field: np.ndarray, heat: float = 0.0, temperature: float = 1.0):
        cool = colormap(0.5 + 0.3 * field, CMAP_FIELD)
        if heat <= 0:
            return cool
        hot = colormap(0.5 + 0.16 * field, CMAP_HOT) * temperature
        return (1 - heat) * cool + heat * hot

    def paint_inflation(self, efolds: float, grid: float = 1.0) -> np.ndarray:
        width = math.exp(-efolds)
        rgb = self.field_rgb(self.view_field(width, efolds))
        if grid > 0:
            lines = self.grid_light(width)[..., None] * grid * 0.45
            rgb = np.clip(rgb + lines * hex_rgb("#bfdbfe"), 0, 1)
        return rgba(rgb, self.mask)

    def paint_widening(self, width: float) -> np.ndarray:
        """After inflation: the frozen pattern, seen in an ever wider window."""

        return rgba(self.field_rgb(self.view_field(width)), self.mask)

    # -- CMB -------------------------------------------------------------------
    def cmb(self) -> np.ndarray:
        """Temperature map: P times an approximate acoustic transfer (not a Boltzmann code).

        T(k) = [1 + 2.2 G(k; 26, 12) + 0.9 G(k; 60, 14)] e^(−(k/95)²), G a Gaussian bump:
        a Sachs–Wolfe plateau, two acoustic peaks and Silk damping, in shape only.
        """

        if self._cmb is None:
            n = self.n
            freq = np.fft.fftfreq(n) * n
            kx, ky = np.meshgrid(freq, freq)
            k = np.sqrt(kx**2 + ky**2)
            transfer = (1 + 2.2 * np.exp(-(((k - 26) / 12) ** 2))
                        + 0.9 * np.exp(-(((k - 60) / 14) ** 2))) * np.exp(-((k / 95) ** 2))
            transfer[0, 0] = 0
            t = np.fft.ifft2(np.fft.fft2(self.P) * transfer).real
            self._cmb = (t - t.mean()) / t.std()
        return self._cmb

    def cmb_rgb(self) -> np.ndarray:
        return colormap(0.5 + 0.22 * sample_periodic(self.cmb(), self.x, self.y), CMAP_CMB)

    # -- cosmic web --------------------------------------------------------------
    def displacement(self) -> tuple[np.ndarray, np.ndarray]:
        """Zel'dovich ψ = −∇φ, ∇²φ = δ, with δ from the primordial potential P.

        Poisson: δ_k = −k² P_k T(k), with an approximate CDM transfer
        T(k) = 1 / (1 + (k/k_eq)²), k_eq = 6 cycles per window (BBKS-like shape, not
        a Boltzmann solution) and a smoothing e^(−(k/22)²) for the nonlinear scale.
        Normalized so that the linear divergence has unit spread at growth D = 1.
        """

        n = self.n
        freq = np.fft.fftfreq(n) * n
        kx, ky = np.meshgrid(freq, freq)
        k = np.sqrt(kx**2 + ky**2)
        transfer = np.exp(-((k / 22) ** 2)) / (1 + (k / 6) ** 2)
        matter = np.fft.ifft2(-(k**2) * np.fft.fft2(self.P) * transfer).real
        # physics returns (row, column) components in grid units; convert to window units
        psi_rows, psi_cols = physics.zeldovich_displacement(matter)
        psi_rows, psi_cols = psi_rows * 2 / n, psi_cols * 2 / n
        divergence = np.gradient(psi_rows, 2 / n, axis=0) + np.gradient(psi_cols, 2 / n, axis=1)
        spread = float(np.std(divergence))
        return psi_rows / spread, psi_cols / spread

    def web_particles(self, growth: float, count: int = 480) -> np.ndarray:
        """x = q + D ψ(q) for a lattice q of count² particles (window units, periodic)."""

        if self._web is None:
            psi_rows, psi_cols = self.displacement()
            c = (np.arange(count) + 0.5) / count * 2 - 1
            qx, qy = np.meshgrid(c, -c)
            # rows run downward: x moves with the column component, y against the row one
            px = sample_periodic(psi_cols, qx, qy)
            py = -sample_periodic(psi_rows, qx, qy)
            self._web = (qx.ravel(), qy.ravel(), px.ravel(), py.ravel())
        qx, qy, px, py = self._web
        scale = 1.0
        return np.column_stack([qx + growth * scale * px, qy + growth * scale * py])

    @staticmethod
    def density(points: np.ndarray, size: int = SIZE, blur: float = 1.4,
                zoom: float = 1.0, center=(0.0, 0.0)) -> np.ndarray:
        """Particle counts per pixel in a view of half-width 1/zoom around `center`."""

        rel = (points - np.asarray(center)) * zoom
        rel = (rel + 1) % 2 - 1 if zoom <= 1.0 else rel
        hist, _, _ = np.histogram2d(-rel[:, 1], rel[:, 0], bins=size,
                                    range=[[-1, 1], [-1, 1]])
        hist = ndimage.gaussian_filter(hist, blur)
        mean = len(points) * (zoom**-2 if zoom > 1 else 1) / size**2
        return hist / max(mean, 1e-9)


# ---------------------------------------------------------------------------
# The hot soup: reheating → recombination on one schedule of soup time τ
# ---------------------------------------------------------------------------
EW = (18.0, 26.0)
HEAVY_DECAY = (27.0, 33.0)
ANNIHILATE = (38.0, 44.0)
GLUON_FADE = (44.0, 50.0)
BIND = (44.0, 52.0)
NU_FREE = 62.0
WEAK = (61.0, 68.0)
LAST_DECAY = 71.0
POSITRON = (63.0, 70.0)
FUSE = (74.0, 84.0)
RECOMBINE = (92.0, 104.0)
DECOUPLE = 100.0
CLEAR = (104.0, 113.0)
TAU_END = 115.0

QUARK_COLORS = ("#ef4444", "#22c55e", "#3b82f6")
ANTIQUARK_COLORS = ("#22d3ee", "#d946ef", "#facc15")
PROTON, NEUTRON = "#fecdd3", "#94a3b8"


@dataclass
class Species:
    name: str
    color: np.ndarray            # (n, 3)
    radius: float                # pixels
    brightness: float
    base: np.ndarray             # (n, 2)
    slow: float                  # fraction of speed lost once the Higgs field is on


class Soup:
    """Every particle's position and brightness as a pure function of soup time τ."""

    def __init__(self, universe: Universe, seed: int = 7) -> None:
        self.u = universe
        rng = np.random.default_rng(seed)
        self.rng_seed = seed
        self.nucleons = self._nucleon_sites(rng)
        n_nuc = len(self.nucleons)
        # Quarks: three survivors per nucleon (one per colour) + 30 losers per colour.
        survivors, losers = [], []
        for k in range(n_nuc):
            for c in range(3):
                survivors.append((self.nucleons[k] + rng.normal(0, 0.06, 2), c, k))
        for c in range(3):
            for _ in range(30):
                losers.append((rng.uniform(-0.95, 0.95, 2), c))
        self.q_pos = np.array([s[0] for s in survivors] + [lo[0] for lo in losers])
        self.q_col = np.array([s[1] for s in survivors] + [lo[1] for lo in losers])
        self.q_nucleon = np.array([s[2] for s in survivors] + [-1] * len(losers))
        self.q_survivor = np.array([True] * len(survivors) + [False] * len(losers))
        loser_index = np.arange(len(survivors), len(survivors) + len(losers))
        self.aq_pos = self.q_pos[loser_index] + rng.normal(0, 0.05, (len(losers), 2))
        self.aq_col = self.q_col[loser_index]
        self.aq_partner = loser_index
        self.pair_time = rng.uniform(ANNIHILATE[0] + 1.2, ANNIHILATE[1], len(losers))
        # Bosons and leptons.
        self.gluons = rng.uniform(-1, 1, (120, 2))
        self.heavy = rng.uniform(-1, 1, (60, 2))
        self.heavy_time = rng.uniform(*HEAVY_DECAY, 60)
        self.photons = rng.uniform(-1, 1, (320, 2))
        self.photon_dir = _unit(rng, 320)
        self.neutrinos = rng.uniform(-1, 1, (140, 2))
        self.nu_dir = _unit(rng, 140)
        # Electrons: 28 bound later (one per proton charge), 100 annihilate with positrons.
        self.nuclei = self._nuclei()
        hosts = []
        for k, (_, charge) in enumerate(self.nuclei):
            hosts += [k] * charge
        self.e_host = np.array(hosts + [-1] * 100)
        bound = [self.nuclei[h][0] + rng.normal(0, 0.12, 2) for h in hosts]
        free = list(rng.uniform(-0.95, 0.95, (100, 2)))
        self.e_pos = np.array(bound + free)
        self.pos_pos = np.array(free) + rng.normal(0, 0.05, (100, 2))
        self.pos_time = rng.uniform(POSITRON[0] + 1.0, POSITRON[1], 100)
        # Jiggle parameters per particle family (3 sinusoids per axis).
        self._jiggle: dict[str, tuple] = {}
        for name, count in (("q", len(self.q_pos)), ("aq", len(self.aq_pos)),
                            ("g", 120), ("h", 60), ("ph", 320), ("nu", 140),
                            ("e", len(self.e_pos)), ("p", 100), ("n", n_nuc)):
            amp = rng.uniform(0.02, 0.05, (count, 2, 3))
            freq = rng.uniform(0.8, 2.6, (count, 1, 3))
            phase = rng.uniform(0, 2 * math.pi, (count, 2, 3))
            self._jiggle[name] = (amp, freq, phase)
        self.births = {name: rng.uniform(0.4, 4.0, count)
                       for name, count in (("q", len(self.q_pos)), ("aq", len(self.aq_pos)),
                                           ("g", 120), ("h", 60), ("ph", 320), ("nu", 140),
                                           ("e", len(self.e_pos)), ("p", 100))}
        # Weak interactions: 11 of 16 neutrons become protons, one more decays later.
        neutrons = [k for k in range(n_nuc) if self.neutron_initial[k]]
        self.flip_time = np.full(n_nuc, np.inf)
        for j, k in enumerate(neutrons[:11]):
            self.flip_time[k] = WEAK[0] + (WEAK[1] - WEAK[0]) * j / 11
        self.flip_time[neutrons[11]] = LAST_DECAY
        self.raster = Raster()
        self._ew_grid = np.linspace(0, TAU_END, 4001)
        self._ew_cumulative = np.concatenate([[0], np.cumsum(
            [ramp(t, *EW) for t in self._ew_grid[1:]]) * (self._ew_grid[1] - self._ew_grid[0])])

    # -- construction helpers ------------------------------------------------------
    def _nucleon_sites(self, rng) -> np.ndarray:
        """32 nucleon sites, preferring over-dense regions of P (baryons trace density)."""

        sites = []
        while len(sites) < 32:
            p = rng.uniform(-0.85, 0.85, 2)
            delta = float(sample_periodic(self.u.P, np.array([p[0]]), np.array([p[1]]))[0])
            if rng.uniform() > 0.5 + 0.25 * delta:
                continue
            if all(np.linalg.norm(p - s) > 0.22 for s in sites):
                sites.append(p)
        sites = np.array(sites)
        self.neutron_initial = np.array([k % 2 == 1 for k in range(32)])
        return sites

    def _nuclei(self) -> list[tuple[np.ndarray, int]]:
        """Final nuclei after fusion: 2 helium-4 (from the 4 last neutrons) + 24 protons."""

        neutrons = [k for k in range(32) if self.neutron_initial[k]]
        last = neutrons[12:]                      # 4 neutrons that survive to fusion
        protons_left = [k for k in range(32) if k not in last]
        groups = []
        used: set[int] = set()
        for pair in (last[:2], last[2:]):
            center = self.nucleons[pair].mean(axis=0)
            near = sorted((k for k in protons_left if k not in used),
                          key=lambda k: np.linalg.norm(self.nucleons[k] - center))[:2]
            used.update(near)
            groups.append(list(pair) + near)
        self.helium = groups
        self.helium_center = [self.nucleons[g].mean(axis=0) for g in groups]
        nuclei = [(c, 2) for c in self.helium_center]
        nuclei += [(self.nucleons[k], 1) for k in range(32)
                   if all(k not in g for g in groups)]
        return nuclei

    # -- motion ----------------------------------------------------------------------
    def higgs(self, tau: float) -> float:
        return ramp(tau, *EW)

    def proper_time(self, tau: float, slow: float) -> float:
        """∫ speed dτ with speed = 1 − slow·h(τ): massive particles slow down."""

        return tau - slow * float(np.interp(tau, self._ew_grid, self._ew_cumulative))

    def jiggle(self, name: str, base: np.ndarray, tau: float, slow: float = 0.0,
               scale: float = 1.0) -> np.ndarray:
        amp, freq, phase = self._jiggle[name]
        t = self.proper_time(tau, slow)
        offset = (amp * np.sin(freq * t * 2.2 + phase)).sum(axis=2) * scale
        return _wrap(base + offset)

    def nucleon_center(self, k: int, tau: float) -> np.ndarray:
        amp, freq, phase = self._jiggle["n"]
        offset = (0.5 * amp[k] * np.sin(freq[k] * tau * 0.8 + phase[k])).sum(axis=1)
        center = self.nucleons[k] + offset
        for g, group in enumerate(self.helium):
            if k in group:
                slot = group.index(k)
                angle = slot * math.pi / 2 + 0.6 * tau
                target = self.helium_center[g] + 0.022 * np.array([math.cos(angle),
                                                                     math.sin(angle)])
                center = (1 - ramp(tau, *FUSE)) * center + ramp(tau, *FUSE) * target
        return center

    def is_neutron(self, k: int, tau: float) -> float:
        if not self.neutron_initial[k]:
            return 0.0
        if not math.isfinite(self.flip_time[k]):
            return 1.0
        return 1.0 - ramp(tau, self.flip_time[k] - 0.8, self.flip_time[k] + 0.8)

    # -- painting --------------------------------------------------------------------
    def paint(self, tau: float) -> np.ndarray:
        r = self.raster
        light = r.blank()
        fade_all = 1 - ramp(tau, *CLEAR)
        born = {k: smoothstep((tau - b) / 0.6) for k, b in self.births.items()}
        if fade_all > 0:
            self._paint_particles(tau, light, born, fade_all)
        # Background: the primordial pattern, heated by reheating, cooling with time.
        heat = ramp(tau, 0.0, 5.0)
        temperature = 1.0 - 0.45 * ramp(tau, 5.0, 100.0)
        field = (1 - heat) * self.u.P_window() + heat * self.u.P_smooth()
        background = self.u.field_rgb(field, heat, temperature)
        bg_strength = 1.0 - 0.62 * heat
        # Recombination haze: the photon-baryon fluid glows, then turns into the CMB.
        xe = 1 - ramp(tau, *RECOMBINE)
        reveal = ramp(tau, 98.0, 110.0)
        haze_rgb = colormap(0.62 + 0.12 * field, CMAP_HOT)
        cmb = self.u.cmb_rgb()
        haze_color = (1 - reveal) * haze_rgb + reveal * cmb
        haze = max(0.55 * ramp(tau, 84.0, 92.0) * xe, reveal)
        base_rgb = background * bg_strength * (1 - haze) * (1 - reveal)
        rgb = base_rgb + haze_color * haze
        rgb = np.clip(rgb + expose(light) * (1 - 0.5 * reveal), 0, 1)
        return rgba(rgb, self.u.mask)

    def _paint_particles(self, tau, light, born, fade) -> None:
        r = self.raster
        h = self.higgs(tau)
        bind = ramp(tau, *BIND)
        # Quarks and antiquarks.
        qx = self.jiggle("q", self.q_pos, tau, slow=0.15)
        ax = self.jiggle("aq", self.aq_pos, tau, slow=0.15)
        q_light = born["q"] * fade
        aq_light = born["aq"] * fade
        loser = ~self.q_survivor
        # losers meet their antiquark and vanish in a flash
        partner_time = np.full(len(self.q_pos), np.inf)
        partner_time[self.aq_partner] = self.pair_time
        meet = np.clip((tau - (partner_time - 1.2)) / 1.2, 0, 1)
        gone = tau > partner_time
        qx_meet = qx.copy()
        mid = 0.5 * (qx[self.aq_partner] + ax)
        qx_meet[self.aq_partner] = (1 - meet[self.aq_partner, None]) * qx[self.aq_partner] \
            + meet[self.aq_partner, None] * mid
        ax = (1 - meet[self.aq_partner, None]) * ax + meet[self.aq_partner, None] * mid
        flash = np.array([bump(tau, t, 0.25) for t in self.pair_time])
        q_int = np.where(loser & gone, 0.0, 1.0) * q_light
        aq_int = np.where(tau > self.pair_time, 0.0, 1.0) * aq_light
        # survivors gather into nucleons
        if bind > 0:
            for i in np.nonzero(self.q_survivor)[0]:
                k = self.q_nucleon[i]
                angle = self.q_col[i] * 2 * math.pi / 3 + 2.5 * tau
                inner = self.nucleon_center(k, tau) + 0.03 * np.array([math.cos(angle),
                                                                        math.sin(angle)])
                qx_meet[i] = (1 - bind) * qx_meet[i] + bind * inner
        q_rgb = np.array([hex_rgb(QUARK_COLORS[c]) for c in self.q_col])
        aq_rgb = np.array([hex_rgb(ANTIQUARK_COLORS[c]) for c in self.aq_col])
        quark_radius = 2.1 * (1 - 0.35 * bind)
        r.splat(light, qx_meet, q_rgb, quark_radius, q_int * (0.9 - 0.3 * bind))
        r.splat(light, ax, aq_rgb, 2.0, aq_int * 0.75)
        r.splat(light, mid, np.broadcast_to(hex_rgb("#fef9c3"), (len(mid), 3)), 2.6,
                flash * 1.6 * fade)
        # Nucleons glow once bound.
        if bind > 0:
            centers = np.array([self.nucleon_center(k, tau) for k in range(32)])
            neutron = np.array([self.is_neutron(k, tau) for k in range(32)])
            color = (neutron[:, None] * hex_rgb(NEUTRON)
                     + (1 - neutron[:, None]) * hex_rgb(PROTON))
            r.splat(light, centers, color, 4.2, 0.6 * bind * fade)
            fuse = ramp(tau, *FUSE)
            if fuse > 0:
                he = np.array(self.helium_center)
                r.splat(light, he, np.broadcast_to(hex_rgb("#fde68a"), (2, 3)), 6.0,
                        0.6 * fuse * fade)
        # Gluons, heavy bosons, photons, neutrinos, electrons, positrons.
        gl = self.jiggle("g", self.gluons, tau)
        r.splat(light, gl, np.broadcast_to(hex_rgb("#f9a8d4"), (120, 3)), 1.4,
                born["g"] * (1 - ramp(tau, *GLUON_FADE)) * 0.7 * fade)
        hv = self.jiggle("h", self.heavy, tau, slow=0.7)
        alive = np.where(tau < self.heavy_time, 1.0, 0.0)
        hflash = np.array([bump(tau, t, 0.25) for t in self.heavy_time])
        r.splat(light, hv, np.broadcast_to(hex_rgb("#a78bfa"), (60, 3)), 2.0 + 1.2 * h,
                born["h"] * alive * fade)
        r.splat(light, hv, np.broadcast_to(hex_rgb("#fef9c3"), (60, 3)), 2.4,
                hflash * 1.4 * fade)
        ph = self.jiggle("ph", self.photons, tau)
        if tau > DECOUPLE:
            start = self.jiggle("ph", self.photons, DECOUPLE)
            ph = _wrap(start + self.photon_dir * 0.32 * (tau - DECOUPLE))
        r.splat(light, ph, np.broadcast_to(hex_rgb("#fef08a"), (320, 3)), 1.4,
                born["ph"] * 0.7 * fade)
        nu = self.jiggle("nu", self.neutrinos, tau)
        if tau > NU_FREE:
            start = self.jiggle("nu", self.neutrinos, NU_FREE)
            nu = _wrap(start + self.nu_dir * 0.3 * (tau - NU_FREE))
        r.splat(light, nu, np.broadcast_to(hex_rgb("#64748b"), (140, 3)), 1.3,
                born["nu"] * 0.6 * fade)
        ex = self.jiggle("e", self.e_pos, tau, slow=0.05)
        px = self.jiggle("p", self.pos_pos, tau, slow=0.05)
        free = np.arange(len(self.e_pos)) >= 28
        pos_meet = np.clip((tau - (self.pos_time - 1.0)) / 1.0, 0, 1)[:, None]
        mid_e = 0.5 * (ex[free] + px)
        ex[free] = (1 - pos_meet) * ex[free] + pos_meet * mid_e
        px = (1 - pos_meet) * px + pos_meet * mid_e
        e_int = np.ones(len(self.e_pos))
        e_int[free] = np.where(tau > self.pos_time, 0.0, 1.0)
        capture = ramp(tau, *RECOMBINE)
        if capture > 0:
            for i in range(28):
                host = self.nuclei[self.e_host[i]][0]
                angle = 3.0 * tau + i
                orbit = host + 0.045 * np.array([math.cos(angle), math.sin(angle)])
                ex[i] = (1 - capture) * ex[i] + capture * orbit
        r.splat(light, ex, np.broadcast_to(hex_rgb("#93c5fd"), (len(ex), 3)), 1.6,
                born["e"] * e_int * 0.9 * fade)
        r.splat(light, px, np.broadcast_to(hex_rgb("#fdba74"), (len(px), 3)), 1.6,
                born["p"] * np.where(tau > self.pos_time, 0.0, 1.0) * 0.9 * fade)
        pflash = np.array([bump(tau, t, 0.25) for t in self.pos_time])
        r.splat(light, mid_e, np.broadcast_to(hex_rgb("#fef9c3"), (100, 3)), 2.2,
                pflash * 1.2 * fade)


def _unit(rng, n: int) -> np.ndarray:
    angle = rng.uniform(0, 2 * math.pi, n)
    return np.column_stack([np.cos(angle), np.sin(angle)])


def _wrap(points: np.ndarray) -> np.ndarray:
    return (points + 1) % 2 - 1


# ---------------------------------------------------------------------------
# Galaxy
# ---------------------------------------------------------------------------
class Galaxy:
    """A two-armed logarithmic spiral (pitch 12°) condensing from a gas cloud."""

    def __init__(self, seed: int = 3, stars: int = 9000) -> None:
        rng = np.random.default_rng(seed)
        spiral = physics.spiral_galaxy(stars, seed, arms=2, pitch_deg=12.0, scale=0.33)
        self.spiral = spiral * 0.55
        n = len(self.spiral)
        self.cloud = rng.normal(0, 0.32, (n, 2))
        radius = np.linalg.norm(self.spiral, axis=1)
        young = rng.uniform(size=n) < 0.55
        self.color = np.where(young[:, None], hex_rgb("#bfdbfe"), hex_rgb("#fde68a"))
        self.color[radius < 0.12] = hex_rgb("#fff7ed")
        self.brightness = 0.5 + 0.6 * np.exp(-radius / 0.15)
        self.raster = Raster()

    def positions(self, form: float, angle: float, center=(0.0, 0.0),
                  scale: float = 1.0) -> np.ndarray:
        p = (1 - form) * self.cloud + form * self.spiral
        c, s = math.cos(angle), math.sin(angle)
        p = p @ np.array([[c, s], [-s, c]])
        return np.asarray(center) + p * scale

    def paint(self, form: float, angle: float, opacity: float = 1.0,
              scale: float = 1.0, center=(0.0, 0.0)) -> np.ndarray:
        light = self.raster.blank()
        pts = self.positions(form, angle, center, scale)
        radius_px = max(0.8, 1.2 * min(1.0, scale ** 0.5))
        self.raster.splat(light, pts, self.color, radius_px, self.brightness * 0.28 * opacity)
        # Unresolved light of the disk and bulge.
        x, y = window_coords()
        rr = np.hypot(x - center[0], y - center[1]) / max(scale, 1e-3)
        glow = np.exp(-rr / 0.09) * 0.55 + np.exp(-rr / 0.35) * 0.12 * form
        light += glow[..., None] * hex_rgb("#fde68a") * opacity
        return light


def mask_disk(radius: float, soft: float = 0.02) -> np.ndarray:
    x, y = window_coords()
    return smoothstep((radius - np.hypot(x, y)) / soft)


def P_window_cache(universe: Universe) -> np.ndarray:
    """The frozen pattern exactly as the end of the widening shows it."""

    return universe.view_field(1.0)


def _p_window(self: Universe) -> np.ndarray:
    if getattr(self, "_p_window", None) is None:
        self._p_window = P_window_cache(self)
    return self._p_window


def _p_smooth(self: Universe) -> np.ndarray:
    if getattr(self, "_p_smooth", None) is None:
        self._p_smooth = ndimage.gaussian_filter(self.P_window(), 2.5, mode="wrap")
    return self._p_smooth


Universe.P_window = _p_window
Universe.P_smooth = _p_smooth


# ---------------------------------------------------------------------------
# Acts 12–14: the web, a galaxy and the horizons in one view
# ---------------------------------------------------------------------------
WINDOW_GLY = 1.0          # half-width of the full-pattern window, in billions of light-years


class Cosmos:
    """The late universe as one zoomable view: z > 1 dives into a node, z < 1 widens."""

    def __init__(self, universe: Universe, galaxy: Galaxy) -> None:
        self.u, self.g = universe, galaxy
        final = universe.web_particles(1.0)
        self.final_points = _wrap(final)
        self.final_density = universe.density(self.final_points)
        self.mips = [self.final_density] + [
            ndimage.gaussian_filter(self.final_density, s, mode="wrap")
            for s in (1, 2, 4, 8, 16, 32)]
        smooth = ndimage.gaussian_filter(self.final_density, 6, mode="wrap")
        x, y = universe.x, universe.y
        central = (np.abs(x) < 0.45) & (np.abs(y) < 0.45)
        k = int(np.argmax(np.where(central, smooth, -np.inf)))
        self.node = np.array([x.flat[k], y.flat[k]])
        lookup = ndimage.gaussian_filter(self.final_density, 1.5, mode="wrap")
        n = SIZE
        ix = np.clip(((self.final_points[:, 0] + 1) / 2 * n).astype(int), 0, n - 1)
        iy = np.clip(((1 - self.final_points[:, 1]) / 2 * n).astype(int), 0, n - 1)
        level = lookup[iy, ix]
        rng = np.random.default_rng(11)
        dense = np.nonzero(level > np.quantile(level, 0.985))[0]
        self.stars = rng.choice(dense, size=min(420, len(dense)), replace=False)
        self.star_twinkle = rng.uniform(0, 2 * math.pi, len(self.stars))
        self.raster = Raster()
        self.d_last_scattering = physics.comoving_distance_gly(1 / 1090.9)
        self.horizons = physics.horizons_gly()

    @staticmethod
    def web_rgb(density: np.ndarray) -> np.ndarray:
        value = np.log10(1 + density) / math.log10(1 + 60)
        return colormap(value, CMAP_WEB)

    def zoom_center(self, zoom: float) -> np.ndarray:
        """View centre: the chosen node moves smoothly to the middle as we dive in."""

        if zoom <= 1:
            return np.zeros(2)
        return self.node * (1 - 1 / zoom**2)

    def web_density(self, growth: float, zoom: float) -> np.ndarray:
        if zoom < 1:
            stride = 1 / zoom
            level = min(len(self.mips) - 1.001, max(0.0, math.log2(max(stride, 1.0))))
            low = int(level)
            frac = level - low
            xs, ys = self.u.x / zoom, self.u.y / zoom
            a = sample_periodic(self.mips[low], xs, ys)
            b = sample_periodic(self.mips[low + 1], xs, ys)
            return (1 - frac) * a + frac * b
        points = _wrap(self.u.web_particles(growth))
        if zoom == 1:
            return self.u.density(points)
        return self.u.density(points, blur=1.4 * zoom**0.5, zoom=zoom,
                              center=self.zoom_center(zoom))

    def to_view(self, points: np.ndarray, zoom: float) -> np.ndarray:
        return (points - self.zoom_center(zoom)) * zoom

    def paint(self, growth: float = 1.0, cmb: float = 0.0, zoom: float = 1.0,
              web: float = 1.0, stars: float = 0.0, galaxy: float = 0.0,
              form: float = 0.0, angle: float = 0.0, horizon: float = 0.0,
              twinkle: float = 0.0) -> np.ndarray:
        rgb = np.zeros((SIZE, SIZE, 3))
        if cmb > 0:
            redden = colormap(0.5 + 0.22 * sample_periodic(self.u.cmb(), self.u.x, self.u.y),
                              CMAP_CMB)
            rgb += redden * cmb
        if web > 0:
            rgb += self.web_rgb(self.web_density(growth, zoom)) * web
        light = self.raster.blank()
        if stars > 0 and zoom >= 1:
            pts = _wrap(self.u.web_particles(growth))[self.stars]
            view = self.to_view(pts, zoom)
            shimmer = 0.75 + 0.25 * np.sin(self.star_twinkle + 6 * twinkle)
            self.raster.splat(light, view, np.broadcast_to(hex_rgb("#fff7ed"),
                                                           (len(view), 3)),
                              1.6, stars * shimmer * 1.3)
        if galaxy > 0:
            gscale = zoom / GALAXY_ZOOM
            center = self.to_view(self.node[None, :], zoom)[0] if zoom >= 1 else \
                self.node * zoom
            light += self.g.paint(form, angle, galaxy, gscale, center)
        rgb = rgb + expose(light)
        alpha = self.u.mask.copy()
        if horizon > 0 and zoom < 1:
            rgb, alpha = self._horizon(rgb, alpha, zoom, horizon)
        return rgba(np.clip(rgb, 0, 1), alpha)

    def _horizon(self, rgb, alpha, zoom, strength):
        """Dark beyond the particle horizon; the last-scattering shell glows just inside."""

        gly_per_unit = WINDOW_GLY / zoom
        r = np.hypot(self.u.x, self.u.y) * gly_per_unit
        particle = self.horizons["particle"]
        inside = smoothstep((particle - r) / (0.012 * gly_per_unit))
        shell = np.exp(-(((r - self.d_last_scattering) / (0.018 * gly_per_unit)) ** 2))
        theta = np.arctan2(self.u.y, self.u.x)
        ring = colormap(0.5 + 0.25 * sample_periodic(self.u.cmb(), 0.95 * np.cos(theta),
                                                     0.95 * np.sin(theta)), CMAP_CMB)
        keep = (1 - strength) + strength * inside
        rgb = rgb * keep[..., None] + ring * (shell * strength)[..., None] * 1.1
        return rgb, alpha * np.maximum(keep, shell * strength)


GALAXY_ZOOM = 7.0
