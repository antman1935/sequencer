from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

from CustomComponents.python.NameDescModel import NameDescModel

QML_IMPORT_NAME = "com.pyobjects.MathObjectScreenModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MathObjectScreenModel(QObject):

    def __init__(self, options: list[NameDescModel]):
        super(MathObjectScreenModel, self).__init__()
        self._options = options
        self._choice = None
        
    @Signal
    def options_changed(self):
        pass

    @Property('QVariantList', notify=options_changed)
    def options(self):
        return self._options
    
    @options.setter
    def options(self, options):
        if options == self._options:
            return
        self._options = options[:]
        self.options_changed.emit()

    @Signal
    def choice_changed(self):
        pass
    
    @Property(str, notify=choice_changed)
    def choice(self):
        return self._choice
    
    @choice.setter
    def choice(self, choice):
        self._choice = choice
        self.choice_changed.emit()