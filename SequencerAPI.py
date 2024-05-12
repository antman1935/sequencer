# author: antman1935, anthony.lamont99@yahoo.com

from CmdTools import Command
from Statistic import Statistic

class SequencerAPI:
    apis = {}
    def __init__(self):
        self.cmd = None
        self.stat = None
    def execute(self):
        raise Exception("unimplemented")
    def setCommand(self, cmd: Command):
        self.cmd = cmd
    def setStatistic(self, stat: Statistic):
        self.stat = stat
    def register(APIClass):
        assert not APIClass.name in SequencerAPI.apis, f"The name {APIClass.name} is already associated with {SequencerAPI.apis[APIClass.name]}. Registering api {APIClass} failed."
        SequencerAPI.apis[APIClass.name] = APIClass

SequencerAPI.register = staticmethod(SequencerAPI.register)

from Importer import Importer

Importer.importSubdirectory("API")