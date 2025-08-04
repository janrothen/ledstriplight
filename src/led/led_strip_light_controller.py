#!/usr/bin/env python3

import logging
from threading import Thread
from typing import Any, Callable

from .color import Color
from .gpio_service import GPIOService


class LEDStripLightController(object):
    def __init__(self, gpio_service: GPIOService) -> None:
        self._gpio_service = gpio_service
        self._interrupt = False
        self._sequence = None

    def switch_on(self) -> None:
        self.set_color(Color.WARM_YELLOW)

    def switch_off(self) -> None:
        self.interrupt()
        self.set_color(Color.BLACK)
        self.resume()

    def interrupt(self) -> None:
        self._interrupt = True

    def resume(self) -> None:
        self._interrupt = False

    def is_on(self) -> bool:
        return not self.get_color().is_black()

    def is_interrupted(self) -> bool:
        """Check if the current sequence should be interrupted."""
        return self._interrupt

    def get_color(self) -> Color:
        return self._gpio_service.get_color()

    def set_color(self, color: Color = Color.WARM_YELLOW) -> None:
        self._gpio_service.set_color(color)
    
    def get_brightness_percentage(self) -> int:
        """Get brightness percentage (0–100%) based on the maximum RGB channel value."""
        current_color = self.get_color()
        if current_color.is_black():
            return 0
        # Use max channel value to determine brightness, matching set_brightness behavior
        max_value = current_color.max_channel()
        return round((max_value / 255) * 100)

    def set_brightness(self, brightness: int) -> None:
        """
        Set brightness (0–100%) while keeping the same color hue.
        Scales current RGB values proportionally.
        """
        if not (0 <= brightness <= 100):
            raise ValueError("Brightness must be between 0 and 100")

        current_color = self.get_color()
        r_current = current_color.red
        g_current = current_color.green
        b_current = current_color.blue

        r_new = g_new = b_new = 0
        if current_color.is_black():
            r_new = g_new = b_new = int(255 * (brightness / 100))
        else:
            current_max = current_color.max_channel()
            scale = (brightness / 100) * (255 / current_max)
            r_new = int(r_current * scale)
            g_new = int(g_current * scale)
            b_new = int(b_current * scale)
        new_color = Color(r_new, g_new, b_new)
        self.set_color(new_color)

    #region Sequence control
    def run_sequence(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.stop_current_sequence()
        self.start_sequence(func, *args, **kwargs)

    def start_sequence(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        logging.info(f"Starting sequence: {func.__name__}")
        self._sequence = Thread(target=func, args=args, kwargs=kwargs)
        self.resume()
        self._sequence.start()

    def stop_current_sequence(self, timeout: int = 60) -> None:
        if self._sequence is None:
            logging.info("No sequence to stop.")
            return
        
        logging.info(f"Stopping sequence: {self._sequence.name}")
        self.interrupt()
        try:
            self._sequence._sequence_stop_signal = True
            self._sequence.join(timeout)
        except AttributeError:
            pass

        self._reset_sequence()
    #endregion

    def _reset_sequence(self) -> None:
        self._sequence = None