from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

QML_IMPORT_NAME = "com.pyobjects.APIModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class APIModel(QObject):

    def __init__(self, name="", desc=""):
        super(APIModel, self).__init__()
        self._name = name
        self._desc = desc

    @Signal
    def name_changed(self):
        pass

    @Property(str, notify=name_changed)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
        self.name_changed.emit()

    @Signal
    def desc_changed(self):
        pass
    
    @Property(str, notify=desc_changed)
    def desc(self):
        return self._desc
    
    @desc.setter
    def desc(self, desc):
        self._desc = desc
        self.desc_changed.emit()