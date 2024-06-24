from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

from CustomComponents.python.ParameterSetModel import ParameterSetModel

from CustomComponents.python.NameDescModel import NameDescModel
from CustomComponents.python.ParameterModel import ParameterModel

QML_IMPORT_NAME = "com.pyobjects.RestrictionGroupModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RestrictionGroupModel(QObject):

    def __init__(self, restrictions: list[ParameterSetModel] = []):
        super(RestrictionGroupModel, self).__init__()
        self._restrictions = restrictions

    @Signal
    def restrictions_changed(self):
        pass

    @Property('QVariantList', notify=restrictions_changed)
    def restrictions(self):
        return self._restrictions
    
    @restrictions.setter
    def restrictions(self, restrictions):
        if restrictions == self._restrictions:
            return
        self._restrictions = restrictions[:]
        self.restrictions_changed.emit()