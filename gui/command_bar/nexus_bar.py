"""
AIOS Nexus Command Bar
======================
A floating, glass-morphic AI-first command overlay.
Activated by Super+Space (or configured hotkey).

Unlike macOS Spotlight (file-first) or Windows Search (app-first),
Nexus Bar is *memory-first* — it shows what you were working on,
what your AI remembers, and suggests actions from context.
"""

import sys
import threading
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QThread, QTimer
)
from PyQt6.QtGui import (
    QKeySequence, QShortcut, QFont, QColor, QPalette,
    QIcon, QPixmap, QPainter, QBrush, QPen
)

NEXUS_API = "http://localhost:11435"


class NexusQueryThread(QThread):
    """Background thread: sends query to Nexus, streams response."""
    result_ready = pyqtSignal(str)  # streamed text chunk
    done = pyqtSignal()
    suggestions_ready = pyqtSignal(list)

    def __init__(self, query: str, is_search: bool = False):
        super().__init__()
        self.query = query
        self.is_search = is_search

    def run(self):
        if self.is_search:
            self._do_memory_search()
        else:
            self._do_chat()

    def _do_memory_search(self):
        try:
            resp = requests.get(
                f"{NEXUS_API}/api/memories",
                params={"q": self.query, "limit": 6},
                timeout=3
            )
            if resp.ok:
                items = resp.json().get("res