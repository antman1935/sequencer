from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import Any

import Commands.CommandRegistration  # registers all commands
from API.RangeAPI import getTableBounds, invert, printResults
from CmdTools import Command
from Parameters import OutputType, ParamType
from Restriction import Restriction
from SequencerAPI import SequencerAPI
from Statistic import Dimension, DimensionType, Statistic


@dataclass
class RangeTable:
    label: str
    row_bounds: tuple[int, int]
    row_dimension: str
    column_bounds: tuple[int, int]
    column_dimension: str
    data: list[list[int]]


@dataclass
class QueryResult:
    summary: str
    text: str
    tables: list[RangeTable]


def format_parameters(values: dict[str, object]) -> str:
    parts = []
    for name, value in values.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        if isinstance(value, OutputType):
            value = output_token(value)
        if isinstance(value, list):
            if all(isinstance(item, Dimension) for item in value):
                value = ",".join(f"{item.name}-{'parameter' if item.dim_type == DimensionType.PARAMETER else 'computed'}" for item in value)
            else:
                value = ",".join(str(item) for item in value)
        parts.append(f"{name}:{value}")
    return "/".join(parts)


def output_token(output_type: OutputType) -> str:
    return {
        OutputType.OEIS_LOOKUP: "oeis",
        OutputType.RAW: "raw",
        OutputType.ASCII_TABLE: "ascii",
        OutputType.LATEX_TABLE: "latex",
    }[output_type]


def instantiate_command(command_name: str, parameters: dict[str, object], restriction_groups: list[list[tuple[str, dict[str, object]]]] | None = None):
    command_class = Command.commands[command_name]
    command = command_class(format_parameters(parameters))
    command.setRestrictions(instantiate_restrictions(restriction_groups))
    return command


def instantiate_restrictions(restriction_groups: list[list[tuple[str, dict[str, object]]]] | None):
    groups = []
    for group in restriction_groups or []:
        parsed_group = []
        for restriction_name, parameters in group:
            parsed_group.append(Restriction.parse(restriction_name + _formatted_suffix(parameters)))
        if parsed_group:
            groups.append(parsed_group)
    return groups


def _formatted_suffix(parameters: dict[str, object]) -> str:
    formatted = format_parameters(parameters)
    return f"/{formatted}" if formatted else ""


def execute_point_query(command_name: str, parameters: dict[str, object], statistic_name: str | None = None, print_elements: bool = False) -> str:
    return run_point_query(command_name, parameters, statistic_name, print_elements).text


def run_point_query(command_name: str, parameters: dict[str, object], statistic_name: str | None = None, print_elements: bool = False, restriction_groups: list[list[tuple[str, dict[str, object]]]] | None = None) -> QueryResult:
    command = instantiate_command(command_name, parameters, restriction_groups)
    api = SequencerAPI.apis["point"](format_parameters({"p": print_elements}))
    api.setCommand(command)
    api.setStatistic(None if statistic_name is None else Statistic.statistics[statistic_name]())

    output = StringIO()
    with redirect_stdout(output):
        api.execute()
    text = output.getvalue()
    return QueryResult(f"Point query on {command}", text, [])


def run_range_query(
    command_name: str,
    parameters: dict[str, object],
    dimensions: list[Dimension],
    statistic_name: str | None = None,
    print_elements: bool = False,
    output_type: OutputType = OutputType.ASCII_TABLE,
    restriction_groups: list[list[tuple[str, dict[str, object]]]] | None = None,
) -> QueryResult:
    command = instantiate_command(command_name, parameters, restriction_groups)
    stat = None if statistic_name is None else Statistic.statistics[statistic_name]()
    api = SequencerAPI.apis["range"](format_parameters({"dimensions": dimensions, "p": print_elements, "out": output_type}))
    api.setCommand(command)
    api.setStatistic(stat)

    captured = StringIO()
    with redirect_stdout(captured):
        ranged_params = [dim for dim in api.dimensions if dim.dim_type == DimensionType.PARAMETER]
        ranged_param_names = [dim.name for dim in ranged_params]
        count: dict[Any, Any] = {}
        api._iterate(count, ranged_params, 0, {k: v for k, v in api.param_limits.items() if k not in ranged_param_names})

    dimension_names = [dim.name for dim in reversed(api.dimensions)]
    tables = range_tables(count, dimension_names) if len(dimension_names) >= 2 and output_type == OutputType.ASCII_TABLE else []

    formatted = StringIO()
    with redirect_stdout(formatted):
        print(f"Range Query on {command}. Dimensions are {[dim.name for dim in api.dimensions]}.")
        if print_elements and captured.getvalue():
            print("Elements:")
            print(captured.getvalue(), end="")
        printResults(output_type, count, dimension_names)

    return QueryResult(f"Range query on {command}", formatted.getvalue(), tables)


def range_tables(result, dimensions: list[str]) -> list[RangeTable]:
    tables: list[RangeTable] = []

    def add_table(label, row_bounds, row_dim, column_bounds, column_dim, data):
        tables.append(RangeTable(label, row_bounds, row_dim, column_bounds, column_dim, data))

    if len(dimensions) == 2:
        column_bounds, row_bounds = getTableBounds(result)
        row_dim, column_dim = reversed(dimensions)
        data = invert(result)
        rows = [
            [0 if c not in data.get(r, {}) else data[r][c] for c in range(column_bounds[0], column_bounds[1] + 1)]
            for r in range(row_bounds[0], row_bounds[1] + 1)
        ]
        add_table("", row_bounds, row_dim, column_bounds, column_dim, rows)
        return tables

    from API.RangeAPI import printMultipleTables

    printMultipleTables(result, dimensions, add_table)
    return tables


def run_query(
    api_name: str,
    command_name: str,
    parameters: dict[str, object],
    statistic_name: str | None = None,
    print_elements: bool = False,
    dimensions: list[Dimension] | None = None,
    output_type: OutputType = OutputType.ASCII_TABLE,
    restriction_groups: list[list[tuple[str, dict[str, object]]]] | None = None,
) -> QueryResult:
    if api_name == "point":
        return run_point_query(command_name, parameters, statistic_name, print_elements, restriction_groups)
    if api_name == "range":
        if not dimensions:
            raise ValueError("Select at least one range dimension.")
        return run_range_query(command_name, parameters, dimensions, statistic_name, print_elements, output_type, restriction_groups)
    raise ValueError(f"Unsupported API: {api_name}")


def coerce_value(param_type: ParamType, value: object):
    if param_type == ParamType.BOOL:
        return bool(value)
    if isinstance(value, OutputType):
        return value
    if value is None or value == "":
        return None
    return ParamType.validateAndConvertParameter(param_type, str(value))
