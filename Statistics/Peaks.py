from Statistic import Statistic
from WordStatistics import makeWord

class Peaks(Statistic):
    name: str = 'peaks'

    def __init__(self):
        super().__init__()

    def calc(self, element):
        return len(makeWord(element).getPeaks())

Statistic.register(Peaks)
