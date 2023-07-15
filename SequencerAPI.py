from CmdTools import Command, CommandParameter, ParamType, CommandParser
class SequencerAPI:
    def __init__(self):
        self.cmd = None
    def execute(self):
        raise Exception("unimplemented")
    def setCommand(self, cmd: Command):
        self.cmd = cmd

class PointAPI(SequencerAPI):
    name: str = "point"
    description: str = "Generate the set of objects for one set of parameters."
    parameters: list[CommandParameter] = [
        CommandParameter("p", False, ParamType.BOOL, "Whether to print the list of items."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def __init__(self, param_str: str):
        super().__init__()
        params = PointAPI.parser.parseInput(param_str)
        self.print = params.get("p", False)
    
    def execute(self):
        assert not self.cmd is None
        
        print(f"Point Query on {self.cmd}.")
        if self.print:
            print("Elements:")
        count = 0
        for word in self.cmd.generator():
            count += 1
            if self.print:
                print(f"\t{word}")
        print(f"|{self.cmd}| = {count}")

from Dimensions import DimensionType, Dimension

def increment(num_dict, indices):
    level = num_dict
    for i in range(len(indices) - 1):
        if indices[i] not in level:
            level[indices[i]] = {}
        level = level[indices[i]]

    if not indices[-1] in level:
        level[indices[-1]] = 0
    level[indices[-1]] += 1

class RangeAPI(SequencerAPI):
    name: str = "range"
    description: str = "Create a sequence or series of tables based on the selected fields to group by."
    parameters: list[CommandParameter] = [
        CommandParameter("dimensions", True, ParamType.LIST_DIM, "List of dimensions to create our sequence or table(s)"),
        CommandParameter("p", False, ParamType.BOOL, "Whether to print the list of items (statistic dimensions printed per element)."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def __init__(self, param_str: str):
        super().__init__()
        params = RangeAPI.parser.parseInput(param_str)
        self.dimensions = params.get("dimensions")
        self.print = params.get("p", False)

    def setCommand(self, cmd: Command):
        super().setCommand(cmd)
        self.param_limits = self.cmd.options.getParameters()

    def _iterate(self, count, ranged_params, rp_index, inst):
        if rp_index >= len(ranged_params):
            inst_options = self.cmd.options_class(**inst)
            self.cmd.options = inst_options
            
            indent = 1
            if self.print and len(ranged_params) > 0:
                print(f"\tParameters: {', '.join([param.name + '=' + str(inst[param.name]) for param in ranged_params])}")
                indent = 2
            for word in self.cmd.generator():
                indices = []
                comps = []
                for dim in reversed(self.dimensions):
                    match dim.dim_type:
                        case DimensionType.PARAMETER:
                            indices.append(inst[dim.name])
                        case DimensionType.COMPUTED:
                            val = dim.compute(word)
                            indices.append(val)
                            comps.append(f"{dim.name}={val}")
                if self.print:
                    suffix = f" ({', '.join(comps)})" if len(comps) > 0 else ""
                    print(indent*'\t', f"{word}{suffix}")


                increment(count, indices)
            return
        
        ranged_param = ranged_params[rp_index]
        [param] = [p for p in self.cmd.parameters if p.name == ranged_param.name]
        for i in range(ParamType.typeMin(param.param_type), self.param_limits[param.name] + 1):
            inst[param.name] = i
            self._iterate(count, ranged_params, rp_index+1, inst)


    def execute(self):
        assert not self.cmd is None

        print(f"Range Query on {self.cmd}. Dimensions are {self.dimensions}.")
        if self.print:
            print("Elements:")
        ranged_params = [dim for dim in self.dimensions if dim.dim_type == DimensionType.PARAMETER]
        ranged_params_names = [dim.name for dim in ranged_params]

        count = {}
        self._iterate(count, ranged_params, 0, {k:v for k,v in self.param_limits.items() if not k in ranged_params_names})
        print(f"count = {count}")