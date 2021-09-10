import contextlib
import inspect
from PySide6 import QtCore, QtQml

from mvvm import _qt_common

_qml_registered_types = []


def _qml_register_type(t):
    if isinstance(t, type) and issubclass(t, QtCore.QObject) and t not in _qml_registered_types:
        _qml_registered_types.append(t)
        QtQml.qmlRegisterType(t, t.__module__, 1, 0, t.__name__)


# QAbstractListModel can't find methods in ObservableCollectionBase unless it's defined first
class ObservableCollection(_qt_common.ObservableCollectionBase, QtCore.QAbstractListModel):
    _MODELDATA_ROLE = QtCore.Qt.UserRole + 1
    _DISPLAY_ROLE = QtCore.Qt.DisplayRole
    _MODELDATA_NAME = QtCore.QByteArray(b"modelData")

    def __init__(self, initial_items=None):
        super(ObservableCollection, self).__init__(initial_items)
        # Explicit initialization of the second base class
        QtCore.QAbstractListModel.__init__(self)

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


Command = QtCore.Slot
Event = QtCore.Signal
Property = _qt_common.Property

_qt_common.add_event_mixins(QtCore.SignalInstance)


class ModelMeta(type(QtCore.QObject)):
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
                    attrs[key] = QtCore.Property(value.type, fget=value.fget, fset=value.fset, constant=True)
                else:
                    signal = QtCore.Signal()
                    signal_name = f"_{key}_property_signal"
                    attrs[signal_name] = signal
                    attrs[key] = QtCore.Property(value.type, fget=value.fget, fset=value.fset, notify=signal)
                if should_register_type:
                    _qml_register_type(value.type)
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, dct):
        super(ModelMeta, cls).__init__(name, bases, dct)
        if cls._should_register_type(dct, bases):
            _qml_register_type(cls)


class ModelBase(QtCore.QObject, metaclass=ModelMeta):
    _qml_register_type = False

    def __init__(self, parent=None):
        super().__init__(parent)

    def __get_signal(self, name) -> QtCore.SignalInstance:
        signal = getattr(self, f"_{name}_property_signal", None)
        if signal:
            return signal
        raise AttributeError(f"{self.__class__.__name__} has no property named {name}")

    def _notify_property_changed(self, name=""):
        if not name:
            name = inspect.stack()[1][3]
        self.__get_signal(name).emit()

    def _propagate_property_changed(self, source, source_property_name, target_property_name=None):
        if not target_property_name:
            target_property_name = source_property_name

        def handler(*args, **kwargs):
            self._notify_property_changed(target_property_name)
        source.on_property_changed(source_property_name).connect(handler)

    def on_property_changed(self, name):
        return self.__get_signal(name)


class ViewModelBase(ModelBase):
    _qml_register_type = True


_qml_register_type(ObservableCollection)
_qml_register_type(QtCore.QAbstractListModel)
_qml_register_type(ModelBase)
