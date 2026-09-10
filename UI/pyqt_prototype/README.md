# Sequencer Python-first Qt Prototype

This is a parallel implementation of the Sequencer UI. It does not replace the existing QML UI.

## Run

```bash
python3 -m venv .venv
.venv/bin/python -m pip install PySide6
.venv/bin/python UI/pyqt_prototype/main.py
```

## Visual preview

Open `UI/pyqt_prototype/prototype_mockup.svg` to see the current polished layout preview.

To capture the native Qt window locally:

```bash
.venv/bin/python UI/pyqt_prototype/capture_screenshot.py
```

That writes `UI/pyqt_prototype/screenshot.png`.

## Design difference

The existing QML UI exposes Python state through QObject models and assembles CLI-style query strings. This prototype keeps Qt but uses Python-generated widgets directly from `CommandParameter` metadata, then runs a point query in a background worker and displays captured output in the window.
