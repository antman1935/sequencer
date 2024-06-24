import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.NameDescModel 1.0


ScrollView {
    id: self
    width: 500
    height: 300

    contentWidth: availableWidth

    property alias itemModels: content.itemModels
    property alias delegateCallbacks: content.delegateCallbacks
    property alias source: content.source
    property int colspacing: 10

    ColumnLoader {
        id: content
        width: parent.width
        spacing: self.colspacing
    }
}
