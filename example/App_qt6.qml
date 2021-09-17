import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

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
                text: "To-do Item"
            }

            TextField {
                id: textInput
                Layout.fillWidth: true

                text: vm.text_entry
                onEditingFinished: vm.text_entry = text
                onAccepted: vm.add_todo_item()
            }

            Button {
                text: "Add"

                onClicked: {
                    vm.add_todo_item();
                    textInput.focus = true;
                }
                enabled: textInput.text != ""
            }
        }
        ScrollView {
            Layout.fillHeight: true
            Layout.fillWidth: true
            ScrollBar.vertical.policy: ScrollBar.AlwaysOn
            contentWidth: flickableContent.width
            contentHeight: flickableContent.height
            clip: true

            ColumnLayout {
                id: flickableContent

                ListView {
                    implicitHeight: contentItem.childrenRect.height
                    model: vm.todo_items
                    spacing: -10
                    delegate: todoItemDelegate
                }
                RowLayout {
                    Label {
                        text: "Completed"
                        font.bold: true
                    }
                    Button {
                        text: "Clear"
                        background: Rectangle {
                            opacity: 0
                        }
                        onClicked: vm.clear_completed()
                        Material.foreground: Material.accent
                    }
                }
                ListView {
                    model: vm.completed_items
                    implicitHeight: contentItem.childrenRect.height
                    spacing: -10
                    delegate: todoItemDelegate
                }
            }
        }

        Component {
            id: todoItemDelegate
            RowLayout {
                CheckBox {
                    checked: modelData.is_complete
                    onToggled: modelData.is_complete = checked;
                    text: modelData.text
                    opacity: modelData.is_complete ? 0.5 : 1.0
                    font.strikeout: modelData.is_complete
                }
            }
        }
    }
    Component.onCompleted: textInput.focus = true
}