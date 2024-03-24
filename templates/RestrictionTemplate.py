# author: antman1935, anthony.lamont99@yahoo.com

from Parameters import CommandParameter, CommandParser, ParamType
from Restriction import Restriction, CacheKeys

class MyRestriction(Restriction):
    """
    TODO: Fill in these fields with appropriate info. The name must be unique among the
    Restriction subclasses.
    """
    name: str = ""
    description: str = ""
    # TODO: delete if you have no parameters.
    parameters: list[CommandParameter] = [
    ]
    parser: CommandParser = CommandParser(parameters)

    """
    TODO: parse your parameters or replace this with 'pass' if
    you have none.
    """
    def parseParameters(self, params: str):
        self.params = MyRestriction.parser.parseInput(params)
        pass

    """
    TODO: compute whether an individual element passes the filter.
    NOTE: If you have another restriction that uses common computed state
    for each element, you can save that state in the cache parameter.
    """
    def passes(self, element, cache: dict = None):
        return True
    
# TODO: Register the class so it is usable in the cli.
Restriction.register(MyRestriction)