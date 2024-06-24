
import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.NameDescModel 1.0

Row {
    id: self
    default property alias content: self.children
    required property NameDescModel data
    height: Math.max(nameTxt.height, descTxt.height) + 10

    Text {
        id: nameTxt
        text: qsTr(self.data?.name ?? "")
        font.pixelSize: 18
        wrapMode: Text.WrapAnywhere
        enabled: true
        y: parent.height / 2 - height / 2 - parent.padding
        width: parent.width * 0.3
    }

    Text {
        id: descTxt
        text: qsTr(self.data?.desc ?? "")
        font.pixelSize: 18
        wrapMode: Text.WordWrap
        y: parent.height / 2 - height / 2 - parent.padding
        width: parent.width - nameTxt.width - parent.spacing
    }
}