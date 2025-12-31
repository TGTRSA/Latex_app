import parser
import time
import os
import subprocess
import sys


filename = "src/integral.txt"
latex_folder_directory = r"/home/tash/pythonProds/latex_app/latex_files"

"""
\documentclass{standalone}
\\begin{document}

\\begin{equation}
"""

# Takes the list of commands from the parser class and writes up latex source code for each instance of a command
class Compiler:
    def __init__(self, cmds):
        self.cmds= cmds
    
    def write_template(self):
        source_code_array = []
        for indx in range(len(cmds)):
            command = cmds[indx][0]
            command_position = cmds[indx][1]
            latex_src_code = "\n".join([
            r"\documentclass{article}",
            r"\usepackage{amsmath}",
            r"\begin{document}",
            r"\begin{equation}",
            rf"${command}$",
            r"\end{equation}",
            r"\end{document}",
                ])                        #time.sleep(1)
            print("Generating source code")
            source_code_array.append([latex_src_code, command_position])
        return source_code_array

    #[TODO]: A function that runs the system commands to compile latex source code to dvi and then the dvi to svg
    def compile(self, source_code_array:list):
        number_of_files = len(source_code_array)
        for indx in range(number_of_files):
            future_file = source_code_array[indx]
            print(future_file)
            self.write_to_latex(future_file)

    def latex_compile(self, latex_filepath):
        print(f"{latex_filepath}\n")
        try:
            if os.path.exists(latex_filepath):
                print(f"{latex_filepath} exists")
                tex_dir = os.path.dirname(latex_filepath)
                tex_file = os.path.basename(latex_filepath)

                subprocess.run(
                    ["latex", tex_file],
                    cwd=tex_dir,      # ← THIS is the key
                    check=True
                    )

            else:
                print("It seems the filepath does not exist??? ")
        except Exception as e:
            print(f"[X] Error : {e}")
            sys.exit(1)
        print(output)

 
    #Creates latex file to be compiled to dvi and then svg
    
    def write_to_latex(self,latex_source_code:list):
        folder = latex_source_code[1]
        print(f"LATEX SOURCE CODE ARRAY: {latex_source_code}")
        
        filename = latex_source_code[1]
        os.system(rf"mkdir ~/pythonProds/latex_app/latex_files/{folder}") 
        latex_filepath = latex_folder_directory +f"/{folder}" + f"/{latex_source_code[1]}.tex"
        
        print(latex_filepath)
        
        with open(latex_filepath, 'w') as latex_file:
            latex_file.write(latex_source_code[0])
        print(f"{filename} created")
        
        self.latex_compile(latex_filepath)

   
text=parser.reader(filename)
cmds = parser.Parser(text).find_cmds()
compiler = Compiler(cmds)
source_code_array = compiler.write_template()
compiler.compile(source_code_array)
