from Statistic import Statistic

class MultiplicitousCount(Statistic):
    name: str = 'multiplicitous_count'
    ui_name: str = 'Multiplicitous Count'
    ui_description: str = 'Return the count of elements that are multiplicitous - appear more than once.'

    def __init__(self):
        super().__init__()

    def calc(self, element):
        elms = {}
        for elm in element:
            if not elm in elms:
                elms[elm] = 0
            elms[elm] += 1
        return sum([value > 1 for _, value in elms.items()])

Statistic.register(MultiplicitousCount)