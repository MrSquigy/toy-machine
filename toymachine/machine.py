from typing import Callable, Final, Tuple, TypeVar

WORD_SIZE: Final[int] = 32
REGISTER_BITS: Final[int] = 3
MEM_ADDR_BITS: Final[int] = 10
OPCODE_BITS: Final[int] = 6

# Binary values are either str "0b0" or int
Binary = TypeVar("Binary", str, int)


def _split_args(args: str, pos: int, second_bits: int = -1) -> Tuple[str, str]:
    """Split arguments for function calls."""
    if second_bits == -1:
        # Calculate remaining bits
        # works for multiline and single instructions
        second_bits = (
            WORD_SIZE - OPCODE_BITS - pos
            if len(args) == WORD_SIZE - OPCODE_BITS
            else WORD_SIZE
        )

    return ("0b" + args[:pos], "0b" + args[-second_bits:])


class Memory:

    memory_blocks: dict[int, str]

    def __init__(self, blocks: int) -> None:
        self.create_memory(blocks)

    def create_memory(self, num: int) -> None:
        self.memory_blocks = {}

        for i in range(num):
            self.memory_blocks[i] = "0b0"

    def dump(self) -> str:
        dump = "Memory Dump\n"

        for addr, block in self.memory_blocks.items():
            dump += f"{addr}: {block}\n"

        return dump[:-1]

    def load(self, address: int, return_type: str = "b") -> Binary:
        if address not in self.memory_blocks:
            raise Exception(f"Memory address {address} does not exist")

        value: Binary = self.memory_blocks[address]

        if return_type == "d":
            value = int(value, 2)

        return value

    def store(self, address: int, value: Binary) -> None:
        if address not in self.memory_blocks:
            raise Exception(f"Memory address {address} does not exist")

        if isinstance(value, int):
            value = bin(value)

        if (l := len(value) - 2) > WORD_SIZE:
            raise Exception(
                f"Memory address {address} is {WORD_SIZE} bits long, but the value to be stored is {l} bits long"
            )

        self.memory_blocks[address] = value


class CPU:
    registers: dict[str, str]

    memory: Memory

    instruction_set: dict[int, Callable[[str], None]]  # opcode, function

    def __init__(self, memory: Memory):
        self.memory = memory
        self.create_registers()
        self.create_instruction_set()

    def create_registers(self) -> None:
        """Create empty registers."""

        self.registers = {
            "AC": "0b0",  # Accumulator
            "DR": "0b0",  # Data
            "CR": "0b0",  # Counter
            "PC": "0b0",  # Program Counter
            "IR": "0b0",  # Instruction
        }

    def dump(self) -> str:
        """Dump the contents of the registers to a string."""

        dump = "Register Dump\n"
        for regid, register in self.registers.items():
            dump += f"{regid}: {register}\n"

        return dump[:-1]

    def load(self, regid: str, return_type: str = "b") -> Binary:
        """Load a value from a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        value: Binary = self.registers[regid]
        if return_type == "d":
            value = int(value, 2)

        return value

    def load_from_memory(self, address: int, return_type: str = "b") -> Binary:
        """Load a value from memory."""

        return self.memory.load(address, return_type)

    def store_in_memory(self, address: int, value: Binary) -> None:
        """Store a value in memory."""

        self.memory.store(address, value)

    def store(self, regid: str, value: Binary) -> None:
        """Store a value in a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        if isinstance(value, int):
            value = bin(value)

        if (l := len(value) - 2) > WORD_SIZE:
            raise Exception(
                f"Register {regid} is {WORD_SIZE} bits long, but the value to be stored is {l} bits long"
            )

        self.registers[regid] = value

    def load_next_instruction(self) -> None:
        """Load the next instruction for execution."""

        next_instruction_location = self.load("PC", "d")
        next_instruction = self.load_from_memory(next_instruction_location)
        self.store("IR", next_instruction)
        self.store("PC", next_instruction_location + 1)

    def analyze_instruction(self) -> Tuple[int, str]:
        instr: str = self.load("IR")
        if len(instr) != WORD_SIZE + 2:  # 0b + instruction
            raise Exception(f"Instruction {instr[2:]} is not in the correct format")

        # Split into opcode (6-bit) & args
        func_header = (int(instr[: OPCODE_BITS + 2], 2), instr[OPCODE_BITS + 2 :])

        return func_header

    def execute_current_instruction(self) -> None:
        func, args = self.analyze_instruction()

        # Is instruction multiline reserved opcode (111111 == 63)?
        if bin(func) == "0b111111":
            # Get actual function opcode and remaining data bits
            self.load_next_instruction()
            func, remaining_args = self.analyze_instruction()

            # Removing trailing 0's
            throwaway_bits = remaining_args.find("1")
            args += remaining_args[throwaway_bits:]

        # Lookup python function by opcode
        func = self.instruction_set[func]
        func(args)

    def create_instruction_set(self) -> None:
        # Limit Size: 63 (6-bit opcode - 1 reserved for multiline)
        self.instruction_set = {
            0: self.move_reg_const,  # 000000
            1: self.move_reg_mem,  # 000001
            2: self.move_mem_const,  # 000010
            3: self.move_mem_mem,  # 000011
            4: self.move_mem_reg,  # 000100
            5: self.add_reg_const,  # 000101
            6: self.add_reg_mem,  # 000110
            7: self.add_mem_reg,  # 000111
        }

    def _to_register(self, addr: str) -> str:
        regs = list(self.registers.keys())
        return regs[int(addr, 2)]

    # * Machine Instruction function definitions follow

    def move_reg_const(self, args: str) -> None:
        """Move a constant value into a register."""
        nargs = _split_args(args, REGISTER_BITS)
        reg = self._to_register(nargs[0])
        self.store(reg, int(nargs[1], 2))

    def move_reg_mem(self, args: str) -> None:
        """Move a memory value into a register."""
        nargs = _split_args(args, REGISTER_BITS, MEM_ADDR_BITS)
        reg = self._to_register(nargs[0])
        value = self.load_from_memory(int(nargs[1], 2))
        self.store(reg, value)

    def move_mem_const(self, args: str) -> None:
        """Move a constant value into a memory address."""
        nargs = _split_args(args, MEM_ADDR_BITS)
        self.store_in_memory(int(nargs[0], 2), nargs[1])

    def move_mem_mem(self, args: str) -> None:
        """Move a memory value into a memory address."""
        nargs = _split_args(args, MEM_ADDR_BITS, MEM_ADDR_BITS)
        value = self.load_from_memory(int(nargs[1], 2))
        self.store_in_memory(int(nargs[0], 2), value)

    def move_mem_reg(self, args: str) -> None:
        """Move a register's contents into a memory address."""
        nargs = _split_args(args, MEM_ADDR_BITS, REGISTER_BITS)
        reg = self._to_register(nargs[1])
        value = self.load(reg)
        self.store_in_memory(int(nargs[0], 2), value)

    # TODO: Test for overflow in add instructions?
    def add_reg_const(self, args: str) -> None:
        """Add a constant value to a register value."""
        nargs = _split_args(args, REGISTER_BITS)
        reg = self._to_register(nargs[0])
        value = self.load(reg, "d") + int(nargs[1], 2)
        self.store(reg, value)

    def add_reg_mem(self, args: str) -> None:
        """Add a memory value to a register value."""
        nargs = _split_args(args, REGISTER_BITS, MEM_ADDR_BITS)
        reg = self._to_register(nargs[0])
        value = self.load_from_memory(int(nargs[1], 2), "d") + self.load(reg, "d")
        self.store(reg, value)

    def add_mem_reg(self, args: str) -> None:
        """Add a register value to a memory value."""
        nargs = _split_args(args, MEM_ADDR_BITS, REGISTER_BITS)
        reg = self._to_register(nargs[1])
        memaddr = int(nargs[0], 2)
        value = self.load_from_memory(memaddr, "d") + self.load(reg, "d")
        self.store_in_memory(memaddr, value)


class Machine:
    cpu: CPU

    memory: Memory

    def __init__(self) -> None:
        self.memory = Memory(blocks=8)
        self.cpu = CPU(self.memory)
        self.print_introduction()

    def dump(self) -> str:
        """Dump the machine state."""

        return self.cpu.dump() + "\n\n" + self.memory.dump()

    def load_from_memory(self, address: int, return_type: str = "b") -> Binary:
        """Load a value from memory."""

        return self.memory.load(address, return_type)

    def load_program(self, program: list[str]) -> None:
        """Load a program into memory."""

        self.cpu.store("PC", 0)  # Restart execution
        for i, line in enumerate(program):
            self.store_in_memory(i, line)

    def store_in_memory(self, address: int, value: Binary) -> None:
        """Store a value in memory."""

        self.memory.store(address, value)

    def print_introduction(self) -> None:
        """Print introductory information."""

        intro = "Toy Machine\n"
        intro += (
            f"This is a toy virtual machine, simulating a {WORD_SIZE} bit computer.\n\n"
        )
        intro += "This project is licensed as free and open source software under the MIT License.\n"
        intro += "Sources available at https://www.github.com/MrSquigy/toy-machine\n"

        intro += "\nCommands\n----------\n"
        intro += "<blank>\t\tExecute next instruction\n"
        intro += "dump\t\tDump CPU registers and all memory locations\n"
        intro += "load <filename>\tLoad an assembled program from disk\n"
        intro += "mem <memaddr>\tCheck the contents of a memory location\n"
        intro += "reg <regname>\tCheck the contents of a CPU register\n"
        intro += "e, q\t\tExit\n"

        print(intro)

