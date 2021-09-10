import sys
import os

backend = "pyqt6"

if backend == "pyqt6":
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QGuiApplication
    from PyQt6.QtQml import QQmlApplicationEngine
elif backend == "pyside6":
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
else:
    raise ImportError("Unknown backend")

import mvvm
mvvm.use(backend)  # Must be called before importing modules which use the library

from example.models import TodoList
from example.viewmodels import TodoListViewModel


def main():
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

    # Create the app and engine
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)

    # Get the QML file URL
    qml_file = os.path.join(os.path.dirname(__file__), "App.qml")
    app_qml = QUrl.fromLocalFile(qml_file)

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
    app.exec()


if __name__ == '__main__':
    main()
