from lark import Lark, Transformer, v_args
import json

filepath = "/home/tash/pythonProds/latex_app/src/latex_template.txt"

#latex_template = "\documentclass{standalone}
 #                   \begin{document}

  #                  \begin{equation}"

#TODO: Utilise the grammar,bnf file for command/syntax detection
#TODO: Add tikz support to the latex source code 


class ASTTransformer(Transformer):
    def document(self, items):
        return {"type": "document", "content": items}
    
    def h1(self, items):
        return {"type": "header", "level": 1, "text": " ".join(str(i) for i in items if i.type == 'TEXT')}
    def h2(self, items):
        return {"type": "header", "level": 2, "text": " ".join(str(i) for i in items if i.type == 'TEXT')}
    def h3(self, items):
        return {"type": "header", "level": 3, "text": " ".join(str(i) for i in items if i.type == 'TEXT')}
    
    def paragraph(self, items):
        return {"type": "paragraph", "sentences": items}
    
    def sentence(self, items):
        # Merge TEXT and inline_command
        text = []
        for i in items:
            if isinstance(i, dict) and i.get("type") == "inline_command":
                text.append(f"${i['command']}$")
            else:
                text.append(str(i))
        return " ".join(text)
    
    def list(self, items):
        return {"type": "list", "items": items}
    
    def item(self, items):
        # Merge text_inline like in sentence
        text = []
        for i in items:
            if isinstance(i, dict) and i.get("type") == "inline_command":
                text.append(f"${i['command']}$")
            elif hasattr(i, 'type') and i.type == 'STAR':
                continue
            else:
                text.append(str(i))
        return " ".join(text)
    
    def inline_command(self, items):
        return {"type": "inline_command", "command": str(items[0])}
    
    def command_block(self, items):
        return {"type": "command_block", "command": str(items[0])}
    
    def TEXT(self, token):
        return str(token)
    
    def COMMAND_TEXT(self, token):
        return str(token)

class Parser:
    def __init__(self,text):
        self.text = text

    def parse(self):
        source = ""
        buffer=1024
        for i in range(0, len(self.text), buffer):
            source += self.text[0:buffer]
         
        latex_file_text = r"\documentclass{standalone}"+"\n"+r"\begin{document}"+"\n"
        latex_file_text += f"{source}\n"
        latex_file_text += r"\end{document}"
        
        return latex_file_text
        #print(latex_file_text)


parser = Lark(open('grammar.ebnf').read(), parser='lalr', start='document')

with open('example.txt', 'r') as file:
    text = file.read()
try:
    tree = parser.parse(text)
    print(parser.parse(text))
except Exception as e:
    print(f"[X] Exception: {e}")
ast = ASTTransformer().transform(tree)
print(json.dumps(ast, indent=2))
#Parser("This is some not so long text $command block$").parse()

