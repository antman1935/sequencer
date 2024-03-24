# author: antman1935, anthony.lamont99@yahoo.com

from Restriction import Restriction, CacheKeys
from WordStatistics import makeWord

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
                cache[CacheKeys.WORD] = {}
            if not str(element) in cache[CacheKeys.WORD]:
                cache[CacheKeys.WORD][str(element)] = makeWord(element)
            word = cache[CacheKeys.WORD][str(element)]
        return word.isFlattened()
Restriction.register(FlatRestriction)