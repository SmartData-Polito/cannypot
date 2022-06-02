import bashlex
import re
import copy
import itertools 
import numpy as np


def _handle_command(statement, full_statement):
    new_statement = statement.parts.copy()
    
    # For generating all the strings for permissions in unix filesystem
    lst = [str(int(el)) for el in np.arange(1,8)]
    permission_combs = ["".join(el) for el in list(itertools.product(lst, repeat=3))] 
    
    #Handle cases such as 'echo "root 123qwe" > /tmp/up.txt;'
    while "redirect" in [el.kind for el in new_statement]:
        index = [el.kind for el in new_statement].index("redirect")
        redirect = new_statement.pop(index)
        new_statement.insert(index+1, redirect.output)
        node_object = copy.deepcopy(redirect.output)
        node_object.pos, node_object.word = redirect.pos, redirect.type
        new_statement.insert(index, node_object)

    key = " ".join([el.word for el in new_statement])
    
    list_of_subtokens = []
    list_of_subtokens.append((new_statement[0].word, "command"))
    for inner_part in new_statement[1:]:
        if "-" in inner_part.word[:2] or "+" in inner_part.word[:2] or inner_part.word in permission_combs:
            list_of_subtokens.append((inner_part.word, "flag"))
        elif ">" == inner_part.word:
            list_of_subtokens.append((inner_part.word, "redirect"))
        else:
            list_of_subtokens.append((inner_part.word, "param"))
    
    return list_of_subtokens


def _parse(cmd):
    line = str(copy.deepcopy(cmd))
    if cmd is None or cmd == "":
        return []

    sub_tokens = []
    
    if "sudo" in line:
        line = line.replace("sudo", "")
    if re.sub('[^A-Za-z0-9]+', '', line)!= "": #Remove empty strings
        if line.split(" ")[0] == "/system": #Capture Mikrotik commands (which we want to avoid for now)
            print("Mikrotik command")
            print("Should do something")
        else:
            if "#" in line: #We have to temporaly remove it since the parser cannot capture it
                line = line.replace("#", "hash").replace("\n", "new_line")
            if line[-1]!=";": #Each line must end with a ";" to be parsed
                line += ";"
            try:
                statements = bashlex.parse(line) #here we separate the statements and analyse them 1 by 1
                for statement in statements[0].parts:
                    if statement.kind == "pipeline":
                        for inner_statement in statement.parts:
                            if inner_statement.kind == "command":  
                                sub_tokens.append(_handle_command(inner_statement, line))
                    elif statement.kind == "command":
                        sub_tokens.append(_handle_command(statement, line))  
            except Exception as e:
                # PRINT EXCEPTION INTO LOGS AND THING ABOUT SOMETHING ELSE
                print(f"exception {e}!")
    return sub_tokens


# Change flags here to decide what to keep
# TODO
def _normalize_command(command_statements, flags=True, params=False, sort=False, executables=False):
    s = []
    # Each command can have a series of statements   
    for statement in command_statements:
        #Each statement has multiple components (i.e. command + flag + param)
        for sub_component in statement:
            if sub_component[1] == "param":
                if params:
                    s.append(sub_component[0].strip())
            elif sub_component[1] == "flag" or sub_component[1] == "redirect":
                if flags:
                    s.append(sub_component[0].strip())
            else:
                if not executables:
                    if "./" == sub_component[0].strip()[:2]:
                        s.append('./EXEC')
                    elif len(sub_component[0].split("/")) != 1:
                        s.append(sub_component[0].split("/")[-1].strip())
                        
                    elif "Enter" != sub_component[0].strip():
                        if sub_component[0].strip()[-1] == ":":
                            s.append(sub_component[0].strip()[:-1])
                        elif sub_component[0].strip() == "LC_ALL=en_US.UTF-8":
                            s.append("bash")
                        else:
                            s.append(sub_component[0].strip())
                else:
                    s.append(sub_component[0].strip())
    if sort:
        s.sort()
    
    return '; '.join(map(str, s))


def process_command(command_to_parse):
    parsed = _parse(command_to_parse)
    normalized = _normalize_command(parsed)
    return normalized