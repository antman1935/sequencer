import QtQuick 6.5
import QtQuick.Controls 6.5

Row {
    id: self
    default property alias content: self.children
    property alias data: deets.data
    data: dataParam
    height: childrenRect.height
    signal deleted

    Row {
        spacing: 10
        width: parent.width

        NameDesc {
            id: deets
            spacing: parent.spacing
            width: parent.width * 0.85
        }

        Button {
            id: delBtn
            text: qsTr("X")
            width: parent.width * 0.15 - parent.spacing
            height: width
            y: parent.height / 2 - height / 2

            onClicked: deleted()
        }
    }
}
