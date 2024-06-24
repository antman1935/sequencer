import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.ParameterModel 1.0

Row {
    id: self
    default property alias content: self.children
    property ParameterModel data: dataParam
    property string check: "false"
    spacing: 10
    Text {
        id: nameTxt
        text: qsTr(self.data?.name ?? "")
        font.pixelSize: 18
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WrapAnywhere
        width: 0.2 * parent.width
        height: parent.height
    }

    Text {
        id: descTxt
        text: qsTr(self.data?.desc ?? "")
        font.pixelSize: 18
        wrapMode: Text.WordWrap
        width: 0.6 * parent.width
    }

    Row {
        id: paramTbx
        width: parent.width - nameTxt.width - descTxt.width - parent.spacing * 2
        y: parent.height / 2 - height / 2
        Row {
            spacing: 5
            x: parent.width / 2 - width / 2
            Text {
                id: enableTxt
                text: qsTr("Enable")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                height: parent.height
            }


            CheckBox {
                id: enableCbo
                checked: check == "true"
                onClicked: {
                    if (check == "true") {
                        check = "false"
                    } else {
                        check = "true"
                    }
                }
            }
        }

        Binding {
            target: self.data
            property: "value"
            value: check
        }
    }
}
