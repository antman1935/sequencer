from enum import Enum, StrEnum
from Dimensions import ComputedDimension, ParameterDimension

class OutputType(Enum):
    OEIS_LOOKUP = 1
    RAW = 2
    ASCII_TABLE = 3
    LATEX_TABLE = 4

"""
Encapsulates the logic for validating different data types of parameters that can
be passed to the generators.
"""
class ParamType(StrEnum):
    NATURAL = "Natural number"
    INTEGER = "Integers"
    INT_POS = "Positive integers"
    BOOL = "Boolean"
    LIST_DIM = "List of dimensions"
    LIST_INT_POS = "List of positive integers"
    OUTPUT = "Table output"

    """
    This function validates the parameter based on the ParamType and returns the valid
    data in the correct datatype.
    """
    def validateAndConvertParameter(param_type, value):
        match param_type:
            case ParamType.NATURAL:
                # ℕ, value must be integer and >= 0
                conv_value = int(value)
                assert conv_value > -1, "Natural numbers should be greater than -1."
                return conv_value
            case ParamType.INTEGER:
                # ℤ, value must be integer
                return int(value)
            case ParamType.INT_POS:
                # ℤ^+, value must be positive integer
                conv_value = int(value)
                assert conv_value > 0, "Positive integers should be greater than 0."
                return conv_value
            case ParamType.BOOL:
                if value.lower() in ["f", "false", "n", "no"]:
                    return False
                elif value.lower() in ["t", "true", "y", "yes"]:
                    return True
                assert False, "Value is not in the list of acceptable boolean values."
            case ParamType.LIST_DIM:
                dim_token_list = value.split(",")
                dim_list = []
                for token in dim_token_list:
                    tokens = token.split("-")
                    assert len(tokens) == 2, f"Invalid parameter type provided: {token}"
                    [name, dim_type] = tokens
                    if dim_type in ["p", "param", "parameter"]:
                        dim_list.append(ParameterDimension(name))
                    elif dim_type in ["c", "comp", "computed"]:
                        dim_list.append(ComputedDimension(name))
                    else:
                        assert False, "Value is not in the list of acceptable dimension types."
                return dim_list
            case ParamType.LIST_INT_POS:
                ints_str = value.split(",")
                ints = []
                for int_str in ints_str:
                    ints.append(ParamType.validateAndConvertParameter(ParamType.INT_POS, int_str))
                return ints
            case ParamType.OUTPUT:
                match value:
                    case "oeis":
                        return OutputType.OEIS_LOOKUP
                    case "raw":
                        return OutputType.RAW
                    case "ascii":
                        return OutputType.ASCII_TABLE
                    case "latex":
                        return OutputType.LATEX_TABLE
                    case _:
                        raise Exception("Unsupported output type:", value)
            case _:
                raise Exception("Unsupported parameter type:", param_type)
            
    def typeMin(param_type):
        match param_type:
            case ParamType.NATURAL:
                # ℕ, value must be integer and >= 0
                return 0
            case ParamType.INTEGER:
                # ℤ, value must be integer
                return 0
            case ParamType.INT_POS:
                # ℤ^+, value must be positive integer
                return 1
            case ParamType.BOOL:
                return 0
            case _:
                raise Exception("Unsupported parameter type:", param_type)

ParamType.validateAndConvertParameterValue = staticmethod(ParamType.validateAndConvertParameter)

"""
A command defines the list of the parameters that can be passed to it, and which ones are required.
"""
class CommandParameter:
    def __init__(self, name: str, required: bool, param_type: ParamType, description: str):
        self.name = name
        self.required = required
        self.param_type = param_type
        self.description = description

    def __str__(self):
        return f"({self.param_type}) {self.name}{' (required)' if self.required else ''} - {self.description}"

"""
Given a list of parameters, allows for a parameter string matching those parameters to be parsed and
validated.
"""
class CommandParser:
    def __init__(self, parameter_list: list[CommandParameter]):
        self.parameters = {}
        for param in parameter_list:
            self.parameters[param.name] = param

    """
    This function takes a string of parameters and extracts them for use in the specfied command.
    The functions returns the options in a dictionary from param name to value.
    The param_str is of the form
        param1_name:param1_value[/paramN_name:paramN_value]
    This function also guarantees that all required parameters are set.
    """
    def parseInput(self, param_str: str):
        params = param_str.split("/")
        param_dict = {}
        if param_str != "":
            for param_pair in params:
                [param_name, param_value] = param_pair.split(":")
                assert param_name in self.parameters, f"Invalid parameter passed: {param_name}"

                value = ParamType.validateAndConvertParameter(self.parameters[param_name].param_type, param_value)
                param_dict[param_name] = value

        for name, param in self.parameters.items():
            if param.required:
                assert name in param_dict, f"Required parameter {name} is not set."

        return param_dict