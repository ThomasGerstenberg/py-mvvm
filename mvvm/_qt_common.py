import contextlib


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


class ObservableCollectionBase:
    _MODELDATA_ROLE = 0
    _DISPLAY_ROLE = 0
    _MODELDATA_NAME = b''

    def __init__(self, initial_items=None):
        self._items = initial_items or []

    @contextlib.contextmanager
    def _insert_context(self, start, end):
        raise NotImplementedError

    @contextlib.contextmanager
    def _remove_context(self, start, end):
        raise NotImplementedError

    @contextlib.contextmanager
    def _item_update_context(self, index):
        raise NotImplementedError

    @contextlib.contextmanager
    def _reset_model_context(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self._items[item]

    def __len__(self):
        return len(self._items)

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
