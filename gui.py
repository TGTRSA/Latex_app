
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

# TODO: create a save button and make it save the file => [DONE]
# TODO: on compile use the outputted latex file and run the neccessary commands to create the .text/.dvi/.svg files
# TODO: create menu box for writing latex code and have it geenrate => $ command $ basis
# TODO: caching for temp files allowing for immediate latex rendering before save


class StartWindow(QMainWindow):
    def __init__(self):
        print("Executing window start")
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Loads all the ui components for the window
        """
        print("[X] LOADING UI COMPONENTS [X]")
        self.setWindowTitle("My PyQt Window")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Top bar for buttons
        top_bar = QHBoxLayout()
        self.compile_button = QPushButton("Compile")
        self.save_file_button = QPushButton("Save")
        top_bar.addStretch()  # pushes buttons to the right
        top_bar.addWidget(self.compile_button)
        top_bar.addWidget(self.save_file_button)
        main_layout.addLayout(top_bar)

        # Splitter for input/output
        self.double_display()
        main_layout.addWidget(self.splitter)

        # Menu bar
        self.create_menu()

        # Button styles
        self.style_sheets()

        # Connect actions
        self.compile_button.clicked.connect(self.compile_text)
        self.save_file_button.clicked.connect(self._save)

        self.show()

    def create_menu(self):
        """
        Creates the top menu with File, Tools, Analyze
        """
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        tools_menu = menubar.addMenu("Tools")
        analyze_menu = menubar.addMenu("Analyze")

        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self._save)

    def double_display(self):
        """
        Screen splitter with input | output sets
        """
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
        """
            Retrieves the input tex and converts into latex formating
        """
        text = self.get_text_input()

        tree = Parser(text).parse()
        tex_output = Compiler().compile(tree)
        
        return tex_output

    def cache_file(self, latex_output):
        random_name = (str(uuid.uuid4()))
        os.makedirs(f"/home/tash/pythonProds/latex_app/temp/{random_name}")
        with open(f"temp/{random_name}/{random_name}.tex", "w") as f:
            f.write(latex_output)
        try:
            result = subprocess.run([f'latex {random_name}.tex'], capture_output=True)
            if result.stderr:
                raise SystemError(f'[ERROR] {result}')
        except Exception as e:
            print(f"[ERROR] {e}:\n{result} ")
    
    def compile_text(self):
        try:
            latex_text= self.convert_to_tex()
            self.cache_file(latex_output)
            self.display_text.clear()
            self.display_text.append(str(latex_text))
            
            #print(latex_text)
        except Exception as e:
            print(f"[ERROR] {e}")

    def _save(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file")
        content = self.convert_to_tex()
        if filepath:
            with open(f"{filepath}.tex", "w") as f:
                f.write(content)

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open file")
        if filepath:
            with open(filepath, "r") as f:
                content = f.read()
            self.text_input.setPlainText(content)

    # ---------------- Styles ----------------
    def style_sheets(self):
        """
        Styles for all of the gui components(for this window)
        """
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

