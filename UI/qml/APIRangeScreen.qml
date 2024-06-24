import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.NameDescModel

import com.pyobjects.APIRangeModel

Rectangle {
        id: self
        required property APIRangeModel model
        required property list<NameDescModel> paramOptions

        Column {
            id: content
            width: parent.width
            height: parent.height - 50
            spacing: 10

            Text {
                id: dimStr
                text: qsTr("The dimensions for the Range API.")
            }

            ScrollLoader {
                height: content.height * 0.90
                width: parent.width
                itemModels: self.model?.chosen_dimensions ?? []
                source: (index) => {return "NameDescDel.qml"}

                delegateCallbacks: QtObject {
                    function onDeleted(item, index) {
                        self.model.chosen_dimensions?.splice(index, 1) ?? 0
                    }
                }
            }

            Dialog {
                id: dialog
                parent: Overlay.overlay 
                anchors.centerIn: parent
                title: "Add Dimension"
                standardButtons: Dialog.Ok | Dialog.Cancel
                width: parent.width * 0.5
                height: parent.width * 0.4
                background: Rectangle{
                    color: Constants.backgroundColor
                    border.width: 1
                }

                ListPick {
                    id: dimensionChoice
                    options: self.paramOptions?.concat(self.model?.dimension_options ?? []) ?? undefined
                    header: "Dimensions"
                    x: 4
                    width: parent.width - x * 2
                    height: parent.height
                }

                onAccepted: {
                    if (dimensionChoice.selectedIndex != -1) {
                        model.chosen_dimensions.push(dimensionChoice.options[dimensionChoice.selectedIndex])
                        dimensionChoice.options[dimensionChoice.selectedIndex].selected = false
                        dimensionChoice.selectedIndex = -1
                    }
                }
                onRejected: {
                    if (dimensionChoice.selectedIndex != -1) {
                        dimensionChoice.options[dimensionChoice.selectedIndex].selected = false
                        dimensionChoice.selectedIndex = -1
                    }
                }
            }

            Button {
                id: addDimensionBtn
                x: parent.width / 2 - width / 2
                text: "Add Dimension"
                onClicked: {
                    dialog.open()
                }
            }
        }
        
    }