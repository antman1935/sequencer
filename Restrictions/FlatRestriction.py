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
                cache[CacheKeys.WORD] = makeWord(element)
            word = cache[CacheKeys.WORD]
        return word.isFlattened()
Restriction.register(FlatRestriction)