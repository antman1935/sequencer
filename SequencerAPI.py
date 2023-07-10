from CmdTools import Command, CommandParameter, ParamType, CommandParser
class SequencerAPI:
    def __init__(self):
        self.cmd = None
    def execute(self):
        raise Exception("unimplemented")
    def getParameters():
        raise Exception("unimplemented")
    def setCommand(self, cmd: Command):
        self.cmd = cmd

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


class RangeAPI(SequencerAPI):
    pass

class TableAPI(SequencerAPI):
    pass