﻿# author: antman1935, anthony.lamont99@yahoo.com

#####################################################################
#                                                                   #
# Configuration Code                                                #
#                                                                   #
#####################################################################

if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())

from CmdTools import Command, CommandOptions
from Parameters import CommandParameter, ParamType, CommandParser

"""
This class allows us to pass arguments to the catalan word
generator below to allow any of the following restrictions to the
words we generate:

1. n - The length of the word
"""
class CatalanGeneratorOptions(CommandOptions):
    def __init__(self, n: int):
        self.n = n

    def getParameters(self):
        return {"n": self.n}

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class CatalanGeneratorCmd(Command):
    name: str = "catalan"
    description: str = "Catalan Words"
    ui_name: str = description
    ui_description: str = "Catalan words of size n are equivalent to balanced strings of length 2n of parentheses."
    parameters: list[CommandParameter] = [
        CommandParameter("n", True, ParamType.NATURAL, "The length of the string"),
    ]
    parser: CommandParser = CommandParser(parameters)
    options_class = CatalanGeneratorOptions


    def __init__(self, param_str: str):
        super().__init__()
        params = CatalanGeneratorCmd.parser.parseInput(param_str)
        self.options = CatalanGeneratorOptions(params["n"])

    def internal_generator(self):
        for word in generateCatalanWords(self.options):
            yield word

    def __str__(self):
        params = {"n": self.options.n}
        return f"CatalanWords({'|'.join([str(key) + ':' + str(value) for key, value in params.items() if not value is None])})"

#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

def generateCatalanWords(options: CatalanGeneratorOptions):
    if options.n == 0:
        yield []
        return
    
    def helper(current_word):
        if len(current_word) == options.n:
            yield current_word[:]
            return
        prev = options.n if len(current_word) == 0 else current_word[-1]
        prev = min(options.n, prev + 2)
        for i in range(0, prev):
            current_word.append(i)
            for value in helper(current_word):
                yield value
            current_word.pop()
        return

    for value in helper([0]):
        yield value

    return

#####################################################################
#                                                                   #
# Tests                                                             #
#                                                                   #
#####################################################################

def base_generator_test():
    param_str = "n:3"
    expected_values = [
        [0,0,0],
        [0,0,1],
        [0,1,0],
        [0,1,1],
        [0,1,2],
    ]

    cmd = CatalanGeneratorCmd(param_str)
    return Command.generator_test(f"Running Catalan generator test ({param_str})", cmd.generator(), expected_values)

def base_generator_test2():
    param_str = "n:4"
    expected_values = [
        [0,0,0,0],
        [0,0,0,1],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,1,2],
        [0,1,0,0],
        [0,1,0,1],
        [0,1,1,0],
        [0,1,1,1],
        [0,1,1,2],
        [0,1,2,0],
        [0,1,2,1],
        [0,1,2,2],
        [0,1,2,3],
    ]

    cmd = CatalanGeneratorCmd(param_str)
    return Command.generator_test(f"Running Catalan generator test ({param_str})", cmd.generator(), expected_values)

def nis0_generator_test():
    param_str = "n:0"
    expected_values = [
        [],
    ]

    cmd = CatalanGeneratorCmd(param_str)
    return Command.generator_test(f"Running Catalan generator test ({param_str})", cmd.generator(), expected_values)

def tests():
    test_funcs = [base_generator_test, base_generator_test2, nis0_generator_test]
    print(f"Running {len(test_funcs)} tests for Catalan Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()