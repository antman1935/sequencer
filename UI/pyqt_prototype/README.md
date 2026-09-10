# Sequencer Python-first Qt Prototype

This is a parallel implementation of the Sequencer UI. It does not replace the existing QML UI.

## Run

```bash
python3 -m venv .venv
.venv/bin/python -m pip install PySide6
.venv/bin/python UI/pyqt_prototype/main.py
```

## Browser-verified visual preview

The Qt app and browser preview share `theme.py` for colors, typography, and core layout constants. Use the browser preview for fast visual iteration before expanding the whole program:

```bash
cd UI/pyqt_prototype
npm install
npm run preview
```

That generates:

- `preview.html` — browser-renderable layout preview
- `preview.svg` — token-rendered fallback preview
- `preview.png` — screenshot proof captured by Playwright, or by the SVG fallback when sandbox browser libraries are unavailable

To capture the native Qt window locally:

```bash
.venv/bin/python UI/pyqt_prototype/capture_screenshot.py
```

That writes `UI/pyqt_prototype/screenshot.png`.

## Design difference

The existing QML UI exposes Python state through QObject models and assembles CLI-style query strings. This prototype keeps Qt but uses Python-generated widgets directly from `CommandParameter` metadata, then runs a point query in a background worker and displays captured output in the window.
