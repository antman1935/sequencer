import QtQuick 6.5
import QtQuick.Controls 6.5
import templates

import com.pyobjects.MathObjectScreenModel

ListPick {
    id: self
    default property alias content: self.children
    required property MathObjectScreenModel model;

    options: model?.options ?? []
    header: "Mathematical Object"
    
    onChoiceChanged: {
        model.choice = self.choice
    }
}