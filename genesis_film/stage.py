"""Layout system for the Genesis film: zones that never overlap, smooth HUD.

Owns:
    The fixed screen zones (title band, centre stage, formula panel, inset
    panel, cosmic clock, confidence badges), the evidence-category colours, and
    animations that change every HUD element by cross-fading, never cutting.

Depends on:
    Manim Community (Text via Pango, no LaTeX required).

Must not:
    Place anything outside its zone, or change a HUD element without an
    animation.

Phase 0:
    Presentation layer only.
"""

from __future__ import annotations

import math

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    AnimationGroup,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Mobject,
    RoundedRectangle,
    Scene,
    Text,
    Triangle,
    ValueTracker,
    VGroup,
    smooth,
)

FONT = "DejaVu Sans"
BG = "#04050b"
INK = "#e6e9f2"
MUTED = "#8a93a8"

# Evidence categories: colour, full meaning (legend) and short meaning (badge).
CATEGORIES = {
    "PROVEN": ("#4ade80", "mathematics: a theorem"),
    "MEASURED": ("#38bdf8", "experiment / observation"),
    "ESTABLISHED": ("#818cf8", "tested standard theory"),
    "ONETHEORY": ("#c084fc", "computed exactly in OneTheory"),
    "SELECTED": ("#fb923c", "chosen realization, conditional"),
    "HYPOTHESIS": ("#facc15", "proposed, untested"),
    "POSSIBLE": ("#fb7185", "one possible reality: a gap filled to stay continuous"),
}
SHORT = {
    "PROVEN": ("PROVEN", "theorem"),
    "MEASURED": ("MEASURED", "observed"),
    "ESTABLISHED": ("ESTABLISHED", "tested theory"),
    "ONETHEORY": ("ONETHEORY", "computed here"),
    "SELECTED": ("SELECTED", "chosen, conditional"),
    "HYPOTHESIS": ("HYPOTHESIS", "untested"),
    "POSSIBLE": ("ONE POSSIBLE REALITY", ""),
}

# Zones (Manim frame is 14.22 x 8).
TITLE_Y, SUBTITLE_Y = 3.55, 3.08
CENTER = np.array([0.0, -0.05, 0.0])
CENTER_W, CENTER_H = 8.2, 5.4
LEFT_X0, LEFT_X1, LEFT_TOP = -7.0, -4.35, 2.55
RIGHT_X0, RIGHT_X1, RIGHT_TOP = 4.35, 7.0, 2.6
BADGE_TOP = -0.5
CLOCK_Y, CLOCK_X0, CLOCK_X1 = -3.5, -6.75, 3.95
LOGT_MIN, LOGT_MAX = -46.0, 17.64


_TEXT_CACHE: dict[tuple, Text] = {}


def text(content: str, size: float = 20, color: str = INK, weight: str = "NORMAL") -> Text:
    """Pango text, laid out once per distinct (content, size, colour, weight) and copied."""

    key = (content, size, color, weight)
    if key not in _TEXT_CACHE:
        _TEXT_CACHE[key] = Text(content, font=FONT, font_size=size, color=color, weight=weight)
    return _TEXT_CACHE[key].copy()


def live_text(content, size: float, color: str, place, opacity=None) -> Text:
    """Text that follows `place()` every frame but is re-laid out only when
    `content()` changes (laying out or copying text costs tens of milliseconds)."""

    label = content()
    mob = text(label, size, color)
    mob.label = label

    def update(m: Text) -> None:
        new = content()
        if new != m.label:
            m.become(text(new, size, color))
            m.label = new
        m.move_to(place())
        if opacity is not None:
            m.set_opacity(opacity())

    mob.add_updater(update)
    update(mob)
    return mob


def fit(mob: Mobject, width: float, height: float) -> Mobject:
    if mob.width > width:
        mob.scale_to_fit_width(width)
    if mob.height > height:
        mob.scale_to_fit_height(height)
    return mob


def clock_x(logt: float) -> float:
    s = (min(max(logt, LOGT_MIN), LOGT_MAX) - LOGT_MIN) / (LOGT_MAX - LOGT_MIN)
    return CLOCK_X0 + s * (CLOCK_X1 - CLOCK_X0)


def time_label(logt: float) -> str:
    if logt <= -45.5:
        return "t → 0"
    seconds = 10**logt
    if seconds < 1:
        exponent = math.floor(logt)
        return f"t ≈ 10{_superscript(exponent)} s"
    if seconds < 60:
        return f"t ≈ {seconds:.0f} s"
    if seconds < 3600 * 24 * 365.25:
        if seconds < 7200:
            return f"t ≈ {seconds / 60:.0f} min"
        return f"t ≈ {seconds / 86400:.0f} days"
    years = seconds / (3600 * 24 * 365.25)
    if years < 1e6:
        return f"t ≈ {years:,.0f} years"
    if years < 1e9:
        return f"t ≈ {years / 1e6:.0f} million years"
    return f"t ≈ {years / 1e9:.1f} billion years"


def _superscript(value: int) -> str:
    table = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(value).translate(table)


def wrap(content: str, size: float, width: float, color: str = INK) -> VGroup:
    """Greedy word wrap measured with the real font."""

    words, lines, current = content.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if current and text(trial, size, color).width > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return VGroup(*[text(line, size, color) for line in lines]).arrange(
        DOWN, aligned_edge=LEFT, buff=0.05)


def badge(category: str, source: str) -> VGroup:
    color = CATEGORIES[category][0]
    label, meaning = SHORT[category]
    width = RIGHT_X1 - RIGHT_X0
    head = VGroup(Dot(radius=0.055, color=color), text(label, 14, color, "BOLD"))
    if meaning:
        head.add(text(meaning, 11, MUTED))
    head.arrange(RIGHT, buff=0.1)
    fit(head, width - 0.3, 0.3)
    body = wrap(source, 12.5, width - 0.32)
    content = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    frame = RoundedRectangle(corner_radius=0.08, width=width, height=content.height + 0.2,
                             stroke_color=color, stroke_width=1.6,
                             fill_color=color, fill_opacity=0.07)
    content.move_to(frame).align_to(frame, LEFT).shift(RIGHT * 0.14)
    return VGroup(frame, content)


class Stage:
    """Owns every HUD element of a scene and changes them only by animation."""

    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.title = VGroup()
        self.subtitle = VGroup()
        self.formulas = VGroup()
        self.inset = VGroup()
        self.badges = VGroup()
        self.logt = ValueTracker(LOGT_MIN)
        self.clock = self._build_clock()

    # -- clock -------------------------------------------------------------
    def _build_clock(self) -> VGroup:
        axis = Line([CLOCK_X0, CLOCK_Y, 0], [CLOCK_X1, CLOCK_Y, 0],
                    stroke_color=MUTED, stroke_width=1.5)
        ticks = VGroup()
        epochs = ((-43.3, "Planck"), (-36, "GUT"), (-32, "inflation"), (-11, "EW"),
                  (-4.6, "QCD"), (2.3, "nuclei"), (13.07, "CMB"), (17.64, "now"))
        for logt, name in epochs:
            x = clock_x(logt)
            ticks.add(Line([x, CLOCK_Y - 0.06, 0], [x, CLOCK_Y + 0.06, 0],
                           stroke_color=MUTED, stroke_width=1.2))
            ticks.add(text(name, 9.5, MUTED).move_to([x, CLOCK_Y - 0.2, 0]))
        caption = text("cosmic clock · logarithmic time", 9, MUTED)
        caption.move_to([CLOCK_X0 + caption.width / 2, CLOCK_Y - 0.4, 0])
        fill = Line([CLOCK_X0, CLOCK_Y, 0], [CLOCK_X0 + 1e-3, CLOCK_Y, 0],
                    stroke_color="#fde68a", stroke_width=3)
        fill.add_updater(lambda m: m.put_start_and_end_on(
            np.array([CLOCK_X0, CLOCK_Y, 0]),
            np.array([max(clock_x(self.logt.get_value()), CLOCK_X0 + 1e-3), CLOCK_Y, 0])))
        marker = Triangle(color="#fde68a", fill_opacity=1, stroke_width=0).scale(0.06)
        marker.rotate(math.pi)
        marker.add_updater(lambda m: m.move_to([clock_x(self.logt.get_value()), CLOCK_Y + 0.12, 0]))
        readout = text(time_label(LOGT_MIN), 12, "#fde68a")
        readout.label = time_label(LOGT_MIN)

        def update_readout(m: Text) -> None:
            label = time_label(self.logt.get_value())
            if label != m.label:
                fresh = text(label, 12, "#fde68a")
                m.become(fresh)
                m.label = label
            m.move_to([min(max(clock_x(self.logt.get_value()), CLOCK_X0 + m.width / 2),
                           CLOCK_X1 - m.width / 2), CLOCK_Y + 0.34, 0])

        readout.add_updater(update_readout)
        return VGroup(axis, ticks, caption, fill, marker, readout)

    def show_clock(self) -> None:
        self.scene.add(self.clock)

    def advance_clock(self, logt: float, run_time: float = 3.0):
        return self.logt.animate(run_time=run_time).set_value(logt)

    # -- title -------------------------------------------------------------
    def set_title(self, title: str, subtitle: str = "", run_time: float = 1.4) -> list:
        new_title = fit(text(title, 34, INK, "BOLD"), 12.5, 0.6).move_to([0, TITLE_Y, 0])
        new_sub = fit(text(subtitle, 17, MUTED), 12.5, 0.4).move_to([0, SUBTITLE_Y, 0])
        anims = self._swap("title", new_title, run_time) + self._swap("subtitle", new_sub, run_time)
        return anims

    def set_subtitle(self, subtitle: str, run_time: float = 1.2) -> list:
        new_sub = fit(text(subtitle, 17, MUTED), 12.5, 0.4).move_to([0, SUBTITLE_Y, 0])
        return self._swap("subtitle", new_sub, run_time)

    # -- formulas (left panel) --------------------------------------------
    def set_formulas(self, lines: list[str], heading: str = "the formulas",
                     run_time: float = 1.2) -> list:
        group = VGroup()
        if lines:
            head = text(heading.upper(), 11, MUTED, "BOLD")
            body = VGroup(*[text(line, 17) for line in lines]).arrange(
                DOWN, aligned_edge=LEFT, buff=0.22)
            group = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            fit(group, LEFT_X1 - LEFT_X0, 5.0)
            group.move_to([0, 0, 0]).align_to([LEFT_X0, 0, 0], LEFT)
            group.align_to([0, LEFT_TOP, 0], UP)
        return self._swap("formulas", group, run_time)

    # -- inset (right panel) ----------------------------------------------
    def inset_frame(self, height: float = 3.0) -> RoundedRectangle:
        width = RIGHT_X1 - RIGHT_X0
        frame = RoundedRectangle(corner_radius=0.1, width=width, height=height,
                                 stroke_color=MUTED, stroke_width=1.2,
                                 fill_color="#0b1020", fill_opacity=0.85)
        frame.move_to([(RIGHT_X0 + RIGHT_X1) / 2, RIGHT_TOP - height / 2, 0])
        return frame

    def inset_box(self, height: float = 3.0) -> tuple[np.ndarray, float, float]:
        """Centre, width and height available for content inside an inset of this height."""

        frame = self.inset_frame(height)
        return frame.get_center() + DOWN * 0.15, frame.width - 0.35, height - 0.65

    def _inset_swap(self, content: Mobject | None, caption: str, height: float,
                    run_time: float, fade_content: bool) -> list:
        """Replace the inset's caption and content; an equal frame stays put."""

        old = self.inset
        keep = len(old.submobjects) >= 2 and content is not None and \
            abs(old.submobjects[0].height - height) < 1e-6
        anims = []
        if keep:
            frame = old.submobjects[0]
            leaving = VGroup(*old.submobjects[1:])
            if len(leaving.submobjects):
                anims.append(FadeOut(leaving, run_time=run_time, rate_func=_first_half))
        else:
            frame = self.inset_frame(height)
            if len(old.submobjects):
                anims.append(FadeOut(old, run_time=run_time, rate_func=_first_half))
            if content is not None:
                anims.append(FadeIn(frame, run_time=run_time, rate_func=_second_half))
        if content is None:
            self.inset = VGroup()
        else:
            cap = fit(text(caption, 11.5, MUTED), frame.width - 0.3, 0.5)
            cap.next_to(frame.get_top(), DOWN, buff=0.12)
            anims.append(FadeIn(cap, run_time=run_time, rate_func=_second_half))
            if fade_content:
                anims.append(FadeIn(content, run_time=run_time, rate_func=_second_half))
            self.inset = VGroup(frame, cap, content)
        # Grouped, so a play-level rate_func cannot override the staggered fades.
        return [_hud(AnimationGroup(*anims, run_time=run_time))] if anims else []

    def adopt_inset(self, content: Mobject, caption: str, height: float = 3.0,
                    run_time: float = 1.2) -> list:
        """New caption around content the caller moves in (or fades in) itself."""

        return self._inset_swap(content, caption, height, run_time, fade_content=False)

    def release_inset(self) -> Mobject | None:
        """Hand the inset content back to the caller; frame and caption stay."""

        if len(self.inset.submobjects) < 3:
            return None
        frame, cap, content = self.inset.submobjects[:3]
        self.inset = VGroup(frame, cap)
        return content

    def fade_released(self, run_time: float = 1.2) -> list:
        return []

    def set_inset(self, content: Mobject | None, caption: str = "", height: float = 3.0,
                  run_time: float = 1.2) -> list:
        if content is not None:
            frame = self.inset_frame(height)
            cap = fit(text(caption, 11.5, MUTED), frame.width - 0.3, 0.5)
            fit(content, frame.width - 0.35, height - cap.height - 0.45)
            content.move_to(frame.get_center() + DOWN * (cap.height + 0.1) / 2)
        return self._inset_swap(content, caption, height, run_time, fade_content=True)

    # -- badges (bottom right) --------------------------------------------
    def set_badges(self, items: list[tuple[str, str]], run_time: float = 1.2) -> list:
        group = VGroup(*[badge(cat, src) for cat, src in items]).arrange(DOWN, buff=0.09)
        if items:
            if group.height > BADGE_TOP + 3.95:
                group.scale_to_fit_height(BADGE_TOP + 3.95)
            # Badges sit at the bottom of their column, close to the clock line.
            group.move_to([(RIGHT_X0 + RIGHT_X1) / 2, 0, 0]).align_to([0, -3.95, 0], DOWN)
        return self._swap("badges", group, run_time)

    # -- generic cross-fade -------------------------------------------------
    def _swap(self, name: str, new: VGroup, run_time: float) -> list:
        old = getattr(self, name)
        setattr(self, name, new)
        anims = []
        if len(old.submobjects):
            anims.append(FadeOut(old, run_time=run_time, rate_func=_first_half))
        if len(new.submobjects):
            anims.append(FadeIn(new, run_time=run_time, rate_func=_second_half))
        return [_hud(AnimationGroup(*anims, run_time=run_time))] if anims else []


def _hud(animation: AnimationGroup) -> AnimationGroup:
    """Mark a HUD change so scene beats keep its own pace instead of stretching it."""

    animation.hud = True
    return animation


def _first_half(t: float) -> float:
    """Old text leaves during the first 55% of a swap, so texts never overlap."""

    return smooth(min(1.0, t / 0.55))


def _second_half(t: float) -> float:
    return smooth(max(0.0, (t - 0.45) / 0.55))


def glow_dot(point: np.ndarray, color: str = WHITE, radius: float = 0.08,
             layers: int = 6) -> VGroup:
    """A soft glowing point made of concentric translucent circles."""

    group = VGroup()
    for i in range(layers, 0, -1):
        r = radius * (1 + 1.6 * i)
        group.add(Circle(radius=r, stroke_width=0, fill_color=color,
                         fill_opacity=0.05 + 0.02 * (layers - i)).move_to(point))
    group.add(Dot(point, radius=radius, color=color))
    return group
