import numpy as np

from util import *
from csr import make_csr

class RISCV:
    def __init__(self):

        # assume 1K memory, enough to store 3 matrices of size 16x16 (A, B, C)
        self.memory = np.zeros(1024, dtype=int)

        # register file: 32 integer registers
        self.rf = np.zeros(32, dtype=int)

        # count number of elements in final output C
        self.num_elements = 0

        # each vector register holds 128 elements
        self.VLEN = 128

        # vector register file: 32 vector registers
        self.vrf = np.zeros((32, self.VLEN), dtype=int)

        # special vector length register (corresponds to number of elements)
        self.vl = 0

        # program counter
        self.pc = 0

        # record runtime metrics
        self.cycles = 0         # number of instructions executed
        self.mem_accesses = 0   # number of elements read/written to memory

    def print_state(self):

        # print special registers
        print(f"pc: {self.pc}")
        print(f"vl: {self.vl}")

        # print rf
        print("rf:")
        for i in range(len(self.rf)):
            reg = f"[x{i}]"
            print(f"{reg:>5} = {self.rf[i]:<8}", end="")
            if (i+1) % 8 == 0:
                print()

        # print first 10 vrf
        print("vrf:")
        for i in range(10):
            print(f"[v{i}] = " + "".join([f"{x:>4}" for x in self.vrf[i][:16]]))

        # print memory, first 128 elements
        print("memory:")
        for i in range(128):
            print(f"[{self.memory[i]:>4}]", end="")
            if (i+1) % 16 == 0:
                print()

    def print_result(self):
        addr = self.rf[get_register_index("x19")] - self.num_elements

        C = self.memory[addr:addr+self.num_elements]

        print("C:")
        for i in range(len(C)):
            print(f"[{C[i]:>4}]", end="")
            if (i+1) % 4 == 0:
                print("")

    def load_dense(self, A, B):
        
        self.num_elements = len(A[0]) * len(B)

        # store number of cols in A into register
        self.rf[get_register_index("x17")] = len(A[0])

        # store number of rows in A into register
        self.rf[get_register_index("x18")] = len(A)

        A = A.reshape(-1)
        B = B.reshape(-1)

        # store end address into register (C)
        self.rf[get_register_index("x19")] = len(A) + len(B)

        # copy all data into memory
        self.rf[get_register_index("x30")] = 0
        self.rf[get_register_index("x31")] = len(A)
        self.memory[0:len(A)] = A
        self.memory[len(A):len(A)+len(B)] = B

    def load_csr(self, A, B):

        self.num_elements = len(A[0]) * len(B)

        (A_row_ptr, A_col, A_val) = make_csr(A)
        (B_row_ptr, B_col, B_val) = make_csr(B)

        data = [A_row_ptr, A_col, A_val, B_row_ptr, B_col, B_val]

        # copy all data into memory
        addr = 0
        for i, v in enumerate(data):
            self.rf[get_register_index(f"x{i+20}")] = addr
            self.rf[get_register_index(f"x{i+26}")] = len(v)
            self.memory[addr:addr+len(v)] = v
            addr += len(v)

        # store number of cols in A into register
        self.rf[get_register_index("x17")] = len(A[0])

        # store number of rows in A into register
        self.rf[get_register_index("x18")] = len(A)

        # store end address into register (C)
        self.rf[get_register_index("x19")] = addr

    def run(self, code: list[Instruction], labels: dict[str, int]):
        while True:
            if self.pc >= len(code):
                break
            
            inst = code[self.pc]
            op = inst.op
            args = inst.args

            # set to true if encounter instruction that modifies self.pc
            branch = False

            match inst.op:
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
                case "sub":
                    a = get_register_index(args[0])
                    b = get_register_index(args[1])
                    c = get_register_index(args[2])
                    self.rf[a] = self.rf[b] - self.rf[c]
                case "mul":
                    a = get_register_index(args[0])
                    b = get_register_index(args[1])
                    c = get_register_index(args[2])
                    self.rf[a] = self.rf[b] * self.rf[c]
                case "j":
                    label = args[0]
                    if label in labels.keys():
                        self.pc = labels[label]
                        branch = True
                    else:
                        print(f"Line {self.pc+1}: Label '{label}' not found.")
                        quit()
                case "beq":
                    a = get_register_index(args[0])
                    b = get_register_index(args[1])
                    label = args[2]
                    if self.rf[a] == self.rf[b]:
                        if label in labels.keys():
                            self.pc = labels[label]
                            branch = True
                        else:
                            print(f"Line {self.pc+1}: Label '{label}' not found.")
                            quit()

                # sets vl to max vector register size (VLEN)
                case "vconfig":
                    self.vl = self.VLEN

                # sets vl to length within reg[b], writes to reg[a]
                case "vsetvl":
                    a = get_register_index(args[0])
                    b = get_register_index(args[1])
                    self.vl = min(self.VLEN, self.rf[b])
                    self.rf[a] = self.vl

                # load vl elements into vector as 32-bit elements
                case "vlw":
                    v = get_register_index(args[0])
                    offset = args[1]
                    r = get_register_index(args[2])
                    addr = self.rf[r]
                    self.vrf[v][0:self.vl] = self.memory[addr+offset:addr+offset+self.vl]
                    self.mem_accesses += self.vl

                # store vl elements into memory as 32-bit elements
                case "vsw":
                    v = get_register_index(args[0])
                    offset = args[1]
                    r = get_register_index(args[2])
                    addr = self.rf[r]
                    self.memory[addr+offset:addr+offset+self.vl] = self.vrf[v][0:self.vl]
                    self.mem_accesses += self.vl

                # copy first element of vector into scalar register
                case "vmv.x.s":
                    r = get_register_index(args[0])
                    v = get_register_index(args[1])
                    self.rf[r] = self.vrf[v][0]

                # copy scalar register into first element of vector
                case "vmv.s.x":
                    v = get_register_index(args[0])
                    r = get_register_index(args[1])
                    self.vrf[v][0] = self.rf[r]

                # copy scalar register into all slots of vector register
                case "vmv.v.x":
                    v = get_register_index(args[0])
                    r = get_register_index(args[1])
                    self.vrf[v][0:self.vl] = self.rf[r]

                # copy vector to vector
                case "vmv.v.v":
                    va = get_register_index(args[0])
                    vb = get_register_index(args[1])
                    self.vrf[va][0:self.vl] = self.vrf[vb][0:self.vl]

                # vector + vector
                case "vadd.vv":
                    va = get_register_index(args[0])
                    vb = get_register_index(args[1])
                    vc = get_register_index(args[2])
                    self.vrf[va] = self.vrf[vb] + self.vrf[vc]

                # vector * scalar
                case "vmul.vx":
                    va = get_register_index(args[0])
                    vb = get_register_index(args[1])
                    r = get_register_index(args[2])
                    self.vrf[va][0:self.vl] = self.vrf[vb][0:self.vl] * self.rf[r]

                # shift elements in vector left, fill remaining with zeros
                case "vslideup.vx":
                    va = get_register_index(args[0])
                    vb = get_register_index(args[1])
                    r = get_register_index(args[2])
                    shift = self.rf[r]
                    self.vrf[va][0:self.vl-shift] = self.vrf[vb][shift:self.vl]
                    self.vrf[va][self.vl-shift+1:self.vl] = 0

                # shift elements in vector right, fill remaining with zeros
                case "vslidedown.vx":
                    va = get_register_index(args[0])
                    vb = get_register_index(args[1])
                    r = get_register_index(args[2])
                    shift = self.rf[r]
                    self.vrf[va][shift:self.vl] = self.vrf[vb][0:self.vl-shift]
                    self.vrf[va][0:shift] = 0

                # new instruction: indexed move
                case "vindexmv":
                    va = get_register_index(args[0])
                    vb = get_register_index(args[1])
                    vc = get_register_index(args[2])
                    for i in range(self.vl):
                        idx = self.vrf[vc][i]
                        self.vrf[va][idx] = self.vrf[vb][i]

                case _:
                    print(f"Instruction '{op}' not recognized.")
                    quit()
            # end match

            # increment program counter
            if not branch:
                self.pc += 1

            self.cycles += 1

            # maintain register x0 = 0
            self.rf[0] = 0