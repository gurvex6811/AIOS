# AIOS GUI — Phase 9 Desktop Dashboard

This is the **AIOS Desktop Dashboard** — a pixel-faithful HTML/CSS/JS implementation of the AIOS GUI as defined in the Master Blueprint v3.0 and the design mockup.

## 🖥️ Features Implemented

| Panel | Description |
|---|---|
| **Top Bar** | Live clock, AIOS logo, system icons, AI Core Active badge |
| **Sidebar** | Navigation: Nexus, Memory, Agents, Projects, Conversations, Files, System, Settings |
| **Nexus Orb** | Animated AI voice orb with pulsing rings and waveform |
| **Active Context** | Developer Mode selector, Focus/Environment/Interruptions metadata, Productivity bar (92%) |
| **System Vitals** | Animated donut chart, CPU/RAM/GPU/Disk/Network bars with sparklines |
| **Central Hero** | Animated rotating rings with Λ logo, beam glow, greeting text |
| **Nexus Graph** | Live canvas animation — infinite memory & intelligence graph with nodes, edges, particles |
| **Active Agents** | Nexus Orchestrator, Async Life Agent, Memory Curator, Code Assistant with live status |
| **Live Insights** | Productivity & focus insights panel |
| **Upcoming** | Calendar events with color-coded dots |
| **Weather** | Current temperature and 4-day forecast |
| **Media Hub** | Lo-Fi Deep Focus player with animated waveform and controls |
| **Bottom Dock** | Global search bar + dock icons (Apps, Widgets, Holo Space, Terminal, Quick Access) |

## 🚀 How to Run

### Option 1: Open directly
```bash
cd gui/
open index.html   # macOS
xdg-open index.html  # Linux
```

### Option 2: Serve with Python
```bash
cd gui/
python3 -m http.server 8080
# Open http://localhost:8080
```

### Option 3: Node.js (if available)
```bash
npx serve gui/ -p 8080
```

## 🎨 Design Language

- **Color Palette:** Deep space dark `#07080f` base with purple (`#7c5fff`), blue (`#3b8bff`), and cyan (`#00d4ff`) accents
- **Typography:** Inter (UI text) + Orbitron (logo/headers)
- **Effects:** Glassmorphism panels, animated rings, canvas graph, glow pulses, waveform animations
- **Layout:** Fixed sidebar + 3-column responsive grid + fixed dock

## 📍 Phase Mapping (Blueprint)

This implements **Phase 9.3** from the AIOS Master Blueprint:
> *"Build a web-based dashboard served at localhost:8080 that provides a visual interface for browsing and managing AIOS memory."*

Later phases will connect this GUI to:
- `nexus/` — FastAPI backend (port 11435)
- `memory/` — SQLite + ChromaDB memory queries
- `agents/` — Real-time agent status via WebSocket
- `emotion/` — Live emotion state display

## 🛠️ Tech Stack

- Pure **HTML5 + CSS3 + Vanilla JS** — zero dependencies
- **Canvas API** for the Nexus Graph animation
- **CSS animations** for orb, rings, waveforms, particles
- **Google Fonts** (Inter + Orbitron) via CDN

---

*AIOS GUI — Phase 9 Implementation — Blueprint v3.0*
