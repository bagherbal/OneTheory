"""Reusable drawing builders for the Genesis film.

Owns:
    Colour maps, a NumPy particle rasterizer, live (per-frame repainted)
    images, the E8 Petrie diagram, chained real slices of the Hesse cubic,
    orthographic 3D wireframes (torus, sphere) and the extended E8 Dynkin
    diagram. Every shape is computed from `physics.py`.

Depends on:
    Manim Community, NumPy and the film's `physics` and `stage` modules.

Must not:
    Invent shapes that `physics.py` does not compute, or use time-dependent
    updaters: every updater reads a ValueTracker, so skipped and rendered
    sections end in the same state.

Phase 0:
    Presentation layer only.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np
import physics
from manim import (
    RESAMPLING_ALGORITHMS,
    Circle,
    Dot,
    ImageMobject,
    Line,
    VGroup,
    VMobject,
    color_to_rgb,
)
from stage import CENTER, INK, MUTED, text

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
LIGHT = "#fff3d6"
E8_COLOR = "#a78bfa"
SU4_COLOR = "#fb923c"
SPIN10_COLOR = "#22d3ee"
HIGGS10_COLOR = "#64748b"
MATTER_COLOR = "#f472b6"
ANTIMATTER_COLOR = "#e879f9"
STRING_COLOR = "#fde68a"
FIELD_COLORS = {
    "Q": "#f87171", "u^c": "#fb923c", "d^c": "#facc15",
    "L": "#4ade80", "e^c": "#38bdf8", "ν^c": "#c4b5fd",
}
QUARK_RGB = ("#ef4444", "#22c55e", "#3b82f6")

CMAP_FIELD = ((0, "#020617"), (0.3, "#172554"), (0.55, "#1d4ed8"), (0.75, "#38bdf8"),
              (0.9, "#e0f2fe"), (1, "#ffffff"))
CMAP_CMB = ((0, "#0a1a5c"), (0.25, "#1d4ed8"), (0.45, "#93c5fd"), (0.55, "#fde68a"),
            (0.75, "#f97316"), (1, "#991b1b"))
CMAP_HOT = ((0, "#000000"), (0.3, "#7c2d12"), (0.6, "#f97316"), (0.85, "#fde68a"),
            (1, "#ffffff"))
CMAP_WEB = ((0, "#000000"), (0.2, "#120c2e"), (0.45, "#5b21b6"), (0.7, "#db2777"),
            (0.88, "#fdba74"), (1, "#fffbeb"))


def hex_rgb(color: str) -> np.ndarray:
    return np.asarray(color_to_rgb(color), dtype=float)


def colormap(values: np.ndarray, stops) -> np.ndarray:
    """Piecewise-linear colour map: values in [0,1] → RGB floats."""

    positions = np.array([s[0] for s in stops], dtype=float)
    colors = np.array([hex_rgb(s[1]) for s in stops])
    v = np.clip(values, 0, 1)
    out = np.empty((*v.shape, 3))
    for c in range(3):
        out[..., c] = np.interp(v, positions, colors[:, c])
    return out


def rgba(rgb: np.ndarray, alpha: np.ndarray | float = 1.0) -> np.ndarray:
    a = np.broadcast_to(np.asarray(alpha, dtype=float), rgb.shape[:2])
    out = np.empty((*rgb.shape[:2], 4), dtype=np.uint8)
    out[..., :3] = np.clip(rgb * 255, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return out


def field_image(field: np.ndarray, stops, contrast: float = 0.32,
                alpha: np.ndarray | float = 1.0) -> np.ndarray:
    """A standardized field mapped through a colour map (mean → 0.5)."""

    return rgba(colormap(0.5 + contrast * field, stops), alpha)


# ---------------------------------------------------------------------------
# Raster particles and live images
# ---------------------------------------------------------------------------
class Raster:
    """Additive Gaussian splats of particles onto a square RGBA canvas.

    The canvas covers [-extent, extent]² in scene units around its centre.
    Overlapping light saturates softly (1 − e^−x), like film exposure.
    """

    def __init__(self, size: int, extent: float) -> None:
        self.size, self.extent = size, extent
        self._kernels: dict[float, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    def _kernel(self, radius_px: float):
        key = round(radius_px, 2)
        if key not in self._kernels:
            half = max(1, int(math.ceil(2.5 * radius_px)))
            dy, dx = np.mgrid[-half:half + 1, -half:half + 1]
            weight = np.exp(-(dx**2 + dy**2) / (2 * radius_px**2))
            self._kernels[key] = (dx.ravel(), dy.ravel(), weight.ravel())
        return self._kernels[key]

    def accumulate(self, buffer: np.ndarray, xy: np.ndarray, rgb: np.ndarray,
                   radius_px: float, intensity: np.ndarray | float) -> None:
        if len(xy) == 0:
            return
        n = self.size
        px = (xy[:, 0] / self.extent * 0.5 + 0.5) * (n - 1)
        py = (0.5 - xy[:, 1] / self.extent * 0.5) * (n - 1)
        ix, iy = np.rint(px).astype(int), np.rint(py).astype(int)
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

    def blank(self) -> np.ndarray:
        return np.zeros((self.size, self.size, 3))

    @staticmethod
    def expose(buffer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        light = 1 - np.exp(-buffer)
        alpha = light.max(axis=2)
        rgb = np.divide(light, alpha[..., None], out=np.zeros_like(light),
                        where=alpha[..., None] > 1e-6)
        return rgba(rgb, alpha * opacity)


def image(array: np.ndarray, height: float, center=CENTER) -> ImageMobject:
    mob = ImageMobject(array)
    mob.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
    mob.height = height
    mob.move_to(center)
    return mob


def live_image(painter: Callable[[], np.ndarray], height: float,
               center=CENTER) -> ImageMobject:
    """An image repainted every frame by `painter`, which must read trackers only."""

    mob = image(painter(), height, center)

    def repaint(m: ImageMobject) -> None:
        m.pixel_array = painter()

    mob.add_updater(repaint)
    return mob


def radial_glow(size: int, sigma: float, color: str, peak: float = 1.0) -> np.ndarray:
    """|ψ₀|² ∝ exp(−r²/2σ²): the vacuum's probability cloud as an RGBA image."""

    y, x = np.mgrid[-1:1:size * 1j, -1:1:size * 1j]
    density = peak * np.exp(-(x**2 + y**2) / (2 * sigma**2))
    rgb = np.broadcast_to(hex_rgb(color), (size, size, 3)).copy()
    return rgba(rgb, np.clip(density, 0, 1))


# ---------------------------------------------------------------------------
# E8
# ---------------------------------------------------------------------------
E8_ROOTS = physics.e8_roots()
E8_PLANE = physics.project(E8_ROOTS)
E8_OUTER = float(np.linalg.norm(E8_PLANE, axis=1).max())
E8_SUBSETS = physics.root_subsets(E8_ROOTS)


def e8_points(radius: float, center=CENTER, rotation: float = 0.0) -> np.ndarray:
    c, s = math.cos(rotation), math.sin(rotation)
    xy = E8_PLANE / E8_OUTER * radius
    xy = xy @ np.array([[c, s], [-s, c]])
    return np.column_stack([xy, np.zeros(len(xy))]) + np.asarray(center)


def e8_edge_pairs(length_class: int = 0) -> np.ndarray:
    """Root pairs with inner product 1 whose projection has the k-th shortest length.

    The 6720 such edges fall into 8 projected-length classes of 840 each.
    """

    gram = E8_ROOTS @ E8_ROOTS.T
    i, j = np.where(np.triu(np.isclose(gram, 1), 1))
    d = np.round(np.linalg.norm(E8_PLANE[i] - E8_PLANE[j], axis=1), 4)
    classes = np.unique(d)
    keep = d == classes[length_class]
    return np.column_stack([i[keep], j[keep]])


def root_category(index: int) -> str:
    """Branching E8 → SU(4) × Spin(10) of each root (see physics.root_subsets)."""

    root = E8_ROOTS[index]
    if E8_SUBSETS["su4"][index]:
        return "su4"
    if E8_SUBSETS["spin10"][index]:
        return "spin10"
    integer = np.all(np.abs(root - np.round(root)) < 1e-9)
    if integer:
        return "6_10"
    chirality = np.sum(root[:3] < 0) % 2
    return "4_16" if chirality == 0 else "4b_16b"


E8_CATEGORY = [root_category(k) for k in range(len(E8_ROOTS))]


# ---------------------------------------------------------------------------
# Spin(10) family chart: (T3, Y) plus a colour offset — a linear projection
# ---------------------------------------------------------------------------
def family_chart_xy(vector: np.ndarray, spread: float = 0.42) -> np.ndarray:
    """Project a Spin(10) weight to (T₃ + colour offset, Y + colour offset).

    s = last five coordinates; Y = (s1+s2+s3)/3 − (s4+s5)/2, T₃ = (s4 − s5)/2;
    the SU(3) weight (λ3, λ8) separates the three colours of a quark.
    """

    s = vector[3:]
    hyper = physics.hypercharge(vector)
    isospin = physics.isospin(vector)
    lam3 = (s[0] - s[1]) / 2
    lam8 = (s[0] + s[1] - 2 * s[2]) / (2 * math.sqrt(3))
    return np.array([isospin * 2.2 + spread * lam3 * 2, hyper * 2.2 + spread * lam8 * 2])


FIELD_NAMES = {"Q": "quark doublet", "u^c": "anti-up", "d^c": "anti-down",
               "L": "lepton doublet", "e^c": "positron-type", "ν^c": "right ν"}


def particle_label(weight: physics.SpinorWeight) -> str:
    s = weight.vector[3:]
    if weight.field == "Q":
        return "u" if s[3] > s[4] else "d"
    if weight.field == "L":
        return "ν" if s[3] > s[4] else "e"
    return {"u^c": "ū", "d^c": "d̄", "e^c": "e⁺", "ν^c": "N"}[weight.field]


def quark_colour_index(weight: physics.SpinorWeight) -> int | None:
    s = weight.vector[3:6]
    if weight.field == "Q":
        minus = [k for k in range(3) if s[k] < 0]
        return minus[0] if minus else None
    if weight.field in ("u^c", "d^c"):
        plus = [k for k in range(3) if s[k] > 0]
        return plus[0] if plus else None
    return None


# ---------------------------------------------------------------------------
# Hesse cubic: chained real slices
# ---------------------------------------------------------------------------
def _crossings(field, xs, ys):
    """Vectorized marching squares: zero-crossing segments of a grid function."""

    f = field
    v00, v10 = f[:-1, :-1], f[:-1, 1:]
    v11, v01 = f[1:, 1:], f[1:, :-1]
    gx, gy = np.meshgrid(xs, ys)
    x0, x1 = gx[:-1, :-1], gx[:-1, 1:]
    y0, y1 = gy[:-1, :-1], gy[1:, :-1]

    def cut(a, b):
        with np.errstate(divide="ignore", invalid="ignore"):
            return a / (a - b)

    edges = (
        ((v00 < 0) != (v10 < 0), lambda t: (x0 + t * (x1 - x0), y0), cut(v00, v10)),
        ((v10 < 0) != (v11 < 0), lambda t: (x1, y0 + t * (y1 - y0)), cut(v10, v11)),
        ((v01 < 0) != (v11 < 0), lambda t: (x0 + t * (x1 - x0), y1), cut(v01, v11)),
        ((v00 < 0) != (v01 < 0), lambda t: (x0, y0 + t * (y1 - y0)), cut(v00, v01)),
    )
    count = sum(e[0].astype(int) for e in edges)
    cells = np.argwhere(count >= 2)
    segments = []
    for i, j in cells:
        pts = []
        for mask, where, t in edges:
            if mask[i, j]:
                px, py = where(t)
                px = px[i, j] if np.ndim(px) else px
                py = py[i, j] if np.ndim(py) else py
                pts.append((float(px), float(py)))
        segments.append((pts[0], pts[1]))
        if len(pts) == 4:
            segments.append((pts[2], pts[3]))
    return segments


def chain(segments, tol: float = 1e-7) -> list[np.ndarray]:
    """Join segments sharing endpoints into polylines."""

    def key(p):
        return (round(p[0] / tol), round(p[1] / tol))

    neighbours: dict[tuple, list[int]] = {}
    for k, (a, b) in enumerate(segments):
        neighbours.setdefault(key(a), []).append(k)
        neighbours.setdefault(key(b), []).append(k)
    used = [False] * len(segments)
    lines = []
    for start in range(len(segments)):
        if used[start]:
            continue
        used[start] = True
        a, b = segments[start]
        line = [a, b]
        for direction in (1, -1):
            while True:
                tip = line[-1] if direction == 1 else line[0]
                nxt = None
                for k in neighbours.get(key(tip), []):
                    if not used[k]:
                        nxt = k
                        break
                if nxt is None:
                    break
                used[nxt] = True
                p, q = segments[nxt]
                other = q if key(p) == key(tip) else p
                if direction == 1:
                    line.append(other)
                else:
                    line.insert(0, other)
        if len(line) > 3:
            lines.append(np.array(line))
    return lines


def hesse_lines(lam: float, extent: float = 3.0, n: int = 181) -> list[np.ndarray]:
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    gx, gy = np.meshgrid(xs, ys)
    return chain(_crossings(physics.hesse(gx, gy, lam), xs, ys))


def polylines(lines: list[np.ndarray], scale: float, center=CENTER,
              color: str = INK, width: float = 3.0, opacity: float = 1.0) -> VGroup:
    group = VGroup()
    for line in lines:
        pts = np.column_stack([line * scale, np.zeros(len(line))]) + np.asarray(center)
        mob = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
        mob.set_points_smoothly(pts[:: max(1, len(pts) // 120)] if len(pts) > 240 else pts)
        group.add(mob)
    return group


# ---------------------------------------------------------------------------
# Orthographic 3D
# ---------------------------------------------------------------------------
def view(points: np.ndarray, tilt: float = 1.05, spin: float = 0.0) -> np.ndarray:
    """Rotate about z by `spin`, then about x by `tilt`; return (x, y, depth)."""

    c, s = math.cos(spin), math.sin(spin)
    x = c * points[..., 0] - s * points[..., 1]
    y = s * points[..., 0] + c * points[..., 1]
    z = points[..., 2]
    ct, st = math.cos(tilt), math.sin(tilt)
    return np.stack([x, ct * y - st * z, st * y + ct * z], axis=-1)


def torus_xyz(u: np.ndarray, v: np.ndarray, big: float = 1.0, small: float = 0.42):
    r = big + small * np.cos(v)
    return np.stack([r * np.cos(u), r * np.sin(u), small * np.sin(v)], axis=-1)


def torus_wire(scale: float, center=CENTER, tilt: float = 1.1, spin: float = 0.0,
               color: str = E8_COLOR, n_u: int = 18, n_v: int = 10,
               pinch: float = 0.0, width: float = 1.6, opacity: float = 0.75) -> VGroup:
    """Wireframe torus; `pinch` ∈ [0,1] collapses one meridian (a singular fibre)."""

    group = VGroup()
    t = np.linspace(0, 2 * math.pi, 73)

    def small_radius(u):
        return 0.42 * (1 - pinch * np.exp(-((np.angle(np.exp(1j * u))) ** 2) / 0.12))

    for k in range(n_u):
        u = 2 * math.pi * k / n_u
        pts = torus_xyz(np.full_like(t, u), t, small=small_radius(u))
        group.add(_wire(pts, scale, center, tilt, spin, color, width, opacity))
    for k in range(n_v):
        v = 2 * math.pi * k / n_v
        r = 1 + small_radius(t) * math.cos(v)
        pts = np.stack([r * np.cos(t), r * np.sin(t), small_radius(t) * math.sin(v)], axis=-1)
        group.add(_wire(pts, scale, center, tilt, spin, color, width, opacity))
    return group


def _wire(pts, scale, center, tilt, spin, color, width, opacity) -> VMobject:
    p = view(pts, tilt, spin)
    xyz = np.column_stack([p[:, 0] * scale, p[:, 1] * scale, np.zeros(len(p))])
    mob = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    mob.set_points_smoothly(xyz + np.asarray(center))
    return mob


def sphere_wire(radius: float, center, tilt: float = 1.15, color: str = MUTED,
                width: float = 1.2, opacity: float = 0.6) -> VGroup:
    group = VGroup()
    t = np.linspace(0, 2 * math.pi, 73)
    for lat in np.linspace(-1.2, 1.2, 5):
        pts = np.stack([np.cos(lat) * np.cos(t), np.cos(lat) * np.sin(t),
                        np.full_like(t, np.sin(lat))], axis=-1)
        group.add(_wire(pts, radius, center, tilt, 0.0, color, width, opacity))
    for lon in np.linspace(0, math.pi, 6, endpoint=False):
        pts = np.stack([np.cos(t) * np.cos(lon), np.cos(t) * np.sin(lon), np.sin(t)], axis=-1)
        group.add(_wire(pts, radius, center, tilt, 0.0, color, width, opacity))
    return group


# ---------------------------------------------------------------------------
# Dynkin diagram of extended E8: removing node 6 leaves D5 × A3
# ---------------------------------------------------------------------------
def dynkin_e8(spin10: str = SPIN10_COLOR, su4: str = SU4_COLOR) -> VGroup:
    """Extended E8 (Bourbaki): chain 1-3-4-5-6-7-8-0 with 2 on 4.

    Deleting node 6 leaves {1,3,4,5,2} = D5 = Spin(10) and {7,8,0} = A3 = SU(4).
    """

    positions = {1: (0, 0), 3: (1, 0), 4: (2, 0), 5: (3, 0), 6: (4, 0), 7: (5, 0),
                 8: (6, 0), 0: (7, 0), 2: (2, 1)}
    colors = {1: spin10, 3: spin10, 4: spin10, 5: spin10, 2: spin10,
              6: MUTED, 7: su4, 8: su4, 0: su4}
    bonds = [(1, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 0), (2, 4)]
    nodes = {k: Circle(radius=0.16, stroke_color=colors[k], stroke_width=3,
                       fill_color=colors[k], fill_opacity=0.35).move_to([x, y, 0])
             for k, (x, y) in positions.items()}
    lines = VGroup(*[Line(nodes[a].get_center(), nodes[b].get_center(), buff=0.16,
                          stroke_color=MUTED, stroke_width=2) for a, b in bonds])
    labels = VGroup(text("Spin(10)", 18, spin10).move_to([2, -0.55, 0]),
                    text("SU(4)", 18, su4).move_to([6, -0.55, 0]),
                    text("cut", 14, MUTED).move_to([4, 0.45, 0]))
    group = VGroup(lines, *nodes.values(), labels)
    group.nodes = nodes
    return group


def glow_points(points: np.ndarray, color: str, radius: float = 0.035,
                halo: float = 2.6, halo_opacity: float = 0.18) -> VGroup:
    """Each point drawn as a bright core with one soft halo."""

    group = VGroup()
    for p in points:
        group.add(VGroup(Dot(p, radius=radius * halo, color=color, fill_opacity=halo_opacity),
                         Dot(p, radius=radius, color=color)))
    return group


def segments(points: np.ndarray, pairs: np.ndarray, color: str, width: float = 0.8,
             opacity: float = 0.35) -> VMobject:
    """Many straight segments as one VMobject (one stroke call, fast to render)."""

    mob = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    for a, b in pairs:
        mob.start_new_path(points[a])
        mob.add_line_to(points[b])
    return mob
