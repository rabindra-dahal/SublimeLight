# SublimeLight — Lightweight Desktop Python IDE 🧠🚀

**SublimeLight** is a high-performance, single-pane desktop text editor and code execution environment built natively from the ground up using **Python** and **CustomTkinter**. Designed as a lightweight alternative to resource-heavy IDEs, it combines an ultra-clean visual profile with highly responsive engineering workflows, structural macro snippet expansions, and intelligent data-driven script execution layers.

The application features a fully decoupled, object-oriented modular architecture to eliminate geometry calculation collisions, ensure rapid startup performance, and deliver a seamless development experience.

---

## 🎨 Core Architectural Highlights

- **Desktop Window Centering Control:** Leverages system viewport dimensions to compute exact monitor coordinates on initialization, launching the application perfectly centered on any display grid automatically.
- **Persistent Session Cache Engine:** Utilizes a localized, background JSON state encoder (`.sublimelight_session.json`) to silently preserve your active directory paths cross-sessions, automatically rebuilding your workspace tree layout on boot.
- **Unified Grid Geometry Protection:** Built with zero-flicker `tk.Grid` configuration managers on the core viewport container layer, preventing layout calculation deadlocks and ensuring stable sizing.
- **Decoupled Extension Modularity:** Separates heavy data-processing structures from display frameworks, abstracting regex syntax engines, search components, and key bindings into isolated execution blocks.

---

## 🛠 Features & Development Utilities

- **Smart Code Auto-Pairing:** Intercepts real-time keyboard inputs to automatically inject closing matches for open symbols `(`, `[`, `{`, `"`, and `'`, shifting the cursor caret right in the center for continuous programming.
- **Intelligent Auto-Indentation:** Overrides standard carriage returns to analyze line text data before execution. If a row terminates with a scoping colon (`:`), the editor automatically shifts your typing line forward exactly 4 spaces on line break.
- **Tab Snippet Macro Expansion:** Combines regex word boundary search filters with custom multiline boilerplates. Typing a keyword (`main`, `def`, `class`, `try`, `for`) and pressing `Tab` instantly substitutes short prefixes with production-grade templates.
- **Interactive Find & Replace Banner:** A toggleable bottom pane activated via `Ctrl + F` that uses a high-contrast overlay tag tracking matrix to flash matching text targets with a vibrant amber tone as you type.
- **Accessibility Font Scaling:** Seamless zoom tracking controls mapped to `Ctrl + Plus` and `Ctrl + Minus` that scale the editor typing frame and line column viewports synchronously to protect readability.
- **Decoupled Script Runner:** Saves active document buffers automatically upon execution and spawns an interactive, standalone external system console window via `F5` to execute Python processes smoothly without slowing down the user interface.

---

## 📂 System Architecture Breakdown

The project follows clean, object-oriented design patterns, cleanly separating frontend visual grids from backend services:

```text
SublimeLight/
│
├── main.py                     # Application Bootstrapper & Main Window Composition Root
├── config.py                   # High-Level Color Baselines & Geometry Dimension Standards
│
├── core/
│   └── app_context.py          # Central Telemetry Domain Context (Tab Memories & Reference Registers)
│
├── components/
│   ├── sidebar/                # Premium Monokai Workspace Explorer Treeview Components
│   ├── statusbar/              # Bottom Metric Tracking Strip Panels
│   └── editor/                 # Modular Text Processing Viewport Matrix
│       ├── view.py             # Slim Editor View Layout Manager
│       ├── tab_bar.py          # Isolated File Tab Strip Row Managers
│       ├── search_panel.py     # Independent Find & Replace Geometry Panel
│       ├── highlighter.py      # Regex Regex-Based Token Color Syntax Engine
│       └── snippet_engine.py   # Intercept Engine Coordinating Tab Key Macro Expansions
│
└── services/
    ├── file_service.py         # Thread-Safe File System Read/Write Utilities
    └── runner_service.py       # Temporary Launcher Compilers & Standalone Process Spawners
```

---

## ⚡ Quick Start & Execution

### Prerequisites
- Python 3.10 or higher
- CustomTkinter UI framework extension

### 1. Clone the repository and establish your local workspace:
```bash
git clone https://github.com/rabindra-dahal/SublimeLight.git
cd SublimeLight
```

### 2. Install dependencies:
```bash
pip install customtkinter
```

### 3. Clear existing bytecode binaries and launch the application:
```bash
# Clean pycache modules safely across your terminal environment tracks
find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +

# Launch the centered desktop editor application
python main.py
```

---

## ⌨️ Global Keyboard Shortcut Mapping Matrix

| Hotkey Combination | Target Command Dispatched / Interface Action Executed |
| :--- | :--- |
| `Ctrl + N` | Instantiates a fresh document layer tab session buffer |
| `Ctrl + O` | Prompts native OS file wizard selectors to load a script into active panel memory |
| `Ctrl + D` | Opens workspace project folder selectors and triggers file tree expansions |
| `Ctrl + S` | Executes thread-safe disk writing routines to validate buffer cache logs |
| `F5` | Saves current editor updates and launches the script inside a native console window |
| `Ctrl + F5` | Spawns a standard Windows Command Prompt session pointing directly to your active directory |
| `Ctrl + F` | Toggles display anchors for the modular Find and Replace search banner grid |
| `Ctrl + T` | Dedicated global key registry tracking loop for theme operations |
| `Ctrl + Plus` | Increases text size readability across typing canvases and row columns synchronously |
| `Ctrl + Minus` | Decreases text font size leading safely down to a stable 8pt baseline constraint |

---

## 📬 Contact & Contributions

Feel free to explore the repository modules, submit issue pull requests, or reach out directly to collaborate on building end-to-end full-stack artificial intelligence platforms, RESTful backends, or desktop microservices!

- **Engineer:** Rabindra Dahal
- **Email:** rabi.vookus@gmail.com
- **LinkedIn:** [Connect with me on LinkedIn](www.linkedin.com/in/rabindra-dahal)
- **GitHub Portfolio:** [Follow my work on GitHub](https://github.com/rabindra-dahal)
