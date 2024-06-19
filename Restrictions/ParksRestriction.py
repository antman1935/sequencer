# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys

class ParksRestriction(Restriction):
    name: str = "parks"
    description: str = "Omit words that are not valid parking functions."
    parameters = []

    def parseParameters(self, params: str):
        pass

    """
    Checks if an array of integers is successful as a parking function.
    In order, it tries to park each 'car' by their preference. If all cars
    park, we return true.
    """
    def passes(self, element, cache: dict = None):
        assert min(element) >= 1, "parking functions must be 1 indexed."
        spots = [False for _ in element]
        for pref in element:
            cur = pref - 1 # zero index
            while cur < len(spots) and spots[cur]:
                cur += 1
            if cur == len(spots):
                return False
            spots[cur] = True
        return True
    
Restriction.register(ParksRestriction)