import QtQuick 6.5
import QtQuick.Controls 6.5
import com.pyobjects.NameDescModel 1.0

Column {
    id: self
    width: 500
    height: childrenRect.height

    property list<QtObject> itemModels: [
        NameDescModel { name: "Apple"; desc: "an apple" },
        NameDescModel { name: "Orange"; desc: "the orange" }
    ]
    property QtObject delegateCallbacks: QtObject{}
    property var source: (index) => {return "NameDescRow.qml"}
    property int colspacing: 10


    Repeater {
        id: myRepeater
        model: self.itemModels.length
        delegate: Item {
            id: myItem
            width: self.width
            height: childrenRect.height
            Loader {
                id: myLoader
                active: self.itemModels.length > 0
                width: parent.width
                source: self.source(index)
                property QtObject dataParam: self.itemModels[index]
            }

            Component.onCompleted: {
                Object.keys(delegateCallbacks).forEach((source) => {
                    if (source.length >= 2 && source.substring(0,2) == "on") {
                        var signalName = source.substring(2,3).toLowerCase() + source.substring(3, source.length)
                        myLoader.item[signalName].connect((...args)=>{delegateCallbacks[source](myLoader.item, index, ...args)})
                    }
                })

            }
        }
    }
}

