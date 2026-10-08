"""Genesis: one continuous Manim film from the unified moment to the horizons.

Owns:
    The `Genesis` scene: fourteen acts played as one unbroken shot. Every
    centre-stage shape is computed by `physics.py`; every act hands its live
    objects to the next one, so nothing is ever cut, only transformed.

Depends on:
    Manim Community, NumPy, and the film's `physics`, `stage` and `visuals`.

Must not:
    Cut between states, use time-dependent updaters, or show a shape without
    the evidence badge that says how sure we are of it.

Phase 0:
    Presentation of established science, OneTheory results and labelled
    hypotheses; it supplies no new physical result.

Render (from this directory):
    manim -qm genesis.py Genesis                  # whole film, 720p30
    GENESIS_ACTS=3-5 manim -ql genesis.py Genesis # only acts 3..5 (others skipped)
"""

from __future__ import annotations

import math
import os

import numpy as np
import physics
import visuals as vis
from late_acts import LateActs
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    ApplyFunction,
    Circle,
    Create,
    DashedLine,
    Dot,
    Ellipse,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    Rectangle,
    ReplacementTransform,
    Rotate,
    Scene,
    Square,
    ValueTracker,
    VGroup,
    VMobject,
    always_redraw,
    linear,
    smooth,
    there_and_back,
)
from manim.animation.animation import prepare_animation
from stage import BG, CENTER, INK, MUTED, Stage, live_text, text

SIGMA = np.linspace(0, 2 * math.pi, 241)
LEFT_MODES = (0.0, 0.9, 0.55, 0.35)
RIGHT_MODES = (0.0, 0.7, 0.6, 0.3)
CLOUD_SIGMA, CLOUD_HEIGHT = 0.3, 7.0
E8_RADIUS = 2.45
HESSE_SCALE = 0.78
HESSE_CENTER = CENTER + np.array([-0.35, -0.2, 0])


def wanted_acts() -> set[int]:
    spec = os.environ.get("GENESIS_ACTS", "").strip()
    if not spec:
        return set(range(1, 100))
    acts: set[int] = set()
    for part in spec.split(","):
        if "-" in part:
            first, last = part.split("-")
            acts.update(range(int(first), int(last) + 1))
        else:
            acts.add(int(part))
    return acts


def wigner_radius(level: float) -> float:
    """Screen radius of the vacuum Wigner contour W = level·W(0) on the cloud image."""

    return math.sqrt(2) * CLOUD_SIGMA * physics.wigner_vacuum_level(level) * CLOUD_HEIGHT / 2


def glow_to(dot: VGroup, color: str | None = None, level: float | None = None,
            scale: float | None = None) -> ApplyFunction:
    """Restyle a (halo, core) glow point: colour, brightness level, size."""

    def change(m: VGroup) -> VGroup:
        if color is not None:
            m.set_color(color)
        if level is not None:
            m[0].set_fill(opacity=0.18 * level)
            m[1].set_fill(opacity=level)
        if scale is not None:
            m.scale(scale)
        return m

    return ApplyFunction(change, dot)


def closed(points: np.ndarray) -> bool:
    return bool(np.linalg.norm(points[0] - points[-1]) < 0.05)


class Genesis(LateActs, Scene):
    """The whole film as one shot."""

    def construct(self) -> None:
        self.camera.background_color = BG
        self.hud = Stage(self)
        acts = (self.act_seed, self.act_string, self.act_dimensions, self.act_breaking,
                self.act_families, self.act_inflation, self.act_reheating, self.act_higgs,
                self.act_confinement, self.act_nuclei, self.act_first_light, self.act_web,
                self.act_galaxy, self.act_horizons)
        chosen = wanted_acts()
        for number, act in enumerate(acts, start=1):
            self.next_section(f"act{number:02d}", skip_animations=number not in chosen)
            act()

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def beat(self, *anims, title=None, sub=None, formulas=None, heading="the formulas",
             badges=None, clock=None, run_time: float = 2.0, rate_func=smooth) -> None:
        hud = []
        if title is not None:
            hud += self.hud.set_title(title, sub or "")
        elif sub is not None:
            hud += self.hud.set_subtitle(sub)
        if formulas is not None:
            hud += self.hud.set_formulas(formulas, heading)
        if badges is not None:
            hud += self.hud.set_badges(badges)
        if clock is not None:
            hud.append(self.hud.advance_clock(clock, run_time).build()
                       .set_rate_func(rate_func))
        centre = []
        for anim in anims:
            anim = prepare_animation(anim)
            if not getattr(anim, "hud", False):
                anim.run_time = run_time
                anim.rate_func = rate_func
            centre.append(anim)
        # No play-level run_time: titles, formulas and badges keep their own short fades
        # while the centre animation runs as long as the beat.
        self.play(*centre, *hud)

    def string_points(self) -> np.ndarray:
        amp, grav = self.t_amp.get_value(), self.t_grav.get_value()
        tau, radius = self.t_tau.get_value(), self.t_radius.get_value()
        loop = physics.string_loop(SIGMA, tau, tuple(a * amp for a in LEFT_MODES),
                                   tuple(a * amp for a in RIGHT_MODES), 1.0)
        quad = physics.graviton_loop(SIGMA, tau, 0.22)
        xy = ((1 - grav) * loop + grav * quad) * radius
        return np.column_stack([xy, np.zeros(len(xy))]) + self.string_center

    def build_string(self) -> VGroup:
        pts = self.string_points()
        opacity = self.t_string_opacity.get_value()
        core = VMobject(stroke_color=vis.STRING_COLOR, stroke_width=4, stroke_opacity=opacity)
        core.set_points_smoothly(pts)
        halo = VMobject(stroke_color=vis.STRING_COLOR, stroke_width=16,
                        stroke_opacity=0.14 * opacity * self.t_bead.get_value())
        halo.set_points_smoothly(pts)
        bead = Dot(pts[0], radius=0.055 * min(1.0, self.t_radius.get_value() / 0.8),
                   color=INK, fill_opacity=opacity * self.t_bead.get_value())
        return VGroup(halo, core, bead)

    # ------------------------------------------------------------------
    # Act 1 · the One
    # ------------------------------------------------------------------
    def act_seed(self) -> None:
        hud = self.hud
        self.wait(0.6)
        seed = vis.image(vis.radial_glow(320, CLOUD_SIGMA, vis.LIGHT), 0.5)
        self.play(FadeIn(seed, scale=0.2), run_time=2.5)
        self.beat(FadeIn(hud.clock),
                  title="GENESIS",
                  sub="From one unified moment to the whole visible universe",
                  badges=[("HYPOTHESIS", "the One: everything begins as one state")],
                  run_time=2.4)
        self.wait(1.4)

        axes = VGroup(
            Line(CENTER + LEFT * 3.2, CENTER + RIGHT * 3.2, stroke_color=MUTED, stroke_width=1,
                 stroke_opacity=0.5),
            Line(CENTER + DOWN * 2.6, CENTER + UP * 2.6, stroke_color=MUTED, stroke_width=1,
                 stroke_opacity=0.5),
            text("x  position", 13, MUTED).move_to(CENTER + RIGHT * 2.75 + DOWN * 0.2),
            text("p  momentum", 13, MUTED).move_to(CENTER + UP * 2.45 + RIGHT * 0.75),
        )
        self.beat(seed.animate.scale(CLOUD_HEIGHT / 0.5),
                  title="1 · The One: a quantum seed",
                  sub="Zoom in on the point: it is not a point. Nature never lets anything "
                      "sit perfectly still.",
                  formulas=["Δx · Δp ≥ ħ/2", "[x̂, p̂] = iħ", "ψ₀(x) ∝ e^(−x²/2)",
                            "E₀ = ½ ħω  (never zero)"],
                  badges=[("HYPOTHESIS", "the One: everything begins as one state"),
                          ("ESTABLISHED", "quantum uncertainty (Heisenberg 1927)")],
                  clock=-45.0, run_time=4.0)
        self.play(seed.animate.scale(1.07), rate_func=there_and_back, run_time=1.8)

        levels = (0.8, 0.5, 0.2, 0.05)
        rings = VGroup(*[Circle(radius=wigner_radius(level), stroke_color=vis.LIGHT,
                                stroke_width=1.6, stroke_opacity=0.55).move_to(CENTER)
                         for level in levels])
        self.beat(FadeIn(axes), LaggedStart(*[Create(r) for r in rings], lag_ratio=0.25),
                  sub="Seen in phase space (position × momentum), the vacuum is a round "
                      "cloud of area ~ħ: rings of equal probability.",
                  formulas=["W₀(x,p) = e^(−(x²+p²)/ħ) / πħ", "rings: W = 0.8, ½, 0.2, 0.05 W₀",
                            "area ≈ ħ: the smallest cell", "[x̂, p̂] = iħ"],
                  run_time=3.0)
        self.play(seed.animate.scale(1.07), rings.animate.scale(1.07),
                  rate_func=there_and_back, run_time=1.8)

        inset = self.trace_inset()
        self.beat(*hud.set_inset(inset, "why the seed cannot be finite", height=2.9),
                  sub="OneTheory proved: no finite table of numbers can obey [x̂, p̂] = iħ. "
                      "The seed must have infinitely many levels.",
                  badges=[("PROVEN", "OneTheory Genesis no-go: AB − BA = λI has no finite "
                                     "solution (trace)"),
                          ("ESTABLISHED", "quantum uncertainty (Heisenberg 1927)"),
                          ("HYPOTHESIS", "the One: everything begins as one state")],
                  run_time=2.4)
        self.play(seed.animate.scale(1.07), rings.animate.scale(1.07),
                  rate_func=there_and_back, run_time=1.8)
        self.wait(1.5)

        # The ½-contour becomes the string; everything else steps back.
        half = rings[1]
        others = VGroup(rings[0], rings[2], rings[3])
        self.play(half.animate.set_stroke(color=vis.STRING_COLOR, width=4, opacity=1),
                  others.animate.set_stroke(opacity=0.0), axes.animate.set_opacity(0.0),
                  seed.animate.set_opacity(0.35), run_time=2.0)
        self.remove(others, axes)
        self.seed, self.half_ring = seed, half

    def trace_inset(self) -> VGroup:
        n, size = 5, 0.26
        cells = VGroup()
        for i in range(n):
            for j in range(n):
                diagonal = i == j
                cells.add(Square(size, stroke_color=MUTED, stroke_width=1,
                                 fill_color=vis.SU4_COLOR if diagonal else BG,
                                 fill_opacity=0.55 if diagonal else 0.0)
                          .move_to([j * size, -i * size, 0]))
        lines = VGroup(text("tr(x̂p̂ − p̂x̂) = 0  always", 15),
                       text("tr(iħ · 𝟙ₙ) = n · iħ ≠ 0", 15),
                       text("⇒ no n×n solution for any n", 15, vis.SU4_COLOR))
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        return VGroup(cells, lines).arrange(DOWN, buff=0.22)

    # ------------------------------------------------------------------
    # Act 2 · one vibrating string
    # ------------------------------------------------------------------
    def act_string(self) -> None:
        hud = self.hud
        self.t_tau, self.t_amp, self.t_grav = ValueTracker(0), ValueTracker(0), ValueTracker(0)
        self.t_radius = ValueTracker(wigner_radius(0.5))
        self.t_string_opacity, self.t_bead = ValueTracker(1), ValueTracker(0)
        self.string_center = np.array(CENTER, dtype=float)
        string = always_redraw(self.build_string)
        self.remove(self.half_ring)
        self.add(string)
        self.string = string

        self.beat(self.t_radius.animate.set_value(1.85), self.seed.animate.set_opacity(0.1),
                  self.t_bead.animate.set_value(1),
                  title="2 · One vibrating string",
                  sub="Zoom further: in OneTheory's chosen picture the seed is a tiny closed "
                      "string, about 10⁻³⁵ m across.",
                  formulas=["X(σ,τ) = X_L(τ+σ) + X_R(τ−σ)", "(∂²τ − ∂²σ) X = 0",
                            "waves run both ways", "size ~ Planck length 1.6×10⁻³⁵ m"],
                  badges=[("SELECTED", "10D E8×E8 heterotic string (Gross–Harvey–Martinec–"
                                       "Rohm 1985)"),
                          ("POSSIBLE", "seed → string: the open Genesis link, one way to "
                                       "draw it")],
                  clock=-43.3, run_time=3.0)
        self.play(*hud.set_inset(None), self.t_amp.animate.set_value(0.2),
                  self.t_tau.animate.set_value(2 * math.pi), run_time=4.0, rate_func=linear)
        self.beat(self.t_tau.animate.set_value(5 * math.pi),
                  sub="Each pattern of vibration is a different particle: one object, every "
                      "kind of matter and force.",
                  run_time=5.0, rate_func=linear)

        # The graviton: a pure quadrupole note.
        self.t_ring = ValueTracker(0)
        ring = always_redraw(lambda: self.test_mass_ring())
        self.beat(self.t_grav.animate.set_value(1), self.t_amp.animate.set_value(0),
                  self.t_tau.animate.set_value(7 * math.pi),
                  sub="This note is the graviton. Gravity is not added by hand: it is one of "
                      "the string's own vibrations.",
                  formulas=["massless spin-2 state", "→ Einstein gravity at low energy",
                            "h₊: stretch x, squeeze y", "G = 6.674×10⁻¹¹ m³ kg⁻¹ s⁻²"],
                  badges=[("PROVEN", "closed strings always contain a massless spin-2 state "
                                     "(Yoneya; Scherk–Schwarz 1974)"),
                          ("MEASURED", "gravitational waves: LIGO 2015; speed = c to 10⁻¹⁵ "
                                       "(GW170817)"),
                          ("SELECTED", "10D E8×E8 heterotic string (GHMR 1985)")],
                  run_time=4.0, rate_func=linear)
        self.add(ring)
        self.play(*hud.adopt_inset(ring, "LIGO's view: a ring of test masses", height=2.9),
                  self.t_ring.animate.set_value(1), self.t_tau.animate.set_value(10 * math.pi),
                  run_time=5.0, rate_func=linear)
        self.play(self.t_tau.animate.set_value(13 * math.pi), run_time=5.0, rate_func=linear)

        # Charges: the roots of E8 stream out of the string.
        target = vis.e8_points(E8_RADIUS)
        rel = target - np.asarray(CENTER)
        angles = np.arctan2(rel[:, 1], rel[:, 0])
        dots = VGroup()
        for k in range(len(target)):
            start = np.asarray(CENTER) + 1.85 * np.array([math.cos(angles[k]),
                                                          math.sin(angles[k]), 0])
            dots.add(vis.glow_points(start[None, :], vis.STRING_COLOR, 0.03)[0])
        self.beat(self.t_grav.animate.set_value(0), self.t_amp.animate.set_value(0.1),
                  self.t_tau.animate.set_value(15 * math.pi), self.t_ring.animate.set_value(0),
                  sub="Other notes carry charges. Their allowed values form a perfect crystal "
                      "in 8 dimensions: the E₈ lattice.",
                  formulas=["massless: ½ p_L² + N_L = 1", "N_L = 0  ⇒  p_L² = 2",
                            "p_L ∈ Γ₈ ⊕ Γ₈ (E₈ × E₈)", "240 + 240 roots + 16 = 496"],
                  badges=[("PROVEN", "E₈ root system: 240 roots of length √2"),
                          ("PROVEN", "anomalies cancel only if dim G = 496 (Green–Schwarz "
                                     "1984)"),
                          ("SELECTED", "10D E8×E8 heterotic string (GHMR 1985)")],
                  run_time=4.0, rate_func=linear)
        self.remove(ring)
        hud.inset = VGroup(*hud.inset.submobjects[:2])
        self.play(FadeIn(dots, lag_ratio=0.01), self.t_tau.animate.set_value(16 * math.pi),
                  run_time=1.5, rate_func=linear)
        flights = [dots[k].animate.move_to(target[k]).set_color(vis.E8_COLOR)
                   for k in np.argsort(np.linalg.norm(rel, axis=1))]
        self.play(LaggedStart(*flights, lag_ratio=0.012),
                  self.t_radius.animate.set_value(0.32), self.t_amp.animate.set_value(0.05),
                  self.t_tau.animate.set_value(19 * math.pi), run_time=5.0)
        edges = vis.segments(target, vis.e8_edge_pairs(0), vis.E8_COLOR, 0.8, 0.3)
        twin = VGroup(*[Dot(p, radius=0.012, color=vis.E8_COLOR, fill_opacity=0.5)
                        for p in vis.e8_points(1.0)])
        twin_edges = vis.segments(vis.e8_points(1.0), vis.e8_edge_pairs(0), vis.E8_COLOR,
                                  0.5, 0.18)
        self.beat(FadeIn(edges), *hud.set_inset(VGroup(twin_edges, twin),
                                                 "E₈′: the hidden twin (meets us only by "
                                                 "gravity)", height=2.9),
                  self.t_tau.animate.set_value(21 * math.pi),
                  sub="E₈: 240 charge directions, drawn here in its most symmetric shadow "
                      "(30-fold). A twin E₈′ is hidden.",
                  run_time=3.0, rate_func=linear)
        self.e8 = VGroup(edges, dots)
        self.play(Rotate(self.e8, math.pi / 15, about_point=CENTER),
                  self.t_tau.animate.set_value(25 * math.pi), run_time=6.0, rate_func=linear)
        self.e8_rotation = math.pi / 15

    def test_mass_ring(self) -> VGroup:
        center, width, height = self.hud.inset_box(2.9)
        radius = min(width, height) * 0.36
        phase, opacity = self.t_tau.get_value(), self.t_ring.get_value()
        strength = 0.22 * self.t_grav.get_value()
        angles = np.linspace(0, 2 * math.pi, 16, endpoint=False)
        group = VGroup(Circle(radius=radius, stroke_color=MUTED, stroke_width=1,
                              stroke_opacity=0.5 * opacity).move_to(center))
        for a in angles:
            x = (1 + strength * math.cos(phase)) * math.cos(a)
            y = (1 - strength * math.cos(phase)) * math.sin(a)
            group.add(Dot(center + radius * np.array([x, y, 0]), radius=0.075,
                          color=vis.SPIN10_COLOR, fill_opacity=opacity))
        return group

    # ------------------------------------------------------------------
    # Act 3 · ten dimensions: three open, six curl up
    # ------------------------------------------------------------------
    def act_dimensions(self) -> None:
        hud = self.hud
        center, width, height = hud.inset_box(2.9)
        scale = min(width, height) / (2 * E8_RADIUS)
        self.e8_scale = scale
        self.beat(self.e8.animate.scale(scale, about_point=CENTER).move_to(center),
                  *hud.adopt_inset(self.e8, "E₈ charges, carried along", height=2.9),
                  self.t_tau.animate.set_value(27 * math.pi),
                  title="3 · Ten dimensions: three open up, six stay tiny",
                  sub="The string moves in 9 space dimensions. At the start all of them may "
                      "have been equally tiny.",
                  formulas=["10 = 4 (spacetime) + 6 (hidden)", "string gas: winding w,",
                            "momentum n, R ↔ ℓ²/R", "w + w̄ → loops in ≤ 3D"],
                  badges=[("HYPOTHESIS", "string gas: windings unwind only in ≤ 3 space dims "
                                         "(Brandenberger–Vafa 1989)"),
                          ("POSSIBLE", "2 of the 9 directions drawn; a box with glued edges")],
                  clock=-42.5, run_time=3.0)

        side = 3.4
        box = Square(side, stroke_color=MUTED, stroke_width=2).move_to(CENTER)
        glue = VGroup(*[t.move_to(box.get_edge_center(d) + d * 0.18)
                        for t, d in ((text("▶", 12, MUTED), RIGHT), (text("▶", 12, MUTED), LEFT),
                                     (text("▲", 12, MUTED), UP), (text("▲", 12, MUTED), DOWN))])
        self.t_wig = ValueTracker(0)
        self.t_meet = ValueTracker(0)
        self.t_box_w, self.t_box_h = ValueTracker(side), ValueTracker(side)
        self.t_windings = ValueTracker(0)
        windings = always_redraw(self.winding_strings)
        self.add(windings)
        self.play(Create(box), FadeIn(glue), self.t_windings.animate.set_value(1),
                  FadeOut(self.seed), self.t_wig.animate.set_value(1),
                  self.t_tau.animate.set_value(29 * math.pi), run_time=2.5, rate_func=linear)
        self.beat(self.t_meet.animate.set_value(1), self.t_wig.animate.set_value(3),
                  self.t_tau.animate.set_value(33 * math.pi),
                  sub="Strings wrapped around space hold it small. Where a winding meets an "
                      "anti-winding they unwrap into loops.",
                  run_time=4.0)
        loops = VGroup(*[Circle(radius=0.16, stroke_color=vis.STRING_COLOR, stroke_width=3)
                         .move_to(CENTER + np.array([x, 0, 0])) for x in (-0.9, 0.9)])
        self.play(FadeIn(loops, scale=0.3), self.t_meet.animate.set_value(1.3),
                  self.t_wig.animate.set_value(3.4), run_time=1.0)
        self.play(loops[0].animate.shift(LEFT * 0.6 + UP * 0.5).scale(0.4).set_opacity(0),
                  loops[1].animate.shift(RIGHT * 0.6 + DOWN * 0.5).scale(0.4).set_opacity(0),
                  self.t_meet.animate.set_value(2), self.t_wig.animate.set_value(4),
                  run_time=2.0)
        self.remove(loops)

        # The unwound direction grows, the wound one stays a tiny circle: a tube.
        def band() -> Rectangle:
            return Rectangle(width=self.t_box_w.get_value(), height=self.t_box_h.get_value(),
                             stroke_color=MUTED, stroke_width=2).move_to(CENTER)

        live_box = always_redraw(band)
        self.remove(box)
        self.add(live_box)
        self.beat(self.t_box_w.animate.set_value(8.0), self.t_box_h.animate.set_value(0.62),
                  self.t_radius.animate.set_value(0.12), self.t_wig.animate.set_value(7),
                  FadeOut(glue),
                  sub="Freed from windings, three directions expand. The others stay curled: "
                      "every point of space hides a tiny shape.",
                  clock=-42.0, run_time=4.5)
        circles = VGroup(*[Ellipse(width=0.16, height=0.62, stroke_color=vis.E8_COLOR,
                                   stroke_width=1.8).move_to(CENTER + RIGHT * x)
                           for x in np.arange(-3.5, 3.51, 0.5)])
        self.play(LaggedStart(*[Create(c) for c in circles], lag_ratio=0.06),
                  self.t_string_opacity.animate.set_value(0), run_time=2.5)
        self.remove(self.string)

        # Zoom into one curled circle: it is a cubic curve.
        self.t_lambda = ValueTracker(1.6)
        self.t_branch = ValueTracker(0)
        oval_line = [ln for ln in vis.hesse_lines(1.6) if closed(ln)][0]
        oval = vis.polylines([oval_line], HESSE_SCALE, HESSE_CENTER, vis.STRING_COLOR, 3.5)[0]
        middle = circles[7]
        rest = VGroup(*[c for k, c in enumerate(circles) if k != 7])
        self.remove(windings)
        self.beat(ReplacementTransform(middle, oval), FadeOut(rest), FadeOut(live_box),
                  title="3 · The hidden shape, slice by slice",
                  sub="Zoom into one tiny circle. Its true shape is an elliptic curve: "
                      "a cubic equation, drawn here as a real slice.",
                  formulas=["x³ + y³ + 1 = 3λ·xy", "cubic curve = elliptic curve",
                            "every λ passes (−1,0), (0,−1)", "λ = 1:  x + y + 1 = 0  (singular)"],
                  badges=[("PROVEN", "the Hesse pencil of cubics (Hesse 1844)"),
                          ("ONETHEORY", "its fibres: p₁ = μF + νG, cubic forms over ℚ(ω)"),
                          ("POSSIBLE", "a real 2D slice of a complex curve")],
                  run_time=3.5)
        axes = VGroup(
            Line(HESSE_CENTER + LEFT * 2.6, HESSE_CENTER + RIGHT * 2.6, stroke_color=MUTED,
                 stroke_width=1, stroke_opacity=0.45),
            Line(HESSE_CENTER + DOWN * 2.4, HESSE_CENTER + UP * 2.6, stroke_color=MUTED,
                 stroke_width=1, stroke_opacity=0.45))
        curve = always_redraw(self.hesse_curve)
        base = VGroup(*[Dot(HESSE_CENTER + HESSE_SCALE * np.array([x, y, 0]), radius=0.07,
                            color=vis.SPIN10_COLOR) for x, y in physics.hesse_base_points()])
        base_label = text("every curve passes here", 13, vis.SPIN10_COLOR)
        base_label.move_to(HESSE_CENTER + HESSE_SCALE * np.array([-1.9, -0.75, 0]))
        lam_label = live_text(lambda: f"λ = {self.t_lambda.get_value():.2f}", 18,
                              vis.STRING_COLOR, lambda: CENTER + np.array([2.9, 2.2, 0]))
        self.remove(oval)
        self.add(curve)
        self.play(self.t_branch.animate.set_value(1), FadeIn(axes), FadeIn(base),
                  FadeIn(base_label), FadeIn(lam_label), run_time=2.0)
        self.beat(self.t_lambda.animate.set_value(1.0),
                  sub="Change λ and the curve changes. At λ = 1 the loop shrinks to a point: "
                      "a singular fibre.",
                  run_time=5.0)
        self.wait(0.8)
        self.beat(self.t_lambda.animate.set_value(0.55),
                  sub="Below 1 the loop is gone from the real slice, yet every curve still "
                      "passes through the same base points.",
                  run_time=3.5)
        self.play(self.t_lambda.animate.set_value(1.45), run_time=4.0)

        # Complex picture: the real oval is one loop on a torus.
        oval_line = [ln for ln in vis.hesse_lines(1.45) if closed(ln)][0]
        frozen = vis.polylines([oval_line], HESSE_SCALE, HESSE_CENTER, vis.STRING_COLOR, 3.5)[0]
        self.add(frozen)
        self.torus_center = np.array(CENTER, dtype=float)
        self.t_spin = ValueTracker(0.0)
        cycle = self.torus_cycle(1.9, self.torus_center)
        self.t_torus_on = ValueTracker(0.0)
        torus = always_redraw(lambda: vis.torus_wire(
            1.9, self.torus_center, spin=self.t_spin.get_value(), color=vis.E8_COLOR,
            opacity=0.6 * self.t_torus_on.get_value()))
        self.beat(ReplacementTransform(frozen, cycle), FadeOut(axes), FadeOut(base),
                  FadeOut(base_label), FadeOut(lam_label), FadeOut(curve),
                  title="3 · Over the complex numbers: a torus",
                  sub="With complex x and y, each cubic curve is a donut. The real loop we "
                      "saw is one of its circles.",
                  formulas=["E = ℂ / (ℤ + τℤ)", "genus 1: one hole", "real oval = one cycle",
                            "two cycles: a, b"],
                  badges=[("PROVEN", "every smooth cubic is a complex torus (Abel, Jacobi, "
                                     "Weierstrass)"),
                          ("ONETHEORY", "its fibres: p₁ = μF + νG, cubic forms over ℚ(ω)")],
                  run_time=3.5)
        self.add(torus)
        self.play(self.t_torus_on.animate.set_value(1.0), self.t_spin.animate.set_value(0.4),
                  run_time=2.5)
        self.play(self.t_spin.animate.set_value(0.9), cycle.animate.set_stroke(opacity=0.0),
                  run_time=3.0)
        self.remove(cycle)

        # Schoen: two families of tori over one sphere.
        self.t_base = ValueTracker(0.0)
        self.t_pinch1, self.t_pinch2 = ValueTracker(0.0), ValueTracker(0.0)
        self.torus_center = np.array(CENTER, dtype=float)
        left_center = CENTER + np.array([-1.65, 0.85, 0])
        right_center = CENTER + np.array([1.65, 0.85, 0])
        sphere_center = CENTER + np.array([0, -1.65, 0])
        self.t_torus_scale = ValueTracker(1.9)
        self.t_torus_shift = ValueTracker(0.0)

        def first_torus():
            s = self.t_torus_shift.get_value()
            c = (1 - s) * np.asarray(CENTER) + s * left_center
            self.torus_center = c
            return vis.torus_wire(self.t_torus_scale.get_value(), c,
                                  spin=self.t_spin.get_value(), color=vis.E8_COLOR,
                                  opacity=0.6, pinch=self.t_pinch1.get_value())

        def second_torus():
            return vis.torus_wire(1.05, right_center, spin=-self.t_spin.get_value() + 0.6,
                                  color="#f0abfc", opacity=0.6 * self.t_second.get_value(),
                                  pinch=self.t_pinch2.get_value())

        self.t_second = ValueTracker(0)
        torus1 = always_redraw(first_torus)
        torus2 = always_redraw(second_torus)
        self.remove(torus)
        self.add(torus1, torus2)
        sphere = vis.sphere_wire(0.85, sphere_center)
        marker = always_redraw(lambda: Dot(self.base_point(sphere_center), radius=0.07,
                                           color=vis.STRING_COLOR,
                                           fill_opacity=self.t_second.get_value()))
        links = always_redraw(lambda: VGroup(
            DashedLine(self.base_point(sphere_center), left_center + DOWN * 0.45,
                       stroke_color=MUTED, stroke_width=1.2,
                       stroke_opacity=0.7 * self.t_second.get_value()),
            DashedLine(self.base_point(sphere_center), right_center + DOWN * 0.45,
                       stroke_color=MUTED, stroke_width=1.2,
                       stroke_opacity=0.7 * self.t_second.get_value())))
        labels = VGroup(text("B₁: torus family 1", 13, vis.E8_COLOR).move_to(left_center
                                                                            + UP * 1.08),
                        text("B₂: torus family 2", 13, "#f0abfc").move_to(right_center
                                                                         + UP * 1.08),
                        text("base sphere P¹", 13, MUTED).move_to(sphere_center + DOWN * 0.98))
        self.beat(self.t_torus_shift.animate.set_value(1), self.t_torus_scale.animate
                  .set_value(1.05), self.t_second.animate.set_value(1), FadeIn(sphere),
                  FadeIn(marker), FadeIn(links), FadeIn(labels),
                  title="3 · Schoen's Calabi–Yau: the shape of the hidden six",
                  sub="Two families of tori over one sphere, glued point by point: a "
                      "six-dimensional Calabi–Yau space.",
                  formulas=["X = B₁ ×_P¹ B₂ (Schoen 1988)", "fibre = torus × torus",
                            "h¹¹ = h²¹ = 19,  χ = 0", "12 pinched fibres per family"],
                  badges=[("PROVEN", "Schoen's threefold is Calabi–Yau, h¹¹ = h²¹ = 19"),
                          ("SELECTED", "this geometry: Braun–Ovrut–Pantev–Reinbacher 2004"),
                          ("ONETHEORY", "exact cover, quotient, intersection ring, deck "
                                        "action")],
                  run_time=3.5)
        self.play(self.t_base.animate.set_value(0.5), self.t_pinch1.animate.set_value(0.9),
                  self.t_spin.animate.set_value(1.3), run_time=3.0)
        self.beat(self.t_base.animate.set_value(1.0), self.t_pinch1.animate.set_value(0.0),
                  self.t_pinch2.animate.set_value(0.9), self.t_spin.animate.set_value(1.7),
                  sub="Walk around the sphere: both donuts change. At 12 points each one pinches "
                      "(the singular fibres we met at λ = 1).",
                  run_time=3.5)
        self.play(self.t_base.animate.set_value(1.5), self.t_pinch2.animate.set_value(0.0),
                  self.t_spin.animate.set_value(2.1), run_time=3.0)

        # The free Z3 x Z3 quotient: nine points become one.
        self.t_orbit = ValueTracker(0.0)
        self.t_merge = ValueTracker(0.0)
        nine = always_redraw(self.nine_points)
        self.play(FadeIn(nine), run_time=1.0)
        self.beat(self.t_orbit.animate.set_value(1.0), self.t_spin.animate.set_value(2.5),
                  sub="A symmetry of order 9 moves every point to 8 partners. Declaring them "
                      "the same point shrinks the shape ninefold.",
                  formulas=["G = ℤ₃ × ℤ₃ acts freely", "X̄ = X / G", "h¹¹ = h²¹ = 19 → 3",
                            "χ(X̄) = 0 / 9 = 0"],
                  run_time=4.0)
        self.play(self.t_merge.animate.set_value(1.0), self.t_spin.animate.set_value(2.9),
                  run_time=3.0)
        self.play(FadeOut(nine), run_time=1.0)
        self.schoen = VGroup(torus1, torus2, sphere, marker, links, labels)
        self.schoen_centers = (left_center, right_center, sphere_center)

    def winding_strings(self) -> VGroup:
        """Strings wound around the glued box; the horizontal pair meets and unwinds."""

        w, h = self.t_box_w.get_value(), self.t_box_h.get_value()
        phase = self.t_wig.get_value()
        meet = self.t_meet.get_value()
        group = VGroup()
        xs = np.linspace(-w / 2, w / 2, 90)
        ys = np.linspace(-h / 2, h / 2, 90)
        fade = max(0.0, 1.0 - max(0.0, meet - 1.0) * 4)
        for sign in (1, -1):
            offset = sign * 0.9 * (1 - min(meet, 1.0)) * h / 3.4
            y = offset + 0.06 * np.sin(2 * math.pi * 3 * xs / max(w, 1e-3) + sign * phase * 3)
            if fade > 0 and meet < 1.5:
                pts = np.column_stack([xs, y, np.zeros_like(xs)]) + np.asarray(CENTER)
                mob = VMobject(stroke_color=vis.STRING_COLOR, stroke_width=2.5,
                               stroke_opacity=fade * self.t_windings.get_value())
                mob.set_points_smoothly(pts)
                group.add(mob)
        for sign in (1, -1):
            x0 = sign * 1.0 * w / 3.4
            x = x0 + 0.06 * np.sin(2 * math.pi * 2 * ys / max(h, 1e-3) + sign * phase * 3)
            pts = np.column_stack([x, ys, np.zeros_like(ys)]) + np.asarray(CENTER)
            mob = VMobject(stroke_color=vis.STRING_COLOR, stroke_width=2.5,
                           stroke_opacity=self.t_string_opacity.get_value()
                           * self.t_windings.get_value())
            mob.set_points_smoothly(pts)
            group.add(mob)
        return group

    def hesse_curve(self) -> VGroup:
        lam = self.t_lambda.get_value()
        group = VGroup()
        for line in vis.hesse_lines(lam):
            opacity = 1.0 if closed(line) else self.t_branch.get_value()
            if opacity <= 0:
                continue
            group.add(*vis.polylines([line], HESSE_SCALE, HESSE_CENTER, vis.STRING_COLOR, 3.5,
                                     opacity))
        near = max(0.0, 1 - abs(lam - 1.0) / 0.06)
        if near > 0:
            group.add(Dot(HESSE_CENTER + HESSE_SCALE * np.array([1, 1, 0]), radius=0.07,
                          color=vis.STRING_COLOR, fill_opacity=near))
        return group

    def torus_cycle(self, scale: float, center) -> VMobject:
        t = np.linspace(0, 2 * math.pi, 121)
        pts = vis.torus_xyz(t, np.full_like(t, math.pi / 2))
        p = vis.view(pts, 1.1, 0.0)
        mob = VMobject(stroke_color=vis.STRING_COLOR, stroke_width=3.5)
        mob.set_points_smoothly(np.column_stack([p[:, 0] * scale, p[:, 1] * scale,
                                                 np.zeros(len(p))]) + np.asarray(center))
        return mob

    def base_point(self, sphere_center) -> np.ndarray:
        angle = 2 * math.pi * self.t_base.get_value() / 1.5
        p = vis.view(np.array([[math.cos(angle), math.sin(angle), 0.0]]), 1.15, 0.0)[0]
        return np.asarray(sphere_center) + 0.85 * np.array([p[0], p[1], 0])

    def nine_points(self) -> VGroup:
        """The 3×3 torsion translates on the first torus, moved by the group, then merged."""

        orbit, merge = self.t_orbit.get_value(), self.t_merge.get_value()
        spin, scale = self.t_spin.get_value(), self.t_torus_scale.get_value()
        group = VGroup()
        for a in range(3):
            for b in range(3):
                u = 2 * math.pi * a / 3 + orbit * 2 * math.pi / 3
                v = 2 * math.pi * b / 3 + 0.6 + orbit * 2 * math.pi / 3
                u = (1 - merge) * u + merge * (orbit * 2 * math.pi / 3)
                v = (1 - merge) * v + merge * (0.6 + orbit * 2 * math.pi / 3)
                p = vis.view(vis.torus_xyz(np.array(u), np.array(v)), 1.1, spin)
                point = np.asarray(self.torus_center) + scale * np.array([p[0], p[1], 0])
                group.add(Dot(point, radius=0.06, color=vis.STRING_COLOR))
        return group

    # ------------------------------------------------------------------
    # Act 4 · the shape chooses the forces
    # ------------------------------------------------------------------
    def act_breaking(self) -> None:
        hud = self.hud
        left_center = self.schoen_centers[0]
        self.t_strands = ValueTracker(0)
        strands = always_redraw(lambda: self.bundle_strands(left_center))
        self.add(strands)
        self.beat(self.t_strands.animate.set_value(1), self.t_spin.animate.set_value(3.3),
                  title="4 · The shape chooses the forces",
                  sub="A field of force is wrapped on the hidden shape: an SU(4) bundle, "
                      "four intertwined strands.",
                  formulas=["V: rank-4 SU(4) bundle on X̄", "c₁(V) = 0,  stable",
                            "c₂(V) = (8/3, 5/3, 4)", "0 → V₁ → V → V₂ → 0"],
                  badges=[("ONETHEORY", "SU(4) bundle: locally free, descends, slope-stable "
                                        "(computed)"),
                          ("SELECTED", "this bundle family over P¹ (alternate-i6-ray-0-1)")],
                  clock=-38.0, run_time=3.5)
        self.play(self.t_spin.animate.set_value(3.7), run_time=2.0)

        # Swap: the geometry goes to the inset, the E8 crystal comes back to the centre.
        content = hud.release_inset()
        center, width, height = hud.inset_box(2.9)
        geometry = VGroup(self.schoen, strands)
        frame_scale = min(width / 7.2, height / 5.4)
        self.clear_updaters_of(geometry)
        self.beat(content.animate.scale(1 / self.e8_scale).move_to(CENTER),
                  geometry.animate.scale(frame_scale, about_point=CENTER).move_to(center),
                  *hud.fade_released(),
                  *hud.adopt_inset(geometry, "the hidden shape with its SU(4) field",
                                   height=2.9),
                  sub="Now look again at the E₈ crystal. The four strands use up an SU(4) "
                      "inside it.",
                  run_time=3.0)
        self.e8 = content
        edges, dots = content
        cats = vis.E8_CATEGORY
        su4 = [dots[k] for k in range(240) if cats[k] == "su4"]
        spin10 = [dots[k] for k in range(240) if cats[k] == "spin10"]
        higgs = [dots[k] for k in range(240) if cats[k] == "6_10"]
        matter = [dots[k] for k in range(240) if cats[k] == "4_16"]
        anti = [dots[k] for k in range(240) if cats[k] == "4b_16b"]
        self.beat(*[d.animate.set_color(vis.SU4_COLOR).scale(1.8) for d in su4],
                  edges.animate.set_stroke(opacity=0.12),
                  formulas=["E₈ ⊃ SU(4) × Spin(10)", "248 = (15,1) + (1,45)",
                            "  + (6,10) + (4,16) + (4̄,1̄6̄)", "roots: 12+40+60+64+64"],
                  badges=[("PROVEN", "E₈ ⊃ SU(4)×Spin(10): branching rule of Lie algebras"),
                          ("ONETHEORY", "SU(4) bundle: locally free, descends, slope-stable "
                                        "(computed)")],
                  run_time=2.5)
        self.beat(*[d.animate.move_to(CENTER).set_opacity(0) for d in su4],
                  sub="Those 12 orange directions are absorbed into the shape. They no longer "
                      "act in our four dimensions.",
                  run_time=3.0)
        self.beat(*[d.animate.set_color(vis.SPIN10_COLOR).scale(1.6) for d in spin10],
                  sub="What commutes with SU(4) survives: Spin(10), 45 forces in one, our "
                      "grand-unified force.",
                  run_time=2.5)
        self.beat(*[d.animate.set_color(vis.HIGGS10_COLOR) for d in higgs],
                  *[d.animate.set_color(vis.MATTER_COLOR) for d in matter],
                  *[glow_to(d, vis.ANTIMATTER_COLOR, level=0.5) for d in anti],
                  *hud.set_inset(vis.dynkin_e8(), "extended E₈ diagram: cut one node", 2.9),
                  sub="The rest become matter (pink: 4 × 16) and Higgs-like fields (grey: "
                      "6 × 10).",
                  run_time=3.0)
        self.play(Rotate(content, math.pi / 30, about_point=CENTER), run_time=3.0)
        self.e8_dots = dots

    def clear_updaters_of(self, group: VGroup) -> None:
        for mob in group.get_family():
            mob.clear_updaters()

    def bundle_strands(self, center) -> VGroup:
        t = np.linspace(0, 2 * math.pi, 181)
        draw = self.t_strands.get_value()
        spin, scale = self.t_spin.get_value(), self.t_torus_scale.get_value()
        shades = ("#fb923c", "#fdba74", "#f97316", "#fed7aa")
        group = VGroup()
        for k, (p, q) in enumerate(((1, 1), (1, 2), (2, 1), (1, -1))):
            n = max(2, int(len(t) * draw))
            pts = vis.torus_xyz(p * t[:n], q * t[:n] + k * 0.9, small=0.42)
            v = vis.view(pts, 1.1, spin)
            mob = VMobject(stroke_color=shades[k], stroke_width=2.6)
            mob.set_points_smoothly(np.column_stack([v[:, 0] * scale, v[:, 1] * scale,
                                                     np.zeros(n)]) + np.asarray(center))
            group.add(mob)
        return group

    # ------------------------------------------------------------------
    # Act 5 · matter: three families
    # ------------------------------------------------------------------
    def act_families(self) -> None:
        hud = self.hud
        family = physics.one_family()
        index = {tuple(np.round(r, 3)): k for k, r in enumerate(vis.E8_ROOTS)}
        picks = [index[tuple(np.round(w.vector, 3))] for w in family]
        dots = self.e8_dots
        chosen = VGroup(*[dots[k] for k in picks])
        others = VGroup(*[d for k, d in enumerate(dots)
                          if k not in picks and vis.E8_CATEGORY[k] != "su4"])
        edges = self.e8[0]
        self.beat(*[glow_to(d, vis.MATTER_COLOR, level=1.0, scale=1.9) for d in chosen],
                  *[glow_to(d, level=0.2) for d in others],
                  edges.animate.set_stroke(opacity=0.05),
                  title="5 · Matter: one family of sixteen",
                  sub="Pick the 16 pink directions with one fixed SU(4) label. Together they "
                      "are one complete family of matter.",
                  formulas=["16 of Spin(10) = one family", "Q = T₃ + Y (electric charge)",
                            "16 → 10 + 5̄ + 1 under SU(5)", "quarks come in 3 colours"],
                  badges=[("PROVEN", "Spin(10) spinor 16 holds a whole family + 1"),
                          ("MEASURED", "all 15 known states of a family are observed"),
                          ("HYPOTHESIS", "the 16th: a right-handed neutrino N, not yet seen")],
                  clock=-37.0, run_time=3.0)

        chart_center = CENTER + np.array([0, 0.1, 0])
        chart_xy = [vis.family_chart_xy(w.vector) for w in family]
        targets = [chart_center + np.array([p[0], p[1], 0]) for p in chart_xy]
        axes = VGroup(
            Line(chart_center + LEFT * 2.6, chart_center + RIGHT * 2.6, stroke_color=MUTED,
                 stroke_width=1, stroke_opacity=0.5),
            Line(chart_center + DOWN * 2.5, chart_center + UP * 2.5, stroke_color=MUTED,
                 stroke_width=1, stroke_opacity=0.5),
            text("isospin T₃ →", 13, MUTED).move_to(chart_center + RIGHT * 2.3 + DOWN * 0.2),
            text("hypercharge Y ↑", 13, MUTED).move_to(chart_center + UP * 2.45 + RIGHT * 1.0))
        hidden = VGroup(*[d for k, d in enumerate(dots) if k not in picks])
        self.beat(*[chosen[k].animate.move_to(targets[k]) for k in range(16)],
                  FadeOut(hidden), FadeOut(edges), FadeIn(axes),
                  sub="Rearranged by their charges (isospin across, hypercharge up), the 16 "
                      "form the family chart.",
                  run_time=4.0)
        labels = VGroup()
        for k, w in enumerate(family):
            offset = np.array([0.0, 0.24, 0]) if w.field != "Q" else np.array([0.26, 0.0, 0])
            labels.add(text(vis.particle_label(w), 15, INK).move_to(targets[k] + offset))
        self.play(FadeIn(labels), run_time=1.5)
        self.wait(1.0)

        # Wilson lines: Spin(10) → Standard Model colours.
        self.beat(*[chosen[k].animate.set_color(vis.FIELD_COLORS[w.field])
                    for k, w in enumerate(family)],
                  sub="Wilson lines around the hidden loops break Spin(10) to the Standard "
                      "Model: the family splits into its pieces.",
                  formulas=["ℤ₃×ℤ₃ Wilson lines:", "Spin(10) → SU(3)×SU(2)", "  × U(1)_Y × "
                            "U(1)_B−L", "Q (6) u^c (3) d^c (3) L (2) e^c ν^c"],
                  badges=[("ONETHEORY", "Wilson lines: SM gauge group, no exotic colour "
                                        "triplets (computed)"),
                          ("MEASURED", "SU(3)×SU(2)×U(1) charges of every known particle")],
                  run_time=3.0)
        legend = VGroup(*[VGroup(Dot(radius=0.06, color=vis.FIELD_COLORS[f]),
                                 text(name, 12, MUTED)).arrange(RIGHT, buff=0.08)
                          for f, name in vis.FIELD_NAMES.items()])
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.07).move_to(CENTER + np.array([3.1,
                                                                                       -1.6, 0]))
        self.play(FadeIn(legend), run_time=1.2)
        self.wait(1.5)

        # Three families.
        chart = VGroup(chosen, labels, axes)
        self.chart = chart
        copies = []
        positions = (CENTER + np.array([-2.75, 0.15, 0]), CENTER + np.array([0, 0.15, 0]),
                     CENTER + np.array([2.75, 0.15, 0]))
        renames = ({"u": "c", "d": "s", "e": "μ", "ν": "ν", "ū": "c̄", "d̄": "s̄", "e⁺": "μ⁺",
                    "N": "N"},
                   {"u": "t", "d": "b", "e": "τ", "ν": "ν", "ū": "t̄", "d̄": "b̄", "e⁺": "τ⁺",
                    "N": "N"})
        copies = []
        for rename in renames:
            new_labels = VGroup(*[text(rename[vis.particle_label(w)], 15, INK)
                                  .move_to(labels[k]).set_opacity(0)
                                  for k, w in enumerate(family)])
            copies.append(VGroup(chosen.copy(), new_labels, axes.copy()))
        self.add(*copies)
        names = ("1st: u d e ν", "2nd: c s μ ν", "3rd: t b τ ν")
        family_labels = VGroup(*[text(n, 14, MUTED).move_to(p + DOWN * 1.5)
                                 for n, p in zip(names, positions, strict=True)])
        def shrink(position, reveal: bool):
            def change(m: VGroup) -> VGroup:
                m.scale(0.5).move_to(position)
                m[2][2].set_opacity(0)
                m[2][3].set_opacity(0)
                if reveal:
                    m[1].set_opacity(1)
                return m
            return change

        self.beat(ApplyFunction(shrink(positions[0], False), chart),
                  ApplyFunction(shrink(positions[1], True), copies[0]),
                  ApplyFunction(shrink(positions[2], True), copies[1]),
                  FadeOut(legend), FadeIn(family_labels),
                  title="5 · Three families, counted by the shape",
                  sub="The shape's topology makes 27 copies on the cover; the ninefold "
                      "identification leaves exactly three.",
                  formulas=["cover: 27 copies of the 16", "27 / |ℤ₃×ℤ₃| = 27 / 9 = 3",
                            "+ 1 Higgs pair", "no anti-families"],
                  badges=[("ONETHEORY", "3 families + 1 Higgs pair from exact cohomology "
                                        "(a constraint, then computed)"),
                          ("MEASURED", "3 light neutrinos: N_ν = 2.984 ± 0.008 (LEP Z width)")],
                  run_time=3.5)
        self.families = VGroup(chart, *copies)
        self.wait(1.0)

        # Masses: measured sizes, OneTheory's texture.
        masses = {"u": (2.16, 1273.0, 172570.0), "d": (4.70, 93.5, 4183.0),
                  "e": (0.511, 105.66, 1776.93), "ν": (5e-8, 5e-8, 5e-8),
                  "ū": (2.16, 1273.0, 172570.0), "d̄": (4.70, 93.5, 4183.0),
                  "e⁺": (0.511, 105.66, 1776.93), "N": (None, None, None)}
        grows = []
        for f, group in enumerate(self.families):
            for k, w in enumerate(family):
                m = masses[vis.particle_label(w)][f]
                if m is None:
                    grows.append(group[0][k].animate.set_opacity(0.25))
                    continue
                size = 0.55 + 0.33 * (math.log10(m) + 8)
                grows.append(group[0][k].animate.scale(size / 1.9))
        texture = self.texture_inset()
        self.beat(*grows, *hud.set_inset(texture, "OneTheory: flavon powers in all four "
                                                  "Yukawas", 2.9),
                  sub="Glow size shows each particle's measured mass: from neutrinos (< 1 eV) "
                      "to the top quark (172.6 GeV).",
                  formulas=["Yukawa ~ ε^(power):", "[ –  0  0 ]", "[ 0  1  1 ]", "[ 0  1  1 ]",
                            "→ 2 unsuppressed, 1 light", "observed: 1 heavy family"],
                  badges=[("MEASURED", "masses e 0.511 MeV … t 172.6 GeV (PDG 2024)"),
                          ("ONETHEORY", "exact holomorphic Yukawas: one anomalous-U(1) "
                                        "texture"),
                          ("HYPOTHESIS", "real hierarchy needs metrics or instantons "
                                         "(open)")],
                  run_time=3.5)
        self.wait(3.0)
        self.family_labels = family_labels

    def texture_inset(self) -> VGroup:
        entries = (("–", "0", "0"), ("0", "1", "1"), ("0", "1", "1"))
        grid = VGroup()
        for i, row in enumerate(entries):
            for j, value in enumerate(row):
                color = {"–": MUTED, "0": vis.SPIN10_COLOR, "1": vis.SU4_COLOR}[value]
                cell = Square(0.5, stroke_color=MUTED, stroke_width=1, fill_color=color,
                              fill_opacity={"–": 0.08, "0": 0.45, "1": 0.25}[value])
                cell.move_to([j * 0.52, -i * 0.52, 0])
                grid.add(VGroup(cell, text(value, 18, INK).move_to(cell)))
        note = VGroup(text("0: unsuppressed   1: one flavon power", 12, MUTED),
                      text("E = family in V₁,  F = two in V₂", 12, MUTED))
        note.arrange(DOWN, buff=0.06)
        return VGroup(grid, note).arrange(DOWN, buff=0.18)

