from mvvm import ModelBase, Property, Event, ObservableCollection, Command
from example.models import TodoList, TodoItem


class TodoItemViewModel(ModelBase):
    def __init__(self, todo_item: TodoItem):
        super().__init__()
        self._item = todo_item
        self._propagate_property_changed(self._item, "text")
        self._propagate_property_changed(self._item, "is_complete")

    @Property(str)
    def text(self):
        return self._item.text

    @Property(bool)
    def is_complete(self):
        return self._item.is_complete

    @is_complete.setter
    def is_complete(self, value):
        self._item.is_complete = value


class TodoListViewModel(ModelBase):
    def __init__(self, todo_list: TodoList):
        super().__init__()
        self._text_entry = ""
        self._todo_list = todo_list
        self._todo_list.todo_item_added.connect(self._item_added)
        self._todo_items = ObservableCollection()

    def _item_added(self, item: TodoItem):
        self._todo_items.append(TodoItemViewModel(item))

    @Property(str)
    def text_entry(self):
        return self._text_entry

    @text_entry.setter
    def text_entry(self, value):
        if self._text_entry == value:
            return
        self._text_entry = value
        self._notify_property_changed()

    @Property(ModelBase)
    def todo_items(self):
        return self._todo_items

    @Command()
    def add_todo_item(self):
        self._todo_list.add_todo_item(self._text_entry)
        self.text_entry = ""
