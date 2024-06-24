import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

Rectangle {
    id: self
    default property alias content: self.children
    required property string header
    property alias options: objectChoice.options;
    property alias selectedIndex: objectChoice.selectedIndex
    property string choice: ""
    property string defaultName: ""
    color: Constants.backgroundColor

    Text {
        id: headerTxt
        x: 4
        text: qsTr(self.header)
        font.pixelSize: 25
    }

    Text {
        id: choiceTxt
        text: {
            if (objectChoice.selectedIndex == -1) {
                qsTr(defaultName)
            } else {
                qsTr(options[objectChoice.selectedIndex]?.name ?? "")
            }
        }
        x: parent.width - choice_metrics.boundingRect.width - parent.border.width * 4
        y: objectChoice.y / 2 - height / 2
        font.pixelSize: 18
    }

    TextMetrics {
        id: choice_metrics
        font: choiceTxt.font
        text: choiceTxt.text
    }

    ClickAndScroll {
        id: objectChoice
        x: 4
        y: 36
        width: parent.width * 0.97
        height: parent.height * 0.87
        onSelectedIndexChanged: {
            if (selectedIndex != -1) {
                self.choice = self.options[selectedIndex].key
            } else {
                self.choice = ""
            }
            choiceChanged()
        }
    }
}