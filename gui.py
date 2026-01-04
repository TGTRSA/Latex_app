import sys
import json
from enum import Enum, auto
import os
import uuid
import hashlib
from pathlib import Path
import shutil
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton,
    QSplitter, QFileDialog, QAction, QInputDialog, QMenu, QFontDialog
)
from PyQt5.QtCore import Qt, QUrl, QObject, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QFont
from compiler import Parser, Compiler

THEMES_PATH = Path("src/themes.json")
GUI_STATE_PATH = Path("src/gui_state_cache.json")


# =======================
# Theme Manager
# =======================

class ThemeManager:
    def __init__(self, app: QApplication, themes_path: Path, state_path: Path, default_theme: str = "Obsidian"):
        self.app = app
        self.themes_path = themes_path
        self.state_path = state_path
        self.default_theme = default_theme

        self.themes = self._load_themes()
        self.state = self._load_state()

    # ---------- Load ----------
    def _load_themes(self):
        if not self.themes_path.exists():
            raise FileNotFoundError(f"Missing themes file: {self.themes_path}")
        with open(self.themes_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_state(self):
        if self.state_path.exists():
            with open(self.state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            state.setdefault("theme", self.default_theme)
            state.setdefault("font", None)
            return state
        return {"theme": self.default_theme, "font": None}

    def _save_state(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    # ---------- Style ----------
    def build_stylesheet(self, theme_name: str) -> str:
        theme = self.themes[theme_name]
        bg = theme["bg"]       # background
        text = theme["text"]   # font color
        accent = theme["accent"]  # outline/highlight

        # If accent has multiple colors, pick first
        if ',' in accent:
            accent = accent.split(',')[0].strip()

        return f"""
        /* Main window and widgets */
        QMainWindow, QWidget {{
            background-color: {bg};
            color: {text};
        }}

        /* Editor */
        QTextEdit {{
            background-color: {bg};
            color: {text};
            border: 2px solid {accent};
            border-radius: 12px;
            padding: 6px;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {text};
            color: {bg};
            border: 2px solid {accent};
            border-radius: 6px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {accent};
            color: {bg};
            opacity: 0.9;
        }}

        /* Menu bar stays white, text black */
        QMenuBar {{
            background-color: #ffffff;
            color: #000000;
        }}

        /* Menus */
        QMenu {{
            background-color: {bg};
            color: {text};
            border: 1px solid {accent};
        }}
        QMenu::item:selected {{
            background-color: {accent};
            color: {text};
        }}
        """

    # ---------- Apply ----------
    def apply(self, theme_name: str):
        if theme_name not in self.themes:
            raise KeyError(f"Unknown theme: {theme_name}")
        self.app.setStyleSheet(self.build_stylesheet(theme_name))
        self.state["theme"] = theme_name
        self._save_state()

    # ---------- Convenience ----------
    def apply_last(self):
        last_theme = self.state.get("theme", self.default_theme)
        self.apply(last_theme)

    # ---------- Menu ----------
    def available_themes(self):
        return list(self.themes.keys())

    def populate_menu(self, menu):
        for theme_name in self.available_themes():
            action = QAction(theme_name, menu)
            action.triggered.connect(lambda checked, t=theme_name: self.apply(t))
            menu.addAction(action)


# =======================
# Menu Options
# =======================

class MenuOptions(Enum):
    BLOCK_EQUATION = auto()
    INLINE_EQUATION = auto()
    TIKZ = auto()
    CHEMFIG = auto()


# =======================
# Cache
# =======================

class Cache:
    ROOT = Path("/home/tash/pythonProds/latex_app/latex_files")
    _temp_dirs = set()

    def __init__(self, source_path: str | None = None):
        Cache.ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = source_path is None

        if self.temp:
            self.id = str(uuid.uuid4())
            Cache._temp_dirs.add(self.id)
        else:
            abs_path = str(Path(source_path).resolve())
            self.id = hashlib.sha256(abs_path.encode()).hexdigest()[:16]

        self.base_dir = Cache.ROOT / self.id
        self.base_dir.mkdir(exist_ok=True)

    @property
    def tex_path(self) -> Path:
        return self.base_dir / "main.tex"

    @property
    def pdf_path(self) -> Path:
        return self.base_dir / "main.pdf"

    def promote(self, source_path: str):
        if not self.temp:
            return
        abs_path = str(Path(source_path).resolve())
        permanent_id = hashlib.sha256(abs_path.encode()).hexdigest()[:16]
        permanent_dir = Cache.ROOT / permanent_id
        permanent_dir.mkdir(exist_ok=True)
        for item in self.base_dir.iterdir():
            shutil.copy(item, permanent_dir / item.name)
        self.id = permanent_id
        self.base_dir = permanent_dir
        self.temp = False
        Cache._temp_dirs.discard(permanent_id)

    @staticmethod
    def cleanup_temp_dirs():
        for temp_id in list(Cache._temp_dirs):
            temp_dir = Cache.ROOT / temp_id
            shutil.rmtree(temp_dir, ignore_errors=True)
            Cache._temp_dirs.discard(temp_id)


# =======================
# Compile Worker
# =======================

class CompileWorker(QObject):
    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, workdir, tex_filename, pdf_path):
        super().__init__()
        self.workdir = workdir
        self.tex_filename = tex_filename
        self.pdf_path = pdf_path

    def run(self):
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", self.tex_filename],
                cwd=self.workdir, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(result.stdout + "\n" + result.stderr)
            if not os.path.exists(self.pdf_path):
                raise RuntimeError("PDF not created")
            self.success.emit(str(self.pdf_path))
        except Exception as e:
            self.error.emit(str(e))


# =======================
# Main Window
# =======================

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cache = Cache()
        self.thread = None
        self.worker = None

        self.theme_manager = ThemeManager(QApplication.instance(), THEMES_PATH, GUI_STATE_PATH)

        self.init_ui()
        self.theme_manager.apply_last()
        self.apply_font_from_state()

    # ---------- Font ----------
    def apply_font_from_state(self):
        font_str = self.theme_manager.state.get("font")
        if font_str:
            font = QFont()
            font.fromString(font_str)
            self.apply_font(font)

    def choose_font(self):
        font, ok = QFontDialog.getFont(QApplication.instance().font(), self, "Choose UI Font")
        if ok:
            self.apply_font(font)
            self.theme_manager.state["font"] = font.toString()
            self.theme_manager._save_state()

    def apply_font(self, font: QFont):
        QApplication.instance().setFont(font)
        self.setFont(font)
        self.editor.setFont(font)
        self.compile_btn.setFont(font)
        self.save_btn.setFont(font)
        self.menuBar().setFont(font)
        for menu in self.menuBar().children():
            if isinstance(menu, QMenu):
                menu.setFont(font)

    # ---------- UI ----------
    def init_ui(self):
        self.setWindowTitle("LaTeX Editor (PDF Preview)")
        self.setGeometry(100, 100, 1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top bar
        top_bar = QHBoxLayout()
        self.compile_btn = QPushButton("Compile")
        self.save_btn = QPushButton("Save")
        top_bar.addStretch()
        top_bar.addWidget(self.compile_btn)
        top_bar.addWidget(self.save_btn)
        layout.addLayout(top_bar)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type your source text here…")
        splitter.addWidget(self.editor)

        self.pdf_view = QWebEngineView()
        self.pdf_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        splitter.addWidget(self.pdf_view)
        splitter.setSizes([550, 550])
        layout.addWidget(splitter)

        # Right-click menu
        self.right_click_menu = QMenu()
        self.create_menu()

        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.show_right_click_menu)

        self.compile_btn.clicked.connect(self.start_compile)
        self.save_btn.clicked.connect(self.save_file)

        self.show()

    # ---------- Right-click ----------
    def show_right_click_menu(self, pos):
        self.right_click_menu.exec_(self.editor.mapToGlobal(pos))

    def create_menu(self):
        file_menu = self.menuBar().addMenu("File")
        add_menu = self.menuBar().addMenu("Add")
        theme_menu = self.menuBar().addMenu("Themes")
        settings_menu = self.menuBar().addMenu("Settings")

        # File menu
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        export_action = QAction("Export", self)
        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        export_action.triggered.connect(self.export_latex_file)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(export_action)

        # Settings menu
        font_action = QAction("Font", self)
        font_action.triggered.connect(self.choose_font)
        settings_menu.addAction(font_action)

        # Add menu
        tikz_menu = add_menu.addMenu("Tikz")
        equation_menu = add_menu.addMenu("Equation")

        chemfig_action = QAction("Chemfig", self)
        draw_action = QAction("Draw", self)
        inline_action = QAction("Inline equation", self)
        block_action = QAction("Block equation", self)

        chemfig_action.triggered.connect(lambda: self.add_to_input_field(MenuOptions.CHEMFIG))
        draw_action.triggered.connect(lambda: self.add_to_input_field(MenuOptions.TIKZ))
        inline_action.triggered.connect(lambda: self.add_to_input_field(MenuOptions.INLINE_EQUATION))
        block_action.triggered.connect(lambda: self.add_to_input_field(MenuOptions.BLOCK_EQUATION))

        tikz_menu.addAction(draw_action)
        equation_menu.addAction(block_action)
        equation_menu.addAction(inline_action)
        add_menu.addAction(chemfig_action)

        self.right_click_menu.addMenu(equation_menu)
        self.right_click_menu.addMenu(tikz_menu)

        self.theme_manager.populate_menu(theme_menu)

    # ---------- Input ----------
    def add_to_input_field(self, option):
        input_text, ok = QInputDialog.getMultiLineText(self, "Command", "Input space")
        if ok:
            match option:
                case MenuOptions.BLOCK_EQUATION:
                    text_to_write = f"! {input_text} !"
                case MenuOptions.INLINE_EQUATION:
                    text_to_write = f"$ {input_text} $"
                case MenuOptions.CHEMFIG:
                    text_to_write = r"\chemfig{" + f"{input_text}" + "}"
                case MenuOptions.TIKZ:
                    text_to_write = "\\begin{tikzpicture}\n" + f"{input_text}\n" + "\\end{tikzpicture}\n"
            self.write_to_input(text_to_write)

    def write_to_input(self, text_to_write):
        cursor = self.editor.textCursor()
        cursor.insertText(text_to_write)
        self.editor.setTextCursor(cursor)

    # ---------- Compile ----------
    def start_compile(self):
        try:
            self.compile_btn.setEnabled(False)
            latex_code = self.generate_latex()
            self.write_tex(latex_code)
            self.run_compile_thread()
        except Exception as e:
            self.display_error(str(e))
            self.compile_btn.setEnabled(True)

    def generate_latex(self):
        source = self.editor.toPlainText()
        tree = Parser(source).parse()
        return Compiler().compile(tree)

    def write_tex(self, latex_code):
        with open(self.cache.tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

    def run_compile_thread(self):
        self.thread = QThread()
        self.worker = CompileWorker(self.cache.base_dir, os.path.basename(self.cache.tex_path), self.cache.pdf_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_compile_success)
        self.worker.error.connect(self.on_compile_error)
        self.worker.success.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.success.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_compile_success(self, pdf_path):
        self.compile_btn.setEnabled(True)
        self.pdf_view.load(QUrl.fromLocalFile(pdf_path))

    def on_compile_error(self, message):
        self.compile_btn.setEnabled(True)
        self.display_error(message)

    # ---------- Errors ----------
    def display_error(self, message):
        self.pdf_view.setHtml(f"""
        <html>
        <body style="background:#1e1e1e;color:#ff6b6b;padding:20px;">
            <h2>Compilation Error</h2>
            <pre>{message}</pre>
        </body>
        </html>
        """)

    # ---------- File Handling ----------
    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text Files (*.txt)")
        if not path:
            return
        with open(f"{path}.txt", "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self.cache.promote(path)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text Files (*.txt)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())
        self.cache = Cache(path)

    def export_latex_file(self):
        pass

    # ---------- Cleanup ----------
    def closeEvent(self, event):
        Cache.cleanup_temp_dirs()
        super().closeEvent(event)


# =======================
# Entry Point
# =======================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())
