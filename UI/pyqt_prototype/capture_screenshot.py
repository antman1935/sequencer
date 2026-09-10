import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from UI.pyqt_prototype.main import APP_STYLE, SequencerPrototypeWindow


OUTPUT_PATH = Path(__file__).with_name("screenshot.png")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    app.setFont(QFont("Arial", 10))

    window = SequencerPrototypeWindow()
    window.resize(1180, 760)
    window.show()

    def capture():
        pixmap = window.grab()
        pixmap.save(str(OUTPUT_PATH))
        app.quit()

    QTimer.singleShot(300, capture)
    app.exec()


if __name__ == "__main__":
    main()
