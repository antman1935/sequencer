import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.UIManager

Rectangle {
    width: Constants.width
    height: Constants.height
    property UIManager manager: myModel

    color: Constants.backgroundColor
    MathObjectScreen {
        id: objectScreen
        model: manager?.object ?? null
        x: 4
        y: 8
        width: 504
        height: 336
        color: Constants.backgroundColor
        radius: 3
        border.color: "#000000"
        border.width: 2
        z: 0

        onChoiceChanged: {
            parameterScreen.key = model.choice
        }
    }

    ParameterScreen {
        id: parameterScreen
        model: manager?.parameters ?? null
        x: 4
        y: 350
        width: 504
        height: 336
        color: Constants.backgroundColor
        radius: 3
        border.color: "#000000"
        border.width: 2
        z: 0
    }

    APIScreen {
        id: apiScreen
        model: manager?.apis ?? null
        parameters: parameterScreen.getCurrentParameters()
        x: 520
        y: 8
        width: 354
        height: 336
        color: Constants.backgroundColor
        radius: 3
        border.color: "#000000"
        border.width: 2
        z: 0
    }

    FunctionScreen {
        id: functionScreen
        model: manager?.functions ?? null
        x: 520
        y: 350
        width: 354
        height: 336
        color: Constants.backgroundColor
        radius: 3
        border.color: "#000000"
        border.width: 2
        z: 0
    }

    RestrictionScreen {
        id: restrictionScreen
        model: manager?.restrictions ?? null
        x: 886
        y: 8
        width: 386
        height: 336
        color: Constants.backgroundColor
        radius: 3
        border.color: "#000000"
        border.width: 2
        z: 0
    }

    Rectangle {
        x: 886
        y: 350
        width: 386
        height: 336
        color: Constants.backgroundColor
        radius: 3
        border.color: "#000000"
        border.width: 2

        Text {
            id: outputTxt
            x: 4
            text: qsTr("Output")
            font.pixelSize: 25
        }

        Button {
            text: "GO!!"
            width: 100
            height: 40
            x: parent.width / 2 - width / 2
            y: parent.height / 2 - height / 2

            onClicked: {
                manager.runQuery()
            }
        }

        TabBar {
            id: tabBar
            x: 8
            y: 36
            width: 240

            TabButton {
                id: tabButton
                text: qsTr("Tab Button")
            }

            TabButton {
                id: tabButton1
                text: qsTr("Tab Button")
            }
        }
    }
}
