import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.ParameterModel
import com.pyobjects.NameDescModel

import com.pyobjects.APIScreenModel

Rectangle {
        id: self
        default property alias content: self.children
        required property APIScreenModel model;
        required property list<ParameterModel> parameters;
        property alias pOptions: range.paramOptions
        width: 354
        height: 336

        Component {
            id: param
            NameDescModel {

            }
        }

        pOptions: {
            return self.parameters.map((item)=>{return param.createObject(range, {name: item.name, desc: item.desc, key: item.name + "-p"})})
        }

        Column {
            id: column
            x: parent.border.width * 2
            width: parent.width - parent.border.width * 4
            height: parent.height
            spacing: 10

            Row {
                id: apiSelector
                width: parent.width
                height: 50
                spacing: 10

                Text {
                    id: apiText
                    y: 0
                    height: parent.height
                    text: qsTr("API")
                    font.pixelSize: 22
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                ComboBox {
                    id: apiCombo
                    model: self.model?.apis ?? null
                    delegate: ItemDelegate {
                        width: apiCombo.width
                        contentItem: Text {
                            text: modelData.display
                            font: apiCombo.font
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                        }
                        highlighted: apiCombo.highlightedIndex === index
                    }
                    displayText: self.model?.apis[apiCombo.currentIndex].display ?? ""
                    y: parent.height / 2 - height / 2
                    width: 216
                    height: 40

                    Binding {
                        target: self.model
                        property: "api"
                        value: self.model?.apis[apiCombo.currentIndex].key ?? ""
                    }
                }
            }

            Text {
                id: apiDescTxt
                text: qsTr(self.model?.api_models[self.model.api]?.desc ?? "")
                font.pixelSize: 16
                wrapMode: Text.WordWrap
                width: parent.width
            }

            Rectangle {
                id: subscreen
                width: parent.width
                height: parent.height - apiSelector.height - apiDescTxt.height - parent.spacing * 2.5
                color: Constants.backgroundColor

                APIPointScreen {
                    width: parent.width
                    height: parent.height
                    color: parent.color
                    model: self.model?.api_models["point"] ?? null
                    visible: (self.model?.api ?? "") == "point"
                }

                APIRangeScreen {
                    id: range
                    width: parent.width
                    height: parent.height
                    model: self.model?.api_models["range"] ?? null
                    visible: (self.model?.api ?? "") == "range"
                    color: parent.color
                }
            }
        }
    }