# Python MVVM Library

Library for creating GUI applications in python using MVVM pattern.

Initially starting with Qt/QML where Models/Viewmodels are in python, Views in QML.
Can also be used with QtWidgets, only difference is the View would also be python.

Paradigms will be similar to C#/WPF with methods like `notify_property_changed()` 
and classes like `ObservableCollection`

Initial example/implementation works with PySide6 and PyQt6

### Goals

- Model/ViewModel code should be reusable with any UI frontend (QtWidgets, QML, TKinter, Kivy, etc.)
- Standardized API for usage (e.g. Signals/Slots are Qt-specific so abstract to Event/Command)
- Support several UI frameworks. Qt will be focused on first and refined before adding others
