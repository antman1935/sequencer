# author: antman1935, anthony.lamont99@yahoo.com

#####################################################################
#                                                                   #
# Configuration Code                                                #
#                                                                   #
#####################################################################

# TODO; Do all of the TODO's here and test your Command by running it
# from the top level directory, i.e.
#   `python3 Commands/YourCustomCommand.py`
# Once all of the tests are passing with good coverage, register the
# command so that it is usable from the cli. 
# See Commands/CommandRegistration.py

if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())

from CmdTools import Command, CommandOptions
from Parameters import CommandParameter, ParamType, CommandParser

"""
This class allows us to pass arguments to the generator below.
It allows any of the following restrictions to the
words we generate:

TODO: List arguments to your generator with descriptions.
1. n - 
"""
class MyGeneratorOptions(CommandOptions):
    """
    TODO: Add all arguments to you generator.
    """
    def __init__(self, n: int):
        self.n = n

    """
    TODO: Return all arguments to the initializer in a dictionary.
    NOTE: The keys must match the __init__ method's parameters exactly.
    """
    def getParameters(self):
        return {"n": self.n}

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class MyGeneratorCmd(Command):
    """
    TODO: Fill in these fields with appropriate info. The name must be unique among the
    Command subclasses. The parameter names must match the Option's classes __init__
    parameters exactly.
    """
    name: str = ""
    description: str = ""
    parameters: list[CommandParameter] = [
        CommandParameter("n", True, ParamType.NATURAL, ""),
    ]
    parser: CommandParser = CommandParser(parameters)
    options_class = MyGeneratorOptions


    def __init__(self, param_str: str):
        super().__init__()
        self.params = MyGeneratorCmd.parser.parseInput(param_str)
        self.options = MyGeneratorOptions(**self.params)

    def internal_generator(self):
        for word in generate(self.options):
            yield word

    def __str__(self):
        return f"Set({'|'.join([str(key) + ':' + str(value) for key, value in self.params.items() if not value is None])})"

#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

"""
TODO: implement generator code. See other Command subclasses for ideas.
Implementations should use constant memory if possible.
"""
def generate(options: MyGeneratorOptions):
   pass

#####################################################################
#                                                                   #
# Tests                                                             #
#                                                                   #
#####################################################################

def base_generator_test():
    param_str = "n:3"
    # TODO: Enter all the expected values of your generator for n = 3, or other small enough case.
    expected_values = [

    ]

    cmd = MyGeneratorCmd(param_str)
    return Command.generator_test(f"Running Catalan generator test ({param_str})", cmd.generator(), expected_values)

def nis0_generator_test():
    param_str = "n:0"
    expected_values = [
        [],
    ]

    cmd = MyGeneratorCmd(param_str)
    return Command.generator_test(f"Running Catalan generator test ({param_str})", cmd.generator(), expected_values)

def tests():
    test_funcs = [nis0_generator_test]
    print(f"Running {len(test_funcs)} tests for Catalan Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()