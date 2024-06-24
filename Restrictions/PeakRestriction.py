# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys
from WordStatistics import makeWord

class PeakRestriction(Restriction):
    name: str = "peaks"
    description: str = "Only accepts word whose peaks match the given peakset."
    ui_name: str = "Peaks"
    ui_description: str = description
    parameters: list[CommandParameter] = [
        CommandParameter("peaks", True, ParamType.LIST_INT_POS, "The list of 1-indexed peak indices."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def parseParameters(self, params: str):
        self.peakset = PeakRestriction.parser.parseInput(params)["peaks"]
    def passes(self, element, cache: dict = None):
        word = None
        if cache is None:
            word = makeWord(element)
        else:
            if not CacheKeys.WORD in cache:
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        return word.matchesPeakSet(self.peakset)
Restriction.register(PeakRestriction)