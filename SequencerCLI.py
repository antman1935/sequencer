# author: antman1935, anthony.lamont99@yahoo.com

import sys, getopt
from SequencerAPI import SequencerAPI
from Restriction import Restriction
from CmdTools import Command
from Statistic import Statistic
import Commands.CommandRegistration # registers all commands

def api_check():
    for _, api in SequencerAPI.apis.items():
        assert not "," in api.name, f"Cannot have ',' in API name: {api.name}"
        assert not "-" in api.name, f"Cannot have '-' in API name: {api.name}"

    for _, cmd in Command.commands.items():
        assert not "," in cmd.name, f"Cannot have ',' in command name: {cmd.name}"
        assert not "-" in cmd.name, f"Cannot have '-' in command name: {cmd.name}"

        for param in cmd.parameters:
            assert not "," in param.name, f"Cannot have ',' in command parameter name: {cmd.name} - {param.name}"
            assert not "-" in param.name, f"Cannot have '-' in command parameter name: {cmd.name} - {param.name}"

    for _, res in Restriction.restrictions.items():
        assert not "," in res.name, f"Cannot have ',' in command name: {res.name}"
        assert not "-" in res.name, f"Cannot have '-' in command name: {res.name}"

        for param in res.parameters:
            assert not "," in param.name, f"Cannot have ',' in parameter name: {res.name} - {param.name}"
            assert not "-" in param.name, f"Cannot have '-' in parameter name: {res.name} - {param.name}"
    

def main(argv):
    usage_string = "usage: SequencerCLI.py -a api_name/api_arguments -c command/command_arguments (-r restrictions_list)*"
    api = None
    api_params = None
    command = None
    command_params = None
    stat = None
    restriction_list = []
    help_requested = False

    api_check()

    try:
        opts, args = getopt.getopt(argv,"ha:c:r:s:",["api=", "command=", "restrictions=", 'stat='])
    except getopt.GetoptError:
        print(f"usage: SequencerCLI.py -a api_name/api_arguments -c command/command_arguments -r restrictions_list [-s stat]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help_requested = True
        elif opt in ["-a", "--api"]:
            api_args = arg.split("/")
            api_name = api_args[0].lower()
            api = SequencerAPI.apis[api_name]
            api_params = "/".join(api_args[1:])
        elif opt in ["-c", "--command"]:
            cmd_args = arg.split("/")
            cmd_name = cmd_args[0].lower()
            command = Command.commands[cmd_name]
            command_params = "/".join(cmd_args[1:])
        elif opt in ["-r", "--restrictions"]:
            res = []
            res_tokens = arg.split("//")
            for res_token in res_tokens:
                res.append(Restriction.parse(res_token))
            restriction_list.append(res)
        elif opt in ["-s", "--stat"]:
            print(arg)
            stat_args = arg.split("/")
            stat_name = stat_args[0].lower()
            stat = Statistic.statistics[stat_name]()
            stat.parseParameters("/".join(stat_args[1:]))

    if help_requested:
        print(usage_string)
        if api is None:
            print("API hasn't been set(-a/--api API name[/parameter_name:parameter_value]). Choose from:")
            for h_api in SequencerAPI.apis.values():
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
            for cmd in Command.commands.values():
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
        
        print("Restrictions (filters) can be set on the datasets you generate. Every time you pass -r on the command line,\n"
              "you give a list of restrictions that are evaluated on the element, and the element is included in the dataset\n"
              "if they all evaluate to true. If -r is passed multliple times, an element is included if it passes any\n"
              "restriction list. Syntax for -r parameter: restriction_name(/param:value*)(//restriction_name(/param:value*)*)\n"
              "Here is the full list of restrictions available:")
        for res in Restriction.restrictions.values():
                print(f"\t-{res.name} - {res.description}")
                if not hasattr(res, "parameters"):
                    print("")
                    continue
                print("\tParameters:")
                for param in res.parameters:
                    print(f"\t\t{param}")
                print("")
        sys.exit()

    if api is None or command is None:
        print(usage_string)
        sys.exit(2)

    api_inst = api(api_params)
    cmd_inst = command(command_params)
    cmd_inst.setRestrictions(restriction_list)
    
    api_inst.setCommand(cmd_inst)
    api_inst.setStatistic(stat)
    api_inst.execute()
            


if __name__ == "__main__":
   main(sys.argv[1:])