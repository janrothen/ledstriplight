#!/usr/bin/env python3

from flask import Flask, Response, send_from_directory, request, jsonify

from config.config_manager import ConfigManager
from led.gpio_service import GPIOService
from led.led_strip_light_controller import LEDStripLightController
from led.effect_runner import EffectRunner
from led.color import Color

app = Flask(__name__, static_folder='static', static_url_path='')
config_manager = ConfigManager()
pin_assignment = config_manager.get_pin_assignment()
gpio_service = GPIOService(
            red_pin=pin_assignment.red,
            green_pin=pin_assignment.green,
            blue_pin=pin_assignment.blue
        )
led_controller = LEDStripLightController(gpio_service=gpio_service)
effect_runner = EffectRunner(led_controller)
current_effect = {"name": None}

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/on", methods=["POST"])
def turn_on():
    led_controller.switch_on()
    return Response(status=200)

@app.route("/off", methods=["POST"])
def turn_off():
    # Stop any running effect first to avoid it resuming after power off
    _stop_active_effect()
    led_controller.switch_off()
    return Response(status=200)

@app.route("/status", methods=["GET"])
def get_status():
    is_on = "1" if led_controller.is_on() else "0"
    return Response(is_on, status=200)

@app.route("/color", methods=["GET"])
def get_color():
    hex_color = led_controller.get_color().to_hex_with_hash()
    return Response(hex_color, status=200)

@app.route("/color/<value>", methods=["POST"])
def set_color(value):
    color = Color.from_hex(value)
    led_controller.set_color(color)
    return Response(status=200)

@app.route("/brightness", methods=["GET"])
def get_brightness():
    brightness = led_controller.get_brightness_percentage()
    return Response(str(brightness), status=200)

@app.route("/brightness/<int:value>", methods=["POST"])
def set_brightness(value):
    led_controller.set_brightness(value)
    return Response(status=200)

# --- Effect management -----------------------------------------------------

def _parse_color(value: str):
    return Color.from_hex(value.lstrip('#'))

def _stop_active_effect():
    """Interrupt any running effect thread and clear active effect state.
    Safe to call when no effect is running.
    """
    try:
        led_controller.stop_current_sequence()
    except Exception:
        pass
    current_effect["name"] = None

@app.route("/effects", methods=["GET"])
def list_effects():
    return jsonify({
        "active": current_effect["name"],
        "available": [
            "breathing", "campfire", "candle", "random", "cycle", "fade"
        ]
    })

@app.route("/effects/stop", methods=["POST"])
def stop_effect():
    _stop_active_effect()
    return jsonify({"status": "stopped"})

@app.route("/effects/<effect_name>", methods=["POST"])
def start_effect(effect_name: str):
    data = request.get_json(silent=True) or {}
    try:
        # Dispatch
        if effect_name == "breathing":
            color_hex = data.get("color", "FF0000")
            duration = int(data.get("duration", 2000))
            effect_runner.run_breathing_effect(color=_parse_color(color_hex), duration=duration)
        elif effect_name == "campfire":
            # Accept optional overrides
            kwargs = {k: data[k] for k in [
                "duration", "update_hz", "min_brightness", "max_brightness", "hue_jitter",
                "saturation", "spark_chance", "spark_gain", "tau_ms", "gamma"
            ] if k in data}
            if "duration" in kwargs:
                kwargs["duration"] = int(kwargs["duration"])
            effect_runner.run_campfire_effect(**kwargs)
        elif effect_name == "candle":
            kwargs = {k: data[k] for k in [
                "duration", "update_hz", "min_brightness", "max_brightness", "hue_jitter",
                "saturation", "spark_chance", "spark_gain", "tau_ms", "gamma"
            ] if k in data}
            if "duration" in kwargs:
                kwargs["duration"] = int(kwargs["duration"])
            effect_runner.run_candle_effect(**kwargs)
        elif effect_name == "random":
            interval = int(data.get("interval", 2000))
            effect_runner.run_random_effect(interval=interval)
        elif effect_name == "cycle":
            duration = int(data.get("duration", 2000))
            colors_raw = data.get("colors")
            colors = None
            if colors_raw:
                if not isinstance(colors_raw, list):
                    raise ValueError("colors must be a list of hex strings")
                colors = [_parse_color(c) for c in colors_raw]
            effect_runner.run_cycle_effect(colors=colors, duration=duration)
        elif effect_name == "fade":
            from_hex = data.get("from", "000000")
            to_hex = data.get("to", "FFFFFF")
            duration = int(data.get("duration", 5000))
            effect_runner.run_fade_effect(from_color=_parse_color(from_hex), to_color=_parse_color(to_hex), duration=duration)
        else:
            return jsonify({"error": f"unknown effect '{effect_name}'"}), 404

        current_effect["name"] = effect_name
        return jsonify({"status": "started", "effect": effect_name, "params": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)