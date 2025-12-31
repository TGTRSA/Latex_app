

filepath = "/home/tash/pythonProds/latex_app/src/latex_template.txt"

#latex_template = "\documentclass{standalone}
 #                   \begin{document}

  #                  \begin{equation}"

#TODO: Add functionality for detecting commands
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

#Parser("This is some not so long text $command block$").parse()

