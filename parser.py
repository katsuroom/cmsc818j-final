from util import *

def parse_line(line: str) -> Instruction:
    parts = line.split()
    op = parts[0]
    args = []
    
    for arg in parts[1:]:
        arg = arg.strip(",")
        if arg.isdigit():
            args.append(int(arg))
        else:
            args.append(arg)

    return Instruction(op, args)

def parse(file) -> list[Instruction]:
    lines = file.readlines()
    instructions = []

    for line in lines:
        line = line.strip()

        inst = parse_line(line)
        instructions.append(inst)

    return instructions