# Basic Outline
 This project will attempt to take in some text and parse it into a latex source file.
 It will use a custom parser, lexer and compiler using some newly defined markdown structured langauge.


# Compiler.py
This file uses some base latex as a template and will structure the text around it. 
It includes the parser which will read the text and parse it into components based on the "grammar.bnf" file using lark as a lexer base.

# Savefiles
The folder in which the generated latex files will go.

# tmp
A folder for temporary latex files that allows for caching generated latex code
