# RISC-V Sparse-Sparse Simulator

Only dependency: `numpy`

Usage: `main.py <text file>`

## Implementation

**main.py** is an example entry point for the simulator, which creates a 4x4 matrix and its transpose. The path to a text file containing RISC-V code provided as a command-line argument is read, and the program calls **parser.py::parse()** to parse the text into a list of instructions and dictionary of labels.

Each instruction creates an Instruction object instance (**util.py**), which contains a string representing the instruction's opcode and a list for the operands. All integer operands are converted from strings into integers.

The provided RISC-V code files include:
- `dense.txt`: Computes dense*dense matrix multiplication
- `csr.txt`: Computes CSR*CSR sparse matrix multiplication using only native RISC-V instructions.
- `csr-opt.txt`: Computes an optimized CSR*CSR using custom instructions.

**riscv.py** includes the definition of the simulator class that handles internal hardware state and executes instructions. After creating a new simulator instance, use **riscv.py::load_csr(A, B)** or **riscv.py::load_dense(A, B)** to load the input matrices into memory and populate the register file.
- If using `csr.txt` or `csr-opt.txt` are passed, **load_csr** must be called.
- if using `dense.txt`, **load_dense** must be called.

The function for converting a 2D matrix to CSR format is implemented in **csr.py**.

Once the simulator has been initialized, use the **riscv.py::run(code, labels)** method to execute the parsed instructions. The list of instructions is run one by one, matching the instruction's opcode and modifying the hardware state accordingly. For the sake of simplicity, only the instructions that appear in the provided RISC-V code files are handled.

After the code execution completes, a few methods can be used to display results.
- **riscv.py::print_state()** displays the values of the registers and a portion of the vector registers, as well as the main memory. This can also be called during code execution for debugging.
- **riscv.py::print_result()** prints the computed output matrix to the console.

**main.py** also includes a few print statements to display the number of instructions executed, number of reads/writes made to memory, and the number of elements processed by the _vscatteracc_ instruction.