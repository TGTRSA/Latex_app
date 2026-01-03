import sys
import os
import uuid
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton,
    QSplitter, QFileDialog, QAction
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

from compiler import Parser, Compiler


# =======================
# Cache / Paths
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
# Main Window
# =======================

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cache = Cache()
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

        # Splitter
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

        self.compile_btn.clicked.connect(self.compile_pipeline)
        self.save_btn.clicked.connect(self.save_file)

        self.show()

    def create_menu(self):
        menu = self.menuBar().addMenu("File")

        open_action = QAction("Open", self)
        save_action = QAction("Save", self)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)

        menu.addAction(open_action)
        menu.addAction(save_action)

    # =======================
    # Compile Pipeline
    # =======================

    def compile_pipeline(self):
        try:
            latex_code = self.generate_latex()
            self.write_tex(latex_code)
            self.compile_pdf()
            self.display_pdf()
        except Exception as e:
            self.display_error(str(e))

    def generate_latex(self):
        source = self.editor.toPlainText()
        tree = Parser(source).parse()
        latex = Compiler().compile(tree)
        return latex

    def write_tex(self, latex_code):
        with open(self.cache.tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

    def compile_pdf(self):
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                os.path.basename(self.cache.tex_path)
            ],
            cwd=self.cache.base_dir,
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

        if not os.path.exists(self.cache.pdf_path):
            raise RuntimeError("pdflatex finished but PDF was not created")

    def display_pdf(self):
        self.pdf_view.load(
            QUrl.fromLocalFile(self.cache.pdf_path)
        )

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
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text Files (*.txt)")
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text Files (*.txt)")
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())

        # Reset cache to avoid PDF collisions
        self.cache = Cache()

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
