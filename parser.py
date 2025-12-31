## the parser will read from some file the text and serialise the tokens into commands then the compielr will compile the 
## document from the serialised tokens/commands

import numpy as np
import re 

latex_file = "src/integral.txt"

# FORMAT => \command{context}
some_text = r"Looking for fraction \frac{a}{b}"


tokens = {
        "\\": "command found",
}

commands = {
        "int": "integral"
        }

commands = []

# OUTLINE: commands_map[1] => ["command", position]
#commands_map


def reader(filename):
    with open(filename, 'r') as file:
        text = file.read()
    return text


class Parser:
    def __init__(self, text):
        self.text =text

    def find_cmds(self):
        command = ""
        length_of_text = len(self.text)
        # Checking every letter of text
        for current_indx in range(length_of_text):
            current_character = self.text[current_indx]
            print(f"c[{current_indx}]: {self.text[current_indx]}")
            # if the current_character is $ then we iterate over the next few characters until }
            if current_character == "$":
                command_position = current_indx
                print("EQUATION FOUND")
                for char in self.text[current_indx+1:length_of_text]:
                    if char != "$":
                        command+=char
                    else:
                        break
                commands.append([command, command_position])
                command = ""
        return commands

    #[TODO]: Command that reads the context of the command ({context})
    def reveal_ctx(self):
        contexts = []
        ctx = ""
        length_of_commands_map = len(commands)
        for command in commands:
            #print(command)
            for j in range(len(command)):
                some_command = command[j]
                if type(some_command) == str:
                    command_length = len(some_command)
                    for u in range(len(some_command)):
                        
                        if some_command[u] =="{":
                            ctx_indx = u
                            for char in some_command[u+1:command_length]:
                                if char == "}":
                                    break
                                ctx+=char

                            contexts.append(ctx)
                     #       print(ctx)
                        ctx = ""
        return contexts
        

if __name__ == "__main__":
    integral_text = reader(latex_file)
    parse = Parser(integral_text)
    cmds = parse.find_cmds()
    ctx_group = parse.reveal_ctx()
    print(f"Commands: {cmds}")
    print(f"Command contexts: {ctx_group}")
