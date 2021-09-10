import sys
import os

framework = "pyside6"

if framework == "pyqt5":
    from PyQt5 import QtCore, QtGui, QtQml
elif framework == "pyqt6":
    from PyQt6 import QtCore, QtGui, QtQml
elif framework == "pyside2":
    from PySide2 import QtCore, QtGui, QtQml
elif framework == "pyside6":
    from PySide6 import QtCore, QtGui, QtQml
else:
    raise ImportError("Unknown framework")

import mvvm
mvvm.use(framework)  # Must be called before importing modules which use the library

from example.models import TodoList
from example.viewmodels import TodoListViewModel


def main():
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

    # Create the app and engine
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    engine.quit.connect(app.quit)

    # Get the QML file URL
    qt_version = 6 if framework in ["pyside6", "pyqt6"] else 5
    qml_file = os.path.join(os.path.dirname(__file__), f"App_qt{qt_version}.qml")
    app_qml = QtCore.QUrl.fromLocalFile(qml_file)

    # Create the model and viewmodel
    todo_list = TodoList()
    todo_list_vm = TodoListViewModel(todo_list)

    # Add the viewmodel as a context to the QML
    engine.rootContext().setContextProperty("vm", todo_list_vm)

    # Load the QML
    engine.load(app_qml)
    if not engine.rootObjects():
        raise RuntimeError("Failed to create QML!")

    # Run the app!
    if framework == "pyside2":
        app.exec_()  # Pyside2 doesn't have exec()
    else:
        app.exec()


if __name__ == '__main__':
    main()
