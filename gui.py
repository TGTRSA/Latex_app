import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QVBoxLayout, 
                             QComboBox, QTextEdit, QPushButton, QHBoxLayout, 
                             QLabel, QLineEdit, QScrollArea, QSplitter, QMenu, QFileDialog)
import PyQt5
from PyQt5.QtCore import Qt
#import numpy as np
from compiler import Parser, Compiler
import os


#TODO: create a save button and make it save the file
#TODO: on compile use the outputted latex file and run the neccessary commands to create the .text/.dvi/.svg files
#TODO: create menu box for writing latex code and have it geenrate => $ command $ basis

class StartWindow(QWidget):
    def __init__(self):
        print("Executing window start")
        super().__init__()
        self.init_ui()

    def include_parser(self, text):
        try:
            tree = Parser(text).parse()
        
            latex_text = Compiler().compile(tree)
            print(latex_text)    
            return latex_text
        except Exception as e:
            print(f"[ERROR] {e}")
            return -1 

    def init_ui(self):
        """
        Loads all the ui components for the window
        """
        print("[X] LOADING UI COMPONENTS [X]")
        self.setWindowTitle("My PyQt Window")
        self.setGeometry(100,100,400,300)
        self.double_display()
        #self.menu_bar()    
        layout = QVBoxLayout()
        layout.addWidget(self.compile_button)
        layout.addWidget(self.splitter)
        #layout.addWidget(self.menu_bar)
        self.style_sheets()

        self.setLayout(layout)
        self.show()
    
    #FIX: Displays the menu at the bottom and it seems to be a huge widget not just a long top bar like in most apps 
    def menu_bar(self):
        self.menu_bar = QMenu()
        file_menu = self.menu_bar.addMenu("&File")
        
        file_menu.addAction("Open")
        file_menu.addAction("Save")

    def double_display(self):
        """
        Screen splitter with input | output sets
        """
        self.splitter = QSplitter(Qt.Horizontal)
        text_input = QTextEdit()
        text_input.setPlaceholderText("Type here")
        self.splitter.addWidget(text_input)

        display_text = QTextEdit()
        display_text.setReadOnly(True)
        self.splitter.addWidget(display_text)

        self.splitter.setSizes([320, 480])
        
        
        self.compile_button = QPushButton("Compile")
        self.save_file_button = QPushButton("Save")
        self.compile_button.setParent(self.splitter)
        self.compile_button.move(300, 450)
        
        def get_text_input():
            text = text_input.toPlainText()
            return text

        def _save():
            filepath, _ = QFileDialog.getSaveFileName(self, "Save file")
            content = get_text_input()
            if filepath:
                with open(filepath, "w") as f:
                    f.write(content)

        def compile_text():
            text = get_text_input()
            latex_text=self.include_parser(text)
            
            display_text.clear()
            display_text.append(str(latex_text))
            
        self.compile_button.clicked.connect(compile_text)
        self.save_file_button.clicked.connect(_save)
        
    def text_inputs(self):
        """
        Slot for all text input components (for this window)
        """
        self.latex_input = QTextEdit()
        self.latex_input.setPlainText("Multi-line here\n")
        self.layout.addWidget(self.latex_input)
        
    
    def style_sheets(self):
        """
        Styles for all of the gui components(for this window)
        """
        self.compile_button.setStyleSheet("""
                                          QPushButton{
                                          background-color: #2ecc71;
                                          border:none;
                                          padding:10px 2px;
                                          border-radius:5px;
                                          max-width:60px;
                                          }
                                          """)

    def show_text_input(self,text):
        if text=='Show Text Input':
            self.text_input.show()
        else:
            self.text_input.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())
