from typing import Any, Callable, Dict, Final, List
from math import floor

word_length: Final = 16


def bin2dec(value: List[int]) -> int:
    val: int = 0
    for pos, bit in enumerate(reversed(value)):
        val += bit * 2 ** pos

    return val


def dec2bin(value: int, bits: int) -> List[int]:
    val = []

    while value > 0:
        val.append(value % 2)
        value = floor(value / 2)

    val.extend(0 for _ in range(bits - len(val)))  # Pad the remaining bits
    val.reverse()

    return val


class Memory:

    memory_blocks: Dict[int, List[int]]

    def __init__(self, num: int):
        self.create_memory(num)

    def create_memory(self, num: int):
        self.memory_blocks = {}

        for i in range(num):
            self.memory_blocks[i] = [0 for _ in range(word_length)]

    def dump(self) -> str:
        dump = "\nMemory Dump\n"

        for addr, block in self.memory_blocks.items():
            dump += f"{addr}: {block}\n"

        return dump[:-1]

    def load(
        self,
        address: int,
        length: int = word_length,
        pos: int = 0,
        return_type: str = "b",
    ) -> Any:
        if address not in self.memory_blocks:
            raise Exception(f"Memory address {address} does not exist")

        mem_length = len(self.memory_blocks[address])

        if (length + pos) > mem_length:
            raise Exception(
                f"Memory address {address} is {mem_length} bits long, but {length} bits were requested from position {pos}"
            )

        value = self.memory_blocks[address][pos : pos + length]

        if return_type == "d":
            value = bin2dec(value)

        return value

    def store(
        self, address: int, value: Any, length: int = word_length, pos: int = 0
    ) -> None:
        if address not in self.memory_blocks:
            raise Exception(f"Memory address {address} does not exist")

        mem_length = len(self.memory_blocks[address]) - pos

        if isinstance(value, int):
            value = dec2bin(value, length)  # Get only the bits needed

        if length < (l := len(value)):
            raise Exception(
                f"Expected value to take {length} bits, however, {l} bits are required"
            )

        if mem_length < length:
            raise Exception(
                f"Memory address {address} (from bit {pos}) is {mem_length} bits long, but the value to be stored is {length} bits long"
            )

        for i in range(len(self.memory_blocks[address])):
            if i >= length:
                break

            self.memory_blocks[address][i + pos] = value[i]


class CPU:
    bits: int

    registers: Dict[str, List[int]]

    memory: Memory

    instruction_set: Dict[int, Callable]  # opcode, function

    def __init__(self, memory: Memory):
        self.memory = memory
        self.create_registers()
        self.create_instruction_set()

    def create_registers(self):
        """Create word_length registers."""

        self.registers = {
            "AC": [0 for _ in range(word_length)],  # Accumulator
            "CR": [0 for _ in range(word_length)],  # Counter
            "IR": [0 for _ in range(word_length)],  # Instruction
            "DR": [0 for _ in range(word_length)],  # Data
            "PC": [0 for _ in range(word_length)],  # Program Counter
        }

    def dump(self) -> str:
        """Dump the contents of the registers to a string."""

        regdump = f"Register Dump\n"
        for regid, register in self.registers.items():
            regdump += f"{regid}: {register}\n"

        return regdump

    def load(self, regid: str, return_type: str = "b") -> Any:
        """Load a value from a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        value = self.registers[regid]
        if return_type == "d":
            value = bin2dec(value)

        return value

    def load_from_memory(
        self,
        address: int,
        length: int = word_length,
        pos: int = 0,
        return_type: str = "b",
    ) -> Any:
        """Load a value from memory."""

        return self.memory.load(address, length, pos, return_type)

    def store_in_memory(
        self, address: int, value: Any, length: int = word_length, pos: int = 0
    ) -> None:
        """Store a value in memory."""

        self.memory.store(address, value, length, pos)

    def store(self, regid: str, value: Any) -> None:
        """Store a value in a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        if isinstance(value, int):
            value = dec2bin(value, word_length)

        if (v := len(value)) > (l := len(self.registers[regid])):
            raise Exception(
                f"Register {regid} is {l} bits long, but the value to be stored is {v} bits long"
            )

        self.registers[regid] = value

    def load_next_instruction(self) -> None:
        """Load the next instruction for execution."""

        next_instruction_location = self.load("PC", "d")
        next_instruction = self.load_from_memory(next_instruction_location)
        print("Next instruction:", next_instruction)
        self.store("IR", next_instruction)
        self.store("PC", next_instruction_location + 1)

    def execute_current_instruction(self) -> None:
        instr = self.load("IR")
        instr = [instr[:4], instr[4:]]  # Split instruction into opcode, operators
        # 4-bit opcode means up to 16 operations

        # Lookup python function by opcode
        instr[0] = self.instruction_set[bin2dec(instr[0])]
        instr[0](instr[1])

    def create_instruction_set(self):
        # have to use decimals for opcode
        # because list type is not hashable
        # Limit Size: 16 (4-bit opcode)
        self.instruction_set = {
            0: self.move,
            1: self.add,
        }

    # * Machine Instruction function definitions follow

    def move(self, args: List[int]) -> None:
        address = bin2dec(args[:6])
        value = bin2dec(args[6:])
        self.store_in_memory(address, value)

    def add(self) -> None:
        print("add instruction called")


class Machine:
    cpu: CPU

    memory: Memory

    def __init__(self):
        self.memory = Memory(4)  # 16 Memory Locations of word_length bits
        self.cpu = CPU(self.memory)

    def dump(self) -> str:
        """Dump the machine state."""

        dump = self.cpu.dump()
        dump += self.memory.dump()

        return dump
