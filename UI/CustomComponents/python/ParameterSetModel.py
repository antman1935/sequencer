from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

from CustomComponents.python.NameDescModel import NameDescModel
from CustomComponents.python.ParameterModel import ParameterModel

QML_IMPORT_NAME = "com.pyobjects.ParameterSetModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ParameterSetModel(QObject):

    def __init__(self, descriptor: NameDescModel = None, parameters: list[ParameterModel] = []):
        super(ParameterSetModel, self).__init__()
        self._descriptor = descriptor
        self._parameters = parameters

    @Signal
    def descriptor_changed(self):
        pass

    @Property(NameDescModel, notify=descriptor_changed)
    def descriptor(self):
        return self._descriptor
    
    @descriptor.setter
    def descriptor(self, descriptor):
        if self._descriptor != descriptor:
            self._descriptor = descriptor
            self.descriptor_changed.emit()

    @Signal
    def parameters_changed(self):
        pass

    @Property('QVariantList', notify=parameters_changed)
    def parameters(self):
        return self._parameters
    
    @parameters.setter
    def parameters(self, parameters):
        if parameters == self._parameters:
            return
        self._parameters = parameters
        self.parameters_changed.emit()