#!/usr/bin/env python3

import argparse
from led.color import Color


class CLIHandler:
    """Handles command-line argument parsing and validation."""
    
    @staticmethod
    def parse_color(color_str):
        """Parse color string to Color object."""
        color_str = color_str.lower()
        color_map = {
            'black': Color.BLACK,
            'white': Color.WHITE,
            'red': Color.RED,
            'green': Color.GREEN,
            'blue': Color.BLUE,
            'yellow': Color.YELLOW,
            'cyan': Color.CYAN,
            'magenta': Color.MAGENTA,
            'orange': Color.ORANGE,
            'purple': Color.PURPLE,
            'pink': Color.PINK,
            'warm_white': Color.WARM_WHITE,
            'cool_white': Color.COOL_WHITE,
        }
        
        if color_str in color_map:
            return color_map[color_str]
        elif color_str.startswith('#'):
            return Color.from_hex(color_str)
        elif len(color_str) == 6 and all(c in '0123456789abcdef' for c in color_str):
            # Handle hex color without # prefix
            return Color.from_hex(color_str)
        else:
            raise ValueError(f"Unknown color: {color_str}")
    
    @staticmethod
    def parse_colors(colors_str):
        """Parse comma-separated color string to list of Color objects."""
        return [CLIHandler.parse_color(c.strip()) for c in colors_str.split(',')]
    
    @staticmethod
    def create_parser():
        """Create command line argument parser."""
        parser = argparse.ArgumentParser(
            description='LED Strip Light Controller',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s profile
  %(prog)s breathing --color red --duration 3000
  %(prog)s random --interval 2000
  %(prog)s cycle --colors red,green,blue --duration 2000
  %(prog)s fade --from black --to white --duration 5000
            """
        )
        
        subparsers = parser.add_subparsers(dest='effect', help='Effect to run')
        subparsers.required = True
        
        # Profile effect
        profile_parser = subparsers.add_parser('profile', help='Fade to active profile color')
        profile_parser.add_argument('--duration', type=int, default=10000, 
                                   help='Fade duration in milliseconds (default: 10000)')
        
        # Breathing effect
        breathing_parser = subparsers.add_parser('breathing', help='Breathing effect')
        breathing_parser.add_argument('--color', default='red', 
                                     help='Color for breathing effect (default: red)')
        breathing_parser.add_argument('--duration', type=int, default=2000,
                                     help='Breathing cycle duration in milliseconds (default: 2000)')
        
        # Random effect
        random_parser = subparsers.add_parser('random', help='Random color changes')
        random_parser.add_argument('--interval', type=int, default=2000,
                                  help='Interval between color changes in milliseconds (default: 2000)')
        
        # Cycle effect
        cycle_parser = subparsers.add_parser('cycle', help='Cycle through colors')
        cycle_parser.add_argument('--colors', default='red,green,blue',
                                 help='Comma-separated list of colors (default: red,green,blue)')
        cycle_parser.add_argument('--duration', type=int, default=2000,
                                 help='Duration for each color in milliseconds (default: 2000)')
        
        # Fade effect
        fade_parser = subparsers.add_parser('fade', help='Fade between two colors')
        fade_parser.add_argument('--from', dest='from_color', default='black',
                                help='Starting color (default: black)')
        fade_parser.add_argument('--to', dest='to_color', default='white',
                                help='Ending color (default: white)')
        fade_parser.add_argument('--duration', type=int, default=5000,
                                help='Fade duration in milliseconds (default: 5000)')
        
        return parser
    
    @staticmethod
    def execute_effect(effect_runner, args):
        """Execute the specified effect with parsed arguments."""
        if args.effect == 'profile':
            effect_runner.run_profile_effect(duration=args.duration)
        
        elif args.effect == 'breathing':
            color = CLIHandler.parse_color(args.color)
            effect_runner.run_breathing_effect(color=color, duration=args.duration)
        
        elif args.effect == 'random':
            effect_runner.run_random_effect(interval=args.interval)
        
        elif args.effect == 'cycle':
            colors = CLIHandler.parse_colors(args.colors)
            effect_runner.run_cycle_effect(colors=colors, duration=args.duration)
        
        elif args.effect == 'fade':
            from_color = CLIHandler.parse_color(args.from_color)
            to_color = CLIHandler.parse_color(args.to_color)
            effect_runner.run_fade_effect(from_color=from_color, to_color=to_color, duration=args.duration)
        
        else:
            raise ValueError(f"Unknown effect: {args.effect}")