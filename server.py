"""
Laptop Remote Server (cross-platform)
--------------------------------------
Runs on your laptop (Windows, macOS, or Linux). Exposes a small web page + API
that lets your phone control play/pause, volume, and brightness over your
local WiFi.

Run:
    pip install -r requirements.txt
    python server.py

Then open http://<your-laptop-ip>:5000 on your phone (same WiFi network).

Platform notes (see README.md for full details):
  - macOS: the first time you run this, macOS will ask you to grant
    "Accessibility" permission to Python/Terminal so it can simulate key presses.
  - Linux: media-key simulation works on X11 desktops out of the box; on
    Wayland it may not work depending on your compositor.
  - Brightness control on macOS/Linux can be more limited than Windows
    depending on your hardware/drivers — see README for fallbacks.
"""

import platform
import subprocess
from flask import Flask, render_template, jsonify
from pynput.keyboard import Controller, Key
import screen_brightness_control as sbc

app = Flask(__name__)
keyboard = Controller()

SYSTEM = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'


# ---------- Media / volume control (cross-platform via pynput) ----------

def tap(key):
    keyboard.press(key)
    keyboard.release(key)


def media_play_pause():
    tap(Key.media_play_pause)


def media_next():
    tap(Key.media_next)


def media_previous():
    tap(Key.media_previous)


def volume_up():
    tap(Key.media_volume_up)


def volume_down():
    tap(Key.media_volume_down)


def volume_mute():
    tap(Key.media_volume_mute)


# ---------- Brightness control (OS-aware) ----------

def get_brightness_value():
    return sbc.get_brightness(display=0)[0]


def change_brightness(delta):
    """Adjust brightness by delta (-100 to 100). Returns new value."""
    if SYSTEM == "Darwin":
        # screen-brightness-control support on macOS is limited to some
        # displays. Try it first, then fall back to the 'brightness' CLI
        # (installed via: brew install brightness).
        try:
            current = get_brightness_value()
            new_val = max(0, min(100, current + delta))
            sbc.set_brightness(new_val)
            return new_val
        except Exception:
            try:
                # 'brightness' CLI takes a 0.0-1.0 float and has no "get"
                # that's reliable across versions, so we estimate by nudging.
                direction = 0.1 if delta > 0 else -0.1
                subprocess.run(
                    ["brightness", str(direction)],
                    check=True, capture_output=True
                )
                return None  # unknown absolute value, but command succeeded
            except Exception as e:
                raise RuntimeError(
                    "Brightness control isn't available. On macOS, install "
                    "the 'brightness' CLI with: brew install brightness"
                ) from e
    else:
        # Windows and most Linux setups
        current = get_brightness_value()
        new_val = max(0, min(100, current + delta))
        sbc.set_brightness(new_val)
        return new_val


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/play-pause", methods=["POST"])
def route_play_pause():
    media_play_pause()
    return jsonify(status="ok")


@app.route("/next-track", methods=["POST"])
def route_next_track():
    media_next()
    return jsonify(status="ok")


@app.route("/prev-track", methods=["POST"])
def route_prev_track():
    media_previous()
    return jsonify(status="ok")


@app.route("/volume-up", methods=["POST"])
def route_volume_up():
    volume_up()
    return jsonify(status="ok")


@app.route("/volume-down", methods=["POST"])
def route_volume_down():
    volume_down()
    return jsonify(status="ok")


@app.route("/volume-mute", methods=["POST"])
def route_volume_mute():
    volume_mute()
    return jsonify(status="ok")


@app.route("/brightness-up", methods=["POST"])
def route_brightness_up():
    try:
        new_val = change_brightness(10)
        return jsonify(status="ok", brightness=new_val)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500


@app.route("/brightness-down", methods=["POST"])
def route_brightness_down():
    try:
        new_val = change_brightness(-10)
        return jsonify(status="ok", brightness=new_val)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500


if __name__ == "__main__":
    print(f"Detected OS: {SYSTEM}")
    # host="0.0.0.0" makes it reachable from other devices on your WiFi (like your phone)
    app.run(host="0.0.0.0", port=5000, debug=False)
