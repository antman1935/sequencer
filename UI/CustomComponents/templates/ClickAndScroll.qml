import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.NameDescModel 1.0


ScrollLoader {
    id: self
    width: 500
    height: 300

    property int selectedIndex: -1
    property alias options: self.itemModels
    source: (index) => {return "NameDescClick.qml"}

    delegateCallbacks: QtObject{
        function onClick(item, index) {
            item.toggleSelected()
            if (item.data.selected) {
                if (self.selectedIndex != -1) {
                    self.options[self.selectedIndex].selected = false
                }
                self.selectedIndex = index;
            } else {
                self.selectedIndex = -1;
            }
        }
    }
}
