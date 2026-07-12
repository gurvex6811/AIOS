"""
AIOS System Tray Application
=============================
The persistent background daemon for the AIOS shell layer.

Responsibilities:
  - Lives in the system tray
  - Registers Super+Space global hotkey → opens Nexus Bar
  - Shows emotion state as tray icon color
  - Provides quick-access context menu
  - Launches and manages GUI sub-processes
"""

import sys
import subprocess
import threading
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter

try:
    from pynput import keyboard as pynput_kb
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

GUI_DIR = Path(__file__).parent.parent


def _color_icon(hex_color: str, size: int = 22) -> QIcon:
    """Generate a solid-circle tray icon from a hex color."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(hex_color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(2, 2, size - 4, size - 4)
    p.end()
    return QIcon(px)


class AITrayApp(QWidget):
    def __init__(self):
        super().__init__()
        self._nexus_bar_proc = None
        self._emotion_color = "#00d4ff"
        self._setup_tray()
        self._setup_hotkey()
        self._start_emotion_polling()

    # ── Tray setup ────────────────────────────────────────────

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(_color_icon(self._emotion_color))
        self._tray.setToolTip("AIOS Nexus — Active")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: rgba(13,17,23,0.95);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 10px;
                color: rgba(255,255,255,0.85);
                font-size: 13px;
                padding: 4px;
            }
            QMenu::item:selected {
                background: rgba(0,212,255,0.12);
                border-radius: 6px;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255,255,255,0.06);
                margin: 4px 8px;
            }
        """)

        action_open = menu.addAction("⦿  Open Nexus Bar")
        action_open.triggered.connect(self._open_nexus_bar)

        action_status = menu.addAction("📊  System Status")
        action_status.triggered.connect(lambda: subprocess.Popen(["nexus", "status"]))

        action_dash = menu.addAction("🗺️  Memory Dashboard")
        action_dash.triggered.connect(
            lambda: subprocess.Popen(["xdg-open", "http://localhost:8080"])
        )

        menu.addSeparator()

        action_pause = menu.addAction("⏸️  Pause AIOS")
        action_pause.triggered.connect(lambda: subprocess.Popen(["nexus", "pause"]))

        action_privacy = menu.addAction("🔒  Privacy Status")
        action_privacy.triggered.connect(
            lambda: subprocess.Popen(["nexus", "privacy", "status"])
        )

        menu.addSeparator()

        action_quit = menu.addAction("✕  Quit AIOS Shell")
        action_quit.triggered.connect(QApplication.quit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    # ── Global hotkey ─────────────────────────────────────────

    def _setup_hotkey(self):
        if not PYNPUT_AVAILABLE:
            print("[Tray] pynput not installed — Super+Space hotkey disabled.")
            print("       Install with: pip install pynput")
            return

        _super_held = {"v": False}

        def _on_press(key):
            try:
                if key == pynput_kb.Key.cmd or key == pynput_kb.Key.cmd_l:
                    _super_held["v"] = True
            except AttributeError:
                pass

        def _on_release(key):
            try:
                if key == pynput_kb.Key.cmd or key == pynput_kb.Key.cmd_l:
                    _super_held["v"] = False
                if key == pynput_kb.Key.space and _super_held["v"]:
                    # Post to main Qt thread
                    QTimer.singleShot(0, self._open_nexus_bar)
            except AttributeError:
                pass

        listener = pynput_kb.Listener(
            on_press=_on_press,
            on_release=_on_release
        )
        listener.daemon = True
        listener.start()
        print("[Tray] Super+Space hotkey registered.")

    # ── Actions ───────────────────────────────────────────────

    def _open_nexus_bar(self):
        """
        Spawn the Nexus Bar process if not already open.
        Using subprocess so the bar has its own Qt loop.
        """
        if self._nexus_bar_proc and self._nexus_bar_proc.poll() is None:
            # Already running — send SIGUSR1 to toggle visibility
            import signal
            self._nexus_bar_proc.send_signal(signal.SIGUSR1)
        else:
            self._nexus_bar_proc = subprocess.Popen(
                [sys.executable, str(GUI_DIR / "command_bar" / "nexus_bar.py")]
            )

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._open_nexus_bar()

    # ── Emotion polling ────────────────────────────────────────

    def _start_emotion_polling(self):
        self._emo_timer = QTimer(self)
        self._emo_timer.setInterval(6000)  # every 6 seconds
        self._emo_timer.timeout.connect(self._poll_emotion)
        self._emo_timer.start()

    def _poll_emotion(self):
        import requests
        EMOTION_COLORS = {
            "focused":    "#00d4ff",
            "stressed":   "#ff6b6b",
            "energized":  "#00ff88",
            "tired":      "#8892a4",
            "happy":      "#ffd700",
            "frustrated": "#ff8c00",
            "neutral":    "#7c3aed",
        }
        try:
            r = requests.get("http://localhost:11435/api/status", timeout=2)
            if r.ok:
                state = r.json().get("emotion", {}).get("state", "neutral")
                color = EMOTION_COLORS.get(state, "#7c3aed")
                if color != self._emotion_color:
                    self._emotion_color = color
                    self._tray.setIcon(_color_icon(color))
                    emoji = r.json().get("emotion", {}).get("emoji", "😐")
                    self._tray.setToolTip(f"AIOS Nexus — {emoji} {state.title()}")
        except Exception:
            pass


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = AITrayApp()
    sys.exit(app.exec())
