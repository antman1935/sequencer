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
This class allows us to pass arguments to the type b partition
generator below to allow any of the following restrictions to the
rankings we generate:

1. n - The length of the word
"""
class TypeBPartitionGeneratorOptions(CommandOptions):
    def __init__(self, n):
        self.n = n

    def getParameters(self):
        return {"n": self.n}

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class TypeBPartitionGeneratorCmd(Command):
    name: str = "type_b"
    description: str = "Type B Partitions"
    ui_name: str = description
    ui_description: str = "Type B partitions are partitions of the set {-n, ..., 0, ..., n} where for every P in the partition, the set -P is also in the partition, and there is only one set where P = -P."
    parameters: list[CommandParameter] = [
        CommandParameter("n", True, ParamType.NATURAL, "The max value of symmetric set {-n,...,0,...,n}"),
    ]
    parser: CommandParser = CommandParser(parameters)
    options_class = TypeBPartitionGeneratorOptions


    def __init__(self, param_str: str):
        super().__init__()
        params = TypeBPartitionGeneratorCmd.parser.parseInput(param_str)
        self.options = TypeBPartitionGeneratorOptions(params["n"])

    def internal_generator(self):
        for word in generateTypeBPartitions(self.options):
            yield word

    def __str__(self):
        params = {"n": self.options.n}
        return f"TypeBPartitions({'|'.join([str(key) + ':' + str(value) for key, value in params.items() if not value is None])})"
        

#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

def generateTypeBPartitions(options: TypeBPartitionGeneratorOptions):
    def helper(current, i):
        if i > options.n:
            yield current
            return
        
        # fourth rule: add {i}, {-i} singleton blocks
        for partition in helper(current + [([i], [-i])], i+1):
            yield partition

        # first rule: increase size of the zero block
        for partition in helper([(current[0][0] + [i, -i], None)] + current[1:], i+1):
            yield partition

        for j in range(1, len(current)):
            # second rule: add i, -i to blocks  b, -b respectively
            for partition in helper([(current[k][0], current[k][1]) if k!=j else (current[k][0] + [i], current[k][1] + [-i]) for k in range(len(current))], i+1):
                yield partition

            # third rule: add -i, i to blocks b, -b respectively
            for partition in helper([(current[k][0], current[k][1]) if k!=j else (current[k][0] + [-i], current[k][1] + [i]) for k in range(len(current))], i+1):
                yield partition

    for partition in helper([([0], None)], 1):
        yield partition

#####################################################################
#                                                                   #
# Tests                                                             #
#                                                                   #
#####################################################################

def base_generator_test():
    param_str = "n:3"
    expected_values = [
        [([0], None), ([1], [-1]), ([2], [-2]), ([3], [-3])],
        [([0], None), ([1, 3], [-1, -3]), ([2], [-2])],
        [([0], None), ([1, -3], [-1, 3]), ([2], [-2])],
        [([0], None), ([1], [-1]), ([2, 3], [-2, -3])],
        [([0], None), ([1], [-1]), ([2, -3], [-2, 3])],
        [([0], None), ([1, 2], [-1, -2]), ([3], [-3])],
        [([0], None), ([1, -2], [-1, 2]), ([3], [-3])],
        [([0], None), ([1, 2, 3], [-1, -2, -3])],
        [([0], None), ([1, 2, -3], [-1, -2, 3])],
        [([0], None), ([1, -2, 3], [-1, 2, -3])],
        [([0], None), ([1, -2, -3], [-1, 2, 3])],
        [([0,3,-3], None), ([1], [-1]), ([2], [-2])],
        [([0,3,-3], None), ([1, 2], [-1, -2])],
        [([0,3,-3], None), ([1, -2], [-1, 2])],
        [([0,1,-1], None), ([2], [-2]), ([3], [-3])],
        [([0,1,-1], None), ([2, 3], [-2, -3])],
        [([0,1,-1], None), ([2, -3], [-2, 3])],
        [([0,1,-1,3,-3], None), ([2], [-2])],
        [([0,2,-2], None), ([1], [-1]), ([3], [-3])],
        [([0,2,-2], None), ([1, 3], [-1, -3])],
        [([0,2,-2], None), ([1, -3], [-1, 3])],
        [([0,2,-2,3,-3], None), ([1], [-1])],
        [([0,1,-1,2,-2], None), ([3], [-3])],
        [([0,1,-1,2,-2,3,-3], None)],
    ]

    cmd = TypeBPartitionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Type B Partition generator test ({param_str})", cmd.generator(), expected_values)

def base_generator_test2():
    param_str = "n:2"
    expected_values = [
        [([0], None), ([1], [-1]), ([2], [-2])],
        [([0], None), ([1, 2], [-1, -2])],
        [([0], None), ([1, -2], [-1, 2])],
        [([0,1,-1], None), ([2], [-2])],
        [([0,2,-2], None), ([1], [-1])],
        [([0,1,-1,2,-2], None)],
    ]

    cmd = TypeBPartitionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Type B Partition generator test ({param_str})", cmd.generator(), expected_values)

def nis0_generator_test():
    param_str = "n:0"
    expected_values = [
        [([0], None)],
    ]

    cmd = TypeBPartitionGeneratorCmd(param_str)
    return Command.generator_test(f"Running Type B Partition generator test ({param_str})", cmd.generator(), expected_values)

def tests():
    test_funcs = [base_generator_test, base_generator_test2, nis0_generator_test]
    print(f"Running {len(test_funcs)} tests for Type B Partition Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()