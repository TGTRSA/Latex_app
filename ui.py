from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QSplitter, QComboBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QColor

# ---------------- Themes ----------------
THEMES = {
    "Obsidian": {"bg": "#4a2c3f", "accent": "#486d83", "text": "#f5f5f5"},
    "Carmine": {"bg": "#7a5063", "accent": "#f4a384", "text": "#ffffff"},
    "Moss": {"bg": "#384514", "accent": "#f8f5f2", "text": "#f8f5f2"},
    "Coffee": {"bg": "#f3e9dc", "accent": "#c08552", "text": "#5e3023"},
    "Dutch Wine": {"bg": "#efdfbb", "accent": "#722f37", "text": "#3a1a1a"}
}

# ---------------- UI ----------------
class EditorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # -------- Top Bar --------
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        # Theme selector
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(THEMES.keys())
        self.theme_selector.setFixedWidth(160)
        self.theme_selector.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-height: 30px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #888;
                font-size: 14px;
            }
        """)

        # Buttons
        self.compile_btn = QPushButton("Compile")
        self.save_btn = QPushButton("Save")

        # Add shadows to buttons
        for btn in (self.compile_btn, self.save_btn):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setXOffset(2)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 120))
            btn.setGraphicsEffect(shadow)

        top_bar.addWidget(self.theme_selector)
        top_bar.addStretch()
        top_bar.addWidget(self.compile_btn)
        top_bar.addWidget(self.save_btn)
        layout.addLayout(top_bar)

        # -------- Split View --------
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type your source text here…")
        editor_shadow = QGraphicsDropShadowEffect()
        editor_shadow.setBlurRadius(15)
        editor_shadow.setXOffset(0)
        editor_shadow.setYOffset(2)
        editor_shadow.setColor(QColor(0, 0, 0, 80))
        self.editor.setGraphicsEffect(editor_shadow)

        self.preview = QWebEngineView()
        self.preview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        preview_shadow = QGraphicsDropShadowEffect()
        preview_shadow.setBlurRadius(15)
        preview_shadow.setXOffset(0)
        preview_shadow.setYOffset(2)
        preview_shadow.setColor(QColor(0, 0, 0, 80))
        self.preview.setGraphicsEffect(preview_shadow)

        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([550, 550])
        layout.addWidget(splitter)

        # Apply default theme
        self.apply_theme("Obsidian")

    def apply_theme(self, name):
        t = THEMES[name]
        selector_text_color = "#000000" if t["bg"] in ["#f3e9dc", "#efdfbb"] else "#ffffff"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {t['bg']};
                color: {t['text']};
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
            }}
            QTextEdit {{
                background-color: rgba(255,255,255,0.05);
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
        """)
