# AIOS GUI — Neuro-Adaptive Shell

> *"The interface should feel like an extension of your mind, not a tool you operate."*

The AIOS UI is fundamentally different from every other OS interface:

| Feature | Windows 11 | macOS | GNOME/KDE | **AIOS Shell** |
|---|---|---|---|---|
| Dock/Taskbar | Bottom bar | Bottom dock | Top/Bottom bar | **Orbital Arc Dock** |
| App launcher | Start Menu | Spotlight | App Grid | **Nexus AI Command Bar** |
| Notifications | Toast popups | Notification Center | Banners | **Context Strips (memory-aware)** |
| Color theme | Static | Static/Dynamic | Static | **Emotion Aura (EIE-driven)** |
| Desktop background | Wallpaper | Wallpaper | Wallpaper | **Live Memory Canvas** |
| Window management | Snap/tiling | Spaces | Workspaces | **Persona Workspaces** |

## Architecture

```
gui/
├── shell/
│   ├── aios_shell.py          # Main shell compositor (PyQt6)
│   ├── emotion_aura.py        # EIE-driven color/theme engine
│   ├── memory_canvas.py       # Live desktop memory background
│   └── persona_switcher.py    # Animated persona transition
├── command_bar/
│   ├── nexus_bar.py           # Super+Space AI command overlay
│   ├── suggestion_engine.py   # Real-time AI suggestions
│   └── voice_indicator.py     # Live waveform when voice active
├── dock/
│   ├── orbital_dock.py        # Circular arc app dock
│   ├── dock_item.py           # Animated dock items
│   └── dock_config.yaml       # Dock layout + app bindings
├── hud/
│   ├── memory_strip.py        # Context strip (top of screen)
│   ├── system_aura.py         # System stats ambient display
│   └── notification_nexus.py  # Memory-aware notifications
├── tray/
│   └── tray_app.py            # System tray daemon
├── dashboard/
│   ├── index.html             # Memory dashboard
│   ├── style.css              # AIOS design tokens
│   └── app.js                 # Dashboard logic
└── themes/
    ├── neuro_dark.css         # Default dark theme
    └── emotion_tokens.json    # Emotion → color mappings
```

## Installation

```bash
pip install PyQt6 PyQt6-WebEngine psutil requests
sudo apt install wmctrl xdotool libappindicator3-1

# Run the shell overlay (does NOT replace your WM)
python gui/shell/aios_shell.py &

# Run the system tray
python gui/tray/tray_app.py &

# Open memory dashboard
xdg-open http://localhost:8080
```

## Design Philosophy

1. **Zero Clutter by Default** — Nothing is visible unless needed. Clean canvas.
2. **Context-First, Not App-First** — You see what you're *doing*, not a list of apps.
3. **Emotion-Responsive** — Stressed? UI softens, dims, focuses. Energized? It opens up.
4. **Memory Everywhere** — Every interface element can recall your past context.
5. **Voice-Native** — Every action has a voice equivalent. No UI is voice-exclusive either.
