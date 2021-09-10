import importlib
from . import _doc


Command = _doc.Command
Event = _doc.Event
ObservableCollection = _doc.ObservableCollection
Property = _doc.Property
ModelBase = _doc.ModelBase
ViewModelBase = _doc.ViewModelBase


FRAMEWORKS = [
    "pyside2",
    "pyside6",
    "pyqt5",
    "pyqt6"
]

current_framework = None


def pyside2():
    use("pyside2")


def pyside6():
    use("pyside6")


def pyqt5():
    use("pyqt5")


def pyqt6():
    use("pyqt6")


def use(framework: str):
    global current_framework
    framework = framework.lower().strip()

    if current_framework:
        if current_framework != framework:
            raise RuntimeError(f"MVVM framework already set to {current_framework}. Cannot change")
        return  # Already set, don't need to do anything else

    if framework not in FRAMEWORKS:
        raise ValueError(f"Unknown backend '{framework}'. "
                         f"Supported backends: {', '.join(FRAMEWORKS)}")

    current_framework = framework
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
