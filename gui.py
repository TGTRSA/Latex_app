
import difflib
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QSplitter, QFileDialog, QAction
)
from PyQt5.QtCore import Qt
from compiler import Parser, Compiler
import os
import uuid
import subprocess


class Cache:
    def __init__(self, random_name):
        self.random_name = random_name
        self.cache = {}

    def initiate(self):
        self.cache['latex_code'] = None
        self.cache['filled'] = False

    def __getitem__(self, key):
        return self.cache[key]

    def load(self, text):
        self.cache['latex_code'] = text
        self.cache['filled'] = True


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        random_name = str(uuid.uuid4())
        self.cache = Cache(random_name)
        self.cache.initiate()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("My PyQt Window")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        top_bar = QHBoxLayout()
        self.compile_button = QPushButton("Compile")
        self.save_file_button = QPushButton("Save")
        top_bar.addStretch()
        top_bar.addWidget(self.compile_button)
        top_bar.addWidget(self.save_file_button)
        main_layout.addLayout(top_bar)

        self.double_display()
        main_layout.addWidget(self.splitter)

        self.create_menu()
        self.style_sheets()

        self.compile_button.clicked.connect(self.compile_text)
        self.save_file_button.clicked.connect(self._save)

        self.show()

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        save_action = QAction("Save", self)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self._save)

    def double_display(self):
        self.splitter = QSplitter(Qt.Horizontal)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type here")
        self.splitter.addWidget(self.text_input)

        self.display_text = QTextEdit()
        self.display_text.setReadOnly(True)
        self.splitter.addWidget(self.display_text)

        self.splitter.setSizes([400, 400])

    # ---------------- Actions ----------------
    def get_text_input(self):
        return self.text_input.toPlainText()

    def convert_to_tex(self):
        text = self.get_text_input()
        tree = Parser(text).parse()
        tex_output = Compiler().compile(tree)
        return tex_output

    def write_latex_to_file(self, tex_file, latex_output):
        with open(tex_file, "w") as f:
            f.write(latex_output)

    def cache_file(self, latex_output):
        path = f"/home/tash/pythonProds/latex_app/latex_files/{self.cache.random_name}"
        os.makedirs(path, exist_ok=True)

        tex_file = f"{path}/{self.cache.random_name}.tex"

        if self.cache['latex_code'] is not None:
            # Compare old and new latex, but still write full latex to file
            old_lines = self.cache['latex_code'].splitlines()
            new_lines = latex_output.splitlines()

            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile='previous',
                tofile='current',
                lineterm=''
            )

            diff_text = "\n".join(diff)
            if diff_text:
                print("[INFO] LaTeX changes detected")

            self.write_latex_to_file(tex_file, latex_output)
            self.cache.load(latex_output)

        else:
            self.write_latex_to_file(tex_file, latex_output)
            self.cache.load(latex_output)

        try:
            result = subprocess.run(
                ['latex', f'{self.cache.random_name}.tex'],
                cwd=path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise SystemError(result.stderr)

        except Exception as e:
            print(f"[ERROR] {e}")

    def compile_tex(self):
        pass

    def compile_text(self):
        try:
            latex_output = self.convert_to_tex()
            self.cache_file(latex_output)

            self.display_text.clear()
            self.display_text.setPlainText(latex_output)

        except Exception as e:
            print(f"[ERROR] {e}")

    def _save(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file")
        if not filepath:
            return

        latex_content = self.convert_to_tex()
        file_content = self.get_text_input()

        with open(f"{filepath}.txt", "w") as f:
            f.write(file_content)

        base_name = os.path.splitext(os.path.basename(filepath))[0]
        latex_file_path = f"/home/tash/{base_name}.tex"

        with open(latex_file_path, "w") as f:
            f.write(latex_content)

    def open_file(self):
        random_name = str(uuid.uuid4())
        self.cache = Cache(random_name)
        self.cache.initiate()

        filepath, _ = QFileDialog.getOpenFileName(self, "Open file")
        if filepath:
            try:
                with open(filepath, "r") as f:
                    content = f.read()
                self.text_input.setPlainText(content)
            except Exception as e:
                print(f"[ERROR] {e}")

    # ---------------- Styles ----------------
    def style_sheets(self):
        self.compile_button.setStyleSheet("""
            QPushButton{
                background-color: #2ecc71;
                border:none;
                padding:10px 5px;
                border-radius:5px;
                min-width:80px;
            }
        """)
        self.save_file_button.setStyleSheet("""
            QPushButton{
                background-color: #3498db;
                border:none;
                padding:10px 5px;
                border-radius:5px;
                min-width:80px;
            }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())

