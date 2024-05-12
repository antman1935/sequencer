
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
        pass
    
    def register(statisticClass):
        assert not statisticClass.name in Statistic.statistics, f"The name {statisticClass.name} is already associated with the stat {Statistic.statistics[statisticClass.name]}. Registering {statisticClass} failed."
        Statistic.statistics[statisticClass.name] = statisticClass

Statistic.register = staticmethod(Statistic.register)

from Importer import Importer

Importer.importSubdirectory("Statistics")