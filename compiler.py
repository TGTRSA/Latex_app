from lark import Lark, Transformer, v_args, Token, Tree

import json

filepath = "/home/tash/pythonProds/latex_app/src/latex_template.txt"

#latex_template = "\documentclass{standalone}
 #                   \begin{document}

  #                  \begin{equation}"

#TODO: Utilise the grammar,bnf file for command/syntax detection
#TODO: Add tikz support to the latex source code 

class Compiler:
    """
    Reads the tokens within the parse tree then 'converts' them into
    latex code
    """
    def compile(self, node):
        if isinstance(node, Tree):
            return self.compile_tree(node)
        elif isinstance(node, Token):
            return node.value
        return ""

    def compile_tree(self, tree):
        method = getattr(self, f"compile_{tree.data}", None)
        if method:
            return method(tree.children)
        else:
            # default: compile children
            return "".join(self.compile(c) for c in tree.children)

    # ---------- document ----------
    def compile_document(self, children):
        body = "".join(self.compile(c) for c in children)
        return (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"{body}\n"
            "\\end{document}"
        )

    # ---------- headers ----------
    def compile_h1(self, children):
        text = self.extract_text(children)
        return f"\\section{{{text}}}\n"

    def compile_h2(self, children):
        text = self.extract_text(children)
        return f"\\subsection{{{text}}}\n"

    def compile_h3(self, children):
        text = self.extract_text(children)
        return f"\\subsubsection{{{text}}}\n"

    # ---------- paragraphs ----------
    def compile_paragraph(self, children):
        text = "".join(self.compile(c) for c in children)
        return f"{text}\n\n"

    def compile_sentence(self, children):
        return "".join(self.compile(c) for c in children)

    # ---------- lists ----------
    def compile_list(self, children):
        items = "".join(self.compile(c) for c in children)
        return "\\begin{itemize}\n" + items + "\\end{itemize}\n"

    def compile_item(self, children):
        text = self.extract_text(children)
        return f"  \\item {text}\n"

    # ---------- commands ----------
    def compile_inline_command(self, children):
        # $ ... $
        return f"${self.extract_text(children)}$"

    def compile_command_block(self, children):
        # ! ... !
        return f"\\[{self.extract_text(children)}\\]\n"

    # ---------- helpers ----------
    def extract_text(self, nodes):
        return "".join(
            self.compile(n)
            for n in nodes
            if not (isinstance(n, Token) and n.type in {"HASH", "STAR", "DOLLAR", "BANG", "NEWLINE"})
        )
   

class Parser:
    def __init__(self,text):
        self.text = text
        self.operator = Lark(open('grammar.ebnf').read(), parser='lalr', start='document')
    
    def parse(self):
        tree = self.operator.parse(self.text)
        return tree
    
    def lex_text(self):
        lexed_text = self.operator.lex(self.text)
        return lexed_text

def travel(tree):
    tree_nodes = []
    token_nodes = []
    for child in tree.children:
        if isinstance(child, Tree):
            tree_nodes.append(child)
            
        if isinstance(child, Token):
            token_nodes.append(child)
    print("Trees:\n", tree_nodes)
    print("Tokens:\n", token_nodes)
            

if __name__ == "__main__":
    with open('example.txt', 'r') as file:
        text = file.read()
    tree = Parser(text).parse()
    latex = Compiler().compile(tree)
    print(latex)
    #for token in lexed_text: 
     #   print(token.type)
    #ast = ASTTransformer().transform(tree)
    #print(type(ast))
    #json.dumps(ast)
