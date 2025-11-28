reg_name = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']

def get_register_index(reg: str) -> int:
    # s0
    if reg in reg_name:
        return reg_name.index(reg)
    
    # x0, v0
    if reg[0] in 'xv' and reg[1:].isdigit():
        return int(reg[1:])

    print(f"Register '{reg}' not found.")
    return -1

class Instruction:
    def __init__(self, op: str, args: list):
        self.op = op
        self.args = args

    def __str__(self) -> str:
        return f"({self.op:<16}{', '.join([str(arg) for arg in self.args])})"