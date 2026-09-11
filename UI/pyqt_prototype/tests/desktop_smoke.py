"""Optional Qt integration: real web form, query, table, and native download."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.environ["QT_QPA_PLATFORM"] == "offscreen":
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QFileDialog
from UI.pyqt_prototype.main import SequencerPrototypeWindow

ARTIFACTS = ROOT / ".venv" / "ui-test-artifacts"
SCRIPT = r"""
(async () => {
  const waitFor = async (test) => {
    for (let i = 0; i < 150; i++) {
      if (test()) return;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    throw new Error('UI operation timed out');
  };
  const select = (selector, value) => {
    const input = document.querySelector(selector);
    input.value = value;
    input.dispatchEvent(new Event('change', {bubbles: true}));
  };
  const run = async () => {
    document.querySelector('#query-form').requestSubmit();
    await waitFor(() => ['Complete', 'Failed'].includes(document.querySelector('#status').textContent));
    if (document.querySelector('#status').textContent !== 'Complete') throw new Error(document.querySelector('#error').textContent);
  };
  try {
    await waitFor(() => document.querySelector('#status')?.textContent === 'Ready');
    document.querySelector('#parameters [data-parameter="n"]').value = '4';
    await run();
    if (!document.querySelector('#panel-0').textContent.includes('= 14')) throw new Error('Wrong point result');
    select('#api', 'range');
    select('#command', 'fubini');
    document.querySelector('#parameters [data-parameter="n"]').value = '3';
    document.querySelector('#dimensions [data-name="n"]').checked = true;
    document.querySelector('#dimensions [data-name="runs"]').checked = true;
    document.querySelector('#add-group').click();
    select('.restriction-heading select', 'zigzag');
    select('.restriction-row [data-parameter="is"]', 'true');
    select('#output', 'latex');
    await run();
    if (document.querySelectorAll('tbody tr').length !== 3) throw new Error('Missing range table');
    document.querySelector('.form-scroll').scrollTop = 0;
    document.querySelector('#downloads a').click();
    document.body.dataset.smoke = 'passed';
  } catch (error) {
    document.body.dataset.smoke = 'failed: ' + error.message;
  }
})();
"""


def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    destination = ARTIFACTS / "desktop-output.tex"
    if destination.exists():
        destination.unlink()
    app = QApplication([])
    window = SequencerPrototypeWindow()
    # Exercise the actual download handler without a person having to pick a path.
    QFileDialog.getSaveFileName = lambda *args, **kwargs: (str(destination), "")
    state = {"started": False, "passed": False, "finished": False}

    def loaded(ok):
        if ok and not state["started"]:
            state["started"] = True
            window.view.page().runJavaScript(SCRIPT)

    def inspected(result):
        if not result or state["finished"]:
            return
        if result.startswith("failed"):
            print(result)
            state["finished"] = True
            window.close()
            app.quit()
        elif destination.exists() and r"\end{document}" in destination.read_text():
            state["passed"] = state["finished"] = True
            window.grab().save(str(ARTIFACTS / "desktop-qt.png"))
            print("Qt WebEngine passed: shared form, point/range queries, restrictions, table, and saved LaTeX download.")
            window.close()
            app.quit()

    window.view.loadFinished.connect(loaded)
    window.show()
    timer = QTimer()
    timer.timeout.connect(lambda: window.view.page().runJavaScript("document.body?.dataset.smoke || ''", inspected))
    timer.start(100)
    QTimer.singleShot(25000, app.quit)
    app.exec()
    window.close()
    if not state["passed"]:
        print("Desktop integration did not complete successfully.")
    return 0 if state["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
