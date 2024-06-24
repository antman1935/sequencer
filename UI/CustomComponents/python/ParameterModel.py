from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

QML_IMPORT_NAME = "com.pyobjects.ParameterModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ParameterModel(QObject):

    def __init__(self, name="", desc="", required = False, type = "str"):
        super(ParameterModel, self).__init__()
        self._name = name
        self._desc = desc
        self._require = required
        self._type = type
        self._value = "" if type == "str" else "false"

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

    @Signal
    def value_changed(self):
        pass
    
    @Property(str, notify=value_changed)
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if (self._value != value):
            self._value = value
            self.value_changed.emit()
    
    @Signal
    def type_changed(self):
        pass

    @Property(str, notify=type_changed)
    def type(self):
        return self._type
    
    @type.setter
    def type(self, new_val):
        if self._type != new_val:
            self._type = new_val
            self.type_changed.emit()

    @Signal
    def require_changed(self):
        pass

    @Property(bool, notify=require_changed)
    def require(self):
        return self._require
    
    @require.setter
    def require(self, new_val):
        if self._require != new_val:
            self._require = new_val
            self.require_changed.emit()