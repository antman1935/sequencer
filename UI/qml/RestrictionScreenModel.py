from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import QmlElement, ListProperty
from PySide6.QtWidgets import QListView

from CustomComponents.python.NameDescModel import NameDescModel
from CustomComponents.python.ParameterModel import ParameterModel
from qml.RestrictionGroupModel import RestrictionGroupModel


QML_IMPORT_NAME = "com.pyobjects.RestrictionScreenModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RestrictionScreenModel(QObject):

    def __init__(self, restrictions: list[NameDescModel] = [], restrictionParameters: list[list[ParameterModel]] = [], restrictionGroups: list[RestrictionGroupModel] = []):
        super(RestrictionScreenModel, self).__init__()
        self._restrictions = restrictions
        self._restrictionParameters = restrictionParameters
        self._restrictionGroups = restrictionGroups

    @Slot()
    def createNewGroup(self):
        group = RestrictionGroupModel()
        self._restrictionGroups.append(group)
        self.restrictionGroups_changed.emit()
        
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

    @Signal
    def restrictionParameters_changed(self):
        pass

    @Property('QVariantList', notify=restrictionParameters_changed)
    def restrictionParameters(self):
        return self._restrictionParameters
    
    @restrictionParameters.setter
    def restrictionParameters(self, restrictionParameters):
        if restrictionParameters == self._restrictionParameters:
            return
        self._restrictionParameters = restrictionParameters[:]
        self.restrictionParameters_changed.emit()

    @Signal
    def restrictionGroups_changed(self):
        pass

    @Property('QVariantList', notify=restrictionGroups_changed)
    def restrictionGroups(self):
        return self._restrictionGroups
    
    @restrictionGroups.setter
    def restrictionGroups(self, restrictionGroups):
        if restrictionGroups == self._restrictionGroups:
            return
        self._restrictionGroups = restrictionGroups[:]
        self.restrictionGroups_changed.emit()