from contextlib import redirect_stdout
from io import StringIO

import Commands.CommandRegistration  # registers all commands
from CmdTools import Command
from Parameters import ParamType
from Restriction import Restriction
from SequencerAPI import SequencerAPI
from Statistic import Statistic


def format_parameters(values: dict[str, object]) -> str:
    parts = []
    for name, value in values.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        parts.append(f"{name}:{value}")
    return "/".join(parts)


def instantiate_command(command_name: str, parameters: dict[str, object]):
    command_class = Command.commands[command_name]
    return command_class(format_parameters(parameters))


def execute_point_query(command_name: str, parameters: dict[str, object], statistic_name: str | None = None, print_elements: bool = False) -> str:
    command = instantiate_command(command_name, parameters)
    api = SequencerAPI.apis["point"](format_parameters({"p": print_elements}))
    api.setCommand(command)
    api.setStatistic(None if statistic_name is None else Statistic.statistics[statistic_name]())

    output = StringIO()
    with redirect_stdout(output):
        api.execute()
    return output.getvalue()


def coerce_value(param_type: ParamType, value: object):
    if param_type == ParamType.BOOL:
        return bool(value)
    if value is None or value == "":
        return None
    return ParamType.validateAndConvertParameter(param_type, str(value))
