import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.RestrictionGroupModel
import com.pyobjects.ParameterModel
import com.pyobjects.ParameterSetModel

Rectangle {
    id: self
    required property RestrictionGroupModel model
    model: dataParam
    height: params.height + 50
    border.width: 2
    width: 400
    color: Constants.backgroundColor
    
    ColumnLoader {
        id: params
        width: parent.width - parent.border.width * 4
        itemModels: self.model?.restrictions ?? []
        source: (index) => {return "ParameterSet.qml"}
        delegateCallbacks: QtObject {
            function onDeleted(item, index) {
                self.model.restrictions[index].destroy()
                self.model.restrictions.splice(index, 1)
            }
        }
    }

    Button {
        text: "Add Restriction"
        height: 40
        width: 3 * (parent.width / 7)
        x: parent.width / 2 - width / 2
        y: params.height + 5
        onClicked: {
            dialog.open()
        }
    }

    Dialog {
        id: dialog

        parent: Overlay.overlay 
        anchors.centerIn: parent
        title: "Add Restriction"
        standardButtons: Dialog.Ok | Dialog.Cancel
        width: parent.width * 0.75
        height: parent.width * 0.4
        background: Rectangle{
            color: Constants.backgroundColor
            border.width: 1
        }

        Row {
            x: 4
            width: parent.width - x * 2
            height: parent.height
            spacing: 4
            ListPick {
                id: restriction
                options: screenModel?.restrictions ?? []
                header: "Restrictions"
                height: parent.height
                width: (parent.width - 10) / 2
            }

            Rectangle {
                width: 2
                height: parent.height * 0.95
                color: "black"
                y: parent.height / 2 - height / 2
            }

            ParameterScroll {
                id: p
                parameters: {(restriction.selectedIndex != -1) ? screenModel?.restrictionParameters[restriction.selectedIndex] ?? [] : []}
                padding: 5
                width: (parent.width - 10) / 2
                height: parent.height
            }
        }

        Component {
            id: new_set
            ParameterSetModel {

            }
        }

        Component {
            id: new_param
            ParameterModel {

            }
        }

        onAccepted: {
            if (restriction.selectedIndex != -1) {
                var parms = []
                if (screenModel.restrictionParameters[restriction.selectedIndex].length > 0) {
                    screenModel.restrictionParameters[restriction.selectedIndex].forEach((item)=>{
                        var parm = new_param.createObject(null, {
                            name: item.name,
                            desc: item.desc,
                            require: item.require,
                            type: item.type
                        })
                        parm.value = item.value
                        parms.push(parm)
                    })
                }

                var obj = new_set.createObject(null, {
                    descriptor: screenModel.restrictions[restriction.selectedIndex]
                })
                // obj.descriptor = screenModel.restrictions[restriction.selectedIndex]
                obj.parameters = parms
                model.restrictions.push(obj)
                restriction.options[restriction.selectedIndex].selected = false
                restriction.selectedIndex = -1
            }
        }
    }
}