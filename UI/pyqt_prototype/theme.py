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
}

TYPOGRAPHY = {
    "ui_font": "Arial, sans-serif",
    "mono_font": "Menlo, Consolas, monospace",
}

LAYOUT = {
    "window_width": 1180,
    "window_height": 760,
}


def web_stylesheet():
    """CSS tokens consumed by the one shared browser/desktop UI."""
    tokens = {key.replace("_", "-"): value for key, value in COLORS.items()}
    tokens["ui-font"] = TYPOGRAPHY["ui_font"]
    tokens["mono-font"] = TYPOGRAPHY["mono_font"]
    return ":root {\n" + "\n".join(f"  --{key}: {value};" for key, value in tokens.items()) + "\n}\n"
