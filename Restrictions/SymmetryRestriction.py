# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys
from WordStatistics import makeWord

class SymmetryRestriction(Restriction):
    name: str = "symmetric"
    description: str = "Omits elements that are not symmetric."
    parameters: list[CommandParameter] = [
        CommandParameter("total", False, ParamType.BOOL, "If false, the word must be piecewise symmetric. Otherwise, the entire word must be symmetric."),
        CommandParameter("is", False, ParamType.BOOL, "If true, filter our words that are not symmetric. If false, filter out words that are symmetric."),
        CommandParameter("peak_length", False, ParamType.INT_POS, "Maximum length of a peak to consider symmetric."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def parseParameters(self, params: str):
        self.params = SymmetryRestriction.parser.parseInput(params)
        self.total = self.params.get("total", True)
        self.dir = self.params.get("is", True)
        self.peak_length = self.params.get("peak_length", 1)
        pass

    def passes(self, element, cache: dict = None):
        word = None
        if cache is None:
            word = makeWord(element)
        else:
            if not CacheKeys.WORD in cache:
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        val = word.isCompletelySymmetric(self.peak_length) if self.total else word.isSymmetric(self.peak_length)
        return self.dir == val
    
Restriction.register(SymmetryRestriction)