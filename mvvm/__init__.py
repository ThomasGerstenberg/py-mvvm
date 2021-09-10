import importlib
from . import _doc


Command = _doc.Command
Event = _doc.Event
ObservableCollection = _doc.ObservableCollection
Property = _doc.Property
ModelBase = _doc.ModelBase
ViewModelBase = _doc.ViewModelBase


FRAMEWORKS = [
    "pyside6",
    "pyqt6"
]


def pyside6():
    use("pyside6")


def pyqt6():
    use("pyqt6")


def use(framework: str):
    framework = framework.lower().strip()
    if framework not in FRAMEWORKS:
        raise ValueError(f"Unknown backend '{framework}'. "
                         f"Supported backends: {', '.join(FRAMEWORKS)}")
    module = importlib.import_module(f"._{framework}", __name__)
    _use(module)


def _use(module):
    global Command, Event, ObservableCollection, Property, ModelBase, ViewModelBase
    Command = module.Command
    Event = module.Event
    ObservableCollection = module.ObservableCollection
    Property = module.Property
    ModelBase = module.ModelBase
    ViewModelBase = module.ViewModelBase
