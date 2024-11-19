import uuid
from typing import List

from mvvm import ModelBase, ViewModelBase, Property, Event, ObservableCollection, Command
from example.models import TodoList, TodoItem


class TodoItemViewModel(ViewModelBase):
    def __init__(self, todo_item: TodoItem):
        super().__init__()
        self._item = todo_item
        # General pattern for pass-through viewmodel properties
        # Essentially links the model's property change to the viewmodel property changed
        self._propagate_property_changed(self._item, "text")
        self._propagate_property_changed(self._item, "is_complete", "is_complete")  # third arg defaults to the other property name

    @Property(uuid.UUID)
    def id(self) -> uuid.UUID:
        return self._item.id

    @Property(str)
    def text(self) -> str:
        return self._item.text

    @Property(bool)
    def is_complete(self) -> bool:
        return self._item.is_complete

    @is_complete.setter
    def is_complete(self, value: bool):
        self._item.is_complete = value


class TodoListViewModel(ViewModelBase):
    def __init__(self, todo_list: TodoList):
        super().__init__()
        self._text_entry = ""
        self._todo_list = todo_list
        self._todo_list.todo_item_added.connect(self._item_added)
        self._todo_list.items_removed.connect(self._items_removed)
        self._todo_items = ObservableCollection()
        self._completed_items = ObservableCollection()

    def _item_added(self, item: TodoItem):
        print("Item Added")
        item_viewmodel = TodoItemViewModel(item)

        if item.is_complete:
            self._completed_items.append(item_viewmodel)
            self._notify_property_changed("completed_items")
        else:
            self._todo_items.append(item_viewmodel)
            self._notify_property_changed("todo_items")

        # Register for whenever the item is completed to move it to the corresponding list
        def on_completed():
            if item_viewmodel.is_complete:
                if item_viewmodel in self._todo_items:
                    self._todo_items.remove(item_viewmodel)
                self._completed_items.append(item_viewmodel)
            else:
                if item_viewmodel in self._completed_items:
                    self._completed_items.remove(item_viewmodel)
                self._todo_items.append(item_viewmodel)
        item_viewmodel.on_property_changed("is_complete").connect(on_completed)

    def _items_removed(self, items: List[TodoItem]):
        # Sort the IDs for the correct list
        todo_ids = []
        completed_ids = []
        for item in items:
            lst = completed_ids if item.is_complete else todo_ids
            lst.append(item.id)

        if todo_ids:
            self._todo_items.filter_remove(lambda item: item.id in todo_ids)
        if completed_ids:
            self._completed_items.filter_remove(lambda item: item.id in completed_ids)

    @Property(str)
    def text_entry(self) -> str:
        return self._text_entry

    @text_entry.setter
    def text_entry(self, value: str):
        if self._text_entry == value:
            return
        self._text_entry = value
        self._notify_property_changed()

    @Property(ObservableCollection)  # TODO: Why doesn't ObservableCollection work here for pyside6??
    def todo_items(self) -> ObservableCollection[TodoItemViewModel]:
        return self._todo_items

    @Property(ObservableCollection)
    def completed_items(self) -> ObservableCollection[TodoItemViewModel]:
        return self._completed_items

    @Command()
    def add_todo_item(self):
        print(f"Adding {self._text_entry}")
        self._todo_list.add_todo_item(self._text_entry)
        self.text_entry = ""

    @Command()
    def clear_completed(self):
        self._todo_list.clear_completed()
