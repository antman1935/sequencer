import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.ParameterModel 1.0

Row {
    id: self
    default property alias content: self.children
    property ParameterModel data: dataParam
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

    TextField {
        id: paramTbx
        placeholderText: qsTr(self.data?.value ?? "")
        text: self.data?.value ?? ""
        width: parent.width - nameTxt.width - descTxt.width - parent.spacing * 2 - 4
        y: parent.height / 2 - height / 2
    }

    Binding {
        target: self.data
        property: "value"
        value: paramTbx.text
    }
}
