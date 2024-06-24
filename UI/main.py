# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial

import sys, os
from pathlib import Path

from PySide6.QtCore import QObject, Slot, QUrl, QCoreApplication, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle

from qml.UIManager import makeManager

#import style_rc

CURRENT_DIRECTORY = Path(__file__).resolve().parent
LIBRARY_DIR = CURRENT_DIRECTORY / "CustomComponents"

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    #QQuickStyle.setStyle("Material")
    # Get the path of the current directory, and then add the name
    # of the QML file, to load it.
    engine = QQmlApplicationEngine()
    engine.addImportPath(os.fspath(LIBRARY_DIR))
    model = makeManager()
    engine.rootContext().setContextProperty("myModel", model)
    url = QUrl.fromLocalFile(os.fspath(CURRENT_DIRECTORY / "qml" / "App.qml"))

    def handle_object_created(obj, obj_url):
        if obj is None and url == obj_url:
            QCoreApplication.exit(-1)

    engine.objectCreated.connect(
        handle_object_created, Qt.ConnectionType.QueuedConnection
    )

    engine.load(url)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
