from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QListView

from CustomComponents.python.NameDescModel import NameDescModel
from CustomComponents.python.ParameterModel import ParameterModel
from CustomComponents.python.ParameterSetModel import ParameterModel
from qml.MathObjectScreenModel import MathObjectScreenModel
from qml.ParameterScreenModel import ParameterScreenModel
from qml.APIScreenModel import APIScreenModel
from qml.APIPointModel import APIPointModel
from qml.APIRangeModel import APIRangeModel
from qml.FunctionScreenModel import FunctionScreenModel
from qml.RestrictionScreenModel import RestrictionScreenModel

QML_IMPORT_NAME = "com.pyobjects.UIManager"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class UIManager(QObject):

    def __init__(self, object: MathObjectScreenModel, parameters: ParameterScreenModel, apis: APIScreenModel, functions: FunctionScreenModel, restrictions: RestrictionScreenModel):
        super(UIManager, self).__init__()
        self._object = object
        self._parameters = parameters
        self._apis = apis
        self._functions = functions
        self._restrictions = restrictions

    @Signal
    def object_changed(self):
        pass

    @Property(MathObjectScreenModel, notify=object_changed)
    def object(self):
        return self._object
    
    @object.setter
    def object(self, object):
        if (self._object != object):
            self._object = object
            self.object_changed.emit()

    @Signal
    def parameters_changed(self):
        pass

    @Property(ParameterScreenModel, notify=parameters_changed)
    def parameters(self):
        return self._parameters
    
    @parameters.setter
    def parameters(self, parameters):
        if (self._parameters != parameters):
            self._parameters = parameters
            self.parameters_changed.emit()

    @Signal
    def apis_changed(self):
        pass

    @Property(APIScreenModel, notify=apis_changed)
    def apis(self):
        return self._apis
    
    @apis.setter
    def apis(self, apis):
        if (self._apis != apis):
            self._apis = apis
            self.apis_changed.emit()

    @Signal
    def functions_changed(self):
        pass

    @Property(FunctionScreenModel, notify=functions_changed)
    def functions(self):
        return self._functions
    
    @functions.setter
    def functions(self, functions):
        if (self._functions != functions):
            self._functions = functions
            self.functions_changed.emit()

    @Signal
    def restrictions_changed(self):
        pass

    @Property(RestrictionScreenModel, notify=restrictions_changed)
    def restrictions(self):
        return self._restrictions
    
    @restrictions.setter
    def restrictions(self, restrictions):
        if (self._restrictions != restrictions):
            self._restrictions = restrictions
            self.restrictions_changed.emit()

    @Slot()
    def collectQuery(self):
        cmd = self.object.choice
        cmd_params = []
        for param in self.parameters.parameters[cmd]:
            if param.require and param.value.strip() == "":
                raise Exception(f"Parameter {param.name} for command {cmd} is required but does not contain a value.")
            elif param.value.strip() == "":
                continue
            cmd_params.append(f"{param.name}:{param.value.strip()}")
        api = self.apis.api
        api_params = ""

        if api == 'range':
            if len(self.apis.api_models[api].chosen_dimensions) == 0:
                raise Exception(f"Range API requires at least one dimension.")
            api_params = f"dimensions:{','.join([dim.key for dim in self.apis.api_models[api].chosen_dimensions])}"

        func = self.functions.choice
        func = "" if func is None else func

        restrictions = []
        for group in self.restrictions.restrictionGroups:
            res_set = []
            for param_set in group.restrictions:
                p_set = []
                for p in param_set.parameters:
                    if p.require and p.value.strip() == "":
                        raise Exception(f"Parameter {p.name} for command {param_set.descriptor.name} is required but does not contain a value.")
                    elif p.value.strip() == "":
                        continue
                    p_set.append(f"{p.name}:{p.value.strip()}")
                res_set.append((param_set.descriptor.key, p_set))
            if len(res_set) == 0:
                continue
            restrictions.append(res_set)

        out = {
            'api': (api, api_params),
            'cmd': (cmd, "/".join(cmd_params)),
            'func': func,
            'restrictions': [[name + (('/' + '/'.join(params)) if len(params) > 0 else '') for name, params in group] for group in restrictions if len(group)]
        }

        outp = f"-a {out['api'][0]}{('/' + out['api'][1]) if len(out['api'][1]) > 0 else ''} " +\
               f"-c {out['cmd'][0]}{('/' + out['cmd'][1]) if len(out['cmd'][1]) > 0 else ''}" +\
               f"{(' -s ' + out['func']) if len(out['func']) > 0 else ''}" +\
               f"{(' -r ' + ' -r '.join(['//'.join(group) for group in out['restrictions']])) if len(out['restrictions']) > 0 else ''}"

        print(outp)

        return out
    
    @Slot()
    def runQuery(self):
        query = self.collectQuery()
        from CmdTools import Command
        from Parameters import ParamType
        from SequencerAPI import SequencerAPI
        from Statistic import Statistic
        from Restriction import Restriction
        command = Command.commands[query["cmd"][0]]
        api = SequencerAPI.apis[query["api"][0]]
        restriction_list = []
        for group in query["restrictions"]:
            res = []
            for r in group:
                res.append(Restriction.parse(r))
            restriction_list.append(res)

        api_inst = api(query["api"][1])
        cmd_inst = command(query["cmd"][1])
        cmd_inst.setRestrictions(restriction_list)
        
        api_inst.setCommand(cmd_inst)
        api_inst.setStatistic(None if query["func"] == "" else Statistic.statistics[query["func"]]())
        api_inst.execute()

        


def load_ui():
    import os, sys
    sys.path.append(os.getcwd())
    from CmdTools import Command
    import Commands.CommandRegistration # registers all commands
    from Parameters import ParamType
    from SequencerAPI import SequencerAPI
    from Statistic import Statistic
    from Restriction import Restriction
    cmds = []
    parameters = {}
    apis = {}
    api_names = []
    funcs = []
    restrictions = []
    restriction_parameters = []
    for name, cmd in Command.commands.items():
        cmds.append(NameDescModel(cmd.ui_name, cmd.ui_description, name))

        params = []
        for param in cmd.parameters:
            params.append(ParameterModel(param.name, param.description, param.required, "str" if param.param_type != ParamType.BOOL else "bool"))
        parameters[cmd.name] = sorted(params, key=lambda p: 1 if p._require else 0, reverse= True)


    if True:
        for name, api in SequencerAPI.apis.items():
            api_names.append({"key": name, "display": api.ui_name})

            if name == "point":
                apis["point"] = APIPointModel(api.ui_name, api.description)
            elif name == "range": 
                computed_dims = []
                for name, stat in Statistic.statistics.items():
                    computed_dims.append(NameDescModel(stat.ui_name, stat.ui_description, stat.name+'-c'))
                apis["range"] = APIRangeModel(api.ui_name, api.description, computed_dims)

    for name, stat in Statistic.statistics.items():
        funcs.append(NameDescModel(stat.ui_name, stat.ui_description, stat.name))

    for name, restriction in Restriction.restrictions.items():
        restrictions.append(NameDescModel(restriction.ui_name, restriction.ui_description, restriction.name))
        params = []
        for param in restriction.parameters:
            params.append(ParameterModel(param.name, param.description, param.required, "str" if param.param_type != ParamType.BOOL else "bool"))
        restriction_parameters.append(params)
    
    return (cmds, parameters, api_names, apis, funcs, restrictions, restriction_parameters)

def makeManager():
    (objects, parameters, api_names, apis, funcs, res, restriction_parameters) = load_ui()
    obj = MathObjectScreenModel(objects)
    params = ParameterScreenModel(parameters)
    api = APIScreenModel(api_names, apis)
    functions = FunctionScreenModel(funcs)
    restrictions = RestrictionScreenModel(res, restriction_parameters)
    return UIManager(obj, params, api, functions, restrictions)