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
This class allows us to pass arguments to the Stirling Permutation ranking
generator below to allow any of the following restrictions to the
rankings we generate:

1. n - The number of positions to give rankings.
2. k - The multiplicity of each number in the permutation. E.g
       k=2 gets 1122 while k=3 gets 111222.
"""
class StirlingGeneratorOptions(CommandOptions):
    def __init__(self, n, k = 2):
        self.n = n
        self.k = k

    def getParameters(self):
        return {"n": self.n, "k": self.k}

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class StirlingGeneratorCmd(Command):
    name: str = "stirling"
    description: str = "Stirling Permutations"
    parameters: list[CommandParameter] = [
        CommandParameter("n", True, ParamType.NATURAL, "The number of positions to give a rank."),
        CommandParameter("k", False, ParamType.INT_POS, "The multiplicity of each number."),
    ]
    parser: CommandParser = CommandParser(parameters)
    options_class = StirlingGeneratorOptions


    def __init__(self, param_str: str):
        super().__init__()
        params = StirlingGeneratorCmd.parser.parseInput(param_str)
        self.options = StirlingGeneratorOptions(params["n"], params.get("k", 2))

    def internal_generator(self):
        for word in generateStirlingPermutations(self.options):
            yield word

    def flat_generator(self):
        for word in generateFlatStirlingPermutations(self.options):
            yield word

    def __str__(self):
        params = {"n": self.options.n, "k": self.options.k}
        return f"StirlingPermutations({'|'.join([str(key) + ':' + str(value) for key, value in params.items() if not value is None])})"
        

#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

"""
Generates all k-Stirling permutations of order n.
"""
def generateStirlingPermutations(options: StirlingGeneratorOptions):
    if options.n == 0:
        yield []
        return
    
    def helper(current: list[int], i: int):
        if i > options.n:
            yield current[:]
            return
        
        for j in range(len(current) + 1):
            for perm in helper(current[0:j] + (options.k * [i]) + current[j:], i+1):
                yield perm

    for perm in helper(options.k * [1], 2):
        yield perm

"""
Returns a list containing the positions right before a descent happens. Stores
them in order of appearance.
"""
def getDescents(perm: list[int]):
    descents = []
    for i in range(len(perm)-1):
        if perm[i] > perm[i+1]:
            descents.append(i)
    return descents

def getInsertionPoints(perm: list[int]):
    insertion_indices = []
    descent = getDescents(perm)
    descent_index = 0 # stays at the next descent coming after position j
    for j in range(len(perm)):
        # if there is a descent here, you can insert ii
        if descent and descent_index < len(descent) and descent[descent_index] == j:
            insertion_indices.append(j)
            descent_index += 1
        # if there is a weak ascent and no more descents, you can insert
        elif not descent or len(descent) <= descent_index:
            insertion_indices.append(j)
        elif j != len(perm)-1 and len(descent) > descent_index:
        # if there is a weak ascent and the next character after this is
        # <= the leading term of the next run, then you can insert
            next_char = perm[j+1]
            next_leading_term = perm[descent[descent_index] + 1]
            if next_char <= next_leading_term:
                insertion_indices.append(j)
    return insertion_indices

"""
Recursively build the set of flattened Stirling permutations on 2[n] from the
set of Stirling permutations on 2[n-1]. It does this by choosing where to insert
k * "n" based on the following rules.
At any position i > 0:
1. If there is a descent immediately after, you can insert. This just extends
   the existing run.
2. If the permutation after position i is weakly increasing, you can insert.
   This ends the current run with "nn" and creates another that is the entirety
   of the rest of the string.
3. If the value at position i+1 is less than or equal to the leading term of the
   next run. This ends the current run and the value at position i + 1 is the
   leading term of the new run, and has to be less than the aforementioned
   leading term for the entire permutation to be flat.
"""
def generateFlatStirlingPermutations(options: StirlingGeneratorOptions):
    def helper(current: list[int], i: int):
        if i > options.n:
            yield current[:]
            return
        insertion_points = getInsertionPoints(current)
        for j in insertion_points:
            for perm in helper(current[:j+1] + (options.k * [i]) + current[j+1:], i+1):
                yield perm

    for perm in helper(options.k * [1], 2):
        yield perm

#####################################################################
#                                                                   #
# Tests                                                             #
#                                                                   #
#####################################################################

def base_generator_test():
    param_str = "n:3"
    expected_values = [
        [1,1,2,2,3,3],
        [1,1,3,3,2,2],
        [1,1,2,3,3,2],
        [1,2,2,1,3,3],
        [1,2,2,3,3,1],
        [1,2,3,3,2,1],
        [1,3,3,1,2,2],
        [1,3,3,2,2,1],
        [2,2,1,1,3,3],
        [2,2,1,3,3,1],
        [2,2,3,3,1,1],
        [2,3,3,2,1,1],
        [3,3,1,1,2,2],
        [3,3,2,2,1,1],
        [3,3,1,2,2,1],
    ]

    cmd = StirlingGeneratorCmd(param_str)
    return Command.generator_test(f"Running Stirling Permutation generator test ({param_str})", cmd.generator(), expected_values)

def test_k_generator():
    param_str = "n:2/k:3"
    expected_values = [
        [1,1,1,2,2,2],
        [1,1,2,2,2,1],
        [1,2,2,2,1,1],
        [2,2,2,1,1,1],
    ]

    cmd = StirlingGeneratorCmd(param_str)
    return Command.generator_test(f"Running Stirling Permutation generator test ({param_str})", cmd.generator(), expected_values)

def nis0_generator_test():
    param_str = "n:0"
    expected_values = [
        [],
    ]

    cmd = StirlingGeneratorCmd(param_str)
    return Command.generator_test(f"Running Stirling Permutation generator test ({param_str})", cmd.generator(), expected_values)

def flat_generator_test():
    param_str = "n:3"
    expected_values = [
        [1,1,2,2,3,3],
        [1,1,3,3,2,2],
        [1,1,2,3,3,2],
        [1,2,2,1,3,3],
        [1,2,2,3,3,1],
        [1,3,3,1,2,2],
    ]

    cmd = StirlingGeneratorCmd(param_str)
    return Command.generator_test(f"Running flat Stirling Permutation generator test ({param_str})", cmd.flat_generator(), expected_values)

def tests():
    test_funcs = [base_generator_test, test_k_generator, nis0_generator_test, flat_generator_test]
    print(f"Running {len(test_funcs)} tests for Stirling Permutation Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()
