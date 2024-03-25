# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys
from WordStatistics import makeWord

class FlatRestriction(Restriction):
    name: str = "flat"
    description: str = "Only accepts flat words."
    parameters: list[CommandParameter] = [
        CommandParameter("weak_ascents", False, ParamType.BOOL, "If true, runs use weak inequality for ascents. If false, runs use strict inequality for ascents."),
        CommandParameter("weak_flat", False, ParamType.BOOL, "If true, omit words where run starts are not weakly increasing. If false, omit words where run starts are not strictly increasing."),
    ]
    parser: CommandParser = CommandParser(parameters)
    def parseParameters(self, params: str):
        params = FlatRestriction.parser.parseInput(params)
        self.weak_ascents = params.get("weak_ascents", True)
        self.weak_flat = params.get("weak_flat", True)

    def passes(self, element, cache: dict = None):
        word = None
        if cache is None:
            word = makeWord(element)
        else:
            if not CacheKeys.WORD in cache:
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        return word.isFlattened(weak_ascents=self.weak_ascents, weak=self.weak_flat)
Restriction.register(FlatRestriction)