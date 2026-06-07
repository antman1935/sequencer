# UI Platform Audit

## Binding And Environment Baseline

The verified Qt binding in this repository is PySide6. The provisional platform plan referred to an expected PyQt6 direction, but the inspected UI source does not contain PyQt6 imports. The current implementation consistently imports PySide6 from the active launcher, generated resource file, Python QML models, and custom component models.

Concrete binding evidence:

- `UI/main.py` imports `QObject`, `Slot`, `QUrl`, `QCoreApplication`, and `Qt` from `PySide6.QtCore`; `QGuiApplication` from `PySide6.QtGui`; `QQmlApplicationEngine` and `QmlElement` from `PySide6.QtQml`; and `QQuickStyle` from `PySide6.QtQuickControls2`.
- `UI/main.py` constructs `QGuiApplication(sys.argv)`, constructs `QQmlApplicationEngine()`, and exposes the Python UI manager to QML with `engine.rootContext().setContextProperty("myModel", model)`.
- `UI/style_rc.py` is generated resource code from the Qt resource compiler and imports `QtCore` with `from PySide6 import QtCore`.
- `UI/qml/UIManager.py` imports `QObject`, `Property`, `Signal`, and `Slot` from `PySide6.QtCore`, imports `QmlElement` from `PySide6.QtQml`, declares `@QmlElement`, exposes `@Property(...)` values with notify signals, and exposes command methods with `@Slot()`.
- `UI/qml/*Model.py` files use PySide6 QML exposure patterns. The inspected model files import `QmlElement`, and most import `QObject`, `Property`, and `Signal` from `PySide6.QtCore`.
- `UI/CustomComponents/python/*Model.py` files also use PySide6. `NameDescModel.py`, `ParameterModel.py`, and `ParameterSetModel.py` define `QObject` subclasses with `@QmlElement`, `@Property(...)`, and notify `@Signal` declarations.

Current QML screens and templates use Qt Quick/QML 6.5 imports. The active files under `UI/qml/*.qml` import `QtQuick 6.5`; all active screen files except `App.qml` also import `QtQuick.Controls 6.5`. The custom templates under `UI/CustomComponents/templates/*.qml` import `QtQuick 6.5`, and templates with controls import `QtQuick.Controls 6.5`.

`UI/view.qml` is different from the active QML 6.5 screen set. It imports `QtQuick 2.0`, `QtQuick.Layouts 1.11`, `QtQuick.Controls 2.1`, `QtQuick.Window 2.1`, and `QtQuick.Controls.Material 2.1`, and appears to be an older sample-style artifact rather than part of the `UI/main.py` launch path.

The project-level Python version remains unresolved from repository metadata. The inspected metadata search found no `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile`, `poetry.lock`, `environment.yml`, or `tox.ini` in the repository search depth used for this audit task. Local environment evidence is available: both `python --version` and `python3 --version` reported `Python 3.14.4`.

## Lifecycle And Pain Points

This section records audit observations only. It does not propose or begin a migration.

- mutable default constructor arguments appear in several QObject-backed models. `UI/qml/APIRangeModel.py` defaults `dimension_options` and `chosen_dimensions` to `[]`; `UI/qml/RestrictionScreenModel.py` defaults `restrictions`, `restrictionParameters`, and `restrictionGroups` to `[]`; `UI/qml/RestrictionGroupModel.py` defaults `restrictions` to `[]`; and `UI/CustomComponents/python/ParameterSetModel.py` defaults `parameters` to `[]`. These defaults can share list instances across model objects if constructors are called without explicit lists.
- `UI/main.py` creates the `UIManager` instance with `makeManager()` and exposes it to QML as the root context property `myModel`. `UI/qml/Main.qml` then stores `property UIManager manager: myModel`. Ownership and lifetime are therefore tied to the Python local `model`, the QQmlApplicationEngine root context, and QML references; the code does not document an explicit ownership or cleanup contract for that context property.
- `UI/CustomComponents/templates/ColumnLoader.qml` dynamically loads delegates with `Loader` and connects callback objects in `Component.onCompleted` by scanning `delegateCallbacks` keys like `onDeleted`. The connection is made with `myLoader.item[signalName].connect(...)`, and no matching disconnect path is present in the inspected template.
- QML mutates list-like model properties in place. `APIRangeScreen.qml` uses `model.chosen_dimensions.push(...)` and `splice(...)`; `RestrictionScreenModel.createNewGroup()` appends to `_restrictionGroups`; `RestrictionGroup.qml` pushes new `ParameterSetModel` objects into `model.restrictions`, calls `destroy()` on deleted restriction items, and splices them from the list. These mutations can bypass Python property setters and their notify signals unless the specific code path emits a signal separately.
- `UI/CustomComponents/python/ParameterModel.py` stores all parameter values as strings. String parameters start as `""`, while boolean parameters start as `"false"` and are updated from `BooleanParameter.qml` with string values `"true"` or `"false"`. `StringParameter.qml` and `BooleanParameter.qml` both use QML `Binding` blocks to write `ParameterModel.value`.
- `RestrictionScreenModel` group mutation is manual. `createNewGroup()` appends a new `RestrictionGroupModel` and emits `restrictionGroups_changed`, while nested restriction additions and removals are performed in QML through dynamic `ParameterSetModel` and `ParameterModel` object creation.
- `UIManager.collectQuery()` performs validation and command-string assembly. It checks required command parameters, required restriction parameters, and range API dimensions, skips blank optional parameters, builds restriction groups, prints a CLI-like command string, and returns a structured query dictionary.
- `UIManager.runQuery()` is side-effectful local execution. It calls `collectQuery()`, looks up `Command`, `SequencerAPI`, `Statistic`, and `Restriction` registrations, instantiates the selected API and command, applies restrictions and statistic selection, and calls `api_inst.execute()`.
- `APIScreen.qml` builds `paramOptions` by creating `NameDescModel` QML objects from the current command parameters with `param.createObject(range, {name: item.name, desc: item.desc, key: item.name + "-p"})`. This creates transient QML-owned objects derived from Python-backed parameter models.
- The inspected UI search found no `QTimer`, QML `Timer`, `QThread`, Python `threading`, `asyncio`, `async`, multiprocessing, or other background-work wiring in the UI files. No timer or background cleanup behavior was identified in the inspected UI path.

## External-Service And Trading Safety

The inspected repository source did not show trading behavior. Searches for trading-related terms found only license text references to trademark/trade-name language, not application behavior, order submission, broker integration, market access, or account-data handling.

The inspected repository source did not show credential, account, external-service, or network behavior. Searches for `credential`, `account`, `broker`, `requests`, `urllib`, `http`, `socket`, `token`, `password`, and `secret` found no application code paths for storing credentials, contacting external services, making network requests, or reading account data. The only network-like references found were documentation or license text, such as README example links and GNU license URLs.

`UIManager.runQuery()` should still be treated as a side-effectful local execution path during audit work. It invokes `collectQuery()`, creates local `SequencerAPI`, `Command`, and optional `Statistic` objects, and calls `api_inst.execute()`. Implementation and verification for this audit node should not invoke `runQuery()`, `api_inst.execute()`, or other live execution paths.
