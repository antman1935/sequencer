# author: antman1935, anthony.lamont99@yahoo.com

from enum import StrEnum
from Parameters import CommandParameter, CommandParser, ParamType
from WordStatistics import makeWord

class CacheKeys(StrEnum):
    WORD = "word"

class Restriction:
    restrictions = {}
    def parseParameters(self, params: str):
        raise Exception("not implemented")
    def passes(self, element, cache: dict = None):
        raise Exception("not implemented")
    def register(RestrictionSubclass):
        assert not RestrictionSubclass.name in Restriction.restrictions
        Restriction.restrictions[RestrictionSubclass.name] = RestrictionSubclass
    def parse(restriction: str):
        res_tokens = restriction.split("/")
        assert res_tokens[0] in Restriction.restrictions, f"Invalid restriction type given: {res_tokens[0]}"
        res = Restriction.restrictions[res_tokens[0]]()
        res.parseParameters("/".join(res_tokens[1:]))
        return res
                
Restriction.parse = staticmethod(Restriction.parse)
Restriction.register = staticmethod(Restriction.register)
    
class FlatRestriction(Restriction):
    name: str = "flat"
    description: str = "Only accepts flat words."
    def parseParameters(self, params: str):
        pass
    def passes(self, element, cache: dict = None):
        word = None
        if cache is None:
            word = makeWord(element)
        else:
            if not CacheKeys.WORD in cache:
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        return word.isFlattened()
Restriction.register(FlatRestriction)
    
class NonflatRestriction(Restriction):
    name: str = "nonflat"
    description: str = "Only accepts nonflat words."
    def parseParameters(self, params: str):
        pass
    def passes(self, element, cache: dict = None):
        word = None
        if cache is None:
            word = makeWord(element)
        else:
            if not CacheKeys.WORD in cache:
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        return not word.isFlattened()
Restriction.register(NonflatRestriction)
    
class PeakRestriction(Restriction):
    name: str = "peaks"
    description: str = "Only accepts word whose peaks match the given peakset."
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
        return not word.matchesPeakSet(self.peakset)
Restriction.register(PeakRestriction)

            
