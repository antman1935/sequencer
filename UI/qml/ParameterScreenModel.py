from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

from CustomComponents.python.ParameterModel import ParameterModel

QML_IMPORT_NAME = "com.pyobjects.ParameterScreenModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ParameterScreenModel(QObject):

    def __init__(self, parameters: dict[str, list[ParameterModel]]):
        super(ParameterScreenModel, self).__init__()
        self._parameters = parameters
        self._key = None
        
    @Signal
    def parameters_changed(self):
        pass

    @Property('QVariantMap', notify=parameters_changed)
    def parameters(self):
        return self._parameters
    
    @parameters.setter
    def parameters(self, parameters):
        if parameters == self._parameters:
            return
        self._parameters = parameters
        self.parameters_changed.emit()

    @Signal
    def key_changed(self):
        pass
    
    @Property(str, notify=key_changed)
    def key(self):
        return self._key
    
    @key.setter
    def key(self, key):
        self._key = key
        self.key_changed.emit()