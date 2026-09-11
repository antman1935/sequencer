"""The UI contract is derived from the same metadata used by the CLI."""
from dataclasses import asdict

from UI.pyqt_prototype.runner import run_query, output_token
from CmdTools import Command
from Parameters import OutputType, ParamType
from Restriction import Restriction
from SequencerAPI import SequencerAPI
from Statistic import Dimension, DimensionType, Statistic


OUTPUTS = [
    (OutputType.ASCII_TABLE, "Rendered table"),
    (OutputType.OEIS_LOOKUP, "OEIS sequence"),
    (OutputType.RAW, "Raw data"),
    (OutputType.LATEX_TABLE, "LaTeX file"),
]
RANGE_TYPES = (ParamType.NATURAL, ParamType.INT_POS, ParamType.INTEGER, ParamType.BOOL)


def parameter_schema(parameter):
    result = {"name": parameter.name, "required": parameter.required,
              "description": parameter.description, "type": parameter.param_type.name.lower()}
    if parameter.param_type in (ParamType.NATURAL, ParamType.INT_POS):
        result["minimum"] = ParamType.typeMin(parameter.param_type)
    return result


def registry_schema(registry):
    return [{"id": key, "label": cls.ui_name,
             "description": getattr(cls, "ui_description", getattr(cls, "description", "")),
             "parameters": [parameter_schema(p) for p in sorted(getattr(cls, "parameters", []), key=lambda p: not p.required)]}
            for key, cls in registry.items()]


def ui_schema():
    commands = registry_schema(Command.commands)
    for item in commands:
        item["dimensions"] = [{"name": p.name, "kind": "parameter", "label": f"Parameter: {p.name}"}
                              for p in Command.commands[item["id"]].parameters if p.param_type in RANGE_TYPES]
        item["dimensions"] += [{"name": key, "kind": "computed", "label": f"Computed: {cls.ui_name}"}
                               for key, cls in Statistic.statistics.items()]
    return {"apis": registry_schema(SequencerAPI.apis), "commands": commands,
            "statistics": registry_schema(Statistic.statistics),
            "restrictions": registry_schema(Restriction.restrictions),
            "outputs": [{"id": output_token(value), "label": label} for value, label in OUTPUTS]}


def parse_parameters(metadata, values):
    if not isinstance(values, dict):
        raise ValueError("Parameters must be an object.")
    by_name = {p.name: p for p in metadata}
    unknown = values.keys() - by_name.keys()
    if unknown:
        raise ValueError(f"Unknown parameter: {next(iter(unknown))}.")
    result = {}
    for name, parameter in by_name.items():
        raw = values.get(name)
        if raw is None or raw == "":
            if parameter.required:
                raise ValueError(f"{name} is required.")
            continue
        if isinstance(raw, (dict, list)) or (isinstance(raw, bool) and parameter.param_type != ParamType.BOOL):
            raise ValueError(f"{name}: invalid value.")
        try:
            result[name] = ParamType.validateAndConvertParameter(parameter.param_type, str(raw))
        except (ValueError, AssertionError) as exc:
            raise ValueError(f"{name}: {exc}") from exc
    return result


def execute_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("A query must be a JSON object.")
    api = payload.get("api", "point")
    command_name = payload.get("command")
    if not isinstance(api, str) or api not in ("point", "range"):
        raise ValueError("Choose a supported API.")
    if not isinstance(command_name, str) or command_name not in Command.commands:
        raise ValueError("Choose a supported object family.")
    command = Command.commands[command_name]
    parameters = parse_parameters(command.parameters, payload.get("parameters", {}))
    statistic = payload.get("statistic") or None
    if statistic is not None and (not isinstance(statistic, str) or statistic not in Statistic.statistics):
        raise ValueError("Choose a supported statistic.")
    print_elements = payload.get("print_elements", False)
    if not isinstance(print_elements, bool):
        raise ValueError("Show generated elements must be a boolean.")
    output = payload.get("output", "ascii")
    outputs = {output_token(value): value for value, _ in OUTPUTS}
    if not isinstance(output, str) or output not in outputs:
        raise ValueError("Choose a supported output format.")
    groups = payload.get("restriction_groups", [])
    if not isinstance(groups, list):
        raise ValueError("Restriction groups must be a list.")
    restrictions = []
    for group in groups:
        if not isinstance(group, list):
            raise ValueError("Each restriction group must be a list.")
        parsed = []
        for item in group:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or item["name"] not in Restriction.restrictions:
                raise ValueError("Choose a supported restriction.")
            cls = Restriction.restrictions[item["name"]]
            parsed.append((item["name"], parse_parameters(cls.parameters, item.get("parameters", {}))))
        if parsed:
            restrictions.append(parsed)
    dimensions = []
    if api == "range":
        raw_dimensions = payload.get("dimensions", [])
        if not isinstance(raw_dimensions, list) or not raw_dimensions:
            raise ValueError("Select at least one range dimension.")
        allowed = {(p.name, "parameter") for p in command.parameters if p.param_type in RANGE_TYPES}
        allowed |= {(key, "computed") for key in Statistic.statistics}
        seen = set()
        for item in raw_dimensions:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not isinstance(item.get("kind"), str):
                raise ValueError("Invalid range dimension.")
            key = (item["name"], item["kind"])
            if key not in allowed or key in seen:
                raise ValueError("Range dimensions must be valid and unique.")
            seen.add(key)
            dimensions.append(Dimension(DimensionType.PARAMETER if key[1] == "parameter" else DimensionType.COMPUTED, key[0]))
    result = asdict(run_query(api, command_name, parameters, statistic, print_elements,
                             dimensions, outputs[output], restrictions))
    # Counts can exceed JavaScript's safe integer range. Preserve every digit.
    for table in result["tables"]:
        table["data"] = [[str(value) for value in row] for row in table["data"]]
    return result
