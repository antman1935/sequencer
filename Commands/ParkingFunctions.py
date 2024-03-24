# author: antman1935, anthony.lamont99@yahoo.com

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
This class allows us to pass arguments to the parking function
generator below to allow any of the following restrictions to the
rankings we generate:

1. n - The length of the word
"""
class ParkingFunctionGeneratorOptions(CommandOptions):
    def __init__(self, n, unit = False, r = 0):
        super().__init__()
        self.n = n
        self.unit = unit
        self.r = r

    def getParameters(self):
        return {"n": self.n, "unit": self.unit, "r": self.r}

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class ParkingFunctionGeneratorCmd(Command):
    name: str = "parking_func"
    description: str = "Parking Functions"
    parameters: list[CommandParameter] = [
        CommandParameter("n", True, ParamType.NATURAL, "The length of the string"),
        CommandParameter("unit", False, ParamType.BOOL, "If true, only consider unit parking functions"),
        CommandParameter("r", False, ParamType.NATURAL, "First r elements of parking function must be distinct")
    ]
    parser: CommandParser = CommandParser(parameters)
    options_class = ParkingFunctionGeneratorOptions


    def __init__(self, param_str: str):
        super().__init__()
        params = ParkingFunctionGeneratorCmd.parser.parseInput(param_str)
        self.options = ParkingFunctionGeneratorOptions(**params)

    def internal_generator(self):
        for word in generateParkingFunctions(self.options):
            yield word

    def __str__(self):
        params = self.options.getParameters()
        return f"ParkingFunctions({'|'.join([str(key) + ':' + str(value) for key, value in params.items() if not value is None])})"
    
#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

# given the attempted parking spot i, return actual parking spot given
# filled spots in parameter spots. All zero indexed.
def park(spots, i):
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
            # if r > 0, then first r values must be distinct
            if options.r > 0 and len(current) < options.r:
                if i in current:
                    continue
            incr_index = park(spots, i-1)
            if incr_index != -1:
                # if generating unit parking functions, only consider choices where the resulting spot
                # is at most 1 away from the desired spot.
                if (not options.unit) or (incr_index+1) - i <= 1:
                    current.append(i)
                    for value in helper(current, spots):
                        yield value
                    current.pop()
                spots[incr_index] -= 1

        return

    for value in helper([], [0 for i in range(options.n)]):
        yield value
    return

#####################################################################
#                                                                   #
# Tests                                                             #
#                                                                   #
#####################################################################

def unit_pf_r_2_generator_test():
    param_str = "n:3/unit:true/r:2"
    expected_values = [
        [1,3,1],
        [3,1,1],
        [1,2,2],
        [2,1,2],
        [1,2,3],
        [1,3,2],
        [2,1,3],
        [2,3,1],
        [3,1,2],
        [3,2,1],
    ]

    cmd = ParkingFunctionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Parking Function generator test ({param_str})", cmd.generator(), expected_values)

def unit_pf_generator_test():
    param_str = "n:3/unit:true"
    expected_values = [
        [1,1,2],
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
    test_funcs = [unit_pf_generator_test, unit_pf_r_2_generator_test, base_generator_test, base_generator_test2, nis0_generator_test]
    print(f"Running {len(test_funcs)} tests for Parking Function Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()


