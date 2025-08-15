#!/usr/bin/env python3

from flask import Flask, Response, send_from_directory, request, jsonify

from config.config_manager import ConfigManager
from led.gpio_service import GPIOService
from led.led_strip_light_controller import LEDStripLightController
from led.effect_runner import EffectRunner
from led.profile_manager import ProfileManager
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
profile_manager = ProfileManager(config_manager)
effect_runner = EffectRunner(led_controller, profile_manager)
active_effect = {"name": None}

# --- Static controller file serving ------------------------------------------
@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

# --- Basic LED control endpoints ---------------------------------------------
@app.route("/on", methods=["POST"])
def turn_on():
    if not _is_led_active():
        led_controller.switch_on()
    return Response(status=200)

@app.route("/off", methods=["POST"])
def turn_off():
    _stop_active_effect()
    led_controller.switch_off()
    return Response(status=200)

@app.route("/status", methods=["GET"])
def get_status():
    return Response("1" if _is_led_active() else "0", status=200)

@app.route("/color", methods=["GET"])
def get_color():
    hex_color = led_controller.get_color().to_hex_with_hash()
    return Response(hex_color, status=200)

@app.route("/color/<value>", methods=["POST"])
def set_color(value):
    _stop_active_effect()
    color = Color.from_hex(value)
    led_controller.set_color(color)
    return Response(status=200)

@app.route("/brightness", methods=["GET"])
def get_brightness():
    brightness = led_controller.get_brightness_percentage()
    return Response(str(brightness), status=200)

@app.route("/brightness/<int:value>", methods=["POST"])
def set_brightness(value):
    _stop_active_effect()
    led_controller.set_brightness(value)
    return Response(status=200)

def _parse_color(value: str):
    return Color.from_hex(value.lstrip('#'))

# --- Effect management -----------------------------------------------------
@app.route("/effects", methods=["GET"])
def list_effects():
    return jsonify({
        "active": active_effect["name"],
        "available": [
            "breathing",
            "campfire",
            "candle",
            "random",
            "cycle",
            "fade",
            "profile"
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
        elif effect_name == "profile":
            duration = int(data.get("duration", 10000))
            effect_runner.run_profile_effect(duration=duration)
        else:
            return jsonify({"error": f"unknown effect '{effect_name}'"}), 404

        active_effect["name"] = effect_name
        return jsonify({"status": "started", "effect": effect_name, "params": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def _stop_active_effect():
    """Interrupt any running effect thread and clear active effect state."""
    if not led_controller.is_sequence_running():
        return

    try:
        led_controller.stop_current_sequence()
        active_effect["name"] = None
    except Exception:
        pass

def _is_led_active():
    return led_controller.is_on() or led_controller.is_sequence_running()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)