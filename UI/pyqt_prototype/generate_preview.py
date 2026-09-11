import html
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Commands.CommandRegistration  # registers all commands
from CmdTools import Command
from Parameters import OutputType
from Statistic import Dimension, DimensionType, Statistic
from UI.pyqt_prototype.runner import run_query
from UI.pyqt_prototype.theme import COLORS, LAYOUT, TYPOGRAPHY

PREVIEW_PATH = Path(__file__).with_name("preview.html")
SVG_PREVIEW_PATH = Path(__file__).with_name("preview.svg")


def parameter_rows(command_name):
    command_class = Command.commands[command_name]
    rows = []
    sample_values = {"n": "3"}
    for parameter in sorted(command_class.parameters, key=lambda p: not p.required):
        required = "  *" if parameter.required else ""
        description = html.escape(parameter.description or "Optional value")
        value = sample_values.get(parameter.name, "unset")
        rows.append(
            f"""
            <section class="parameter-row">
              <div class="field-label">{html.escape(parameter.name)}{required}</div>
              <div class="field-hint">{description}</div>
              <div class="input">{html.escape(value)}</div>
            </section>
            """
        )
    return "\n".join(rows)


def options(registry, selected_key):
    return "\n".join(
        f'<option {"selected" if key == selected_key else ""}>{html.escape(item.ui_name)}</option>'
        for key, item in registry.items()
    )


def result_table_html(table):
    row_start, row_end = table.row_bounds
    col_start, col_end = table.column_bounds
    headers = "".join(f"<th>{html.escape(table.column_dimension)}={col}</th>" for col in range(col_start, col_end + 1))
    rows = []
    for row_number, values in zip(range(row_start, row_end + 1), table.data):
        cells = "".join(f"<td>{'' if value == 0 else value}</td>" for value in values)
        rows.append(f"<tr><th>{html.escape(table.row_dimension)}={row_number}</th>{cells}</tr>")
    title = f'<div class="table-title">{html.escape(table.label or "Rendered range table")}</div>'
    return f"{title}<table><thead><tr><th></th>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def preview_data():
    command_name = "fubini" if "fubini" in Command.commands else next(iter(Command.commands))
    result = run_query(
        "range",
        command_name,
        {"n": 3},
        dimensions=[Dimension(DimensionType.PARAMETER, "n"), Dimension(DimensionType.COMPUTED, "runs")],
        output_type=OutputType.ASCII_TABLE,
        restriction_groups=[[('zigzag', {'is': True})]],
    )
    return command_name, result


def build_html():
    command_name, result = preview_data()
    statistic_name = next(iter(Statistic.statistics), None)
    statistic_label = "Count objects" if statistic_name is None else "Count objects"
    c = COLORS
    font = TYPOGRAPHY["ui_font"]
    mono = TYPOGRAPHY["mono_font"]
    table = result_table_html(result.tables[0]) if result.tables else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sequencer Prototype Preview</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; width: {LAYOUT['window_width']}px; min-height: {LAYOUT['window_height']}px; background: {c['app_bg']}; color: {c['text']}; font-family: {font}; }}
.app {{ padding: 24px 28px 28px; }}
.eyebrow {{ color: {c['muted']}; font-size: 12px; font-weight: 700; letter-spacing: 1.4px; margin-bottom: 10px; }}
h1 {{ color: {c['title']}; font-size: 26px; line-height: 1.2; margin: 0 0 8px; }}
.subtitle {{ color: {c['muted']}; font-size: 13px; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: {LAYOUT['query_card_width']}px 1fr; gap: 18px; align-items: stretch; min-height: 606px; }}
.card {{ background: {c['card_bg']}; border: 1px solid {c['card_border']}; border-radius: 14px; padding: 20px 22px; box-shadow: 0 12px 28px rgba(15, 23, 42, .08); }}
.card h2 {{ color: {c['title']}; font-size: 17px; margin: 0 0 10px; }}
.help {{ color: {c['muted']}; font-size: 13px; line-height: 1.45; margin-bottom: 18px; }}
.setup {{ display: flex; flex-direction: column; min-height: 606px; }}
.field-block {{ margin-bottom: 13px; }}
.field-label {{ color: #111827; font-size: 13px; font-weight: 750; margin-bottom: 7px; }}
select, .input {{ width: 100%; height: 38px; border: 1px solid {c['input_border']}; border-radius: 8px; background: #fff; color: #111827; font-size: 14px; padding: 0 12px; display: flex; align-items: center; }}
.parameter-list {{ display: flex; flex-direction: column; gap: 10px; margin: 0 0 12px; max-height: 172px; overflow: hidden; }}
.field-hint {{ color: {c['hint']}; font-size: 12px; line-height: 1.35; margin-bottom: 7px; min-height: 16px; }}
.dimension-list {{ border: 1px solid {c['card_border']}; border-radius: 10px; padding: 10px 12px; display: grid; gap: 8px; margin-bottom: 12px; }}
.restriction-list {{ border: 1px solid {c['card_border']}; border-radius: 10px; padding: 10px 12px; display: grid; gap: 8px; margin-bottom: 12px; background: #f8fbff; }}
.restriction-pill {{ border-radius: 999px; background: #e0ecff; color: {c['primary']}; padding: 4px 9px; font-size: 12px; font-weight: 750; width: max-content; }}
.check {{ display: flex; align-items: center; gap: 9px; color: #334155; font-size: 14px; }}
.box {{ width: 16px; height: 16px; border: 1px solid #94a3b8; border-radius: 3px; background: #fff; }}
.box.on {{ background: {c['primary']}; box-shadow: inset 0 0 0 3px #fff; }}
.spacer {{ flex: 1; }}
button {{ width: 100%; height: 42px; border: 0; border-radius: 10px; background: {c['primary']}; color: #fff; font-weight: 750; font-size: 14px; }}
.status {{ color: {c['muted']}; font-size: 13px; margin-top: 10px; }}
.tabs {{ display: flex; gap: 0; margin: 4px 0 0; }}
.tab {{ border: 1px solid {c['card_border']}; border-bottom: 0; border-radius: 8px 8px 0 0; padding: 8px 14px; background: #e8eef7; color: {c['muted']}; font-size: 13px; }}
.tab.active {{ background: #fff; color: {c['title']}; font-weight: 700; }}
.panel {{ border: 1px solid {c['card_border']}; border-radius: 0 12px 12px 12px; height: 490px; padding: 20px; background: #fff; }}
.table-title {{ color: {c['title']}; font-weight: 750; margin-bottom: 14px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
th {{ background: #eef4ff; color: {c['title']}; font-weight: 700; }}
th, td {{ border: 1px solid {c['card_border']}; padding: 10px 12px; text-align: center; }}
td {{ color: {c['text']}; }}
.output-note {{ margin-top: 18px; border-radius: 12px; background: {c['output_bg']}; color: {c['output_muted']}; padding: 14px; font: 12px/1.45 {mono}; }}
</style>
</head>
<body>
  <main class="app">
    <div class="eyebrow">SEQUENCER PROTOTYPE</div>
    <h1>Build mathematical queries directly from Python metadata</h1>
    <div class="subtitle">Python-first Qt coverage for point and range queries, with real rendered range tables.</div>
    <div class="grid">
      <section class="card setup">
        <h2>Query setup</h2>
        <div class="help">Choose API, object family, optional statistic, and typed parameters.</div>
        <div class="field-block"><div class="field-label">API</div><select><option selected>Range</option></select></div>
        <div class="field-block"><div class="field-label">Object</div><select>{options(Command.commands, command_name)}</select></div>
        <div class="field-block"><div class="field-label">Statistic</div><select><option selected>{html.escape(statistic_label)}</option></select></div>
        <div class="field-block"><div class="field-label">Range output</div><select><option selected>Rendered table</option></select></div>
        <div class="parameter-list">{parameter_rows(command_name)}</div>
        <div class="field-label">Range dimensions</div>
        <div class="dimension-list">
          <label class="check"><span class="box on"></span><span>Parameter: n</span></label>
          <label class="check"><span class="box on"></span><span>Computed: Runs</span></label>
          <label class="check"><span class="box"></span><span>Computed: Weak Runs</span></label>
        </div>
        <div class="field-label">Restrictions</div>
        <div class="restriction-list">
          <div class="restriction-pill">Group 1 · all selected must pass</div>
          <label class="check"><span class="box on"></span><span>ZigZag · is = true</span></label>
        </div>
        <label class="check"><span class="box"></span><span>Show generated elements</span></label>
        <div class="spacer"></div>
        <button>Run query</button>
        <div class="status">Complete</div>
      </section>
      <section class="card">
        <h2>Result</h2>
        <div class="help">Range table output is rendered as selectable Qt tables; text output remains available. This preview applies the ZigZag restriction.</div>
        <div class="tabs"><div class="tab">Text</div><div class="tab active">Table</div></div>
        <div class="panel">{table}<div class="output-note">{html.escape(result.text.splitlines()[0])}<br>Structured table data is rendered directly, not parsed from ASCII.</div></div>
      </section>
    </div>
  </main>
</body>
</html>
"""


def build_svg():
    c = COLORS
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{LAYOUT['window_width']}" height="{LAYOUT['window_height']}" viewBox="0 0 {LAYOUT['window_width']} {LAYOUT['window_height']}">
  <rect width="100%" height="100%" fill="{c['app_bg']}"/>
  <text x="28" y="38" fill="{c['muted']}" font-family="Arial" font-size="12" font-weight="700" letter-spacing="1.4">SEQUENCER PROTOTYPE</text>
  <text x="28" y="73" fill="{c['title']}" font-family="Arial" font-size="26" font-weight="800">Build mathematical queries directly from Python metadata</text>
  <text x="28" y="102" fill="{c['muted']}" font-family="Arial" font-size="13">Python-first Qt coverage for APIs, restrictions, and real rendered range tables.</text>
  <rect x="28" y="126" width="430" height="606" rx="14" fill="{c['card_bg']}" stroke="{c['card_border']}"/>
  <rect x="476" y="126" width="676" height="606" rx="14" fill="{c['card_bg']}" stroke="{c['card_border']}"/>
  <text x="50" y="165" fill="{c['title']}" font-family="Arial" font-size="17" font-weight="750">Query setup</text>
  <text x="50" y="194" fill="{c['muted']}" font-family="Arial" font-size="13">Choose API, object family, optional statistic, and typed parameters.</text>
  <text x="50" y="232" fill="#111827" font-family="Arial" font-size="13" font-weight="750">API</text>
  <rect x="50" y="242" width="386" height="38" rx="8" fill="#fff" stroke="{c['input_border']}"/><text x="62" y="267" fill="#111827" font-family="Arial" font-size="14">Range</text>
  <text x="50" y="305" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Object</text>
  <rect x="50" y="315" width="386" height="38" rx="8" fill="#fff" stroke="{c['input_border']}"/><text x="62" y="340" fill="#111827" font-family="Arial" font-size="14">Fubini Rankings</text>
  <text x="50" y="378" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Statistic</text>
  <rect x="50" y="388" width="386" height="38" rx="8" fill="#fff" stroke="{c['input_border']}"/><text x="62" y="413" fill="#111827" font-family="Arial" font-size="14">Count objects</text>
  <text x="50" y="451" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Range output</text>
  <rect x="50" y="461" width="386" height="38" rx="8" fill="#fff" stroke="{c['input_border']}"/><text x="62" y="486" fill="#111827" font-family="Arial" font-size="14">Rendered table</text>
  <text x="50" y="524" fill="#111827" font-family="Arial" font-size="13" font-weight="750">n *</text>
  <rect x="50" y="535" width="386" height="38" rx="8" fill="#fff" stroke="{c['input_border']}"/><text x="62" y="560" fill="#111827" font-family="Arial" font-size="14">3</text>
  <text x="50" y="586" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Range dimensions</text>
  <rect x="50" y="598" width="386" height="48" rx="10" fill="#fff" stroke="{c['card_border']}"/>
  <rect x="64" y="614" width="16" height="16" rx="3" fill="{c['primary']}"/><text x="90" y="628" fill="#334155" font-family="Arial" font-size="14">Parameter: n</text>
  <rect x="224" y="614" width="16" height="16" rx="3" fill="{c['primary']}"/><text x="250" y="628" fill="#334155" font-family="Arial" font-size="14">Computed: Runs</text>
  <text x="50" y="668" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Restrictions</text>
  <rect x="50" y="678" width="386" height="36" rx="10" fill="#f8fbff" stroke="{c['card_border']}"/>
  <rect x="64" y="688" width="16" height="16" rx="3" fill="{c['primary']}"/><text x="90" y="702" fill="#334155" font-family="Arial" font-size="14">ZigZag · is = true</text>
  <text x="498" y="165" fill="{c['title']}" font-family="Arial" font-size="17" font-weight="750">Result</text>
  <text x="498" y="194" fill="{c['muted']}" font-family="Arial" font-size="13">Rendered table with ZigZag restriction applied.</text>
  <rect x="498" y="226" width="60" height="34" rx="8" fill="#e8eef7" stroke="{c['card_border']}"/><text x="514" y="248" fill="{c['muted']}" font-family="Arial" font-size="13">Text</text>
  <rect x="558" y="226" width="64" height="34" rx="8" fill="#fff" stroke="{c['card_border']}"/><text x="574" y="248" fill="{c['title']}" font-family="Arial" font-size="13" font-weight="700">Table</text>
  <rect x="498" y="260" width="632" height="446" rx="12" fill="#fff" stroke="{c['card_border']}"/>
  <text x="520" y="298" fill="{c['title']}" font-family="Arial" font-size="15" font-weight="750">Rendered range table</text>
  <g font-family="Arial" font-size="14" text-anchor="middle">
    <rect x="520" y="320" width="420" height="160" fill="#fff" stroke="{c['card_border']}"/>
    <path d="M520 360H940M520 400H940M520 440H940M625 320V480M730 320V480M835 320V480" stroke="{c['card_border']}"/>
    <rect x="520" y="320" width="420" height="40" fill="#eef4ff"/>
    <text x="677" y="345" fill="{c['title']}">runs=1</text><text x="782" y="345" fill="{c['title']}">runs=2</text><text x="887" y="345" fill="{c['title']}">runs=3</text>
    <text x="572" y="385" fill="{c['title']}">n=1</text><text x="677" y="385" fill="{c['text']}">1</text>
    <text x="572" y="425" fill="{c['title']}">n=2</text><text x="677" y="425" fill="{c['text']}">1</text><text x="782" y="425" fill="{c['text']}">1</text>
    <text x="572" y="465" fill="{c['title']}">n=3</text><text x="782" y="465" fill="{c['text']}">6</text>
  </g>
</svg>'''


def main():
    PREVIEW_PATH.write_text(build_html())
    SVG_PREVIEW_PATH.write_text(build_svg())
    print(PREVIEW_PATH)
    print(SVG_PREVIEW_PATH)


if __name__ == "__main__":
    main()
