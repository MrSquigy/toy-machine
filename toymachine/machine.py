from typing import Any, Callable, Dict, Final, List
from math import floor

word_size: Final = 32


class Memory:

    memory_blocks: Dict[int, str]

    def __init__(self, num: int):
        self.create_memory(num)

    def create_memory(self, num: int):
        self.memory_blocks = {}

        for i in range(num):
            self.memory_blocks[i] = "0b0"

    def dump(self) -> str:
        dump = "Memory Dump\n"

        for addr, block in self.memory_blocks.items():
            dump += f"{addr}: {block}\n"

        return dump[:-1]

    def load(self, address: int, return_type: str = "b",) -> Any:
        if address not in self.memory_blocks:
            raise Exception(f"Memory address {address} does not exist")

        value = self.memory_blocks[address]

        if return_type == "d":
            value = int(value, 2)

        return value

    def store(self, address: int, value: Any) -> None:
        if address not in self.memory_blocks:
            raise Exception(f"Memory address {address} does not exist")

        if isinstance(value, int):
            value = bin(value)

        if (l := len(value) - 2) > word_size:
            raise Exception(
                f"Memory address {address} is {word_size} bits long, but the value to be stored is {l} bits long"
            )

        self.memory_blocks[address] = value


class CPU:
    registers: Dict[str, str]

    memory: Memory

    instruction_set: Dict[int, Callable]  # opcode, function

    def __init__(self, memory: Memory):
        self.memory = memory
        self.create_registers()
        self.create_instruction_set()

    def create_registers(self):
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

    def load(self, regid: str, return_type: str = "b") -> Any:
        """Load a value from a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        value = self.registers[regid]
        if return_type == "d":
            value = int(value, 2)

        return value

    def load_from_memory(self, address: int, return_type: str = "b",) -> Any:
        """Load a value from memory."""

        return self.memory.load(address, return_type)

    def store_in_memory(self, address: int, value: Any) -> None:
        """Store a value in memory."""

        self.memory.store(address, value)

    def store(self, regid: str, value: Any) -> None:
        """Store a value in a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        if isinstance(value, int):
            value = bin(value)

        if (l := len(value) - 2) > word_size:
            raise Exception(
                f"Register {regid} is {word_size} bits long, but the value to be stored is {l} bits long"
            )

        self.registers[regid] = value

    def load_next_instruction(self) -> None:
        """Load the next instruction for execution."""

        next_instruction_location = self.load("PC", "d")
        next_instruction = self.load_from_memory(next_instruction_location)
        self.store("IR", next_instruction)
        self.store("PC", next_instruction_location + 1)

    def execute_current_instruction(self) -> None:
        instr: str = self.load("IR")
        if len(instr) != word_size + 2:  # 0b + instruction
            raise Exception(f"Instruction {instr[2:]} is not in the correct format")

        # Split into opcode (6-bit) & operators
        func_header = [int(instr[:8], 2), instr[8:]]

        # Lookup python function by opcode
        func_header[0] = self.instruction_set[func_header[0]]
        func_header[0](func_header[1])

    def create_instruction_set(self):
        # Limit Size: 64 (6-bit opcode)
        self.instruction_set = {
            0: self.move_reg_const,
            1: self.move_reg_mem,
            2: self.move_mem_const,
            3: self.move_mem_mem,
            4: self.move_mem_reg,
            5: self.add,
        }

    def _to_register(self, addr: str) -> str:
        regs = list(self.registers.keys())
        return regs[int(addr, 2)]

    # * Machine Instruction function definitions follow

    def move_reg_const(self, args: str) -> None:
        """Move a constant value into a register."""
        # 3 bits for register, 23 bits for const
        nargs = ["0b" + args[:3], "0b" + args[3:]]
        reg = self._to_register(nargs[0])
        self.store(reg, int(nargs[1], 2))

    def move_reg_mem(self, args: str) -> None:
        """Move a memory value into a register."""
        # 3 bits for register, 23 bits for memaddr
        nargs = ["0b" + args[:3], "0b" + args[3:]]
        reg = self._to_register(nargs[0])
        value = self.load_from_memory(int(nargs[1], 2))
        self.store(reg, value)

    def move_mem_const(self, args: str) -> None:
        """Move a constant value into a memory address."""
        # 10 bits for memaddr, 16 bits for const
        nargs = ["0b" + args[:10], "0b" + args[10:]]
        self.store_in_memory(int(nargs[0], 2), nargs[1])

    def move_mem_mem(self, args: str) -> None:
        """Move a memory value into a memory address."""
        # 13 bits for each memaddr
        nargs = ["0b" + args[:13], "0b" + args[13:]]
        value = self.load_from_memory(int(nargs[1], 2))
        self.store_in_memory(int(nargs[0], 2), value)

    def move_mem_reg(self, args: str) -> None:
        """Move a register's contents into a memory address."""
        # 23 bits for memaddr, 3 bits for register
        nargs = ["0b" + args[:23], "0b" + args[23:]]
        reg = self._to_register(nargs[1])
        value = self.load(reg)
        self.store_in_memory(int(nargs[0], 2), value)

    def add(self) -> None:
        print("add instruction called")


class Machine:
    cpu: CPU

    memory: Memory

    def __init__(self):
        self.memory = Memory(4)  # 4 Memory Locations of word_size bits
        self.cpu = CPU(self.memory)

    def dump(self) -> str:
        """Dump the machine state."""

        return self.cpu.dump() + "\n\n" + self.memory.dump()

    def load_from_memory(self, address: int, return_type: str = "b",) -> Any:
        """Load a value from memory."""

        return self.memory.load(address, return_type)

    def store_in_memory(self, address: int, value: Any) -> None:
        """Store a value in memory."""

        self.memory.store(address, value)
