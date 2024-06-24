# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys

class ZigZagRestriction(Restriction):
    name: str = "zigzag"
    description: str = "Omits elements with subsequences (length > 1) of constant chars."
    ui_name: str = "ZigZag"
    ui_description: str = description
    parameters: list[CommandParameter] = [
        CommandParameter("is", False, ParamType.BOOL, "If true, filter our words that are not zigzag. If false, filter out words that are zigzag."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def parseParameters(self, params: str):
        self.params = ZigZagRestriction.parser.parseInput(params)
        self.dir = self.params.get('is', True)

    def _helper(self, element):
        if len(element) == 2:
            return element[0] != element[1]
        for i in range(len(element) - 2):
            if not ((element[i] > element[i+1] and element[i+2] > element[i+1]) or (element[i] < element[i+1] and element[i+2] < element[i+1])):
                return False
        return True
    def passes(self, element, cache: dict = None):
        return self.dir == self._helper(element)
    
Restriction.register(ZigZagRestriction)