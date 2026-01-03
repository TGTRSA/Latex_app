
from PyQt5.QtGui import QColor

# ---------------- Themes ----------------
THEMES = {
    "Obsidian": {"bg": "#4a2c3f", "accent": "#486d83", "text": "#f5f5f5"},
    "Carmine": {"bg": "#7a5063", "accent": "#f4a384", "text": "#ffffff"},
    "Moss": {"bg": "#384514", "accent": "#f8f5f2", "text": "#f8f5f2"},
    "Coffee": {"bg": "#f3e9dc", "accent": "#c08552", "text": "#5e3023"},
    "Dutch Wine": {"bg": "#efdfbb", "accent": "#722f37", "text": "#3a1a1a"}
}

def is_light(hex_color: str) -> bool:
    """Return True if the color is light, False otherwise."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4],16), int(hex_color[4:6],16)
    return (0.299*r + 0.587*g + 0.114*b) > 186

def get_stylesheet(theme_name: str) -> str:
    """
    Return a complete stylesheet string for the given theme.
    Editor background automatically adapts for light/dark themes.
    """
    t = THEMES[theme_name]
    selector_text_color = "#000000" if is_light(t["bg"]) else "#ffffff"
    # Adaptive editor background
    editor_bg = "#ffffff20" if not is_light(t["bg"]) else "#00000010"

    return f"""
        QWidget {{
            background-color: {t['bg']};
            color: {t['text']};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
        }}
        QTextEdit {{
            background-color: {editor_bg};
            border-radius: 12px;
            padding: 12px;
            color: {t['text']};
        }}
        QPushButton {{
            background-color: {t['accent']};
            color: {t['text']};
            border: none;
            padding: 10px 18px;
            border-radius: 12px;
            font-weight: 600;
        }}
        QPushButton:hover {{ opacity: 0.85; }}
        QComboBox {{
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: bold;
            color: {selector_text_color};
            background-color: rgba(255,255,255,0.15);
            min-height: 32px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['bg']};
            color: {t['text']};
            font-size: 14px;
            selection-background-color: {t['accent']};
        }}
    """

