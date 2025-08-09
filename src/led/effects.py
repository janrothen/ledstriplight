#!/usr/bin/env python3

import logging
from time import sleep, monotonic
from typing import Protocol, Iterable, Optional
from .color import Color

FADE_STEP_MS: float = 10.0  # 10 ms per step ≈ 100 Hz
DEFAULT_EFFECT_DURATION_MS: int = 2000  # Default duration in milliseconds


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
) -> None:
    """Fade smoothly from color_start to color_end over the given duration (ms)."""
    r_start, g_start, b_start = color_start.rgb
    r_end, g_end, b_end = color_end.rgb
    r_diff = r_end - r_start
    g_diff = g_end - g_start
    b_diff = b_end - b_start

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

        # Normalized progress (1..steps) → (0,1]
        t = (step + 1) / steps

        r_current = int(round(r_start + (r_diff * t)))
        g_current = int(round(g_start + (g_diff * t)))
        b_current = int(round(b_start + (b_diff * t)))

        strip.set_color(Color.from_tuple((r_current, g_current, b_current)))

        # Align sleep to the original start to reduce drift over long fades
        next_due = start_time + ((step + 1) * FADE_STEP_MS / 1000.0)
        sleep(max(0.0, next_due - monotonic()))

    strip.set_color(color_end)
    logging.debug("Fade completed to %s", color_end)