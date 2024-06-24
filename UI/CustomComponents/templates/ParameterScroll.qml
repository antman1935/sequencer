import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.ParameterModel

ScrollLoader {
    id: self
    width: 500
    height: 300
    implicitWidth: width

    property alias parameters: self.itemModels

    itemModels: parameters
    source: (index) => {
        if (self.itemModels[index] !== undefined && self.itemModels[index] !== null) {
            if (self.itemModels[index].type == "str") {
                return "StringParameter.qml"
            } else {
                return "BooleanParameter.qml"
            }
        } else {
            return ""
        }
    }
}