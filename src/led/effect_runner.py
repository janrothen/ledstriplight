#!/usr/bin/env python3

import logging
from typing import Any, List, Optional
from .color import Color
from .effects import breathing_effect, fade_effect, random_color_effect, color_cycle_effect


class EffectRunner:
    """
    Manages and executes LED strip light effects.

    Provides a clean interface for running different effects on an LED strip light
    with various parameters and configurations.
    """
    
    def __init__(self, strip_controller: Any, profile_manager: Optional[Any] = None) -> None:
        self.strip = strip_controller
        self.profile_manager = profile_manager
    
    def run_profile_effect(self, duration: int = 10000) -> None:
        """Run profile-based effect."""
        if not self.profile_manager:
            raise ValueError("ProfileManager required for profile effect")
        
        color = self.profile_manager.get_active_profile_color()
        logging.info(f"Using active profile color: {color}")
        self.strip.run_sequence(fade_effect, self.strip, Color.BLACK, color, duration)
    
    def run_breathing_effect(self, color: Color = Color.RED, duration: int = 2000) -> None:
        """Run breathing effect."""
        logging.info(f"Starting breathing effect with color: {color}")
        self.strip.run_sequence(breathing_effect, self.strip, color, duration)
    
    def run_random_effect(self, interval: int = 2000) -> None:
        """Run random color effect."""
        logging.info(f"Starting random color effect with interval: {interval}ms")
        self.strip.run_sequence(random_color_effect, self.strip, interval)
    
    def run_cycle_effect(self, colors: Optional[List[Color]] = None, duration: int = 2000) -> None:
        """Run color cycle effect."""
        if colors is None:
            colors = [Color.RED, Color.GREEN, Color.BLUE]
        
        logging.info(f"Starting color cycle with colors: {[str(c) for c in colors]}")
        self.strip.run_sequence(color_cycle_effect, self.strip, colors, duration)
    
    def run_fade_effect(self, from_color: Color = Color.BLACK, to_color: Color = Color.WHITE, duration: int = 5000) -> None:
        """Run fade effect."""
        logging.info(f"Fading from {from_color} to {to_color}")
        self.strip.run_sequence(fade_effect, self.strip, from_color, to_color, duration)