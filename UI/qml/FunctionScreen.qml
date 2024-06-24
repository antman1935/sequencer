import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.FunctionScreenModel

ListPick {
    id: self
    default property alias content: self.children
    required property FunctionScreenModel model;

    options: self.model?.options ?? []
    header: "Function"
    defaultName: "Count"
    
    onChoiceChanged: {
        model.choice = self.choice
    }
}