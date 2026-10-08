"""Acts 6 to 14 of the Genesis film: from inflation to the cosmic horizons.

Owns:
    The second half of the one-shot film as a mixin of the `Genesis` scene:
    inflation, reheating, the Higgs field, confinement, nucleosynthesis, the
    first light, the cosmic web, a galaxy and the horizons, plus the finale.
    One live image (the cosmic window) carries every act; its painters hand
    over at frames where they paint identical pixels.

Depends on:
    Manim Community, NumPy, and the film's `physics`, `cosmos`, `stage` and
    `visuals` modules.

Must not:
    Cut, use time-dependent updaters, or show a scene without its evidence
    badges.

Phase 0:
    Presentation of established science, measurements and labelled hypotheses.
"""

from __future__ import annotations

import math

import cosmos
import numpy as np
import physics
import visuals as vis
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Group,
    Line,
    Rectangle,
    ValueTracker,
    VGroup,
    VMobject,
    always_redraw,
    linear,
)
from stage import CATEGORIES, CENTER, INK, MUTED, SHORT, fit, live_text, text

WINDOW_HEIGHT = 5.3
INSET_HEIGHT = 2.9
GYR_S = physics.GYR_S


def logt_of_gyr(gyr: float) -> float:
    return math.log10(gyr * GYR_S)


def _late(t: float) -> float:
    """Appear in the second half of a beat, after the old inset has left."""

    return float(np.clip((t - 0.45) / 0.55, 0, 1) ** 2 * (3 - 2 * np.clip((t - 0.45) / 0.55,
                                                                         0, 1)))


class LateActs:
    """Mixin: acts 6–14. Expects `self.hud`, `self.beat` and act 5's objects."""

    # ------------------------------------------------------------------
    # the cosmic window
    # ------------------------------------------------------------------
    def build_window(self) -> None:
        self.universe = cosmos.Universe()
        self.soup = cosmos.Soup(self.universe)
        self.galaxy = cosmos.Galaxy()
        self.late = cosmos.Cosmos(self.universe, self.galaxy)
        self.window_mode = "inflation"
        self.t_window = ValueTracker(0.0)
        self.t_efolds, self.t_grid = ValueTracker(0.0), ValueTracker(1.0)
        self.t_logw = ValueTracker(-cosmos.N_END)
        self.t_soup = ValueTracker(0.0)
        self.t_growth, self.t_cmb = ValueTracker(0.0), ValueTracker(1.0)
        self.t_logzoom, self.t_web = ValueTracker(0.0), ValueTracker(0.0)
        self.t_stars, self.t_gal = ValueTracker(0.0), ValueTracker(0.0)
        self.t_form, self.t_angle = ValueTracker(0.0), ValueTracker(0.0)
        self.t_horizon, self.t_twinkle = ValueTracker(0.0), ValueTracker(0.0)
        self.window = vis.live_image(self.paint_window, WINDOW_HEIGHT)

    def paint_window(self) -> np.ndarray:
        mode = self.window_mode
        if mode == "inflation":
            array = self.universe.paint_inflation(self.t_efolds.get_value(),
                                                  self.t_grid.get_value())
        elif mode == "widening":
            array = self.universe.paint_widening(math.exp(self.t_logw.get_value()))
        elif mode == "soup":
            array = self.soup.paint(self.t_soup.get_value())
        else:
            array = self.late.paint(
                growth=self.t_growth.get_value(), cmb=self.t_cmb.get_value(),
                zoom=math.exp(self.t_logzoom.get_value()), web=self.t_web.get_value(),
                stars=self.t_stars.get_value(), galaxy=self.t_gal.get_value(),
                form=self.t_form.get_value(), angle=self.t_angle.get_value(),
                horizon=self.t_horizon.get_value(), twinkle=self.t_twinkle.get_value())
        opacity = self.t_window.get_value()
        if opacity < 0.999:
            array = array.copy()
            array[..., 3] = (array[..., 3] * opacity).astype(np.uint8)
        return array

    def window_point(self, xy) -> np.ndarray:
        """Scene point of window coordinates in [-1, 1]²."""

        return np.asarray(CENTER) + np.array([xy[0], xy[1], 0]) * WINDOW_HEIGHT / 2

    def show_inset(self, content, caption: str, builder=None) -> list:
        """Swap the inset. Static `content` fades in; a live `builder` (geometry only,
        no text) is redrawn every frame and faded by a tracker, so it keeps moving
        while it appears."""

        parts = VGroup() if content is None else content
        anims = []
        if builder is not None:
            appear = ValueTracker(0.0)
            live = always_redraw(lambda: builder().fade(1 - appear.get_value()))
            self.add(live)
            parts = VGroup(parts, live)
            group = AnimationGroup(appear.animate(rate_func=_late).set_value(1.0), run_time=1.2)
            group.hud = True
            anims.append(group)
        anims = self.hud.adopt_inset(parts, caption, height=INSET_HEIGHT) + anims
        if content is not None:
            group = AnimationGroup(FadeIn(content, rate_func=_late), run_time=1.2)
            group.hud = True
            anims.append(group)
        return anims

    def plot(self, xs, ys, x_range, y_range, color: str, width: float = 2.5):
        """A polyline in the inset's data box; returns (mobject, to_screen, frame)."""

        center, w, h = self.hud.inset_box(INSET_HEIGHT)
        w, h = w * 0.82, h * 0.7
        origin = center + np.array([-w / 2 + 0.12, -h / 2 + 0.05, 0])

        def to_screen(x, y):
            return origin + np.array([(x - x_range[0]) / (x_range[1] - x_range[0]) * w,
                                      (y - y_range[0]) / (y_range[1] - y_range[0]) * h, 0])

        pts = np.array([to_screen(x, y) for x, y in zip(xs, ys, strict=True)])
        line = VMobject(stroke_color=color, stroke_width=width)
        line.set_points_as_corners(pts)
        return line, to_screen, (origin, w, h)

    def axes(self, frame, x_label: str, y_label: str) -> VGroup:
        origin, w, h = frame
        return VGroup(
            Line(origin, origin + RIGHT * w, stroke_color=MUTED, stroke_width=1.2),
            Line(origin, origin + UP * h, stroke_color=MUTED, stroke_width=1.2),
            text(x_label, 10.5, MUTED).next_to(origin + RIGHT * w / 2, DOWN, buff=0.06),
            text(y_label, 10.5, MUTED).rotate(math.pi / 2).next_to(origin + UP * h / 2, LEFT,
                                                                   buff=0.06))

    # ------------------------------------------------------------------
    # Act 6 · inflation
    # ------------------------------------------------------------------
    def act_inflation(self) -> None:
        hud = self.hud
        self.build_window()
        group = VGroup(self.families, self.family_labels)
        center, width, height = hud.inset_box(INSET_HEIGHT)
        scale = min(width / group.width, height / group.height) * 0.95
        self.add(self.window)
        self.beat(group.animate.scale(scale).move_to(center),
                  *hud.adopt_inset(group, "the rules of matter: three families",
                                   INSET_HEIGHT),
                  self.t_window.animate.set_value(1.0),
                  title="6 · Inflation: space stretches, ripples freeze",
                  sub="Now the stage itself: space. In a split instant it doubles again and "
                      "again: inflation.",
                  formulas=["a(t) ∝ e^(Ht)", "N ≈ 60 e-folds: ×10²⁶",
                            "δφ ≈ H / 2π at horizon exit", "Δ² ∝ k^(n_s − 1)",
                            "n_s = 0.9649 ± 0.0042"],
                  badges=[("MEASURED", "nearly scale-free ripples: n_s = 0.9649 ± 0.0042 "
                                       "(Planck 2018)"),
                          ("HYPOTHESIS", "inflation and its inflaton field: favoured, not "
                                         "proven"),
                          ("POSSIBLE", "7.8 of ~60 e-folds shown; begins after the shape "
                                       "settles")],
                  clock=-36.0, run_time=3.0)
        exit_plot = self.horizon_exit_plot()
        self.play(*self.show_inset(exit_plot, "a ripple's size vs the horizon"), run_time=1.5)
        n_end = cosmos.N_END
        self.beat(self.t_efolds.animate.set_value(n_end * 0.3),
                  sub="Quantum jitters (the same trembling as the seed) appear at the horizon's "
                      "size…",
                  clock=-34.5, run_time=7.0, rate_func=linear)
        self.beat(self.t_efolds.animate.set_value(n_end * 0.65),
                  sub="…are stretched far beyond it and freeze into ripples of space itself.",
                  clock=-33.2, run_time=8.0, rate_func=linear)
        self.beat(self.t_efolds.animate.set_value(n_end), self.t_grid.animate.set_value(0.0),
                  sub="Earlier ripples end up larger. The pattern is almost the same at every "
                      "scale: n_s = 0.965.",
                  clock=-32.0, run_time=7.0, rate_func=linear)
        self.window_mode = "widening"
        self.beat(self.t_logw.animate.set_value(0.0),
                  sub="Inflation ends. Zoom back out: the frozen ripples cover the region that "
                      "becomes our visible universe.",
                  run_time=6.0)
        self.wait(0.8)

    def horizon_exit_plot(self) -> VGroup:
        n_end = cosmos.N_END
        xs = np.linspace(0, n_end, 2)
        horizon, to_screen, frame = self.plot(xs, [math.log(cosmos.LAMBDA_BORN)] * 2,
                                              (0, n_end), (-4.5, 3.0), vis.STRING_COLOR)
        group = VGroup(self.axes(frame, "time (e-folds)", "log size"), horizon)
        for layer in self.universe.layers[2::2]:
            ys = math.log(layer.wavelength) + xs
            ys = np.clip(ys, -4.5, 3.0)
            line, _, _ = self.plot(xs, ys, (0, n_end), (-4.5, 3.0), vis.SPIN10_COLOR, 1.6)
            group.add(line)
        group.add(text("horizon", 10.5, vis.STRING_COLOR).move_to(
            to_screen(n_end * 0.82, math.log(cosmos.LAMBDA_BORN)) + UP * 0.13))
        group.add(text("ripples", 10.5, vis.SPIN10_COLOR).move_to(
            to_screen(n_end * 0.2, 1.6)))
        marker = always_redraw(lambda: Line(
            to_screen(self.t_efolds.get_value(), -4.5), to_screen(self.t_efolds.get_value(), 3),
            stroke_color=INK, stroke_width=1.5, stroke_opacity=0.8))
        group.add(marker)
        return group

    # ------------------------------------------------------------------
    # Act 7 · reheating
    # ------------------------------------------------------------------
    def act_reheating(self) -> None:
        self.window_mode = "soup"
        legend = self.particle_legend()
        self.beat(self.t_soup.animate.set_value(5.0), *self.show_inset(legend, "who is in the "
                                                                               "soup"),
                  title="7 · Reheating: the energy becomes particles",
                  sub="The inflaton's energy pours into a hot soup of every particle of the "
                      "three families, all moving near light speed.",
                  formulas=["inflaton → quarks, gluons,", "  leptons, photons, W, Z, H",
                            "ρ ∝ T⁴ (radiation)", "T_reheat: unknown, ≤ 10¹⁶ GeV",
                            "denser where ripples were higher"],
                  badges=[("ESTABLISHED", "the hot Big Bang: radiation era, ρ ∝ a⁻⁴"),
                          ("MEASURED", "T_reheat above ~5 MeV (nucleosynthesis works)"),
                          ("HYPOTHESIS", "how and how hot reheating happened"),
                          ("POSSIBLE", "particles drawn as icons; ~10⁸⁰ in reality")],
                  clock=-25.0, run_time=6.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(14.0),
                  sub="Colour-charged quarks (red, green, blue) and their antiquarks (cyan, "
                      "magenta, yellow) fill space with gluons and light.",
                  clock=-12.5, run_time=9.0, rate_func=linear)

    def particle_legend(self) -> VGroup:
        rows = (("#ef4444", "quarks: red green blue"), ("#22d3ee", "antiquarks: anticolours"),
                ("#f9a8d4", "gluons"), ("#a78bfa", "W, Z, Higgs, top"),
                ("#93c5fd", "electrons"), ("#fdba74", "positrons"),
                ("#64748b", "neutrinos"), ("#fef08a", "photons (light)"))
        group = VGroup(*[VGroup(Dot(radius=0.07, color=c), text(t, 13, INK))
                         .arrange(RIGHT, buff=0.12) for c, t in rows])
        group.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        center, width, height = self.hud.inset_box(INSET_HEIGHT)
        return fit(group, width, height).move_to(center)

    # ------------------------------------------------------------------
    # Act 8 · the Higgs field
    # ------------------------------------------------------------------
    def act_higgs(self) -> None:
        self.t_T, self.t_hat = ValueTracker(400.0), ValueTracker(0.0)
        hat = always_redraw(self.higgs_hat)
        reading = live_text(lambda: f"T = {5 * round(self.t_T.get_value() / 5):3d} GeV", 16,
                            vis.STRING_COLOR, lambda: np.asarray(CENTER) + np.array([3.4, 2.3, 0]),
                            opacity=lambda: self.t_hat.get_value())
        self.add(hat, reading)
        self.beat(self.t_hat.animate.set_value(1.0), self.t_window.animate.set_value(0.32),
                  self.t_soup.animate.set_value(18.0), self.t_T.animate.set_value(260.0),
                  *self.show_inset(self.mass_labels(), "masses switched on by the field",
                                   builder=self.mass_bars),
                  title="8 · The Higgs field settles",
                  sub="As the soup cools, the energy landscape of the Higgs field changes "
                      "shape. Hot: its lowest point is the centre.",
                  formulas=["V(φ) = λ/4 (φ² − v²)²", "λ = m_H² / 2v² = 0.129",
                            "v = 246.22 GeV", "T_c ≈ 159.5 GeV,  t ≈ 9×10⁻¹² s",
                            "m_W = g v / 2 = 80.4 GeV"],
                  badges=[("MEASURED", "m_H = 125.20 ± 0.11 GeV, v = 246.22 GeV (PDG)"),
                          ("ESTABLISHED", "Higgs mechanism; smooth crossover at 159.5 GeV "
                                          "(lattice)"),
                          ("POSSIBLE", "thermal shape: a mean-field sketch; height rescaled")],
                  clock=-11.6, run_time=4.0, rate_func=linear)
        self.beat(self.t_T.animate.set_value(0.0), self.t_soup.animate.set_value(26.0),
                  sub="Below 159.5 GeV the lowest point moves off-centre: the field settles at "
                      "v = 246 GeV everywhere at once.",
                  clock=-10.5, run_time=8.0, rate_func=linear)
        self.wait(1.0)
        self.beat(self.t_hat.animate.set_value(0.0), self.t_window.animate.set_value(1.0),
                  self.t_soup.animate.set_value(34.0),
                  sub="Particles that feel the field gain mass and slow down. W, Z, Higgs and "
                      "top quarks soon decay away.",
                  clock=-7.5, run_time=8.0, rate_func=linear)
        self.remove(hat, reading)

    def higgs_hat(self) -> VGroup:
        temperature, opacity = self.t_T.get_value(), self.t_hat.get_value()
        v, lam = physics.HIGGS_V_GEV, physics.higgs_lambda()
        norm = lam * v**4 / 4
        rs = np.linspace(0, 1.5, 61)
        heights = (physics.higgs_potential(rs * v, temperature)
                   - physics.higgs_potential(0.0, temperature)) / norm
        scale = 1.0 / max(1.0, float(np.max(np.abs(heights))) / 1.45)
        center = np.asarray(CENTER) + DOWN * 0.15
        radius, lift = 1.95, 0.85

        def point(r, theta):
            h = float(np.interp(r, rs, heights)) * scale
            return center + np.array([radius * r * math.cos(theta),
                                      0.36 * radius * r * math.sin(theta) + lift * h, 0])

        group = VGroup()
        thetas = np.linspace(0, 2 * math.pi, 73)
        for r in np.linspace(0.15, 1.5, 10):
            ring = VMobject(stroke_color=vis.E8_COLOR, stroke_width=1.6,
                            stroke_opacity=0.75 * opacity)
            ring.set_points_smoothly([point(r, t) for t in thetas])
            group.add(ring)
        for theta in np.linspace(0, 2 * math.pi, 28, endpoint=False):
            spoke = VMobject(stroke_color=vis.E8_COLOR, stroke_width=1.2,
                             stroke_opacity=0.5 * opacity)
            spoke.set_points_smoothly([point(r, theta) for r in np.linspace(0, 1.5, 25)])
            group.add(spoke)
        r_min = math.sqrt(max(0.0, 1 - (temperature / 159.5) ** 2))
        ball = point(r_min, -math.pi / 2) + UP * 0.1
        group.add(Dot(ball, radius=0.22, color=vis.STRING_COLOR, fill_opacity=0.2 * opacity))
        group.add(Dot(ball, radius=0.11, color=vis.STRING_COLOR, fill_opacity=opacity))
        return group

    MASSES = (("W", 80.37), ("Z", 91.19), ("Higgs", 125.20), ("top", 172.57))

    def mass_layout(self):
        center, width, height = self.hud.inset_box(INSET_HEIGHT)
        top = center[1] + height / 2 - 0.25
        left = center[0] - width / 2 + 0.55
        return center, top, left, width - 1.35

    def mass_labels(self) -> VGroup:
        center, top, left, span = self.mass_layout()
        group = VGroup()
        for k, (name, mass) in enumerate(self.MASSES):
            y = top - k * 0.5
            group.add(text(name, 13, INK).move_to([left - 0.3, y, 0]))
            group.add(text(f"{mass:.1f} GeV", 12, MUTED).move_to([left + span + 0.35, y, 0]))
        group.add(text("bar = coupling × ⟨φ⟩;  numbers: today", 11, MUTED).move_to(
            [center[0], top - 2.0, 0]))
        return group

    def mass_bars(self) -> VGroup:
        temperature = self.t_T.get_value()
        fraction = math.sqrt(max(0.0, 1 - (temperature / 159.5) ** 2))
        _, top, left, span = self.mass_layout()
        group = VGroup()
        for k, (_, mass) in enumerate(self.MASSES):
            m = mass * fraction
            group.add(Rectangle(width=max(span * m / 180, 1e-3), height=0.22, stroke_width=0,
                                fill_color=vis.E8_COLOR, fill_opacity=0.85)
                      .move_to([left + span * m / 360, top - k * 0.5, 0]))
        return group

    # ------------------------------------------------------------------
    # Act 9 · confinement
    # ------------------------------------------------------------------
    def act_confinement(self) -> None:
        self.beat(self.t_soup.animate.set_value(44.0),
                  *self.show_inset(self.proton_labels(), "inside a proton",
                                   builder=self.proton_inset),
                  title="9 · Quarks lock into protons and neutrons",
                  sub="Quarks meet antiquarks and annihilate in flashes of light. For every "
                      "billion pairs, one extra quark survives.",
                  formulas=["T_c ≈ 156 MeV (lattice QCD)", "t ≈ 2 × 10⁻⁵ s",
                            "proton = uud,  neutron = udd", "m_p = 938.27 MeV",
                            "m_u + m_u + m_d ≈ 9.0 MeV"],
                  badges=[("MEASURED", "matter excess η = 6.1×10⁻¹⁰ per photon (Planck, "
                                       "BBN)"),
                          ("ESTABLISHED", "confinement; QCD crossover ≈ 156 MeV (lattice)"),
                          ("HYPOTHESIS", "why matter won: e.g. leptogenesis via the 16th "
                                         "particle N"),
                          ("POSSIBLE", "survivors drawn ~10⁸× more often than real")],
                  clock=-5.2, run_time=10.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(52.0),
                  sub="Colour can no longer roam free: the survivors lock in threes, one red, "
                      "one green, one blue.",
                  clock=-4.6, run_time=8.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(58.0),
                  sub="99% of a proton's mass is the energy of the gluon field binding its "
                      "quarks (E = mc²).",
                  clock=-3.5, run_time=6.0, rate_func=linear)

    def proton_labels(self) -> VGroup:
        center, _, _ = self.hud.inset_box(INSET_HEIGHT)
        return VGroup(
            text("u u d: two up quarks, one down", 11.5, INK).move_to(center + DOWN * 0.62),
            text("quarks ≈ 9 MeV, proton 938.3 MeV", 11.5, INK).move_to(center + DOWN * 0.84),
            text("the rest is gluon-field energy", 11.5, MUTED).move_to(center + DOWN * 1.06))

    def proton_inset(self) -> VGroup:
        center, _, _ = self.hud.inset_box(INSET_HEIGHT)
        c = center + UP * 0.3
        spin = 0.8 * self.t_soup.get_value()
        group = VGroup(Circle(radius=0.72, stroke_color=MUTED, stroke_width=1,
                              stroke_opacity=0.5).move_to(c))
        quarks = []
        for k, color in enumerate(("#ef4444", "#22c55e", "#3b82f6")):
            angle = spin + k * 2 * math.pi / 3
            quarks.append((c + 0.5 * np.array([math.cos(angle), 0.8 * math.sin(angle), 0]),
                           color))
        for p, _ in quarks:
            group.add(Line(c, p, stroke_color="#f9a8d4", stroke_width=5, stroke_opacity=0.55))
        for p, color in quarks:
            group.add(Dot(p, radius=0.13, color=color))
        return group

    # ------------------------------------------------------------------
    # Act 10 · the first nuclei
    # ------------------------------------------------------------------
    def act_nuclei(self) -> None:
        abundances = self.abundance_inset()
        self.beat(self.t_soup.animate.set_value(63.0),
                  title="10 · The first three minutes: nuclei",
                  sub="One second: neutrinos stop interacting and stream away. Weak reactions "
                      "turn neutrons (grey) into protons (pink).",
                  formulas=["n/p = e^(−Δm/kT),  Δm = 1.293 MeV", "freeze-out ≈ 1 s: n/p ≈ 1/6",
                            "τ_n = 878 s → n/p ≈ 1/7", "Y_p ≈ 2(n/p)/(1 + n/p) ≈ 0.25"],
                  badges=[("MEASURED", "helium Y_p = 0.245 ± 0.003; D/H = 2.55×10⁻⁵"),
                          ("ESTABLISHED", "Big-Bang nucleosynthesis (Alpher–Gamow 1948; "
                                          "Wagoner 1967)"),
                          ("POSSIBLE", "32 nuclei shown; proportions as in nature")],
                  clock=0.0, run_time=6.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(72.0),
                  sub="Electrons and positrons annihilate. About one neutron per six protons "
                      "is frozen in; free neutrons slowly decay.",
                  clock=1.6, run_time=9.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(84.0), *self.show_inset(abundances, "made in "
                                                                                    "the first "
                                                                                    "minutes"),
                  sub="By three minutes almost every neutron is locked into helium-4: a quarter "
                      "of all ordinary matter by mass.",
                  clock=2.4, run_time=10.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(88.0), clock=3.5, run_time=3.5,
                  rate_func=linear)

    def abundance_inset(self) -> VGroup:
        center, width, height = self.hud.inset_box(INSET_HEIGHT)
        rows = (("hydrogen", 0.754, cosmos.PROTON), ("helium-4", 0.246, "#fde68a"))
        group = VGroup()
        left = center[0] - width / 2 + 0.2
        right = center[0] + width / 2 - 0.2
        for k, (name, share, color) in enumerate(rows):
            y = center[1] + 0.55 - k * 0.6
            label = text(name, 13, INK)
            group.add(label.move_to([left + label.width / 2, y + 0.22, 0]))
            value = text(f"{share * 100:.1f}% by mass", 12, MUTED)
            group.add(value.move_to([right - value.width / 2, y + 0.22, 0]))
            group.add(Rectangle(width=(width - 0.4) * share, height=0.2, stroke_width=0,
                                fill_color=color, fill_opacity=0.9)
                      .move_to([left + (width - 0.4) * share / 2, y, 0]))
        group.add(text("deuterium D/H = 2.5×10⁻⁵", 11.5, MUTED).move_to(center + DOWN * 0.55))
        group.add(text("lithium-7/H ≈ 1.6×10⁻¹⁰", 11.5, MUTED).move_to(center + DOWN * 0.8))
        return group

    # ------------------------------------------------------------------
    # Act 11 · the first light
    # ------------------------------------------------------------------
    def act_first_light(self) -> None:
        spectrum = self.blackbody_inset()
        self.beat(self.t_soup.animate.set_value(95.0),
                  title="11 · The fog clears: the first light",
                  sub="For 380,000 years light cannot travel far: it keeps scattering off free "
                      "electrons. The universe is a glowing fog.",
                  formulas=["e⁻ + p → H + γ  at T ≈ 3000 K", "z ≈ 1090,  t ≈ 372,000 yr",
                            "T₀ = 2.7255 K today", "ΔT/T ≈ 10⁻⁵ (contrast ×10⁴ here)"],
                  badges=[("MEASURED", "CMB T₀ = 2.7255 K, ripples 10⁻⁵ (COBE, WMAP, "
                                       "Planck)"),
                          ("ESTABLISHED", "recombination at z ≈ 1090 (ΛCDM)"),
                          ("POSSIBLE", "map grown from our inflation ripples; peaks "
                                       "approximated")],
                  clock=9.0, run_time=8.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(104.0),
                  sub="At 3000 K electrons settle onto nuclei: the first atoms. The fog clears "
                      "and light flies free.",
                  clock=12.9, run_time=9.0, rate_func=linear)
        self.beat(self.t_soup.animate.set_value(cosmos.TAU_END),
                  *self.show_inset(spectrum, "its spectrum today: a perfect blackbody"),
                  sub="That light still reaches us, stretched 1090× into microwaves: the "
                      "cosmic microwave background, the ripples of inflation.",
                  clock=13.07, run_time=10.0, rate_func=linear)
        self.wait(1.5)

    def blackbody_inset(self) -> VGroup:
        nu = np.linspace(1, 700, 160)
        x = nu * 0.0479924 / 2.7255
        b = x**3 / np.expm1(x)
        curve, to_screen, frame = self.plot(nu, b / b.max(), (0, 700), (0, 1.1), "#f97316")
        peak = to_screen(160.2, 1.0)
        return VGroup(self.axes(frame, "frequency (GHz)", "brightness"), curve,
                      Dot(peak, radius=0.05, color=INK),
                      text("peak 160 GHz", 10.5, INK).move_to(peak + RIGHT * 0.6 + UP * 0.05),
                      text("T₀ = 2.7255 K", 12, "#f97316").move_to(to_screen(470, 0.65)))

    # ------------------------------------------------------------------
    # Act 12 · the cosmic web
    # ------------------------------------------------------------------
    def act_web(self) -> None:
        self.window_mode = "late"
        growth = self.growth_inset()
        self.beat(self.t_cmb.animate.set_value(0.3), self.t_growth.animate.set_value(0.35),
                  self.t_web.animate.set_value(1.0),
                  *self.show_inset(growth, "growth of structure D(t)"),
                  title="12 · Gravity weaves the cosmic web",
                  sub="Dark ages: the light fades into the infrared and there are no stars yet. "
                      "But gravity is at work.",
                  formulas=["x(t) = q + D(t) · ψ(q)", "∇ · ψ = −δ(q)",
                            "δ = ∇² of the ripples", "D ∝ a in the matter era",
                            "Ω_m = 0.315 (85% dark)"],
                  badges=[("ESTABLISHED", "Zel'dovich approximation (1970); ΛCDM growth"),
                          ("MEASURED", "Ω_m = 0.315 ± 0.007 (Planck); web mapped by SDSS, "
                                       "DESI"),
                          ("HYPOTHESIS", "what dark matter is; one idea: the hidden E₈′ "
                                         "sector")],
                  clock=15.2, run_time=8.0)
        self.beat(self.t_cmb.animate.set_value(0.0), self.t_growth.animate.set_value(1.0),
                  sub="Slightly denser regions pull in more matter: sheets, filaments and "
                      "knots, the cosmic web.",
                  clock=16.0, run_time=9.0)
        self.beat(self.t_stars.animate.set_value(1.0), self.t_twinkle.animate.set_value(2.0),
                  sub="In the densest knots gas collapses and ignites: the first stars, about "
                      "100–200 million years after the beginning.",
                  clock=16.5, run_time=6.0, rate_func=linear)

    def growth_inset(self) -> VGroup:
        a = np.logspace(-3, 0, 40)
        t = np.array([physics.age_at(x, 20000) for x in a])
        d = np.array([physics.growth_factor(x) for x in a])
        curve, to_screen, frame = self.plot(t, d, (0, 14), (0, 1.05), vis.MATTER_COLOR)

        def marker() -> Dot:
            gyr = 10 ** self.hud.logt.get_value() / GYR_S
            return Dot(to_screen(min(gyr, 14), float(np.interp(gyr, t, d))), radius=0.06,
                       color=INK)

        return VGroup(self.axes(frame, "time (billion years)", "D"), curve,
                      always_redraw(marker))

    # ------------------------------------------------------------------
    # Act 13 · a galaxy
    # ------------------------------------------------------------------
    def act_galaxy(self) -> None:
        log_max = math.log(cosmos.GALAXY_ZOOM)
        rotation = self.rotation_inset()
        self.beat(self.t_logzoom.animate.set_value(log_max * 0.45),
                  self.t_gal.animate.set_value(0.7), self.t_twinkle.animate.set_value(4.0),
                  title="13 · A galaxy is born",
                  sub="Dive into one knot of the web. Gas keeps falling in, spinning faster as "
                      "it shrinks.",
                  formulas=["r = r₀ e^(θ·tan p),  p ≈ 12°", "v(r) ≈ 220–230 km/s, flat",
                            "visible mass only: v ∝ r^(−½)", "⇒ M(r) ∝ r: a dark halo"],
                  badges=[("MEASURED", "flat rotation curves (Rubin & Ford 1970s); Sun at "
                                       "8.2 kpc, 230 km/s"),
                          ("HYPOTHESIS", "a dark-matter halo (or modified gravity)"),
                          ("POSSIBLE", "an illustrative two-armed spiral")],
                  clock=16.8, run_time=7.0)
        self.beat(self.t_logzoom.animate.set_value(log_max), self.t_web.animate.set_value(0.0),
                  self.t_stars.animate.set_value(0.0), self.t_gal.animate.set_value(1.0),
                  self.t_form.animate.set_value(1.0), self.t_angle.animate.set_value(1.6),
                  sub="It flattens into a spinning disk, and spiral arms of young blue stars "
                      "form.",
                  clock=17.2, run_time=9.0)
        self.t_sun = ValueTracker(0.0)
        sun = VGroup(always_redraw(self.sun_marker),
                     live_text(lambda: "Sun", 13, vis.STRING_COLOR,
                               lambda: self.sun_point() + np.array([0.0, 0.24, 0]),
                               opacity=lambda: self.t_sun.get_value()))
        self.add(sun)
        self.beat(self.t_angle.animate.set_value(2.6), self.t_sun.animate.set_value(1.0),
                  *self.show_inset(rotation, "how fast its stars orbit"),
                  sub="Far from the centre stars still orbit at about 230 km/s. Visible matter "
                      "alone cannot hold them: unseen mass must.",
                  clock=17.46, run_time=8.0, rate_func=linear)
        self.beat(self.t_angle.animate.set_value(3.4),
                  sub="One ordinary star among 100 billion forms 4.6 billion years ago, 26,000 "
                      "light-years from the centre: the Sun.",
                  clock=17.55, run_time=6.0, rate_func=linear)
        self.sun = sun

    def sun_point(self) -> np.ndarray:
        zoom = math.exp(self.t_logzoom.get_value())
        scale = zoom / cosmos.GALAXY_ZOOM
        center = self.late.to_view(self.late.node[None, :], zoom)[0]
        angle = 2.2 + self.t_angle.get_value()
        r = 0.48 * scale
        return self.window_point(center + r * np.array([math.cos(angle), math.sin(angle)]))

    def sun_marker(self) -> VGroup:
        return Circle(radius=0.09, stroke_color=vis.STRING_COLOR, stroke_width=2,
                      stroke_opacity=self.t_sun.get_value()).move_to(self.sun_point())

    def rotation_inset(self) -> VGroup:
        r = np.linspace(0.2, 25, 80)
        flat, to_screen, frame = self.plot(r, physics.flat_rotation_speed(r), (0, 25),
                                           (0, 260), vis.SPIN10_COLOR)
        kepler, _, _ = self.plot(r, physics.keplerian_speed(r), (0, 25), (0, 260),
                                 vis.SU4_COLOR, 2.0)
        return VGroup(self.axes(frame, "distance (kpc)", "speed"), flat, kepler,
                      text("observed", 11, vis.SPIN10_COLOR).move_to(to_screen(18, 240)),
                      text("visible mass only", 11, vis.SU4_COLOR).move_to(to_screen(16, 95)))

    # ------------------------------------------------------------------
    # Act 14 · the horizons
    # ------------------------------------------------------------------
    def act_horizons(self) -> None:
        hz = self.late.horizons
        final_log = math.log(0.9 * cosmos.WINDOW_GLY / hz["particle"])
        expansion = self.expansion_inset()
        self.beat(self.t_logzoom.animate.set_value(0.0), self.t_web.animate.set_value(1.0),
                  self.t_sun.animate.set_value(0.0), self.t_angle.animate.set_value(4.0),
                  title="14 · To the horizons",
                  sub="Zoom out. Our galaxy is one of about two trillion, strung along the "
                      "cosmic web.",
                  formulas=[f"c / H₀ = {hz['hubble']:.1f} Gly  (Hubble sphere)",
                            f"∫ c dt / a = {hz['particle']:.1f} Gly  (particle horizon)",
                            f"event horizon: {hz['event']:.1f} Gly",
                            f"t₀ = {physics.age_at(1.0):.2f} Gyr"],
                  badges=[("MEASURED", "H₀ = 67.4 km/s/Mpc, Ω_Λ = 0.685 (Planck 2018); "
                                       "acceleration (1998)"),
                          ("ESTABLISHED", "horizons of flat ΛCDM, computed here"),
                          ("HYPOTHESIS", "dark energy is a cosmological constant Λ?")],
                  clock=17.6, run_time=8.0)
        self.remove(self.sun)
        self.beat(self.t_logzoom.animate.set_value(math.log(0.12)),
                  *self.show_inset(expansion, "the expansion: a(t)"),
                  sub="On the largest scales the web looks the same everywhere and in every "
                      "direction.",
                  run_time=7.0)
        self.beat(self.t_logzoom.animate.set_value(final_log), self.t_horizon.animate
                  .set_value(1.0),
                  sub="Here is the edge of what we can see: light that left 13.8 billion years "
                      "ago, from places now 46 billion light-years away.",
                  clock=17.64, run_time=7.0)
        scene_per_gly = WINDOW_HEIGHT / 2 * 0.9 / hz["particle"]
        center = np.asarray(CENTER)
        hubble = Circle(radius=hz["hubble"] * scene_per_gly, stroke_color=vis.SPIN10_COLOR,
                        stroke_width=2).move_to(center)
        event = Circle(radius=hz["event"] * scene_per_gly, stroke_color=vis.SU4_COLOR,
                       stroke_width=2).move_to(center)
        particle = Circle(radius=hz["particle"] * scene_per_gly, stroke_color=INK,
                          stroke_width=1.5, stroke_opacity=0.7).move_to(center)
        here = VGroup(Dot(center, radius=0.05, color=vis.STRING_COLOR),
                      text("you are here", 12, vis.STRING_COLOR).move_to(center + DOWN * 0.22))
        labels = VGroup(
            text(f"Hubble sphere {hz['hubble']:.1f} Gly", 12, vis.SPIN10_COLOR)
            .move_to(center + np.array([-1.1, 1.18, 0])),
            text(f"event horizon {hz['event']:.1f} Gly", 12, vis.SU4_COLOR)
            .move_to(center + np.array([1.1, -1.18, 0])),
            text(f"edge of the visible universe {hz['particle']:.1f} Gly", 12, INK)
            .move_to(center + np.array([0, 2.6, 0])),
            text("first light (CMB shell)", 12, "#fca5a5")
            .move_to(center + np.array([0, -2.6, 0])))
        self.beat(Create(hubble), Create(event), Create(particle), FadeIn(here),
                  FadeIn(labels),
                  sub="The glowing shell is the first light again: the same ripples born during "
                      "inflation, now at the edge of the visible universe.",
                  run_time=4.0)
        self.wait(2.5)
        self.beat(event.animate.set_stroke(width=4),
                  sub="Beyond 16.7 billion light-years, dark energy carries galaxies away "
                      "faster than their light can ever reach us.",
                  run_time=3.0)
        self.wait(2.5)
        self.finale(VGroup(hubble, event, particle, here, labels))

    def expansion_inset(self) -> VGroup:
        a = np.linspace(0.02, 1.9, 60)
        t = np.array([physics.age_at(x, 20000) for x in a])
        past = t <= physics.age_at(1.0)
        curve, to_screen, frame = self.plot(t[past], a[past], (0, 30), (0, 2.0),
                                            vis.SPIN10_COLOR)
        future, _, _ = self.plot(t[~past], a[~past], (0, 30), (0, 2.0), vis.SPIN10_COLOR, 1.5)
        future.set_stroke(opacity=0.5)
        turn = (physics.OMEGA_M / (2 * physics.OMEGA_L)) ** (1 / 3)
        t_turn = physics.age_at(turn)
        now = to_screen(physics.age_at(1.0), 1.0)
        return VGroup(self.axes(frame, "time (billion years)", "size a"), curve, future,
                      Dot(now, radius=0.05, color=INK),
                      text("now", 10.5, INK).move_to(now + UP * 0.17 + LEFT * 0.1),
                      Dot(to_screen(t_turn, turn), radius=0.04, color=vis.SU4_COLOR),
                      text(f"speeds up from {t_turn:.1f} Gyr", 10, vis.SU4_COLOR)
                      .move_to(to_screen(t_turn, turn) + RIGHT * 0.25 + DOWN * 0.22))

    def finale(self, overlay: VGroup) -> None:
        hud = self.hud
        rows = []
        for name, (color, _) in CATEGORIES.items():
            label, meaning = SHORT[name]
            row = VGroup(Dot(radius=0.07, color=color), text(label, 14, color, "BOLD"))
            if meaning:
                row.add(text(meaning, 12.5, INK))
            rows.append(row.arrange(RIGHT, buff=0.12))
        legend = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        center, width, height = hud.inset_box(INSET_HEIGHT)
        fit(legend, width, height).move_to(center)
        self.beat(*self.show_inset(legend, "how sure we are: the colour key"),
                  title="From One to everything",
                  sub="One seed, one string, one hidden shape, three families, and the universe "
                      "you live in.",
                  formulas=["Genesis → string", "the vacuum: moduli, Λ",
                            "physical masses (metrics)", "matter over antimatter",
                            "what dark matter is", "what dark energy is"],
                  heading="still open",
                  badges=[("ONETHEORY", "this film: every shape drawn from the repository's "
                                        "formulas"),
                          ("PROVEN", "where a theorem stands behind a shape, it says so")],
                  run_time=3.0)
        self.wait(6.0)
        everything = Group(self.window, overlay, hud.formulas, hud.inset, hud.badges,
                           hud.clock, hud.subtitle)
        self.play(FadeOut(everything), run_time=3.5)
        self.wait(1.0)
        self.play(FadeOut(hud.title), run_time=2.0)
        self.wait(0.5)
