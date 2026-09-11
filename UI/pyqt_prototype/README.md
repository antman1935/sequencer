# Sequencer shared UI

The browser and desktop now present the **same HTML, CSS, and JavaScript** from
`web/`. The desktop is a small Qt WebEngine host. Both call the same local HTTP
API, which derives forms from the command/restriction metadata and executes the
existing Python query runner. The original QML application in `UI/main.py` is
unchanged.

## Run in a browser

From the repository root (Python 3.11+; no third-party packages needed):

```sh
python UI/pyqt_prototype/web_server.py
```

Open http://127.0.0.1:8765/. Use `--port 8766` to choose a different port.
The server binds only to loopback. This is a local application, not a production
internet-facing server. Ctrl+C stops it.

## Run on desktop

```sh
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r UI/pyqt_prototype/requirements.txt
.\.venv\Scripts\python.exe UI/pyqt_prototype/main.py
```

macOS/Linux:

```sh
.venv/bin/python -m pip install -r UI/pyqt_prototype/requirements.txt
.venv/bin/python UI/pyqt_prototype/main.py
```

Desktop mode starts its own local server on an available port and stops it when
the window closes. To share an already-running browser server, add
`--url http://127.0.0.1:8765/`. Closing that desktop window leaves the separately
started server running. Both hosts render the same form; each window keeps its
own in-progress inputs and results.

## Functionality

- All registered object families, statistics, and typed parameters.
- Point and range queries, parameter/computed dimensions, and generated elements.
- AND restrictions within each group; OR between groups. Add or remove rows/groups.
- Explicit true/false and zero values, separately from omitted/default values.
- Text, rendered tables (including multiple tables), OEIS, raw output, and LaTeX.
- LaTeX downloads in the browser and a native Save dialog on desktop.
- Loading/error states, keyboard-accessible controls, and responsive layout.

`schema.py` is the single metadata/validation adapter. `runner.py` is the shared
query service; query execution is serialized because the legacy APIs capture
process-wide stdout. HTTP requests run on background threads so the UI remains
responsive. No Node runtime, frontend build, or duplicated Qt widget layout is
needed to run the app.

## Verification and screenshots

From the repository root:

```sh
python -m unittest discover -s UI/pyqt_prototype/tests -p "test_*.py"
```

Browser integration tests and screenshots use the existing development packages:

```sh
cd UI/pyqt_prototype
npm ci
npx playwright install chromium
npm run test:ui
```

The browser tests start and stop their own server. `SEQUENCER_PYTHON` can select
a Python executable; otherwise they use the repository's `.venv` if present.
Set `SEQUENCER_BROWSER_CHANNEL=msedge` to use an installed Edge browser instead
of downloading Chromium. With PySide6 installed, run
`python UI/pyqt_prototype/tests/desktop_smoke.py` from the repository root to
verify the same form and native download handling inside Qt WebEngine.

With the web server running, `npm run capture-preview` writes `preview.png` from
the actual app. Set `SEQUENCER_URL` to capture another local port. There is no
separate preview template or mock renderer.

For a desktop screenshot, run `python UI/pyqt_prototype/capture_screenshot.py`
with the desktop dependencies installed. It waits for the shared page to load
and writes `UI/pyqt_prototype/screenshot.png`.
