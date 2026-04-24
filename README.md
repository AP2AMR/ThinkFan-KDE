# ThinkPad Fan Control — KDE Tray Widget

A lightweight KDE system tray widget for monitoring CPU temperatures and manually controlling fan speed on ThinkPad laptops via the `/proc/acpi/ibm/fan` ACPI interface.

![Python](https://img.shields.io/badge/python-3.x-blue) ![PyQt5](https://img.shields.io/badge/PyQt5-Qt5-green) ![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)

---

## Features

- Live CPU core temperatures and fan RPM in the tray tooltip
- Fan level control: levels 0–7, Auto, and Full-speed
- Frameless popup on left-click, stays resident on close
- Minimal footprint — no daemon, no config file

## Requirements

- Linux with a ThinkPad exposing `/proc/acpi/ibm/fan` (most models do)
- `lm-sensors` (`sudo apt install lm-sensors`, then run `sudo sensors-detect`)
- `python3-pyqt5`

```bash
sudo apt install python3-pyqt5 lm-sensors
```

## Privilege Setup

The widget writes to `/proc/acpi/ibm/fan` via `sudo tee`. Add a targeted sudoers rule so it can do so without a password prompt:

```bash
sudo visudo -f /etc/sudoers.d/thinkfan-tray
```

Add this line (replace `yourusername`):

```
yourusername ALL=(root) NOPASSWD: /usr/bin/tee /proc/acpi/ibm/fan
```

Verify `tee` is at `/usr/bin/tee` on your system (`which tee`). Only this one command is granted elevated access — the rest of the app runs as your normal user.

## Usage

```bash
python3 fan-kde.py
```

- **Left-click** tray icon — toggle the control popup
- **Hover** tray icon — see current temps and fan RPM
- **Right-click** tray icon — Quit

## Autostart on Login (KDE)

Create `~/.config/autostart/thinkfan-tray.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=ThinkFan Tray
Exec=python3 /path/to/fan-kde.py
Icon=temperature-symbolic
X-KDE-AutostartEnabled=true
```

Or add it via **System Settings → Autostart → Add Script**.
## Notes

- Fan level `auto` returns control to the BIOS/EC firmware
- Fan level `full-speed` is loud — useful for sustained load or thermal emergencies
- Tested on a ThinkPad with the `thinkpad_acpi` kernel module loaded
