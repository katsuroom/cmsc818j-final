import numpy as np

from util import *
from csr import make_csr

class RISCV:
    def __init__(self):

        # assume 1K memory, enough to store 3 matrices of size 16x16 (A, B, C)
        self.memory = np.zeros(1024, dtype=int)

        # register file: 32 integer registers
        self.rf = np.zeros(32, dtype=int)

        # vector register file: 32 vector registers, each 128 elements
        self.vrf = np.zeros((32, 128), dtype=int)

        # index into self.memory
        self.addr_ptr = 0

        # record runtime metrics
        self.cycles = 0
        self.mem_accesses = 0

    def print_state(self):
        # print rf
        print("rf:")
        for i in range(len(self.rf)):
            reg = f"[x{i}]"
            print(f"{reg:>5} = {self.rf[i]:<8}", end="")
            if (i+1) % 8 == 0:
                print()

        # print first 8 vrf
        print("vrf:")
        for i in range(8):
            print(f"[v{i}] = {', '.join([str(x) for x in self.vrf[i][:16]])}")
            pass

        # print memory, first 128 elements
        print("memory:")
        for i in range(128):
            print(f"[{self.memory[i]:>4}]", end="")
            if (i+1) % 16 == 0:
                print()


    def load_csr(self, A, B):
        (A_row_ptr, A_col, A_val) = make_csr(A)
        (B_row_ptr, B_col, B_val) = make_csr(B)

        data = [A_row_ptr, A_col, A_val, B_row_ptr, B_col, B_val]

        # copy all data into memory, moving self.addr_ptr
        for i, v in enumerate(data):
            addr = self.addr_ptr
            self.rf[get_register_index(f"x{i+18}")] = addr
            self.memory[addr:addr+len(v)] = v
            self.addr_ptr += len(v)

    def run(self, code: list[Instruction]):
        for inst in code:
            op = inst.op
            args = inst.args

            match(inst.op):
                case "addi":
                    a = get_register_index(args[0])
                    b = get_register_index(args[1])
                    imm = args[2]
                    self.rf[a] = self.rf[b] + imm
                case "add":
                    a = get_register_index(args[0])
                    b = get_register_index(args[1])
                    c = get_register_index(args[2])
                    self.rf[a] = self.rf[b] + self.rf[c]

                case _:
                    print(f"Instruction '{op}' not recognized.")
                    quit()

        # end for