from mvvm import _qt_common


Command = _qt_common.QtSlot
Event = _qt_common.QtSignal
Property = _qt_common.Property


class ObservableCollection(_qt_common.QtObservableCollectionBase):
    pass


class ModelBase(_qt_common.QtModelBase):
    pass


class ViewModelBase(ModelBase):
    _qml_register_type = True


_qt_common.qml_register_type(ObservableCollection)
_qt_common.qml_register_type(ModelBase)
