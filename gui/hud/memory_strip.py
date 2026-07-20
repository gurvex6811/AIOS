"""
AIOS Memory Strip — Top HUD
============================
A 32px-tall context bar at the top of the screen.
Shows:
  - Current persona badge (Developer / Student / Creative / Business)
  - Active project chip (clickable → opens project in Nexus Bar)
  - Recent memory chips (last 3 relevant context items)
  - Emotion aura indicator (coloured dot + label)
  - System quick stats (CPU / RAM) on hover

Design: NOT a traditional menubar or top panel.
It’s translucent, minimal, and disappears when fullscreen.
"""

import sys
import time
import threading
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import psutil

NEXUS_API = "http://localhost:11435"


class MemoryStrip(QWidget):
    state_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__(None,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._aura_color = "#00d4ff"
        self._emotion = "neutral"
        self._persona = "developer"
        self._setup_ui()
        self._setup_polling()
        self._stretch_to_top()

    # ── UI ─────────────────────────────────────────────────────

    def _setup_ui(self):
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(6)

        # AIOS orb
        orb = QLabel("⦿")
        orb.setStyleSheet("color: #00d4ff; font-size: 14px;")
        layout.addWidget(orb)

        # Persona badge
        self._persona_lbl = QLabel("DEVELOPER")
        self._persona_lbl.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00d4ff, stop:1 #0077cc);
                color: #000;
                border-radius: 10px;
                padding: 1px 10px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(self._persona_lbl)

        # Active project chip
        self._project_chip = self._make_chip("🛠️  AIOS / UI")
        layout.addWidget(self._project_chip)

        # Memory context chips (filled dynamically)
        self._mem_chips: list[QLabel] = []
        for _ in range(3):
            chip = self._make_chip("")
            chip.setVisible(False)
            layout.addWidget(chip)
            self._mem_chips.append(chip)

        layout.addStretch()

        # CPU + RAM
        self._sys_lbl = QLabel("CPU 0%  RAM 0%")
        self._sys_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.25); font-size: 11px;"
            "font-family: 'JetBrains Mono', monospace;"
        )
        layout.addWidget(self._sys_lbl)

        # Emotion aura dot
        self._aura_dot = QLabel()
        self._aura_dot.setFixedSize(8, 8)
        self._aura_dot.setStyleSheet(f"""
            QLabel {{
                background: {self._aura_color};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self._aura_dot)

        self._emotion_lbl = QLabel("🎯  Focused")
        self._emotion_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.32); font-size: 11px;"
        )
        layout.addWidget(self._emotion_lbl)

    def _make_chip(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 10px;
                color: rgba(255,255,255,0.45);
                font-size: 11px;
                padding: 1px 10px;
            }
            QLabel:hover {
                background: rgba(255,255,255,0.08);
                color: rgba(255,255,255,0.85);
            }
        """)
        lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        return lbl

    def _stretch_to_top(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.setFixedWidth(geo.width())
            self.move(geo.x(), geo.y())

    # ── Polling ────────────────────────────────────────────────

    def _setup_polling(self):
        # System stats every 4 seconds
        self._sys_timer = QTimer(self)
        self._sys_timer.setInterval(4000)
        self._sys_timer.timeout.connect(self._refresh_sys)
        self._sys_timer.start()
        # Nexus state every 8 seconds
        self._nexus_timer = QTimer(self)
        self._nexus_timer.setInterval(8000)
        self._nexus_timer.timeout.connect(self._refresh_nexus)
        self._nexus_timer.start()
        # Initial load
        self._refresh_sys()
        self._refresh_nexus()

    def _refresh_sys(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        color = "rgba(255,255,255,0.25)"
        if cpu > 80 or ram > 85:
            color = "#ff6b6b"
        elif cpu > 50 or ram > 65:
            color = "#ffd700"
        self._sys_lbl.setText(f"CPU {cpu:.0f}%  RAM {ram:.0f}%")
        self._sys_lbl.setStyleSheet(
            f"color: {color}; font-size: 11px;"
            "font-family: 'JetBrains Mono', monospace;"
        )

    def _refresh_nexus(self):
        try:
            r = requests.get(f"{NEXUS_API}/api/status", timeout=2)
            if not r.ok:
                return
            data = r.json()
            # Emotion
            emo = data.get("emotion", {})
            label = emo.get("state", "neutral")
            emoji = emo.get("emoji", "😐")
            self._emotion_lbl.setText(f"{emoji}  {label.title()}")
            # Persona
            persona = data.get("persona", "developer").upper()
            self._persona_lbl.setText(persona)
            # Memory chips
            mems = data.get("recent_memories", [])
            for i, chip in enumerate(self._mem_chips):
                if i < len(mems):
                    chip.setText("💾  " + mems[i].get("summary", "")[:28] + "…")
                    chip.setVisible(True)
                else:
                    chip.setVisible(False)
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    strip = MemoryStrip()
    strip.show()
    sys.exit(app.exec())
