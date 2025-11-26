from riscv import RISCV
from parser import parse
from util import *

import sys
import numpy as np

def print_instructions(code: list[Instruction]):
    for instruction in code:
        print(instruction)

def main():
    # expect 1 input file argument
    if len(sys.argv) != 2:
        print("usage: sim <file>")
        quit()
    
    # parse instructions
    file = open(sys.argv[1], "r")
    code: list[Instruction] = parse(file)
    print_instructions(code)

    # load input matrices
    A = np.array([
        [3,2,0,0],
        [0,0,0,0],
        [4,5,1,0],
        [0,0,3,2]
    ])

    B = A.T

    # create simulator
    riscv = RISCV()

    # load A and B in CSR format into memory
    riscv.load_csr(A, B)

    # run code
    riscv.run(code)

    riscv.print_state()

if __name__ == "__main__":
    main()