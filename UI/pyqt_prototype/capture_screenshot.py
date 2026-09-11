"""Capture the actual desktop web view after its metadata has loaded."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.environ["QT_QPA_PLATFORM"] == "offscreen":
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from UI.pyqt_prototype.main import SequencerPrototypeWindow


def main():
    app = QApplication(sys.argv)
    window = SequencerPrototypeWindow()
    window.show()
    captured = False

    def ready(loaded):
        nonlocal captured
        if loaded and not captured:
            captured = True
            window.grab().save(str(Path(__file__).with_name("screenshot.png")))
            window.close()
            app.quit()

    timer = QTimer()
    timer.timeout.connect(lambda: window.view.page().runJavaScript("document.querySelector('#status')?.textContent === 'Ready'", ready))
    timer.start(100)
    QTimer.singleShot(15000, app.quit)
    app.exec()
    window.close()
    return 0 if captured else 1


if __name__ == "__main__":
    sys.exit(main())
