# author: antman1935, anthony.lamont99@yahoo.com

from CmdTools import Command
from Parameters import CommandParameter, ParamType, CommandParser, OutputType
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

def invert(d: dict[int, dict[int, int]]):
    new_d = {}
    for x, interior in d.items():
        for y, count in interior.items():
            if not y in new_d:
                new_d[y] = {}
            new_d[y][x] = count
    return new_d

def printMultipleTables(result, dimensions: list[str], print_func):
    def helper(curr, i, idxs):
        if i == len(dimensions) - 2:
            print(f"Print Table for ({';'.join([dimensions[j] + '=' + str(idxs[j]) for j in range(len(idxs))])}):")
            print_func(invert(curr), [dim for dim in reversed(dimensions[i:])])
            return
        for j in range(min(curr.keys()), max(curr.keys()) + 1):
            if not j in curr:
                continue
            idxs.append(j)
            helper(curr[j], i+1, idxs)
            idxs.pop()

    helper(result, 0, [])

def getTableBounds(table):
    min_row = min(table.keys())
    max_row = max(table.keys())
    min_column = min(table[max_row].keys())
    max_column = max(table[max_row].keys())
    column_widths = {}
    column_widths["row_start"] = 0
    for r in range(min_row, max_row + 1):
        min_column = min(min_column, min(table[r].keys()))
        max_column = max(max_column, max(table[r].keys()))
        column_widths["row_start"] = max(column_widths["row_start"], len(str(r)))
        for c, count in table[r].items():
            if not c in column_widths:
                column_widths[c] = 0
            column_widths[c] = max(column_widths[c], len(str(count)))
            
    return [min_row, max_row], [min_column, max_column], column_widths

def printAsciiRow(row: list, column_widths: list[int], print_zeros = False):
    out_str = "|"
    first = True
    for value, width in zip(row, column_widths):
        p = value if print_zeros or first or value != 0 else ""
        first = False
        out_str += f" {(width - len(str(p))) * ' '}{p} |"
    print(out_str)

def printAsciiTable(result: dict[int, dict[int, int]], dimensions: list[str]):
    # get the row and column bounds, plus max column width for each column
    row_bounds, column_bounds, column_widths = getTableBounds(result)
    dim_str = " \\ ".join(dimensions)
    column_widths["row_start"] = max(column_widths["row_start"], len(dim_str))
    column_widths = [column_widths["row_start"]] + [column_widths[c] for c in range(column_bounds[0], column_bounds[1] + 1)]

    data = [[0 if c not in result[r] else result[r][c] for c in range(column_bounds[0], column_bounds[1] + 1)] for r in range(row_bounds[0], row_bounds[1] + 1)]

    row_length = sum(column_widths) + 3 * len(column_widths) + 1
    print("-" * row_length)
    printAsciiRow([dim_str] + [c for c in range(column_bounds[0], column_bounds[1] + 1)], column_widths, print_zeros=True)
    print("|"+("-" * (row_length-2))+"|")
    for r, row in zip([r for r in range(row_bounds[0], row_bounds[1] + 1)], data):
        if sum(row) == 0:
            continue
        printAsciiRow([r] + row, column_widths)
        if r != row_bounds[1]:
            print("|"+("-" * (row_length-2))+"|")
        else:
            print("-" * row_length)

def printLatexTable(result: dict[int, dict[int, int]], dimensions: list[str]):
    print("You gotta know when to hold them... know when to fold them. KNow when to walk away. KNow hmm hmmm")

def printResults(output_type: OutputType, result, dimensions: list[str]):
    match output_type:
        case OutputType.OEIS_LOOKUP:
            assert len(dimensions) == 1, "This output is only available for sequences."
            print(f"{dimensions[0]}: {' '.join(['0' if not i in result else str(result[i]) for i in range(min(result.keys()), max(result.keys()) + 1)])}")
        case OutputType.RAW:
            print("Raw output:", result)
        case OutputType.ASCII_TABLE:
            if len(dimensions) == 1:
                printResults(OutputType.OEIS_LOOKUP, result, dimensions)
            elif len(dimensions) == 2:
                printAsciiTable(invert(result), [dim for dim in reversed(dimensions)])
            else:
                printMultipleTables(result, dimensions, printAsciiTable)
        case OutputType.LATEX_TABLE:
            if len(dimensions) == 2:
                printLatexTable(invert(result), [dim for dim in reversed(dimensions)])
            else:
                printMultipleTables(result, dimensions, printLatexTable)
        case _:
            raise Exception(f"Invalid type selected for printing: {output_type}")


class RangeAPI(SequencerAPI):
    name: str = "range"
    description: str = "Create a sequence or series of tables based on the selected fields to group by."
    parameters: list[CommandParameter] = [
        CommandParameter("dimensions", True, ParamType.LIST_DIM, "List of dimensions to create our sequence or table(s)"),
        CommandParameter("p", False, ParamType.BOOL, "Whether to print the list of items (statistic dimensions printed per element)."),
        CommandParameter("out", False, ParamType.OUTPUT, "How to output the generated data."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def __init__(self, param_str: str):
        super().__init__()
        params = RangeAPI.parser.parseInput(param_str)
        self.dimensions = params.get("dimensions")
        self.print = params.get("p", False)
        self.output = params.get("out", OutputType.ASCII_TABLE)

        if self.output == OutputType.OEIS_LOOKUP:
            assert len(self.dimensions) == 1, "This format is only for sequences."

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

        print(f"Range Query on {self.cmd}. Dimensions are {[dim.name for dim in self.dimensions]}.")
        if self.print:
            print("Elements:")
        ranged_params = [dim for dim in self.dimensions if dim.dim_type == DimensionType.PARAMETER]
        ranged_params_names = [dim.name for dim in ranged_params]

        count = {}
        self._iterate(count, ranged_params, 0, {k:v for k,v in self.param_limits.items() if not k in ranged_params_names})
        printResults(self.output, count, [dim.name for dim in reversed(self.dimensions)])