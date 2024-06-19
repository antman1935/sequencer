from Statistic import Statistic

class MultiplicitousSum(Statistic):
    name: str = 'multiplicitous_sum'
    ui_name: str = 'Multiplicitous Sum'
    ui_description: str = 'Return the sum of all occurrences of the elements that are multiplicitous - appear more than once.'

    def __init__(self):
        super().__init__()

    def calc(self, element):
        elms = {}
        for elm in element:
            if not elm in elms:
                elms[elm] = 0
            elms[elm] += 1
        return sum([value for _, value in elms.items() if value > 1])

Statistic.register(MultiplicitousSum)