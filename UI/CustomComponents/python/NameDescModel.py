from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "com.pyobjects.NameDescModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class NameDescModel(QObject):

    def __init__(self, name="", desc="", key="", selected = False):
        super(NameDescModel, self).__init__()
        self._name = name
        self._desc = desc
        self._selected = selected
        self._key = key

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
    def key_changed(self):
        pass
    
    @Property(str, notify=key_changed)
    def key(self):
        return self._key
    
    @key.setter
    def key(self, key):
        self._key = key
        self.key_changed.emit()
    
    @Signal
    def selection_changed(self):
        pass

    @Property(bool, notify=selection_changed)
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, new_val):
        if self._selected != new_val:
            self._selected = new_val
            self.selection_changed.emit()