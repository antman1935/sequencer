import QtQuick 6.5
import QtQuick.Controls 6.5

import com.pyobjects.ParameterSetModel

Row {
    id: self
    padding: 4
    required property ParameterSetModel model;
    model: dataParam
    signal deleted

    height: Math.max(resName.height, ps.height, btns.height)
    spacing: 4

    Text {
        id: resName
        text: qsTr(self.model?.descriptor.name ?? "")
        font.pixelSize: 18
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.Wrap
        width: parent.width * 0.2
        y: parent.height / 2 - height / 2
    }

    Column {
        id: ps
        spacing: 1
        width: parent.width * 0.57
        y: parent.height / 2 - height / 2
        Rectangle {
            width: parent.width
            height: 0.1
        }
        Repeater {
            model: self.model?.parameters.length ?? 0
            delegate: Text{
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.Wrap
                text: qsTr(self.model.parameters[index].name + ": " + self.model.parameters[index].value)
                width: parent.width
            }
        }
    }

    Row {
        id: btns
        width: parent.width * 0.2 - parent.spacing * 2
        spacing: width * 0.2
        y: parent.height / 2 - height / 2
        Button {
            text: "U"
            font.bold: true
            width: parent.width * 0.4
            height: width
            y: parent.height / 2 - height / 2
            onClicked: {
                dialog.open()
            }
        }

        Button {
            text: "X"
            width: parent.width * 0.4
            height: width
            y: parent.height / 2 - height / 2
            onClicked: {
                self.deleted()
            }
        }
    }

    Dialog {
        id: dialog
        parent: Overlay.overlay 
        anchors.centerIn: parent
        title: "Edit " + (self.model?.descriptor.name ?? "") + " Parameters"
        standardButtons: Dialog.Ok
        width: parent.width * 0.5
        height: parent.width * 0.4
        background: Rectangle{
            color: Constants.backgroundColor
            border.width: 1
        }

        Text {
            id: popDesc
            wrapMode: Text.WordWrap
            font.pixelSize: 18
            width: parent.width - x * 2
            x: 4
            text: qsTr(model?.descriptor.desc ?? "")
        }

        ParameterScroll {
            id: dimensionChoice
            parameters: self.model?.parameters ?? []
            x: 4
            y: popDesc.y + popDesc.height + 5
            width: parent.width - x * 2
            height: parent.height - y
        }
    }
}