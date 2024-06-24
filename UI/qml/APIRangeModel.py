from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

from CustomComponents.python.NameDescModel import NameDescModel
from qml.APIModel import APIModel

QML_IMPORT_NAME = "com.pyobjects.APIRangeModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class APIRangeModel(APIModel):

    def __init__(self, name="", desc="", dimension_options: list[NameDescModel] = [], chosen_dimensions: list[NameDescModel] = []):
        super(APIRangeModel, self).__init__(name, desc)
        self._chosen_dimensions = chosen_dimensions
        self._dimension_options = dimension_options

    @Signal
    def chosen_dimensions_changed(self):
        pass

    @Property('QVariantList', notify=chosen_dimensions_changed)
    def chosen_dimensions(self):
        return self._chosen_dimensions
    
    @chosen_dimensions.setter
    def chosen_dimensions(self, chosen_dimensions):
        if chosen_dimensions == self._chosen_dimensions:
            return
        self._chosen_dimensions = chosen_dimensions[:]
        self.chosen_dimensions_changed.emit()

    @Signal
    def dimension_options_changed(self):
        pass

    @Property('QVariantList', notify=dimension_options_changed)
    def dimension_options(self):
        return self._dimension_options
    
    @dimension_options.setter
    def dimension_options(self, dimension_options):
        if dimension_options == self._dimension_options:
            return
        self._dimension_options = dimension_options[:]
        self.dimension_options_changed.emit()