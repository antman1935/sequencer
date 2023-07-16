# author: antman1935, anthony.lamont99@yahoo.com

import sys, getopt
from SequencerAPI import PointAPI, RangeAPI
from Restrictions import Restriction
from CatalanWords import CatalanGeneratorCmd
from FubiniRankings import FubiniGeneratorCmd
from ParkingFunctions import ParkingFunctionGeneratorCmd
from StirlingPermutations import StirlingGeneratorCmd
from TypeBPartitions import TypeBPartitionGeneratorCmd

apis = [PointAPI, RangeAPI]
commands = [CatalanGeneratorCmd, FubiniGeneratorCmd, ParkingFunctionGeneratorCmd, StirlingGeneratorCmd, TypeBPartitionGeneratorCmd]

def main(argv):
    api = None
    api_params = None
    command = None
    command_params = None
    restriction_list = []
    help_requested = False

    api_dict = {apiClass.name.lower(): apiClass for apiClass in apis}
    command_dict = {commandClass.name.lower(): commandClass for commandClass in commands}

    try:
        opts, args = getopt.getopt(argv,"ha:c:r:",["api=", "command=", "restrictions="])
    except getopt.GetoptError:
        print(f"usage: SequencerCLI.py -a api_name/api_arguments -c command/command_arguments -r restrictions_list")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help_requested = True
        elif opt in ["-a", "--api"]:
            api_args = arg.split("/")
            api_name = api_args[0].lower()
            api = api_dict[api_name]
            api_params = "/".join(api_args[1:])
        elif opt in ["-c", "--command"]:
            cmd_args = arg.split("/")
            cmd_name = cmd_args[0].lower()
            command = command_dict[cmd_name]
            command_params = "/".join(cmd_args[1:])
        elif opt in ["-r", "--restrictions"]:
            print("parsing restriction", arg)
            res = []
            res_tokens = arg.split("//")
            for res_token in res_tokens:
                res.append(Restriction.parse(res_token))
            restriction_list.append(res)

    if help_requested:
        print(f"usage: SequencerCLI.py -a api_name/api_arguments -c command/command_arguments -r restrictions_list")
        if api is None:
            print("API hasn't been set(-a/--api API name[/parameter_name:parameter_value]). Choose from:")
            for h_api in apis:
                print(f"\t-{h_api.name} - {h_api.description}")
                print("\tParameters:")
                for param in h_api.parameters:
                    print(f"\t\t{param}")
                print("")
        else:
            print(f"{api.name} API selected. Parameters:")
            for param in api.parameters:
                print(f"\t{param}")
            print("")
        if command is None:
            print("Command hasn't been set(-c/--command Command name[/parameter_name:parameter_value]). Choose from:")
            for cmd in commands:
                print(f"\t-{cmd.name} - {cmd.description}")
                print("\tParameters:")
                for param in cmd.parameters:
                    print(f"\t\t{param}")
                print("")
        else:
            print(f"{command.name} command selected. Parameters:")
            for param in command.parameters:
                print(f"\t{param}")
            print("")
        sys.exit()

    if api is None or command is None:
        print(f"usage: SequencerCLI.py -a api_name/api_arguments -c command/command_arguments")
        sys.exit(2)

    api_inst = api(api_params)
    cmd_inst = command(command_params)
    cmd_inst.setRestrictions(restriction_list)
    
    api_inst.setCommand(cmd_inst)
    api_inst.execute()
            


if __name__ == "__main__":
   main(sys.argv[1:])