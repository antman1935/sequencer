COLORS = {
    "app_bg": "#f6f8fc",
    "card_bg": "#ffffff",
    "card_border": "#d7dfeb",
    "text": "#172033",
    "title": "#0f172a",
    "muted": "#53627a",
    "hint": "#64748b",
    "input_border": "#cbd5e1",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_pressed": "#1e40af",
    "disabled": "#94a3b8",
    "output_bg": "#111827",
    "output_border": "#0f172a",
    "output_text": "#e5e7eb",
    "output_muted": "#93a4c7",
}

TYPOGRAPHY = {
    "ui_font": "Arial, sans-serif",
    "mono_font": "Menlo, Consolas, monospace",
    "qt_ui_font": "Arial",
}

LAYOUT = {
    "window_width": 1180,
    "window_height": 760,
    "shell_margin_x": 28,
    "shell_margin_top": 24,
    "shell_margin_bottom": 28,
    "shell_gap": 18,
    "card_radius": 14,
    "card_padding_x": 22,
    "card_padding_y": 20,
    "query_card_width": 430,
}


def qt_stylesheet():
    c = COLORS
    return f"""
QMainWindow, QWidget#appRoot {{
    background: {c['app_bg']};
    color: {c['text']};
}}
QFrame#card {{
    background: {c['card_bg']};
    border: 1px solid {c['card_border']};
    border-radius: 14px;
}}
QWidget#cardBody, QWidget#parameterList, QWidget#parameterRow, QWidget#fieldBlock {{
    background: transparent;
}}
QLabel {{
    background: transparent;
    color: {c['text']};
}}
QLabel#eyebrow {{
    color: {c['muted']};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.4px;
}}
QLabel#title {{
    color: {c['title']};
    font-size: 26px;
    font-weight: 800;
}}
QLabel#subtitle, QLabel#helpText, QLabel#statusText {{
    color: {c['muted']};
    font-size: 13px;
}}
QLabel#sectionTitle {{
    color: {c['title']};
    font-size: 17px;
    font-weight: 750;
}}
QLabel#fieldLabel {{
    color: #111827;
    font-size: 13px;
    font-weight: 750;
}}
QLabel#fieldHint {{
    color: {c['hint']};
    font-size: 12px;
    line-height: 145%;
}}
QComboBox, QLineEdit, QSpinBox {{
    background: {c['card_bg']};
    border: 1px solid {c['input_border']};
    border-radius: 8px;
    color: #111827;
    padding: 7px 10px;
    min-height: 28px;
    selection-background-color: #dbeafe;
}}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{
    border: 1px solid {c['primary']};
}}
QCheckBox {{
    background: transparent;
    color: #334155;
    spacing: 9px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
}}
QPushButton {{
    background: {c['primary']};
    border: none;
    border-radius: 10px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 750;
    min-height: 42px;
    padding: 0 18px;
}}
QPushButton:hover {{
    background: {c['primary_hover']};
}}
QPushButton:pressed {{
    background: {c['primary_pressed']};
}}
QPushButton:disabled {{
    background: {c['disabled']};
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QTextEdit {{
    background: {c['output_bg']};
    border: 1px solid {c['output_border']};
    border-radius: 12px;
    color: {c['output_text']};
    font-family: SF Mono, Menlo, Consolas, monospace;
    font-size: 13px;
    padding: 14px;
}}
"""
