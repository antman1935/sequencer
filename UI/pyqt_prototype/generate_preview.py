import html
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Commands.CommandRegistration  # registers all commands
from CmdTools import Command
from Statistic import Statistic
from UI.pyqt_prototype.theme import COLORS, LAYOUT, TYPOGRAPHY

PREVIEW_PATH = Path(__file__).with_name("preview.html")
SVG_PREVIEW_PATH = Path(__file__).with_name("preview.svg")


def parameter_rows(command_name):
    command_class = Command.commands[command_name]
    rows = []
    for parameter in sorted(command_class.parameters, key=lambda p: not p.required):
        required = "  *" if parameter.required else ""
        description = html.escape(parameter.description or "Optional value")
        if str(parameter.param_type).endswith("BOOL"):
            control = '<label class="check"><span class="box"></span><span>Enabled</span></label>'
        else:
            value = "1" if parameter.required else "unset"
            control = f'<div class="input">{html.escape(value)}</div>'
        rows.append(
            f"""
            <section class="parameter-row">
              <div class="field-label">{html.escape(parameter.name)}{required}</div>
              <div class="field-hint">{description}</div>
              {control}
            </section>
            """
        )
    return "\n".join(rows)


def options(registry, selected_key):
    return "\n".join(
        f'<option {"selected" if key == selected_key else ""}>{html.escape(item.ui_name)}</option>'
        for key, item in registry.items()
    )


def build_html():
    command_name = "fubini" if "fubini" in Command.commands else next(iter(Command.commands))
    command_class = Command.commands[command_name]
    statistic_name = next(iter(Statistic.statistics), None)
    statistic_label = Statistic.statistics[statistic_name].ui_name if statistic_name else "Count objects"
    c = COLORS
    font = TYPOGRAPHY["ui_font"]
    mono = TYPOGRAPHY["mono_font"]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sequencer Prototype Preview</title>
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  width: {LAYOUT['window_width']}px;
  min-height: {LAYOUT['window_height']}px;
  background: {c['app_bg']};
  color: {c['text']};
  font-family: {font};
}}
.app {{ padding: 24px 28px 28px; }}
.eyebrow {{ color: {c['muted']}; font-size: 12px; font-weight: 700; letter-spacing: 1.4px; margin-bottom: 10px; }}
h1 {{ color: {c['title']}; font-size: 26px; line-height: 1.2; margin: 0 0 8px; }}
.subtitle {{ color: {c['muted']}; font-size: 13px; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: {LAYOUT['query_card_width']}px 1fr; gap: 18px; align-items: stretch; min-height: 606px; }}
.card {{ background: {c['card_bg']}; border: 1px solid {c['card_border']}; border-radius: 14px; padding: 20px 22px; box-shadow: 0 12px 28px rgba(15, 23, 42, .08); }}
.card h2 {{ color: {c['title']}; font-size: 17px; margin: 0 0 10px; }}
.help {{ color: {c['muted']}; font-size: 13px; line-height: 1.45; margin-bottom: 18px; }}
.setup {{ display: flex; flex-direction: column; min-height: 606px; }}
.field-block {{ margin-bottom: 16px; }}
.field-label {{ color: #111827; font-size: 13px; font-weight: 750; margin-bottom: 7px; }}
select, .input {{ width: 100%; height: 44px; border: 1px solid {c['input_border']}; border-radius: 8px; background: #fff; color: #111827; font-size: 14px; padding: 0 12px; display: flex; align-items: center; }}
.parameter-list {{ display: flex; flex-direction: column; gap: 14px; margin: 3px 0 18px; max-height: 312px; overflow: hidden; }}
.field-hint {{ color: {c['hint']}; font-size: 12px; line-height: 1.45; margin-bottom: 7px; min-height: 17px; }}
.check {{ display: flex; align-items: center; gap: 9px; color: #334155; font-size: 14px; height: 30px; }}
.box {{ width: 16px; height: 16px; border: 1px solid #94a3b8; border-radius: 3px; background: #fff; }}
.spacer {{ flex: 1; }}
button {{ width: 100%; height: 42px; border: 0; border-radius: 10px; background: {c['primary']}; color: #fff; font-weight: 750; font-size: 14px; }}
.status {{ color: {c['muted']}; font-size: 13px; margin-top: 10px; }}
.output {{ height: 490px; border-radius: 12px; border: 1px solid {c['output_border']}; background: {c['output_bg']}; color: {c['output_muted']}; padding: 18px; font: 13px/1.55 {mono}; }}
.result-value {{ color: {c['output_text']}; margin-top: 22px; }}
</style>
</head>
<body>
  <main class="app">
    <div class="eyebrow">SEQUENCER PROTOTYPE</div>
    <h1>Build mathematical queries directly from Python metadata</h1>
    <div class="subtitle">A cleaner Qt Widgets direction before expanding coverage beyond point queries.</div>
    <div class="grid">
      <section class="card setup">
        <h2>Query setup</h2>
        <div class="help">Choose an object, optional statistic, and generated parameters.</div>
        <div class="field-block">
          <div class="field-label">Object</div>
          <select>{options(Command.commands, command_name)}</select>
        </div>
        <div class="field-block">
          <div class="field-label">Statistic</div>
          <select><option selected>{html.escape(statistic_label)}</option></select>
        </div>
        <div class="parameter-list">{parameter_rows(command_name)}</div>
        <label class="check"><span class="box"></span><span>Show generated elements</span></label>
        <div class="spacer"></div>
        <button>Run point query</button>
        <div class="status">Ready</div>
      </section>
      <section class="card">
        <h2>Result</h2>
        <div class="help">Captured command output appears here without freezing the interface.</div>
        <pre class="output">Run a query to see results here.

<span class="result-value">Example: Point Query on {html.escape(command_class.ui_name)}.</span></pre>
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
  <text x="28" y="102" fill="{c['muted']}" font-family="Arial" font-size="13">A cleaner Qt Widgets direction before expanding coverage beyond point queries.</text>
  <rect x="28" y="126" width="430" height="606" rx="14" fill="{c['card_bg']}" stroke="{c['card_border']}"/>
  <rect x="476" y="126" width="676" height="606" rx="14" fill="{c['card_bg']}" stroke="{c['card_border']}"/>
  <text x="50" y="165" fill="{c['title']}" font-family="Arial" font-size="17" font-weight="750">Query setup</text>
  <text x="50" y="194" fill="{c['muted']}" font-family="Arial" font-size="13">Choose an object, optional statistic, and generated parameters.</text>
  <text x="50" y="233" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Object</text>
  <rect x="50" y="246" width="386" height="44" rx="8" fill="#fff" stroke="{c['input_border']}"/>
  <text x="62" y="274" fill="#111827" font-family="Arial" font-size="14">Fubini Rankings</text>
  <text x="50" y="323" fill="#111827" font-family="Arial" font-size="13" font-weight="750">Statistic</text>
  <rect x="50" y="336" width="386" height="44" rx="8" fill="#fff" stroke="{c['input_border']}"/>
  <text x="62" y="364" fill="#111827" font-family="Arial" font-size="14">Count objects</text>
  <text x="50" y="417" fill="#111827" font-family="Arial" font-size="13" font-weight="750">n *</text>
  <text x="50" y="440" fill="{c['hint']}" font-family="Arial" font-size="12">length of the ranking</text>
  <rect x="50" y="453" width="386" height="44" rx="8" fill="#fff" stroke="{c['input_border']}"/>
  <text x="62" y="481" fill="#111827" font-family="Arial" font-size="14">1</text>
  <text x="50" y="536" fill="#111827" font-family="Arial" font-size="13" font-weight="750">k</text>
  <text x="50" y="559" fill="{c['hint']}" font-family="Arial" font-size="12">number of blocks</text>
  <rect x="50" y="572" width="386" height="44" rx="8" fill="#fff" stroke="{c['input_border']}"/>
  <text x="62" y="600" fill="#111827" font-family="Arial" font-size="14">unset</text>
  <rect x="50" y="648" width="16" height="16" rx="3" fill="#fff" stroke="#94a3b8"/>
  <text x="75" y="661" fill="#334155" font-family="Arial" font-size="14">Show generated elements</text>
  <rect x="50" y="680" width="386" height="42" rx="10" fill="{c['primary']}"/>
  <text x="190" y="706" fill="#fff" font-family="Arial" font-size="14" font-weight="750">Run point query</text>
  <text x="498" y="165" fill="{c['title']}" font-family="Arial" font-size="17" font-weight="750">Result</text>
  <text x="498" y="194" fill="{c['muted']}" font-family="Arial" font-size="13">Captured command output appears here without freezing the interface.</text>
  <rect x="498" y="216" width="632" height="490" rx="12" fill="{c['output_bg']}" stroke="{c['output_border']}"/>
  <text x="516" y="250" fill="{c['output_muted']}" font-family="Menlo, Consolas, monospace" font-size="13">Run a query to see results here.</text>
  <text x="516" y="308" fill="{c['output_text']}" font-family="Menlo, Consolas, monospace" font-size="13">Example: Point Query on Fubini Rankings.</text>
</svg>'''


def main():
    PREVIEW_PATH.write_text(build_html())
    SVG_PREVIEW_PATH.write_text(build_svg())
    print(PREVIEW_PATH)
    print(SVG_PREVIEW_PATH)


if __name__ == "__main__":
    main()
