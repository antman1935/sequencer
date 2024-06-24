from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

from qml.APIModel import APIModel

QML_IMPORT_NAME = "com.pyobjects.APIScreenModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class APIScreenModel(QObject):

    def __init__(self, apis: list[dict[str, str]], api_models: dict[str, APIModel]):
        super(APIScreenModel, self).__init__()
        self._apis = apis
        self._api_models = api_models
        self._api = ""

    @Signal
    def api_changed(self):
        pass

    @Property(str, notify=api_changed)
    def api(self):
        return self._api
    
    @api.setter
    def api(self, api):
        if api == self._api:
            return
        self._api = api
        self.api_changed.emit()
        
    @Signal
    def apis_changed(self):
        pass

    @Property('QVariantList', notify=apis_changed)
    def apis(self):
        return self._apis
    
    @apis.setter
    def apis(self, apis):
        if apis == self._apis:
            return
        self._apis = apis
        self.apis_changed.emit()

    @Signal
    def api_models_changed(self):
        pass
    
    @Property('QVariantMap', notify=api_models_changed)
    def api_models(self):
        return self._api_models
    
    @api_models.setter
    def api_models(self, api_models):
        self._api_models = api_models
        self.api_models_changed.emit()