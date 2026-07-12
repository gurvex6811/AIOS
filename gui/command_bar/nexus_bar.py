"""
AIOS Nexus Command Bar
======================
Floating, glass-morphic AI-first command overlay.
Activated by Super+Space (configurable hotkey).

Memory-first design:
  - Shows recent context before you type
  - Searches semantic memory as you type
  - Sends natural language to Nexus when you press Enter
  - Streams AI response inline — no separate window needed
"""

import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QLabel,
    QFrame, QScrollArea
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QThread, QTimer, QPoint
)
from PyQt6.QtGui import (
    QKeySequence, QShortcut, QFont, QColor,
    QPalette, QScreen
)

NEXUS_API = "http://localhost:11435"


class NexusQueryThread(QThread):
    chunk_received = pyqtSignal(str)
    suggestions_ready = pyqtSignal(list)
    done = pyqtSignal()

    def __init__(self, query: str, mode: str = "chat"):
        super().__init__()
        self.query = query
        self.mode = mode

    def run(self):
        if self.mode == "search":
            self._memory_search()
        else:
            self._chat_stream()

    def _memory_search(self):
        try:
            r = requests.get(
                f"{NEXUS_API}/api/memories",
                params={"q": self.query, "limit": 6},
                timeout=3
            )
            if r.ok:
                mems = r.json().get("results", [])
                suggestions = [
                    {
                        "icon": self._type_icon(m.get("type", "conversation")),
                        "title": m.get("summary", m.get("content", ""))[:72],
                        "meta": f"📅 {m.get('created_at', '')[:10]}  │  🎯 {m.get('importance', 0):.1f}",
                        "tag": m.get("type", "memory").upper(),
                        "raw": m
                    }
                    for m in mems
                ]
                self.suggestions_ready.emit(suggestions)
        except Exception:
            pass
        self.done.emit()

    def _chat_stream(self):
        try:
            with requests.post(
                f"{NEXUS_API}/api/chat",
                json={"message": self.query, "stream": True},
                stream=True, timeout=30
            ) as resp:
                for chunk in resp.iter_content(chunk_size=None):
                    if chunk:
                        self.chunk_received.emit(chunk.decode("utf-8", errors="replace"))
        except Exception as e:
            self.chunk_received.emit(f"\n[Nexus offline — start with: nexus start]")
        self.done.emit()

    @staticmethod
    def _type_icon(t: str) -> str:
        return {
            "conversation": "💬",
            "goal": "🎯",
            "project": "🛠️",
            "task": "✓",
            "fact": "ℹ️",
            "decision": "✶",
            "file": "📄",
        }.get(t, "💾")


class NexusBar(QWidget):
    """
    The AIOS Nexus Command Bar — Super+Space overlay.
    """
    closed = pyqtSignal()

    PLACEHOLDER_IDLE = "Ask anything, search memory, or run a command…"
    PLACEHOLDER_VOICE = "🎤  Listening…"

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self._query_thread = None
        self._response_text = ""
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(220)
        self._debounce_timer.timeout.connect(self._trigger_memory_search)
        self._setup_ui()
        self._setup_hotkey()
        self._center_on_screen()

    # ── UI Setup ─────────────────────────────────────────────

    def _setup_ui(self):
        self.setMinimumWidth(680)
        self.setMaximumWidth(720)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # — Container panel (glass)
        self._panel = QFrame(self)
        self._panel.setObjectName("nexusPanel")
        self._panel.setStyleSheet("""
            QFrame#nexusPanel {
                background: rgba(13,17,23,0.88);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 20px;
            }
        """)
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(0, 0, 0, 12)
        panel_layout.setSpacing(0)

        # — Input row
        input_row = QHBoxLayout()
        input_row.setContentsMargins(20, 16, 20, 14)
        input_row.setSpacing(12)

        self._icon_label = QLabel("⦿")  # AIOS orb icon
        self._icon_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 22px;
                min-width: 28px;
            }
        """)
        input_row.addWidget(self._icon_label)

        self._input = QLineEdit()
        self._input.setPlaceholderText(self.PLACEHOLDER_IDLE)
        self._input.setStyleSheet("""
            QLineEdit {
                background: none;
                border: none;
                color: rgba(255,255,255,0.92);
                font-size: 17px;
                font-family: 'Inter', 'SF Pro Display', system-ui;
                selection-background-color: rgba(0,212,255,0.25);
                caret-color: #00d4ff;
            }
        """)
        self._input.returnPressed.connect(self._on_submit)
        self._input.textChanged.connect(self._on_text_changed)
        input_row.addWidget(self._input)

        self._voice_btn = QLabel("🎤")
        self._voice_btn.setStyleSheet("color: rgba(255,255,255,0.3); font-size:16px; cursor:pointer;")
        self._voice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        input_row.addWidget(self._voice_btn)

        panel_layout.addLayout(input_row)

        # — Divider
        self._divider = QFrame()
        self._divider.setFrameShape(QFrame.Shape.HLine)
        self._divider.setStyleSheet("color: rgba(255,255,255,0.05);")
        panel_layout.addWidget(self._divider)

        # — Results / Response
        self._results_list = QListWidget()
        self._results_list.setStyleSheet("""
            QListWidget {
                background: none;
                border: none;
                outline: none;
                padding: 4px 8px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 10px;
                color: rgba(255,255,255,0.88);
                font-size: 13px;
            }
            QListWidget::item:hover, QListWidget::item:selected {
                background: rgba(255,255,255,0.05);
            }
        """)
        self._results_list.setMaximumHeight(360)
        self._results_list.setVisible(False)
        panel_layout.addWidget(self._results_list)

        # — AI response area
        self._response_label = QLabel()
        self._response_label.setWordWrap(True)
        self._response_label.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.82);
                font-size: 13px;
                font-family: 'Inter', system-ui;
                padding: 8px 20px 4px 20px;
                line-height: 1.6;
            }
        """)
        self._response_label.setVisible(False)
        panel_layout.addWidget(self._response_label)

        # — Footer hints
        footer = QHBoxLayout()
        footer.setContentsMargins(20, 6, 20, 0)
        hints = [("Enter", "Ask AI"), ("Tab", "Search memory"),
                 ("↑↓", "Navigate"), ("Esc", "Close")]
        for key, label in hints:
            key_lbl = QLabel(key)
            key_lbl.setStyleSheet("""
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.45);
                font-size: 10px;
                border-radius: 4px;
                padding: 1px 6px;
                font-family: 'JetBrains Mono', monospace;
            """)
            val_lbl = QLabel(label)
            val_lbl.setStyleSheet("color: rgba(255,255,255,0.25); font-size: 10px;")
            footer.addWidget(key_lbl)
            footer.addWidget(val_lbl)
            footer.addSpacing(8)
        footer.addStretch()
        panel_layout.addLayout(footer)

        root.addWidget(self._panel)
        self.setLayout(root)

    def _setup_hotkey(self):
        # Global hotkey: Super+Space
        # (handled by tray_app.py via pynput; this is a fallback)
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self.hide_bar)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.x() + (geo.width() - self.minimumWidth()) // 2,
                geo.y() + (geo.height() - 480) // 2
            )

    # ── Visibility ───────────────────────────────────────────

    def show_bar(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self._input.setFocus()
        self._input.selectAll()
        self._load_initial_suggestions()

    def hide_bar(self):
        self._input.clear()
        self._results_list.clear()
        self._results_list.setVisible(False)
        self._response_label.setVisible(False)
        self._response_label.setText("")
        self._response_text = ""
        self.hide()
        self.closed.emit()

    # ── Interaction ──────────────────────────────────────────

    def _on_text_changed(self, text: str):
        if len(text) >= 2:
            self._debounce_timer.start()  # debounce 220ms
        elif not text:
            self._load_initial_suggestions()

    def _trigger_memory_search(self):
        q = self._input.text().strip()
        if not q:
            return
        t = NexusQueryThread(q, mode="search")
        t.suggestions_ready.connect(self._show_suggestions)
        t.start()

    def _on_submit(self):
        q = self._input.text().strip()
        if not q:
            return
        # Clear suggestions, show loading state
        self._results_list.setVisible(False)
        self._response_label.setText("⦿  Thinking…")
        self._response_label.setVisible(True)
        self._response_text = ""
        # Start streaming
        self._query_thread = NexusQueryThread(q, mode="chat")
        self._query_thread.chunk_received.connect(self._on_chunk)
        self._query_thread.done.connect(self._on_done)
        self._query_thread.start()

    def _on_chunk(self, chunk: str):
        self._response_text += chunk
        self._response_label.setText(self._response_text)
        self.adjustSize()

    def _on_done(self):
        pass  # response complete

    def _load_initial_suggestions(self):
        """Show recent memories and quick actions when bar opens."""
        try:
            r = requests.get(f"{NEXUS_API}/api/memories",
                             params={"limit": 5, "sort": "recent"}, timeout=2)
            if r.ok:
                mems = r.json().get("results", [])
                self._show_suggestions([
                    {
                        "icon": "💬",
                        "title": m.get("summary", m.get("content", ""))[:72],
                        "meta": m.get("created_at", "")[:10],
                        "tag": "RECENT",
                    }
                    for m in mems
                ])
        except Exception:
            # Nexus not running — show static quick actions
            self._show_suggestions([
                {"icon": "🗨️", "title": "Start a conversation with AIOS",
                 "meta": "Type a message and press Enter", "tag": "AI"},
                {"icon": "🔍", "title": "Search your memory archive",
                 "meta": "Press Tab to switch to memory search mode", "tag": "MEMORY"},
                {"icon": "⚡", "title": "nexus start — Start Nexus daemon",
                 "meta": "Nexus API is not running", "tag": "CMD"},
            ])

    def _show_suggestions(self, items: list):
        self._results_list.clear()
        for it in items:
            lbl = QLabel()
            lbl.setText(
                f"<b style='font-size:13px'>{it['icon']}  {it['title']}</b>"
                f"<br><span style='color:rgba(255,255,255,0.38);font-size:11px'>"
                f"{it.get('meta','')}  "
                f"<span style='color:#00d4ff'>{it.get('tag','')}</span></span>"
            )
            lbl.setStyleSheet("background:none;color:rgba(255,255,255,0.88);padding:2px 4px;")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            item = QListWidgetItem(self._results_list)
            item.setSizeHint(lbl.sizeHint())
            item.setSizeHint(item.sizeHint().__class__(
                item.sizeHint().width(), 52
            ))
            self._results_list.addItem(item)
            self._results_list.setItemWidget(item, lbl)
        self._results_list.setVisible(bool(items))
        self.adjustSize()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_bar()
        elif event.key() == Qt.Key.Key_Tab:
            self._trigger_memory_search()
        else:
            super().keyPressEvent(event)


# ── Entry point (standalone test) ────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar = NexusBar()
    bar.show_bar()
    sys.exit(app.exec())
