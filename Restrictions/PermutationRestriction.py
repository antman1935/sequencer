# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys
from WordStatistics import makeWord

class PermutationRestriction(Restriction):
    name: str = "perm"
    description: str = "Can filter out words that are or are not permutations."
    # TODO: delete if you have no parameters.
    parameters: list[CommandParameter] = [
        CommandParameter("is", False, ParamType.BOOL, "If true, filter our words that are not permutations. If false, filter out words that are permutations."),
    ]
    parser: CommandParser = CommandParser(parameters)


    def parseParameters(self, params: str):
        self.params = PermutationRestriction.parser.parseInput(params)
        self.dir = self.params.get('is', True)

    def passes(self, element, cache: dict = None):
        word = None
        if cache is None:
            word = makeWord(element)
        else:
            if not CacheKeys.WORD in cache:
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        return self.dir == word.isPermutation()
    
Restriction.register(PermutationRestriction)