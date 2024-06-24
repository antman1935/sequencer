from PySide6.QtQml import QmlElement

from qml.APIModel import APIModel

QML_IMPORT_NAME = "com.pyobjects.APIPointModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class APIPointModel(APIModel):

    def __init__(self, name="", desc=""):
        super(APIPointModel, self).__init__(name, desc)