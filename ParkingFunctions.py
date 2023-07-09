# author: antman1935, anthony.lamont99@yahoo.com

#####################################################################
#                                                                   #
# Configuration Code                                                #
#                                                                   #
#####################################################################

from CmdTools import CommandParameter, ParamType, CommandParser, Command

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class ParkingFunctionGeneratorCmd(Command):
    parameters: list[CommandParameter] = [
        CommandParameter("n", True, ParamType.NATURAL, "The length of the string"),
    ]
    parser: CommandParser = CommandParser(parameters)


    def __init__(self, param_str: str):
        params = ParkingFunctionGeneratorCmd.parser.parseInput(param_str)
        self.options = ParkingFunctionGeneratorOptions(params["n"])

    def generator(self):
        for word in generateParkingFunctions(self.options):
            yield word
        

"""
This class allows us to pass arguments to the parking function
generator below to allow any of the following restrictions to the
rankings we generate:

1. n - The length of the word
"""
class ParkingFunctionGeneratorOptions:
    def __init__(self, n):
        self.n = n

#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

def insert(spots, i):
    while i < len(spots) and spots[i] != 0:
        i += 1

    if i == len(spots):
        return -1

    spots[i] += 1
    return i

def generateParkingFunctions(options: ParkingFunctionGeneratorOptions):
    def helper(current, spots):
        if len(current) == options.n:
            yield current + []
            return
        for i in range(1, options.n + 1):
            incr_index = insert(spots, i-1)
            if incr_index != -1:
                current.append(i)
                for value in helper(current, spots):
                    yield value
                spots[incr_index] -= 1
                current.pop()

        return

    for value in helper([], [0 for i in range(options.n)]):
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
        [1,1,1],
        [1,1,2],
        [1,2,1],
        [2,1,1],
        [1,1,3],
        [1,3,1],
        [3,1,1],
        [1,2,2],
        [2,1,2],
        [2,2,1],
        [1,2,3],
        [1,3,2],
        [2,1,3],
        [2,3,1],
        [3,1,2],
        [3,2,1],
    ]

    cmd = ParkingFunctionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Parking Function generator test ({param_str})", cmd.generator(), expected_values)

def base_generator_test2():
    param_str = "n:2"
    expected_values = [
        [1,1],
        [1,2],
        [2,1],
    ]

    cmd = ParkingFunctionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Parking Function generator test ({param_str})", cmd.generator(), expected_values)

def nis0_generator_test():
    param_str = "n:0"
    expected_values = [
        [],
    ]

    cmd = ParkingFunctionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Parking Function generator test ({param_str})", cmd.generator(), expected_values)

def tests():
    test_funcs = [base_generator_test, base_generator_test2, nis0_generator_test]
    print(f"Running {len(test_funcs)} tests for Parking Function Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()


