# author: antman1935, anthony.lamont99@yahoo.com

from enum import StrEnum

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

            
from Importer import Importer

Importer.importSubdirectory("Restrictions")