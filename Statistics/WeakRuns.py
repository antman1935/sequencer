from Statistic import Statistic
from WordStatistics import makeWord

class WeakRuns(Statistic):
    name: str = 'weak_runs'
    ui_name: str = 'Weak Runs'
    ui_description: str = 'Count the number of weak runs in a list - maximal sequences of weakly increasing elements.'

    def __init__(self):
        super().__init__()

    def calc(self, element):
        w = makeWord(element)
        return w.getNumRuns(weak=True)

Statistic.register(WeakRuns)