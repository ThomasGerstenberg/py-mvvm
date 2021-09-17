from __future__ import annotations
from typing import Generic, TypeVar, Any, List, Tuple, Union, Callable


T = TypeVar("T")


class ObservableCollection(Generic[T]):
    def __init__(self, initial_items: List[T] = None):
        raise NotImplementedError

    def __getitem__(self, item) -> T:
        pass

    def __len__(self):
        pass

    def __contains__(self, item):
        pass

    def __iter__(self):
        pass

    @property
    def items(self) -> List[T]:
        return []

    def append(self, item: T):
        pass

    def remove(self, item: T):
        pass

    def filter_remove(self, func):
        pass

    def insert(self, index: int, item: T):
        pass

    def extend(self, items: Union[List[T], Tuple[T]]):
        pass

    def replace(self, index: int, item: T):
        pass

    def clear(self):
        pass

    def reverse(self):
        pass


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


class Event(Generic[T]):
    def __init__(self, *types):
        raise NotImplementedError

    def __add__(self, callback) -> Event:
        pass

    def __sub__(self, callback) -> Event:
        pass

    def emit(self, *args):
        pass

    def raise_event(self, *args):
        pass

    def connect(self, callback):
        pass

    def disconnect(self, callback):
        pass


class Command:
    def __init__(self, *types, name: str = None, result: Any = None):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        pass


class ModelBase:
    def __init__(self, parent=None):
        raise NotImplementedError

    def _notify_property_changed(self, name=""):
        pass

    def _propagate_property_changed(self, source: ModelBase, source_property_name: str, target_property_name: str = None):
        pass

    def on_property_changed(self, name: str) -> Event:
        pass


class ViewModelBase(ModelBase):
    pass