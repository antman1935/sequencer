from Statistic import Statistic
from WordStatistics import makeWord

class Peaks(Statistic):
    name: str = 'peaks'
    ui_name: str = 'Peaks'
    ui_description: str = 'Count the number of peaks in a list - non endpoint that is greater than both neighbors.'

    def __init__(self):
        super().__init__()

    def calc(self, element):
        return len(makeWord(element).getPeaks())

Statistic.register(Peaks)
