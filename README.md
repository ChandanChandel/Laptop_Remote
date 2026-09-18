# Laptop Remote

Control your laptop's media playback, volume, and brightness from your phone's browser — no app store needed. Works on **Windows, macOS, and Linux**.

## How it works
- `server.py` runs a small web server on your laptop.
- Your phone opens a webpage served by that server (over your home WiFi).
- Tapping a button sends a request to the laptop, which simulates the real media key or adjusts brightness directly.

## Setup (all platforms)

1. **Install Python 3.9+** if you don't have it: https://www.python.org/downloads/
   - On Windows, check "Add Python to PATH" during install.

2. **Open a terminal** in this folder (`laptop-remote`) and install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```
   python server.py
   ```
   It will print the detected OS and start on port 5000.

4. **Find your laptop's local IP address:**
   - Windows: open Command Prompt, run `ipconfig`, look for "IPv4 Address"
   - macOS: System Settings → Network → WiFi → Details (or run `ipconfig getifaddr en0` in Terminal)
   - Linux: run `hostname -I` or `ip addr`

5. **On your phone** (connected to the **same WiFi network**), open a browser and go to:
   ```
   http://<your-laptop-ip>:5000
   ```

6. Tap the buttons to control play/pause, volume, and brightness!

## Platform-specific notes

### Windows
- The first time you run `server.py`, Windows Firewall may prompt you to allow network access — click **Allow**.
- If you missed the prompt: Windows Defender Firewall → "Allow an app through firewall" → enable Python for Private networks.
- Media keys and brightness work out of the box.

### macOS
- **Accessibility permission required**: the first time the server tries to simulate a key press, macOS will ask you to grant Accessibility access to Python (or Terminal, if running from there). Go to **System Settings → Privacy & Security → Accessibility** and enable it, then restart the server.
- **Brightness**: built-in laptop screens usually work directly. If brightness control fails, install the community CLI tool:
  ```
  brew install brightness
  ```
  The server will automatically fall back to using it.
- External monitors on macOS often don't support software brightness control at all (Apple restricts this depending on the connection type).

### Linux
- Media key simulation works well on **X11** desktops (GNOME, KDE, XFCE, etc. on X11) since these keys are already bound to system actions.
- On **Wayland**, key simulation may not work depending on your compositor — this is a known limitation of most simulated-input tools. If it doesn't work, try switching your session to X11 at the login screen (most distros offer this as an option).
- Brightness control depends on your hardware/drivers. `screen-brightness-control` uses `xrandr` or `/sys/class/backlight`. If it fails:
  - Try installing `xrandr` (`sudo apt install x11-xserver-utils` on Debian/Ubuntu), or
  - Install `light` (`sudo apt install light`) as an alternative backend, or
  - You may need to run the server with permission to write to `/sys/class/backlight/*/brightness` (some distros require being in the `video` group).

## General troubleshooting
- **"Could not reach laptop"** on the phone page: double check both devices are on the same WiFi network (not one on WiFi and one on mobile data), and that the IP address hasn't changed.
- **Buttons do nothing**: check the terminal running `server.py` for error messages — brightness/media key issues are usually OS permission or missing-tool issues covered above.
- **Add to home screen**: open the page in your phone's browser, then use "Add to Home Screen" (Safari/Chrome) so it launches like a normal app icon.

## Ideas to extend this
- Add a mouse trackpad (move cursor, click) using `pyautogui`
- Add app shortcuts (open Netflix, mute Zoom, etc.)
- Add a PIN/password check if you're on a shared network
- Make the server auto-start when your laptop boots
