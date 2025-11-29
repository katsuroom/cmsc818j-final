from riscv import RISCV
from parser import parse
from util import *

import sys
import numpy as np

def print_instructions(code: list[Instruction]):
    for i, instruction in enumerate(code):
        print(f"{i:<4}: {instruction}")

def print_labels(labels):
    print(labels)

def main():
    # expect 1 input file argument
    if len(sys.argv) != 2:
        print("usage: sim <file>")
        quit()
    
    # parse instructions
    file = open(sys.argv[1], "r")
    code, labels = parse(file)
    print_instructions(code)
    print_labels(labels)

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
    # riscv.load_dense(A, B)

    # run code
    riscv.run(code, labels)

    riscv.print_state()

    riscv.print_result()

    print(f"Completed in {riscv.cycles} cycles, {riscv.mem_accesses} memory accesses.")

if __name__ == "__main__":
    main()