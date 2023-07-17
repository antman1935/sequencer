# author: antman1935, anthony.lamont99@yahoo.com

from SequencerAPI import SequencerAPI
from Parameters import CommandParameter, ParamType, CommandParser, OutputType

class PointAPI(SequencerAPI):
    name: str = "point"
    description: str = "Generate the set of objects for one set of parameters."
    parameters: list[CommandParameter] = [
        CommandParameter("p", False, ParamType.BOOL, "Whether to print the list of items."),
    ]
    parser: CommandParser = CommandParser(parameters)

    def __init__(self, param_str: str):
        super().__init__()
        params = PointAPI.parser.parseInput(param_str)
        self.print = params.get("p", False)
    
    def execute(self):
        assert not self.cmd is None
        
        print(f"Point Query on {self.cmd}.")
        if self.print:
            print("Elements:")
        count = 0
        for word in self.cmd.generator():
            count += 1
            if self.print:
                print(f"\t{word}")
        print(f"|{self.cmd}| = {count}")

SequencerAPI.register(PointAPI)