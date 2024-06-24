import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.ParameterScreenModel

Rectangle {
    id: self
    default property alias content: self.children
    required property ParameterScreenModel model;
    property string key: ""

    function getCurrentParameters() {
        return p.parameters;
    }

    Text {
        id: parameterTxt
        x: 4
        text: qsTr("Parameters")
        font.pixelSize: 25
    }

    ParameterScroll {
        id: p
        parameters: {(key != "") ? model?.parameters[key] ?? [] : []}
        x: 4
        y: 36
        padding: 5
        width: parent.width - padding * 2 - parent.border.width * 2 - x * 2
        height: parent.height 
    }
}