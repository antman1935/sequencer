from Statistic import Statistic
from WordStatistics import makeWord

class Runs(Statistic):
    name: str = 'runs'
    ui_name: str = 'Runs'
    ui_description: str = 'Count the number of runs in a list - maximal sequences of strictly increasing elements.'

    def __init__(self):
        super().__init__()

    def calc(self, element):
        w = makeWord(element)
        return w.getNumRuns(weak=False)

Statistic.register(Runs)