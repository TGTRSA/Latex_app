# Basic Outline
 This project will attempt to take in some text and parse it into a latex source file.
 It will use a custom parser, lexer and compiler using some newly defined markdown structured langauge.


# Compiler.py
This file uses some base latex as a template and will structure the text around it. 
It includes the parser which will read the text and parse it into components based on the "grammar.bnf" file using lark as a lexer base.

# gui.py
## Cache
        uses random name initated at the start of a window and changed upon a file being opened more akin to a session ID
        

### Savefiles
    The folder in which the generated text files will go.

# tmp
A folder for temporary latex files that allows for caching generated latex code
tmp will hold the filenames as directories where the .tex/.dvi/.svg versions of the file will be geld

