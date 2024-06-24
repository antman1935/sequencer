import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.RestrictionScreenModel
import com.pyobjects.RestrictionGroupModel

Rectangle {
    id: self
    required property RestrictionScreenModel model

    Text {
        id: restrictionTxt
        x: 4
        y: 8
        text: qsTr("Restrictions")
        font.pixelSize: 25
    }

    Rectangle {
        x: parent.border.width
        width: parent.width - x * 2
        color: Constants.backgroundColor
        height: (addResButton.y - y) - 3
        
        y: 36

        ScrollLoader {
            id: groups
            x: 4
            width: parent.width  - x * 2
            height: parent.height * 0.97
            itemModels: self.model?.restrictionGroups ?? []
            source: (index) => {return "../../qml/RestrictionGroup.qml"}
            property RestrictionScreenModel screenModel: self.model
        }
    }
    
    Button {
        id: addResButton
        height: 40
        width: 3 * (parent.width / 7)
        x: parent.width / 2 - width / 2
        y: parent.height - height - 3
        text: "Add Restriction Group"

        onClicked: {
            model.createNewGroup()
        }
    }
}