# Wiring Map

This map documents the current Python-to-QML state flow for the Qt Quick UI. It is limited to observed repository behavior and does not change runtime code.

## Launcher To Root Context

`UI/main.py` is the active UI launcher. In its `__main__` block it:

1. Creates a `QGuiApplication` from `sys.argv`.
2. Creates a `QQmlApplicationEngine`.
3. Adds `UI/CustomComponents` as a QML import path through `engine.addImportPath(os.fspath(LIBRARY_DIR))`; this exposes the `templates` module used by QML screens and custom components.
4. Calls `makeManager()` from `qml.UIManager` to build the top-level `UIManager` object and its child screen models.
5. Stores that object in the QML root context as `myModel` with `engine.rootContext().setContextProperty("myModel", model)`.
6. Builds a `QUrl` for `UI/qml/App.qml`, connects `engine.objectCreated` to an error handler, loads the URL, checks `engine.rootObjects()`, then starts the Qt event loop with `app.exec()`.

`UI/qml/App.qml` imports `QtQuick 6.5` and `templates`, creates the top-level `Window`, and instantiates `Main`.

`UI/qml/Main.qml` imports `QtQuick 6.5`, `QtQuick.Controls 6.5`, `templates`, and `com.pyobjects.UIManager`. It declares:

```qml
property UIManager manager: myModel
```

That declaration is the bridge from the Python context property to the QML screen tree.

## UIManager Screen Model Fanout

`UI/qml/UIManager.py` defines `UIManager(QObject)` with typed `Property` accessors and notify `Signal` methods for each screen model. `Main.qml` fans those properties out to the screen components:

| UIManager property | Python model type | QML receiver | QML assignment |
| --- | --- | --- | --- |
| `manager.object` | `MathObjectScreenModel` | `MathObjectScreen` | `model: manager?.object ?? null` |
| `manager.parameters` | `ParameterScreenModel` | `ParameterScreen` | `model: manager?.parameters ?? null` |
| `manager.apis` | `APIScreenModel` | `APIScreen` | `model: manager?.apis ?? null` |
| `manager.functions` | `FunctionScreenModel` | `FunctionScreen` | `model: manager?.functions ?? null` |
| `manager.restrictions` | `RestrictionScreenModel` | `RestrictionScreen` | `model: manager?.restrictions ?? null` |

`APIScreen` also receives the currently visible command parameters from `ParameterScreen` with `parameters: parameterScreen.getCurrentParameters()`.

## Python Model Exposure

The Python UI layer exposes QML-facing state with `QObject` subclasses decorated by `@QmlElement`. Properties use PySide6 `Property(..., notify=...)` declarations paired with notify `Signal` methods.

Top-level model properties:

| File | Exposed data |
| --- | --- |
| `UI/qml/UIManager.py` | Object-typed properties for `object`, `parameters`, `apis`, `functions`, and `restrictions`. |
| `UI/qml/MathObjectScreenModel.py` | `options` as `QVariantList`; `choice` as `str`. |
| `UI/qml/ParameterScreenModel.py` | `parameters` as `QVariantMap`; `key` as `str`. |
| `UI/qml/APIScreenModel.py` | `api` as `str`; `apis` as `QVariantList`; `api_models` as `QVariantMap`. |
| `UI/qml/APIRangeModel.py` | `chosen_dimensions` and `dimension_options` as `QVariantList`. |
| `UI/qml/FunctionScreenModel.py` | `options` as `QVariantList`; `choice` as `str`. |
| `UI/qml/RestrictionScreenModel.py` | `restrictions`, `restrictionParameters`, and `restrictionGroups` as `QVariantList`. |
| `UI/qml/RestrictionGroupModel.py` | `restrictions` as `QVariantList`. |
| `UI/CustomComponents/python/NameDescModel.py` | `name`, `desc`, and `key` as `str`; `selected` as `bool`. |
| `UI/CustomComponents/python/ParameterModel.py` | `name`, `desc`, `value`, and `type` as `str`; `require` as `bool`. |
| `UI/CustomComponents/python/ParameterSetModel.py` | `descriptor` as `NameDescModel`; `parameters` as `QVariantList`. |

The collection-heavy surfaces are therefore plain `QVariantList` and `QVariantMap` properties rather than Qt item models.

## QML Imports

Active QML screens import the generated Python model modules with `com.pyobjects.*` names:

| QML file | Python model imports |
| --- | --- |
| `UI/qml/Main.qml` | `com.pyobjects.UIManager` |
| `UI/qml/MathObjectScreen.qml` | `com.pyobjects.MathObjectScreenModel` |
| `UI/qml/ParameterScreen.qml` | `com.pyobjects.ParameterScreenModel` |
| `UI/qml/APIScreen.qml` | `com.pyobjects.ParameterModel`, `com.pyobjects.NameDescModel`, `com.pyobjects.APIScreenModel` |
| `UI/qml/APIPointScreen.qml` | `com.pyobjects.APIPointModel` |
| `UI/qml/APIRangeScreen.qml` | `com.pyobjects.NameDescModel`, `com.pyobjects.APIRangeModel` |
| `UI/qml/FunctionScreen.qml` | `com.pyobjects.FunctionScreenModel` |
| `UI/qml/RestrictionScreen.qml` | `com.pyobjects.RestrictionScreenModel`, `com.pyobjects.RestrictionGroupModel` |
| `UI/qml/RestrictionGroup.qml` | `com.pyobjects.RestrictionGroupModel`, `com.pyobjects.ParameterModel`, `com.pyobjects.ParameterSetModel` |

The active screens also import the local `templates` module made available by `engine.addImportPath(UI/CustomComponents)`. Template files then import the model types they render:

| Template file | Python model imports |
| --- | --- |
| `ParameterScroll.qml` | `com.pyobjects.ParameterModel` |
| `StringParameter.qml` | `com.pyobjects.ParameterModel 1.0` |
| `BooleanParameter.qml` | `com.pyobjects.ParameterModel 1.0` |
| `ParameterSet.qml` | `com.pyobjects.ParameterSetModel` |
| `ScrollLoader.qml` | `com.pyobjects.NameDescModel 1.0` |
| `ClickAndScroll.qml` | `com.pyobjects.NameDescModel 1.0` |
| `ColumnLoader.qml` | `com.pyobjects.NameDescModel 1.0` |
| `NameDesc.qml` | `com.pyobjects.NameDescModel 1.0` |

`ListPick.qml` imports `templates` because it composes `ClickAndScroll`, `Constants`, and related custom components.

## QML To Python Mutations

The UI sends state back into Python model objects through direct property writes, QML `Binding` blocks, and in-place mutation of Python-exposed `QVariantList` values. This is separate from the Python-to-QML exposure above: Python creates and exposes the object graph, while the following QML handlers mutate the exposed objects.

| User action or QML event | QML source | Python-facing mutation |
| --- | --- | --- |
| Mathematical object selection changes | `UI/CustomComponents/templates/ListPick.qml` updates `choice` from `options[selectedIndex].key`; `UI/qml/MathObjectScreen.qml` handles `onChoiceChanged` | `MathObjectScreenModel.choice` is assigned with `model.choice = self.choice`. |
| Selected object changes current parameter set | `UI/qml/Main.qml` handles `MathObjectScreen.onChoiceChanged` | `parameterScreen.key = model.choice`; `UI/qml/ParameterScreen.qml` uses that key to select `model.parameters[key]`. |
| String parameter text changes | `UI/CustomComponents/templates/StringParameter.qml` | A QML `Binding` writes `ParameterModel.value` from `paramTbx.text`. |
| Boolean parameter checkbox changes | `UI/CustomComponents/templates/BooleanParameter.qml` | `onClicked` toggles the local string `check` between `"true"` and `"false"`; a QML `Binding` writes `ParameterModel.value` from `check`. |
| API selection changes | `UI/qml/APIScreen.qml` `ComboBox` current index changes | A QML `Binding` writes `APIScreenModel.api` from `self.model.apis[apiCombo.currentIndex].key`. |
| Range dimension is added | `UI/qml/APIRangeScreen.qml` dialog `onAccepted` | `model.chosen_dimensions.push(...)` mutates `APIRangeModel.chosen_dimensions` in place. |
| Range dimension is removed | `UI/qml/APIRangeScreen.qml` `ScrollLoader.delegateCallbacks.onDeleted` | `self.model.chosen_dimensions?.splice(index, 1)` mutates `APIRangeModel.chosen_dimensions` in place. |
| Function selection changes | `UI/qml/FunctionScreen.qml` handles `onChoiceChanged` | `FunctionScreenModel.choice` is assigned with `model.choice = self.choice`. |
| Restriction group is added | `UI/qml/RestrictionScreen.qml` Add Restriction Group button | Calls `RestrictionScreenModel.createNewGroup()`, which appends a `RestrictionGroupModel` and emits `restrictionGroups_changed`. |
| Restriction is added to a group | `UI/qml/RestrictionGroup.qml` dialog `onAccepted` | Dynamically creates `ParameterModel` objects, copies their values, dynamically creates a `ParameterSetModel`, assigns `obj.parameters`, and appends it with `model.restrictions.push(obj)`. |
| Restriction is deleted from a group | `UI/qml/RestrictionGroup.qml` `ColumnLoader.delegateCallbacks.onDeleted` | Calls `self.model.restrictions[index].destroy()` and then `self.model.restrictions.splice(index, 1)`. |

`UI/qml/APIScreen.qml` also creates transient `NameDescModel` QML objects from the current command parameters with `param.createObject(range, {name: item.name, desc: item.desc, key: item.name + "-p"})`; those objects become range API parameter-dimension options.

## Command Execution Path

The GO button in `UI/qml/Main.qml` calls `manager.runQuery()`. `UI/qml/UIManager.py` exposes `runQuery` as a `@Slot`, so this QML call enters Python.

`runQuery()` first calls `collectQuery()`. `collectQuery()` reads the current Python model graph:

1. `self.object.choice` provides the selected command key.
2. `self.parameters.parameters[cmd]` provides the active command `ParameterModel` list.
3. `self.apis.api` and, for range queries, `self.apis.api_models[api].chosen_dimensions` provide the API selection and dimensions.
4. `self.functions.choice` provides the optional statistic/function selection.
5. `self.restrictions.restrictionGroups` provides selected restriction groups, restriction descriptors, and copied restriction parameters.

Validation currently happens inside `collectQuery()`:

| Validation case | Location | Behavior |
| --- | --- | --- |
| Required command parameter is blank | Loop over `self.parameters.parameters[cmd]` | Raises `Exception(f"Parameter {param.name} for command {cmd} is required but does not contain a value.")`. |
| Range API has no dimensions | `if api == 'range'` block | Raises `Exception("Range API requires at least one dimension.")`. |
| Required restriction parameter is blank | Nested loop over `group.restrictions` and `param_set.parameters` | Raises `Exception(f"Parameter {p.name} for command {param_set.descriptor.name} is required but does not contain a value.")`. |

After validation, `collectQuery()` returns a dictionary with `api`, `cmd`, `func`, and `restrictions`, and also prints a CLI-like query string.

`runQuery()` then performs the local execution setup:

1. Imports `Command`, `SequencerAPI`, `Statistic`, and `Restriction`.
2. Resolves `command = Command.commands[query["cmd"][0]]`.
3. Resolves `api = SequencerAPI.apis[query["api"][0]]`.
4. Parses each restriction string with `Restriction.parse(r)`.
5. Instantiates `api_inst = api(query["api"][1])`.
6. Instantiates `cmd_inst = command(query["cmd"][1])`.
7. Calls `cmd_inst.setRestrictions(restriction_list)`.
8. Calls `api_inst.setCommand(cmd_inst)`.
9. Calls `api_inst.setStatistic(None if query["func"] == "" else Statistic.statistics[query["func"]]())`.
10. Calls `api_inst.execute()`.

This command path is local Sequencer API execution. The audit task documents the path only; it does not require launching the UI or invoking `runQuery()`.
