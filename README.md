
# LED Strip Light

Feature-rich Raspberry Pi project for controlling an RGB LED strip light. Includes:

- Web-based REST API (Flask) for remote control (on/off, color, brightness, effects)
- Web-based interface for manual remote control
- Homebridge integration for Apple HomeKit and Siri voice control
- Command-line interface for scripting and manual control
- Multiple built-in LED effects (breathing, fade, color cycle, random, and more)
- Time-based color profiles and scheduled automation (systemd, cron)
- Modular, testable Python codebase with hardware abstraction and full unit test suite

Easily automate, script, or integrate your LED strip with smart home platforms and custom workflows.

## Prerequisites

- LED strip light connected to a Raspberry Pi Zero W
- Python 3
- Python packages listed in [requirements.txt](src/requirements.txt)
- pigpio daemon (for GPIO control)

The guide [How to control a RGB LED Strip Light with a Raspberry Pi Zero W](https://janrothen.github.io/ledstriplight/pi-zero-w-rgb-led-strip-control.html) shows how to physically connect a 12 V RGB strip to a Raspberry Pi Zero W.

## Installing

Configure the scripts: [config.conf](src/config.conf)

This project uses the [pigpio](https://abyz.me.uk/rpi/pigpio/download.html) library for PWM control of the GPIO pins. To install it on your Raspberry Pi:
```bash
sudo apt-get install pigpio
```
then start the service
```bash
sudo systemctl start pigpiod
```

## Development Setup

### Virtual Environment
Create and activate a virtual environment for development in the src directory:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

### Running the Application
The application supports multiple effects via command-line arguments:

```bash
# Basic profile effect (morning/evening colors based on time of the day)
./run.py profile

# Breathing effect with custom color and duration
./run.py breathing --color red --duration 3000

# Use hex colors
./run.py breathing --color "#FF6347"

# Color cycling through multiple colors
./run.py cycle --colors red,green,blue,yellow --duration 500

# Fade between two colors
./run.py fade --from black --to white --duration 5000

# Random color changes
./run.py random --interval 2000

# Get help
./run.py --help
```

### Running Tests
The project includes comprehensive unit tests with hardware mocking:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_color.py

# Run tests with detailed coverage report (generates HTML)
pytest --cov=led --cov=config --cov=cli --cov=utils --cov-report=html
```

### Project Structure
```
ledstriplight/
├── etc/
│   ├── systemd.d/               # Systemd service files and installation guide
│   ├── cron.d/                  # Cron job files for scheduled automation
│   └── homebridge/              # Homebridge integration
└── src/                         # Application source code
    ├── run.py                   # Main application entry point
    ├── http_server.py           # Flask REST API server
    ├── led/                     # Core LED control modules
    │   ├── effects.py           # LED effects (breathing, fade, etc.)
    │   ├── effect_runner.py     # Effect runner
    │   ├── gpio_service.py      # Hardware GPIO interface
    │   ├── led_strip_light_controller.py # Main LED controller
    │   └── profile_manager.py   # Time-based color profiles
    ├── cli/
    │   └── cli_handler.py       # Command-line interface handler
    ├── config/
        └── config_manager.py    # Configuration manager 
    ├── utils/                   # Utilities (logging, shutdown handling)
    └── tests/                   # Unit tests with mocked hardware
```

## REST API (Flask Server)

The project includes a Flask server for remote control via HTTP endpoints and a web-based control interface.

### Web Interface

A responsive web interface is available for controlling the LED strip through your browser:

- **Access:** Navigate to `http://localhost:5000` (or `http://YOUR_PI_IP:5000` from other devices)
- **Features:**
  - Power control (On/Off) with visual status indicators
  - Color picker and preset color buttons (Red, Green, Blue, White, Yellow, Magenta, Cyan)
  - Brightness slider with real-time adjustment
  - Live status updates and error handling
  - Mobile-friendly responsive design

### API Endpoints

**Endpoints:**

- `POST /on` — Turn the light on (white)
- `POST /off` — Turn the light off (black)
- `GET /status` — Get on/off state and current color (hex)
- `GET /color` — Get current color (hex)
- `POST /color/<value>` — Set color (hex string or named color)
- `GET /brightness` — Get current brightness (0–100)
- `POST /brightness/<int:value>` — Set brightness (0–100)

**Starting the server:**
```bash
cd src
./http_server.py
```

Example usage:
```bash
curl -X POST http://localhost:5000/on
curl -X POST http://localhost:5000/color/ff0000
curl -X POST http://localhost:5000/brightness/80
curl http://localhost:5000/status
```

## Homebridge Integration

You can integrate the LED strip with Homebridge for Apple HomeKit support. All installation and configuration instructions, including example Homebridge accessory configuration, can be found in the `etc/homebridge/` directory of this repository.

See [`README.md`](etc/homebridge/README.md) for details on how to set up Homebridge integration and connect it to the Flask server endpoints.
