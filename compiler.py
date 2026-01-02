from lark import Lark, Transformer, v_args, Token, Tree
import os
import json

filepath = "/home/tash/pythonProds/latex_app/src/latex_template.txt"

#latex_template = "\documentclass{standalone}
 #                   \begin{document}

  #                  \begin{equation}"

#TODO: Utilise the grammar,bnf file for command/syntax detection => DONE
#TODO: Add tikz support to the latex source code 


class Compiler:
    """
    Converts the parse tree into LaTeX code.
    Only command blocks produce special LaTeX environments.
    """
    
    def compile(self, node):
        # initialize flag on first ever call
        if not hasattr(self, "_is_root"):
            self._is_root = True
        is_root_call = self._is_root
        self._is_root = False

        if isinstance(node, Tree):
            result = self.compile_tree(node)

            # ✅ wrap only ONCE, only at root, only if not already document
            if is_root_call and node.data != "document":
                return self.compile_document([node])

            return result

        elif isinstance(node, Token):
            return node.value

        return ""


    def compile_tree(self, tree):
        method = getattr(self, f"compile_{tree.data}", None)
        if method:
            return method(tree.children)
        else:
            return "".join(self.compile(c) for c in tree.children)

    # ---------- document ----------
    def compile_document(self, children):
        body = "".join(self.compile(c) for c in children)
        return (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage{amsmath}\n"
            "\\usepackage{amssymb}\n"
            "\\usepackage{tikz}\n"
            "\\usepackage{geometry}\n"
            "\\begin{document}\n"
            f"{body}\n"
            "\\end{document}"
        )

    # ---------- headers ----------
    def compile_h1(self, children):
        return f"\\section{{{self.extract_text(children)}}}\n"
    def compile_h2(self, children):
        return f"\\subsection{{{self.extract_text(children)}}}\n"
    def compile_h3(self, children):
        return f"\\subsubsection{{{self.extract_text(children)}}}\n"

    # ---------- paragraphs ----------
    def compile_paragraph(self, children):
        return "".join(self.compile(c) for c in children) + "\n\n"
    def compile_sentence(self, children):
        return "".join(self.compile(c) for c in children)

    # ---------- lists ----------
    def compile_list(self, children):
        return "\\begin{itemize}\n" + "".join(self.compile(c) for c in children) + "\\end{itemize}\n"
    def compile_item(self, children):
        return "  \\item " + self.extract_text(children) + "\n"

    # ---------- command blocks ----------
    def compile_command_block(self, children):
        body = self.extract_text(children)
        return f"\\begin{{equation}}\n{body}\n\\end{{equation}}\n"

    # ---------- helpers ----------
    def extract_text(self, nodes):
        return "".join(
            self.compile(n)
            for n in nodes
            if not (isinstance(n, Token) and n.type in {"HASH", "STAR", "BANG", "NEWLINE"})
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
    for example in os.listdir('examples/'):
        print(f'Starting parser on {example}\n')

        with open(f'examples/{example}', 'r') as file:
            text = file.read()
        tree = Parser(text).parse()
        print(f'Tree for {example}:\n{tree}')
        latex = Compiler().compile(tree)
        print(latex)
    
