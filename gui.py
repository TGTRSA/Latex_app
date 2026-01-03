import sys
from enum import Enum, auto
import os
import uuid
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton,
    QSplitter, QFileDialog, QAction, QInputDialog
)
from PyQt5.QtCore import Qt, QUrl, QObject, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineSettings
)

from compiler import Parser, Compiler

class MenuOptions(Enum):
    BLOCK_EQUATION = auto()
    INLINE_EQUATION = auto()
    TIKZ = auto()
    


class MenuComponents:
    pass

# =======================
# Cache
# =======================

class Cache:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.base_dir = f"/home/tash/pythonProds/latex_app/latex_files/{self.id}"
        os.makedirs(self.base_dir, exist_ok=True)

    @property
    def tex_path(self):
        return os.path.join(self.base_dir, f"{self.id}.tex")

    @property
    def pdf_path(self):
        return os.path.join(self.base_dir, f"{self.id}.pdf")



# =======================
# Worker (runs in thread)
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
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    self.tex_filename
                ],
                cwd=self.workdir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "LaTeX compilation failed:\n\n"
                    + result.stdout
                    + "\n"
                    + result.stderr
                )

            if not os.path.exists(self.pdf_path):
                raise RuntimeError("pdflatex finished but PDF was not created")

            self.success.emit(self.pdf_path)

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
        self.init_ui()

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

        # Split view
        splitter = QSplitter(Qt.Horizontal)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type your source text here…")
        splitter.addWidget(self.editor)

        self.pdf_view = QWebEngineView()
        self.pdf_view.settings().setAttribute(
            QWebEngineSettings.PluginsEnabled, True
        )
        splitter.addWidget(self.pdf_view)

        splitter.setSizes([550, 550])
        layout.addWidget(splitter)

        self.create_menu()
        self.apply_styles()

        self.compile_btn.clicked.connect(self.start_compile)
        self.save_btn.clicked.connect(self.save_file)

        self.show()

    # ================|
    # MENU COMPONENTS |
    # ================|

    def create_menu(self):
        menu = self.menuBar().addMenu("File")
        add = self.menuBar().addMenu("Add")
        tikz_menu = add.addMenu("Tikz")
        equation_menu = add.addMenu("Equation")
        
        tikz_menu.setMouseTracking(True)
        equation_menu.setMouseTracking(True)

        draw_action = QAction("Draw", self)
        tikz_menu_action = QAction("Node", self)

        inline_action = QAction("Inline equation", self)
        block_equation_action = QAction("Block equation", self)

        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        export_action = QAction("Export", self)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        export_action.triggered.connect(self.export_latex_file)
        inline_action.triggered.connect(lambda: self.add_to_input_field(MenuOptions.INLINE_EQUATION))
        block_equation_action.triggered.connect(lambda: self.add_to_input_field(MenuOptions.BLOCK_EQUATION))
        
        menu.addAction(open_action)
        menu.addAction(save_action)
        menu.addAction(export_action)

        tikz_menu.addAction(draw_action)
        
        equation_menu.addAction(block_equation_action)
        equation_menu.addAction(inline_action)
        #add.addAction(tikz_action)
    
    
    def add_to_input_field(self, option):
        
        input_text, ok = QInputDialog.getMultiLineText(self, "Command","Input space" )
        if ok:
            match option:
                case MenuOptions.BLOCK_EQUATION:
                    text_to_write = f"! {input_text} !"
                    #self.write_to_input(bo)
                case MenuOptions.INLINE_EQUATION:
                    text_to_write = f"$ {input_text} $"
                
        self.write_to_input(text_to_write)

    def write_to_input(self, text_to_write):
        cursor = self.editor.textCursor()
        index = cursor.position()
        #cursor.setPosition(index)
        cursor.insertText(text_to_write)
        self.editor.setTextCursor(cursor)
        pass



    #TODO
    def write_tikz(self):
        # Open a list of options for what the inidividual wants to write

        # switch case based on enums and then compile code based on chose enum

        # convert to tikz formulae

        pass

    # =======================
    # Compile Pipeline
    # =======================

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
    
    #TODO
    def export_latex_file(self):
        
        pass

    def write_tex(self, latex_code):
        with open(self.cache.tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

    def run_compile_thread(self):
        self.thread = QThread()
        self.worker = CompileWorker(
            self.cache.base_dir,
            os.path.basename(self.cache.tex_path),
            self.cache.pdf_path
        )

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

    # =======================
    # Thread Callbacks
    # =======================

    def on_compile_success(self, pdf_path):
        self.compile_btn.setEnabled(True)
        self.pdf_view.load(QUrl.fromLocalFile(pdf_path))

    def on_compile_error(self, message):
        self.compile_btn.setEnabled(True)
        self.display_error(message)

    # =======================
    # Errors
    # =======================

    def display_error(self, message):
        self.pdf_view.setHtml(f"""
        <html>
        <body style="background:#1e1e1e;color:#ff6b6b;padding:20px;">
            <h2>Compilation Error</h2>
            <pre>{message}</pre>
        </body>
        </html>
        """)

    # =======================
    # File Handling
    # =======================

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save file", "", "Text Files (*.txt)"
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "Text Files (*.txt)"
        )
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())

        self.cache = Cache()  # prevent collisions

    # =======================
    # Styles
    # =======================

    def apply_styles(self):
        self.compile_btn.setStyleSheet("""
            QPushButton {
                background:#2ecc71;
                border:none;
                padding:8px 16px;
                border-radius:6px;
            }
        """)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background:#3498db;
                border:none;
                padding:8px 16px;
                border-radius:6px;
            }
        """)


# =======================
# Entry Point
# =======================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())
