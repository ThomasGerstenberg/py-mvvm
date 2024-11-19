import uuid
from mvvm import ModelBase, Property, Event


class TodoItem(ModelBase):
    def __init__(self, text: str, is_complete=False):
        super().__init__()
        self._id = uuid.uuid4()
        self._text = text
        self._is_complete = is_complete

    def __repr__(self):
        return f"TodoItem(is_complete={self._is_complete}, text={self._text})"

    @Property(uuid.UUID)
    def id(self) -> uuid.UUID:
        return self._id

    @Property(str)
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if self._text == value:
            return
        self._text = value
        self._notify_property_changed()

    @Property(bool)
    def is_complete(self) -> bool:
        return self._is_complete

    @is_complete.setter
    def is_complete(self, value: bool):
        if self._is_complete == value:
            return
        self._is_complete = value
        self._notify_property_changed()


class TodoList(ModelBase):
    todo_item_added = Event(TodoItem)
    items_removed = Event(list)

    def __init__(self, items: list[TodoItem] = None):
        super().__init__()
        self._items = items or []

    @property
    def items(self) -> list[TodoItem]:
        return self._items

    def add_todo_item(self, text: str):
        item = TodoItem(text)
        self._items.append(item)
        self.todo_item_added.raise_event(item)

    def clear_completed(self):
        completed_items = list(filter(lambda x: x.is_complete, self._items))
        for item in completed_items:
            self._items.remove(item)
        self.items_removed.raise_event(completed_items)
