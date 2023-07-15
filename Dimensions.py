from enum import Enum

class DimensionType(Enum):
    PARAMETER = 1
    COMPUTED = 2

class Dimension:
    def __init__(self, dim_type, name):
        self.dim_type = dim_type
        self.name = name

class ParameterDimension(Dimension):
    def __init__(self, name):
        super().__init__(DimensionType.PARAMETER, name)

class DimensionComputation:
    def __init__(self, name: str, description: str, function):
        self.name = name
        self.description = description
        self.function = function

def getMultiplicityG1Count(word: list[int]):
    elms = {}
    for elm in word:
        if not elm in elms:
            elms[elm] = 0
        elms[elm] += 1
    return sum([value > 1 for _, value in elms.items()])

def getMultiplicityG1Sum(word: list[int]):
    elms = {}
    for elm in word:
        if not elm in elms:
            elms[elm] = 0
        elms[elm] += 1
    return sum([value for _, value in elms.items() if value > 1])

computed_dims = [
    DimensionComputation("mult>1", "Returns the number of elements in the word with multiplicity > 1", getMultiplicityG1Count),
    DimensionComputation("Sum(mult>1)", "Returns the sum of the multiplicity of the elements with multiplicity > 1", getMultiplicityG1Sum),
]

for dim in computed_dims:
    assert not "," in dim.name, f"Cannot have ',' in computed dimension name: {dim.name}"
    assert not "-" in dim.name, f"Cannot have '-' in computed dimension name: {dim.name}"

class ComputedDimension(Dimension):
    computed_statistics = {dim.name: dim for dim in computed_dims}

    def __init__(self, name):
        super().__init__(DimensionType.COMPUTED, name)
        assert self.name in ComputedDimension.computed_statistics, f"Computed dimension {self.name} does not exist."
        self.func = ComputedDimension.computed_statistics[self.name].function

    def compute(self, word):
        return self.func(word)