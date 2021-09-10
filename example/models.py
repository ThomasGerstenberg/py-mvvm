from mvvm import ModelBase, Property, Event


class TodoItem(ModelBase):
    def __init__(self, text: str, is_complete=False):
        super().__init__()
        self._text = text
        self._is_complete = is_complete

    @Property(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self._notify_property_changed()

    @Property(bool)
    def is_complete(self):
        return self._is_complete

    @is_complete.setter
    def is_complete(self, value):
        if self._is_complete == value:
            return
        self._is_complete = value
        self._notify_property_changed()


class TodoList(ModelBase):
    todo_item_added = Event(TodoItem)

    def __init__(self, items=None):
        super().__init__()
        self._items = items or []

    @property
    def items(self):
        return self._items

    def add_todo_item(self, text):
        item = TodoItem(text)
        self._items.append(item)
        self.todo_item_added.raise_event(item)
