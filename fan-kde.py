#!/usr/bin/env python3
"""
ThinkPad Fan Control — KDE system tray widget
Author: AbdulMoeed K. Raja
Website: https://www.abdulmoeed.com
License : GPL v3 or above
Requires: python3-pyqt5, lm-sensors
Privilege: add to sudoers via `sudo visudo -f /etc/sudoers.d/thinkfan-tray`:
    <yourusername> ALL=(root) NOPASSWD: /usr/bin/tee /proc/acpi/ibm/fan
"""

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QCursor


def get_info():
    """Parse `sensors` output. Returns (temps, fans) as lists of strings."""
    try:
        lines = subprocess.check_output(
            ["sensors"], stderr=subprocess.DEVNULL
        ).decode().splitlines()
    except subprocess.CalledProcessError:
        return ["sensors unavailable"], ["—"]

    temps, fans = [], []
    core = 0
    for line in lines:
        if "Core" in line:
            temp = line.split(":")[-1].split("(")[0].strip()
            temps.append(f"Core {core}: {temp}")
            core += 1
        if line.lower().startswith("fan"):
            name, val = line.split(":", 1)
            fans.append(f"{name.strip()}: {val.strip()}")

    return temps or ["No temp data"], fans or ["No fan data"]


def set_speed(level):
    """Write fan level to ACPI interface via sudoers-permitted tee."""
    result = subprocess.run(
        f"echo level {level} | sudo tee /proc/acpi/ibm/fan",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[fan error] {result.stderr.strip()}")


class FanPopup(QWidget):
    def __init__(self):
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowTitle("ThinkFan Control")
        self.setFixedWidth(320)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(3)

        self.temp_label = QLabel("Loading…")
        self.fan_label  = QLabel("")
        root.addWidget(self.temp_label)
        root.addWidget(self.fan_label)

        # Numeric level buttons 0–7
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Level:"))
        for i in range(8):
            btn = QPushButton(str(i))
            btn.setFixedWidth(30)
            btn.clicked.connect(lambda _, x=i: set_speed(x))
            row1.addWidget(btn)
        root.addLayout(row1)

        # Auto / Full-speed
        row2 = QHBoxLayout()
        auto_btn = QPushButton("Auto")
        full_btn = QPushButton("Full")
        auto_btn.clicked.connect(lambda: set_speed("auto"))
        full_btn.clicked.connect(lambda: set_speed("full-speed"))
        row2.addWidget(auto_btn)
        row2.addWidget(full_btn)
        root.addLayout(row2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)
        self.update_info()

    def update_info(self):
        temps, fans = get_info()
        self.temp_label.setText("\n".join(temps))
        self.fan_label.setText("\n".join(fans))


class ThinkFanTray:
    def __init__(self):
        self.app = QApplication.instance()

        icon = QIcon.fromTheme("temperature-symbolic",
               QIcon.fromTheme("configure"))
        self.tray = QSystemTrayIcon(icon)
        self.tray.show()

        self.popup = FanPopup()

        menu = QMenu()
        quit_act = menu.addAction("Quit")
        quit_act.triggered.connect(self.app.quit)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self.on_click)

        self.tooltip_timer = QTimer()
        self.tooltip_timer.timeout.connect(self.update_tooltip)
        self.tooltip_timer.start(2000)
        self.update_tooltip()

    def update_tooltip(self):
        temps, fans = get_info()
        self.tray.setToolTip(
            "ThinkPad Fan Control\n\n"
            + "\n".join(temps)
            + "\n\n"
            + "\n".join(fans)
        )

    def on_click(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.popup.isVisible():
                self.popup.hide()
                return

            # QSystemTrayIcon.geometry() returns (0,0,0,0) on Linux — use
            # cursor position instead, which is always on the icon at click time.
            cursor    = QCursor.pos()
            popup_w   = self.popup.width()
            popup_h   = self.popup.sizeHint().height()
            screen    = QApplication.primaryScreen().availableGeometry()

            # Centre horizontally on cursor, push above it
            x = cursor.x() - popup_w // 2
            y = cursor.y() - popup_h

            # Flip below cursor if not enough room above (top panel)
            if y < screen.top():
                y = cursor.y()

            # Clamp horizontally to screen edges
            x = max(screen.left(), min(x, screen.right() - popup_w))

            self.popup.move(x, y)
            self.popup.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = ThinkFanTray()
    sys.exit(app.exec_())
