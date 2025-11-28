from util import *

import re

# return True if line is an instruction
def parse_line(line: str, linenum: int, instructions: list, labels: dict) -> int:

    # if label
    if line[-1] == ":":
        label_name = line[:-1]
        if bool(re.search("[a-zA-Z]([a-zA-Z]|[0-9]|_)*:", line)):
            if label_name in labels.keys():
                print(f"Line {linenum+1}: Label '{label_name}' already exists.")
                quit()
        
            labels[line[:-1]] = linenum
            return False
        else:
            print(f"Line {linenum+1}: Invalid label name '{label_name}'.")
            quit()
    
    parts = line.split()
    op = parts[0]
    args = []

    
    for arg in parts[1:]:
        arg = arg.strip(",")

        # if const int
        if arg.isdigit():
            args.append(int(arg))

        # if binary int
        elif arg.startswith("0b") and arg[2:].isdigit():
            args.append(int(arg[2:], 2))

        # if memory offset (ex. 0(x1))
        elif bool(re.search("^[0-9]+(.+)", arg)):
            parts = arg.split("(", 1)
            offset = int(parts[0])
            reg = parts[1].strip(")")
            if get_register_index(reg) == -1:
                print(f"Line {linenum+1}:Invalid register argument.")
                quit()
            
            args.append(offset)
            args.append(reg)

        else:
            args.append(arg)

    instructions.append(Instruction(op, args))
    return True

def parse(file) -> tuple[list[Instruction], dict[str, int]]:
    lines = file.readlines()
    instructions = []
    labels = {}

    linenum = 0
    for line in lines:
        # remove comments
        line = line.split(';', 1)[0].strip()
        if line == "":
            continue

        is_inst = parse_line(line, linenum, instructions, labels)
        if is_inst:
            linenum += 1

    return (instructions, labels)