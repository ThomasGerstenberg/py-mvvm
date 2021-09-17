from __future__ import annotations
import contextlib
import inspect
import mvvm

if mvvm.current_framework.startswith("pyside"):
    version = mvvm.current_framework[-1]
    if version == "6":
        from PySide6 import QtCore, QtQml
    elif version == "2":
        from PySide2 import QtCore, QtQml
    else:
        raise RuntimeError("Unknown framework trying to use QtCommon")

    model_data_role = QtCore.Qt.UserRole + 1
    display_role = QtCore.Qt.DisplayRole
    QtProperty = QtCore.Property
    QtSignal = QtCore.Signal
    QtBoundSignal = QtCore.SignalInstance
    QtSlot = QtCore.Slot
elif mvvm.current_framework.startswith("pyqt"):
    version = mvvm.current_framework[-1]

    if version == "6":
        from PyQt6 import QtCore, QtQml
    elif version == "5":
        from PyQt5 import QtCore, QtQml
    else:
        raise RuntimeError("Unknown framework trying to use QtCommon")

    model_data_role = QtCore.Qt.ItemDataRole.UserRole + 1
    display_role = QtCore.Qt.ItemDataRole.DisplayRole
    QtProperty = QtCore.pyqtProperty
    QtSignal = QtCore.pyqtSignal
    QtBoundSignal = QtCore.pyqtBoundSignal
    QtSlot = QtCore.pyqtSlot
else:
    raise RuntimeError("Unknown framework trying to use QtCommon")


qml_registered_types = []


def qml_register_type(t):
    if isinstance(t, type) and issubclass(t, QtCore.QObject) and t not in qml_registered_types:
        qml_registered_types.append(t)
        QtQml.qmlRegisterType(t, t.__module__, 1, 0, t.__name__)


def _raise_event(self, *args, **kwargs):
    self.emit(*args, **kwargs)


def _add_handler(self, *args, **kwargs):
    self.connect(*args, **kwargs)
    return self


def _sub_handler(self, *args, **kwargs):
    self.disconnect(*args, **kwargs)
    return self


def add_event_mixins(cls: type):
    cls.raise_event = _raise_event
    cls.__add__ = _add_handler
    cls.__sub__ = _sub_handler


add_event_mixins(QtBoundSignal)


class QtObservableCollectionBase(QtCore.QAbstractListModel):
    _MODELDATA_ROLE = model_data_role
    _DISPLAY_ROLE = display_role
    _MODELDATA_NAME = QtCore.QByteArray(b"modelData")

    def __init__(self, initial_items=None):
        super().__init__()
        self._items = initial_items or []

    def __getitem__(self, item):
        return self._items[item]

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item in self._items

    def __iter__(self):
        return self._items

    @contextlib.contextmanager
    def _insert_context(self, start, end):
        try:
            self.beginInsertRows(QtCore.QModelIndex(), start, end)
            yield
        finally:
            self.endInsertRows()

    @contextlib.contextmanager
    def _remove_context(self, start, end):
        try:
            self.beginRemoveRows(QtCore.QModelIndex(), start, end)
            yield
        finally:
            self.endRemoveRows()

    @contextlib.contextmanager
    def _item_update_context(self, index):
        idx = self.createIndex(index, 0)
        try:
            yield
        finally:
            self.dataChanged.emit(idx, idx)

    @contextlib.contextmanager
    def _reset_model_context(self):
        try:
            self.beginResetModel()
            yield
        finally:
            self.endResetModel()

    @property
    def items(self):
        return self._items

    def roleNames(self):
        return {self._MODELDATA_ROLE: self._MODELDATA_NAME}

    def data(self, index, role=_MODELDATA_ROLE):
        if role not in [self._DISPLAY_ROLE, self._MODELDATA_ROLE]:
            return None

        i = index.row()
        if 0 <= i < len(self._items):
            return self._items[i]

    def rowCount(self, parent=None):
        return len(self._items)

    def append(self, item):
        size = len(self._items)
        with self._insert_context(size, size):
            self._items.append(item)

    def remove(self, item):
        idx = self._items.index(item)
        with self._remove_context(idx, idx):
            self._items.remove(item)

    def filter_remove(self, func):
        with self._reset_model_context():
            items_to_remove = list(filter(func, self._items))
            for item in items_to_remove:
                self._items.remove(item)
            return items_to_remove

    def at(self, index):
        return self._items[index]

    def insert(self, index, item):
        with self._insert_context(index, index):
            self._items.insert(index, item)

    def extend(self, items):
        start = len(self._items)
        size = len(items)
        with self._insert_context(start, start+size-1):
            self._items.extend(items)

    def replace(self, index, item):
        with self._item_update_context(index):
            self._items[index] = item

    def clear(self):
        with self._reset_model_context():
            self._items = []

    def reverse(self):
        with self._reset_model_context():
            self._items.reverse()


class Property(property):
    def __init__(self, type_=None, fget=None, fset=None, fdel=None, doc=None, constant=False):
        self.type = type_
        self.constant = constant
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

    def __call__(self, fget=None, fset=None, fdel=None, doc=None):
        super(Property, self).__init__(fget, fset, fdel, doc)
        return self

    def getter(self, fget):
        return self.__class__(self.type, fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return self.__class__(self.type, self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return self.__class__(self.type, self.fget, self.fset, fdel, self.__doc__)


class QtModelMeta(type(QtCore.QObject)):
    @staticmethod
    def _should_register_type(class_dict, bases):
        result = class_dict.get("_qml_register_type", None)
        if result is None:
            result = any(getattr(b, "_qml_register_type", False) for b in bases)
        return result

    def __new__(cls, name, bases, attrs):
        should_register_type = cls._should_register_type(attrs, bases)

        for key in tuple(attrs.keys()):
            value = attrs[key]
            if isinstance(value, Property):
                if value.constant:
                    attrs[key] = QtProperty(value.type, fget=value.fget, fset=value.fset, constant=True)
                else:
                    signal = QtSignal()
                    signal_name = f"_{key}_property_signal"
                    attrs[signal_name] = signal
                    attrs[key] = QtProperty(value.type, fget=value.fget, fset=value.fset, notify=signal)
                if should_register_type:
                    qml_register_type(value.type)
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, dct):
        super(QtModelMeta, cls).__init__(name, bases, dct)
        if cls._should_register_type(dct, bases):
            qml_register_type(cls)


class QtModelBase(QtCore.QObject, metaclass=QtModelMeta):
    _qml_register_type = False

    def __init__(self, parent=None):
        super().__init__(parent)

    def __get_signal(self, name) -> QtCore.pyqtBoundSignal:
        signal = getattr(self, f"_{name}_property_signal", None)
        if signal:
            return signal
        raise AttributeError(f"{self.__class__.__name__} has no property named {name}")

    def _notify_property_changed(self, name=""):
        if not name:
            name = inspect.stack()[1][3]
        self.__get_signal(name).emit()

    def _propagate_property_changed(self, source: QtModelBase, source_property_name, target_property_name=None):
        if not target_property_name:
            target_property_name = source_property_name

        def handler(*args, **kwargs):
            self._notify_property_changed(target_property_name)
        source.on_property_changed(source_property_name).connect(handler)

    def on_property_changed(self, name):
        return self.__get_signal(name)


qml_register_type(QtCore.QAbstractListModel)
qml_register_type(QtObservableCollectionBase)
