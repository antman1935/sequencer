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
This class allows us to pass arguments to the fubini ranking
generator below to allow any of the following restrictions to the
rankings we generate:

1. n - The number of positions to give rankings.
2. k - The maximum number of positions in an individual tie. E.g
       [1,2,2,4,4,6,6,6] has 2 ties between two positions (2/4) and 1
       tie between 3 positions, so k < 3 would cause this fubini
       ranking to be omitted by the generator.
3. t - The maximum number of ties. [1,2,2,4,4,6,6,6] has 3 ties, so
       t < 3 would cause this fubini ranking to be omitted.
4. r - First r positions must be distinct. For r=2, [1,3,1] is valid
       but [1,1,3] is not.
"""
class FubiniGeneratorOptions(CommandOptions):
    def __init__(self, n, k = None, t = None, r = None):
        self.n = n
        self.k = k
        self.t = t
        self.r = r

    def getParameters(self):
        return {"n": self.n, "k": self.k, "t": self.t, 'r': self.r}

"""
This class takes in a string with all the necessary and optional
parameters for this generator and gives access to the generator with
those parameters.
"""
class FubiniGeneratorCmd(Command):
    name: str = "fubini"
    description: str = "Fubini Rankings"
    ui_name: str = description
    ui_description: str = "Fubini rankings are rankings of n competitors so that if j competitors take spot i, then the next ranking in increasing order must be rank i + j."
    parameters: list[CommandParameter] = [
        CommandParameter("k", False, ParamType.INT_POS, "The maximum number of positions in an individual tie."),
        CommandParameter("n", True, ParamType.INT_POS, "The number of positions to give a rank."),
        CommandParameter("t", False, ParamType.NATURAL, "The maximum number of ties."),
        CommandParameter("r", False, ParamType.INT_POS, "First r elements of ranking must be distinct"),
    ]
    parser: CommandParser = CommandParser(parameters)
    options_class = FubiniGeneratorOptions


    def __init__(self, param_str: str):
        super().__init__()
        params = FubiniGeneratorCmd.parser.parseInput(param_str)
        self.options = FubiniGeneratorOptions(params["n"], params.get("k", None), params.get("t", None), params.get("r", None))

    def internal_generator(self):
        for word in generateFubiniRankings(self.options):
            yield word

    def __str__(self):
        params = self.options.getParameters()
        return f"FubiniRankings({'|'.join([str(key) + ':' + str(value) for key, value in params.items() if not value is None])})"

#####################################################################
#                                                                   #
# Generator Code                                                    #
#                                                                   #
#####################################################################

from typing import Optional

def placeAvailable(i: int, places: dict[int, int], k: Optional[int] = None, t: Optional[int] = None):
    check_i = places[i] + i
    if t is not None and places[i] > 0 and sum([places[j] > 1 for j in places if j != i]) == t:
        return False
    if k is not None and places[i] == k:
        return False
    if check_i > len(places) or places[check_i] > 0:
        return False
    if sum([places[j] + j - 1 >= check_i for j in places if j < i]) > 0:
        return False
    return True

def generateFubiniRankings(options: FubiniGeneratorOptions):
    def helper(current_ranking, places):
        if len(current_ranking) == options.n:
            yield current_ranking[:]
        else:
            for i in range(1, options.n+1):
                if options.r is not None:
                    if len(current_ranking) < options.r and i in current_ranking:
                        continue
                if placeAvailable(i, places, options.k, options.t):
                    places[i] += 1
                    current_ranking.append(i)
                    for ranking in helper(current_ranking, places):
                        yield ranking
                    places[i] -= 1
                    current_ranking.pop()
        return

    for ranking in helper([], {i+1:0 for i in range(options.n)}):
        yield ranking

#####################################################################
#                                                                   #
# Tests                                                             #
#                                                                   #
#####################################################################
        
def distinct_generator_test():
    param_str = "n:3/r:2"
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

    cmd = FubiniGeneratorCmd(param_str)
    return Command.generator_test(f"Running Fubini generator test ({param_str})", cmd.generator(), expected_values)

def base_generator_test():
    param_str = "n:3"
    expected_values = [
        [1,1,1],
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

    cmd = FubiniGeneratorCmd(param_str)
    return Command.generator_test(f"Running Fubini generator test ({param_str})", cmd.generator(), expected_values)

def test_k_generator():
    param_str = "n:3/k:2"
    expected_values = [
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

    cmd = FubiniGeneratorCmd(param_str)
    return Command.generator_test(f"Running Fubini generator test ({param_str})", cmd.generator(), expected_values)

def test_t_generator():
    param_str = "n:3/k:3/t:0"
    expected_values = [
        [1,2,3],
        [1,3,2],
        [2,1,3],
        [2,3,1],
        [3,1,2],
        [3,2,1],
    ]

    cmd = FubiniGeneratorCmd(param_str)
    return Command.generator_test(f"Running Fubini generator test ({param_str})", cmd.generator(), expected_values)

def nis0_generator_test():
    param_str = "n:0"
    expected_values = [
        [],
    ]

    cmd = FubiniGeneratorCmd(param_str)
    return Command.generator_test(f"Running Fubini generator test ({param_str})", cmd.generator(), expected_values)

def tests():
    test_funcs = [distinct_generator_test, base_generator_test, test_k_generator, test_t_generator, nis0_generator_test]
    print(f"Running {len(test_funcs)} tests for Fubini Generator.")
    success = sum([func() for func in test_funcs])
    print(f"{success}/{len(test_funcs)} tests passed.")

if __name__ == "__main__":
    tests()