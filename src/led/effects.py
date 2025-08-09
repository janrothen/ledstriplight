#!/usr/bin/env python3

import logging
from time import sleep, monotonic
from typing import Protocol, Iterable, Optional, Callable
from .color import Color

FADE_STEP_MS: float = 10.0  # 10 ms per step ≈ 100 Hz
DEFAULT_EFFECT_DURATION_MS: int = 2000  # Default duration in milliseconds

# ── Easing functions ───────────────────────────────────────────────────────
def ease_linear(t: float) -> float:
    return t

def ease_in_out_sine(t: float) -> float:
    # Smooth start and end (default)
    from math import cos, pi
    return 0.5 * (1 - cos(pi * t))

def ease_in_quad(t: float) -> float:
    return t * t

def ease_out_quad(t: float) -> float:
    return t * (2 - t)

# ── Gamma-aware channel interpolation ─────────────────────────────────────
def _interp_channel(v0: int, v1: int, t: float, gamma: Optional[float]) -> int:
    """Interpolate one 8-bit channel from v0→v1 at progress t in [0,1].
    If gamma is provided, interpolate in linear light and convert back.
    """
    if gamma and gamma > 0:
        a = (v0 / 255.0) ** gamma
        b = (v1 / 255.0) ** gamma
        lin = a + (b - a) * t
        enc = lin ** (1.0 / gamma)
        return int(round(enc * 255.0))
    # Linear (no gamma)
    return int(round(v0 + (v1 - v0) * t))


class StripLike(Protocol):
    """Minimal interface needed by the effects in this module."""
    def set_color(self, color: Color) -> None: ...
    def is_interrupted(self) -> bool: ...


def breathing_effect(strip: StripLike, color: Color = Color.RED, duration: int = DEFAULT_EFFECT_DURATION_MS) -> None:
    """Creates a breathing effect by fading in and out."""
    while not strip.is_interrupted():
        # Fade in
        fade_effect(strip, Color.BLACK, color, duration)
        if strip.is_interrupted():
            break

        # Fade out
        fade_effect(strip, color, Color.BLACK, duration)
        if strip.is_interrupted():
            break


def random_color_effect(strip: StripLike, interval: int = DEFAULT_EFFECT_DURATION_MS) -> None:
    """Changes colors randomly at specified intervals."""
    while not strip.is_interrupted():
        strip.set_color(Color.random_pastel())
        sleep(interval / 1000.0)  # Convert ms to seconds


def color_cycle_effect(
    strip: StripLike,
    colors: Optional[Iterable[Color]] = None,
    duration: int = DEFAULT_EFFECT_DURATION_MS,
) -> None:
    """Cycles through a list of colors with smooth transitions between them."""
    palette = list(colors) if colors is not None else [Color.RED, Color.GREEN, Color.BLUE]
    if not palette:
        return

    # Start with the first color
    strip.set_color(palette[0])

    while not strip.is_interrupted():
        for i in range(len(palette)):
            if strip.is_interrupted():
                break

            # Get current and next color (wrap around to first color)
            current_color = palette[i]
            next_color = palette[(i + 1) % len(palette)]

            # Fade from current to next color
            fade_effect(strip, current_color, next_color, duration)

            if strip.is_interrupted():
                break

            sleep(0.5)  # Hold color for 0.5 seconds


def fade_effect(
    strip: StripLike,
    color_start: Color = Color.BLACK,
    color_end: Color = Color.WHITE,
    duration: int = DEFAULT_EFFECT_DURATION_MS,
    *,
    ease: Callable[[float], float] = ease_in_out_sine,
    gamma: Optional[float] = None,
) -> None:
    """Fade from color_start to color_end over duration (ms).
    Options:
      - ease: easing function mapping t∈[0,1]→[0,1] (e.g. ease_in_out_sine)
      - gamma: if set (e.g. 2.2), interpolate in linear light for smoother fades
    """
    r_start, g_start, b_start = color_start.rgb
    r_end, g_end, b_end = color_end.rgb

    # Guard against too-small duration to avoid division by zero
    steps = max(1, int(float(duration) / FADE_STEP_MS))

    logging.debug(
        "Fading from R=%3d G=%3d B=%3d to R=%3d G=%3d B=%3d in %d steps",
        r_start, g_start, b_start, r_end, g_end, b_end, steps,
    )

    start_time = monotonic()
    for step in range(steps):
        if strip.is_interrupted():
            logging.debug("Fading interrupted at step %d/%d", step + 1, steps)
            return

        # Normalized progress (1..steps) → (0,1], then apply easing
        t = ease((step + 1) / steps)

        r_current = _interp_channel(r_start, r_end, t, gamma)
        g_current = _interp_channel(g_start, g_end, t, gamma)
        b_current = _interp_channel(b_start, b_end, t, gamma)

        strip.set_color(Color.from_tuple((r_current, g_current, b_current)))

        # Align sleep to the original start to reduce drift over long fades
        next_due = start_time + ((step + 1) * FADE_STEP_MS / 1000.0)
        sleep(max(0.0, next_due - monotonic()))

    strip.set_color(color_end)
    logging.debug("Fade completed to %s", color_end)