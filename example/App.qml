import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 600
    height: 600
    title: "MVVM Example"

    ColumnLayout {
        anchors.margins: 5
        anchors.fill: parent

        RowLayout {

            Label {
                text: "To-do Item:"
            }

            TextField {
                id: textInput
                Layout.fillWidth: true

                text: vm.text_entry
                onEditingFinished: vm.text_entry = text
                onAccepted: vm.add_todo_item()
            }

            Button {
                text: "Add to List"

                onClicked: {
                    vm.add_todo_item();
                    textInput.focus = true;
                }
                enabled: textInput.text != ""
            }
        }

        ListView {
            model: vm.todo_items
            spacing: 0
            Layout.fillHeight: true

            delegate: Component {
                RowLayout {
                    CheckBox {
                        checked: modelData.is_complete
                        onToggled: modelData.is_complete = checked;
                    }
                    Label {
                        text: modelData.text
                        opacity: modelData.is_complete ? 0.5 : 1.0
                        font.strikeout: modelData.is_complete
                    }
                }
            }
        }
    }
}