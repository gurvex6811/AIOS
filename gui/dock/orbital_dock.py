"""
AIOS Orbital Dock
=================
A magnification dock inspired by macOS but redesigned:
  - No straight bottom bar — it’s a floating pill
  - Emotion-aura glow on the active item
  - Running-app indicators (dots) beneath icons
  - Context labels show last memory related to the app
  - Persona badges on grouped app sections
"""

import sys
import json
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, QPoint,
    QEasingCurve
)
from PyQt6.QtGui import QFont, QEnterEvent
import psutil

CONFIG_PATH = Path(__file__).parent / "dock_config.yaml"


def _load_config() -> dict:
    try:
        import yaml
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except Exception:
        return {"items": [
            {"icon": "🔍", "label": "Nexus",   "cmd": "nexus start"},
            {"icon": "💻", "label": "Terminal", "cmd": "x-terminal-emulator"},
            {"icon": "🌐", "label": "Browser", "cmd": "xdg-open https://"},
            {"icon": "📁", "label": "Files",   "cmd": "nautilus"},
            {"icon": "⚙️", "label": "Settings","cmd": "gnome-control-center"},
        ]}


class DockItem(QWidget):
    BASE_SIZE = 48
    HOVER_SIZE = 60

    def __init__(self, config: dict, aura_color: str = "#00d4ff", parent=None):
        super().__init__(parent)
        self._cfg = config
        self._aura_color = aura_color
        self._is_running = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        self._icon_lbl = QLabel(self._cfg.get("icon", "💾"))
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl.setFixedSize(self.BASE_SIZE, self.BASE_SIZE)
        self._icon_lbl.setStyleSheet(f"""
            QLabel {{
                background: rgba(28,35,51,0.9);
                border-radius: 12px;
                font-size: 22px;
                border: 1px solid rgba(255,255,255,0.06);
            }}
            QLabel:hover {{
                background: rgba(40,50,70,0.95);
                border-color: {self._aura_color};
            }}
        """)
        layout.addWidget(self._icon_lbl)

        self._dot = QLabel()
        self._dot.setFixedSize(5, 5)
        self._dot.setStyleSheet(f"""
            QLabel {{
                background: {self._aura_color};
                border-radius: 2px;
                opacity: 0;
            }}
        """)
        self._dot.setVisible(False)
        layout.addWidget(self._dot, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Tooltip label
        self._tooltip = QLabel(self._cfg.get("label", ""))
        self._tooltip.setStyleSheet("""
            QLabel {
                background: rgba(22,27,34,0.95);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                color: rgba(255,255,255,0.85);
                font-size: 11px;
                padding: 2px 8px;
            }
        """)
        self._tooltip.setVisible(False)

    def enterEvent(self, event):
        self._icon_lbl.setFixedSize(self.HOVER_SIZE, self.HOVER_SIZE)
        self._icon_lbl.setStyleSheet(f"""
            QLabel {{
                background: rgba(40,50,70,0.95);
                border-radius: 14px;
                font-size: 26px;
                border: 1px solid {self._aura_color};
                box-shadow: 0 0 20px {self._aura_color}40;
            }}
        """)
        self._tooltip.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._icon_lbl.setFixedSize(self.BASE_SIZE, self.BASE_SIZE)
        self._icon_lbl.setStyleSheet(f"""
            QLabel {{
                background: rgba(28,35,51,0.9);
                border-radius: 12px;
                font-size: 22px;
                border: 1px solid rgba(255,255,255,0.06);
            }}
        """)
        self._tooltip.setVisible(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._launch()
        super().mousePressEvent(event)

    def _launch(self):
        cmd = self._cfg.get("cmd", "")
        if cmd:
            subprocess.Popen(cmd.split(), start_new_session=True)

    def set_running(self, running: bool):
        self._is_running = running
        self._dot.setVisible(running)

    def update_aura(self, color: str):
        self._aura_color = color
        self._icon_lbl.setStyleSheet(f"""
            QLabel {{
                background: rgba(28,35,51,0.9);
                border-radius: 12px;
                font-size: 22px;
                border: 1px solid rgba(255,255,255,0.06);
            }}
        """)


class OrbitalDock(QWidget):
    """
    Floating pill dock that sits at the bottom-center of screen.
    Hides when cursor is away; shows on approach (auto-hide).
    """

    def __init__(self):
        super().__init__(None,
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._config = _load_config()
        self._aura_color = "#00d4ff"
        self._items: list[DockItem] = []
        self._setup_ui()
        self._position_dock()
        # Poll running apps every 3s
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(3000)
        self._poll_timer.timeout.connect(self._refresh_running)
        self._poll_timer.start()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._dock_frame = QFrame()
        self._dock_frame.setStyleSheet("""
            QFrame {
                background: rgba(13,17,23,0.82);
                backdrop-filter: blur(24px);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 22px;
            }
        """)

        row = QHBoxLayout(self._dock_frame)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(4)

        items = self._config.get("items", [])
        for i, cfg in enumerate(items):
            if cfg.get("separator"):
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.VLine)
                sep.setFixedWidth(1)
                sep.setStyleSheet("background: rgba(255,255,255,0.06); margin: 8px 4px;")
                row.addWidget(sep)
            else:
                item = DockItem(cfg, aura_color=self._aura_color)
                row.addWidget(item)
                self._items.append(item)

        outer.addWidget(self._dock_frame)
        self.setLayout(outer)
        self.adjustSize()

    def _position_dock(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.x() + (geo.width() - self.sizeHint().width()) // 2,
                geo.y() + geo.height() - self.sizeHint().height() - 16
            )

    def _refresh_running(self):
        running_names = {p.name().lower() for p in psutil.process_iter(["name"])}
        for item in self._items:
            proc = item._cfg.get("process_name", "").lower()
            item.set_running(bool(proc and proc in running_names))

    def update_aura(self, color: str):
        self._aura_color = color
        for item in self._items:
            item.update_aura(color)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dock = OrbitalDock()
    dock.show()
    sys.exit(app.exec())
