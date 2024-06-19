from enum import Enum

"""
Dimensions are used as parameters to at least the RangeAPI. You can pass any
of the defined computed statistics or any of the parameters of the Command
as a dimension.
"""
class DimensionType(Enum):
    PARAMETER = 1
    COMPUTED = 2

class Dimension:
    def __init__(self, dim_type, name):
        self.dim_type = dim_type
        self.name = name

"""
Base class for all of the statistics we'll create. Has a calc function called in
each api on each element.
"""
class Statistic:
    statistics = {}
    def __init__(self):
        pass

    def calc(self, element):
        raise Exception("unimplemented")
    
    def parseParameters(self, params: str):
        # TODO: refactor to allow parameters to these statistics. Merge WeakRuns and Runs into one class.
        pass
    
    def register(statisticClass):
        assert not statisticClass.name in Statistic.statistics, f"The name {statisticClass.name} is already associated with the stat {Statistic.statistics[statisticClass.name]}. Registering {statisticClass} failed."
        Statistic.statistics[statisticClass.name] = statisticClass

Statistic.register = staticmethod(Statistic.register)

from Importer import Importer

Importer.importSubdirectory("Statistics")