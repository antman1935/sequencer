# author: antman1935, anthony.lamont99@yahoo.com

from enum import StrEnum

"""
Encapsulates the logic for validating different data types of parameters that can
be passed to the generators.
"""
class ParamType(StrEnum):
    NATURAL = "Natural number"
    INTEGER = "Integers"
    INT_POS = "Positive integers"

    """
    This function validates the parameter based on the ParamType and returns the valid
    data in the correct datatype.
    """
    def validateAndConvertParameter(param_type: ParamType, value):
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
            case _:
                raise Exception("Unsupported parameter type:", param_type)

ParamType.validateAndConvertParameterValue = staticmethod(ParamType.validateAndConvertParameterValue)

"""
A command defines the list of the parameters that can be passed to it, and which ones are required.
"""
class CommandParameter:
    def __init__(self, name: str, required: bool, param_type: ParamType, description: str):
        self.name = name
        self.required = required
        self.param_type = param_type
        self.description = description

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
        param1_name:param1_value[|paramN_name:oaramN_value]
    This function also guarantees that all required parameters are set.
    """
    def parseInput(self, param_str: str):
        params = param_str.split("|")
        param_dict = {}
        for param_pair in params:
            [param_name, param_value] = param_pair.split(":")
            assert param_name in self.parameters, f"Invalid parameter passed: {param_name}"

            value = ParamType.validateAndConvertParameter(self.parameters[param_name].param_type, param_value)
            param_dict[param_name] = value

        for name, param in self.parameters.items():
            if param.required:
                assert name in param_dict, f"Required parameter {name} is not set."

        return param_dict


"""
Base class for all of the commands we'll create. Has a generator function that should
be overriden by all the subclasses.
"""
class Command:
    def generator(self):
        raise Exception("unimplemented")

    """
    Convienence function for testing generator output. Given a command that generates words, check that
    its output matches the list. Gives delta from both list if there is a miss-match.
    """
    def generator_test(name: str, cmd: Command, expected_list):
        print(name)
        cmd_m_expected_list = []
        expected_list_m_cmd = []

        temp = []
        for word in cmd.generator():
            if not word in expected_list:
                cmd_m_expected_list.append(word)
            else:
                temp.append(word)

        for word in expected_list:
            if not word in temp:
                expected_list_m_cmd.append(word)

        if len(cmd_m_expected_list) > 0 or len(expected_list_m_cmd) > 0:
            print(f"Generator test failed.\n\tExtra entries generated: {cmd_m_expected_list}.\n\tExpected entries missed: {expected_list_m_cmd}.")
            return False
    
        print("Success!")
        return True

Command.generator_test = static_method(Command.generator_test)