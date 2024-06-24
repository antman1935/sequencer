import QtQuick 6.5
import QtQuick.Controls 6.5

Rectangle {
    id: self
    default property alias content: self.children
    property alias data: deets.data
    data: dataParam
    color: Constants.backgroundColor
    height: background.height / 0.95
    width: 500
    signal click

    function toggleSelected() {
        self.data.selected = !self.data.selected
    }

    states: [
        State {
            name: "selected"
            when: self.data?.selected ?? false
            PropertyChanges { target: background; color: "cyan" }
        },
        State {
            name: "unselected"
            when: !self.data?.selected ?? false
            PropertyChanges { target: background; color: self.color }
        }
    ]

    Rectangle {
        id: background
        width: parent.width * 0.95
        height: deets.height
        anchors.verticalCenter: self.verticalCenter
        anchors.horizontalCenter: self.horizontalCenter
        
        NameDesc {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            id: deets
            spacing: 10
            width: parent.width * 0.95
        }
    }

    MouseArea {
        id: mouse
        width: parent.width
        height: parent.height
        onClicked: (evt) => {
            self.click()
        }
    }
}
