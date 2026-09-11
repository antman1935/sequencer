"""Desktop host for exactly the same UI served to a normal browser."""
import argparse
import sys
from pathlib import Path
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from UI.pyqt_prototype.theme import LAYOUT
from UI.pyqt_prototype.web_server import SequencerServer


class SequencerPrototypeWindow(QMainWindow):
    def __init__(self, url=None):
        super().__init__()
        self.setWindowTitle("Sequencer")
        self.server = None
        if url is None:
            self.server = SequencerServer().start()
            url = self.server.url
        else:
            parsed = urlsplit(url)
            if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost") or parsed.username or parsed.password:
                raise ValueError("The desktop host accepts only a local Sequencer URL.")
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)
        self.view.page().profile().downloadRequested.connect(self.save_download)
        self.view.loadFinished.connect(self.loaded)
        self.view.setUrl(QUrl(url))
        self.resize(LAYOUT["window_width"], LAYOUT["window_height"])

    def loaded(self, ok):
        if not ok:
            self.statusBar().showMessage("Could not load Sequencer. Check the local server and reopen the app.")

    def save_download(self, download):
        destination, _ = QFileDialog.getSaveFileName(self, "Save query output", download.downloadFileName())
        if not destination:
            download.cancel()
            return
        path = Path(destination)
        download.setDownloadDirectory(str(path.parent))
        download.setDownloadFileName(path.name)
        download.accept()

    def closeEvent(self, event):
        if self.server is not None:
            self.server.stop()
            self.server = None
        super().closeEvent(event)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Use an already-running local Sequencer server.")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    try:
        window = SequencerPrototypeWindow(args.url)
    except (OSError, ValueError) as exc:
        QMessageBox.critical(None, "Could not start Sequencer", str(exc))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
