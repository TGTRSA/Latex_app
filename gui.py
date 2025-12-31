import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QVBoxLayout, 
                             QComboBox, QTextEdit, QPushButton, QHBoxLayout, 
                             QLabel, QLineEdit, QScrollArea, QSplitter, QMenu)
import PyQt5
from PyQt5.QtCore import Qt
#import numpy as np
from compiler import Parser

#TODO: create a save button and make it save the file
#TODO: on compile use the outputted latex file and run the neccessary commands to create the .text/.dvi/.svg files
#TODO: create menu box for writing latex code and have it geenrate => $ command $ basis

class StartWindow(QWidget):
    def __init__(self):
        print("Executing window start")
        super().__init__()
        self.init_ui()

    def include_parser(self, text):
        latex_file_text=Parser(text).parse()
        return latex_file_text 

    def init_ui(self):
        """
        Loads all the ui components for the window
        """
        print("[X] LOADING UI COMPONENTS [X]")
        self.setWindowTitle("My PyQt Window")
        self.setGeometry(100,100,400,300)
        self.double_display()
        self.menu_bar()    
        layout = QVBoxLayout()
        layout.addWidget(self.compile_button)
        layout.addWidget(self.splitter)
        layout.addWidget(self.menu_bar)
        self.setLayout(layout)
        self.show()
    
    #FIX: Displays the menu at the bottom and it seems to be a huge widget not just a long top bar like in most apps 
    def menu_bar(self):
        self.menu_bar = QMenu()
        file_menu = self.menu_bar.addMenu("&File")
        
        file_menu.addAction("Open")

    def double_display(self):
        self.splitter = QSplitter(Qt.Horizontal)
        text_input = QTextEdit()
        text_input.setPlaceholderText("Type here")
        self.splitter.addWidget(text_input)

        display_text = QTextEdit()
        display_text.setReadOnly(True)
        self.splitter.addWidget(display_text)

        self.splitter.setSizes([320, 480])
        
        #FIX: Compile button is too large and in the middle which just looks dreadful
        self.compile_button = QPushButton("Compile")
        self.save_file_button = QPushButton("Save")

        def compile_text():
            text = text_input.toPlainText()
            latex_file_text=self.include_parser(text)
            
            display_text.clear()
            display_text.append(latex_file_text)
            
        self.compile_button.clicked.connect(compile_text)

    def text_inputs(self):
        self.latex_input = QTextEdit()
        self.latex_input.setPlainText("Multi-line here\n")
        self.layout.addWidget(self.latex_input)
        
    
    def show_text_input(self,text):
        if text=='Show Text Input':
            self.text_input.show()
        else:
            self.text_input.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    sys.exit(app.exec_())
