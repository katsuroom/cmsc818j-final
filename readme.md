# RISC-V Sparse-Sparse Simulator

### Files
- main.py
    - Entry point, loads input file and runs simulation.
- csr.py
    - `make_csr(A)`: Given a 2D array, converts it into CSR format.
- parser.py
    - `parse(file)`: Parses a file containing RISC-V code into a list of Instruction objects.
- util.py
    - `Instruction` class
        - `op`: str, opcode of the instruction (ex. addi)
        - `args`: list, list of arguments for the instruction.
            - Register arguments are in **str** type.
            - Integer arguments are in **int** type.
    - `get_register_index(str)`: Given a register name in str type, return the index that the register corresponds to in the RISC-V register file.
- risc.py
    - Simulator class.