from typing import Any, Dict, List
from math import floor


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

    def __init__(self, num: int, bytes: int):
        self.create_memory(num, bytes)

    def create_memory(self, num: int, bytes: int):
        self.memory_blocks = {}

        for i in range(num):
            self.memory_blocks[i] = [0 for _ in range(8 * bytes)]

    def dump(self) -> str:
        dump = "\nMemory Dump\n"

        for addr, block in self.memory_blocks.items():
            dump += f"{addr}: {block}\n"

        return dump

    def load(
        self, address: int, length: int = 8, pos: int = 0, return_type: str = "b"
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

    def store(self, address: int, value: Any, length: int = 8, pos: int = 0) -> None:
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

    def __init__(self, memory: Memory, bits: int = 8):
        self.memory = memory
        self.bits = bits
        self.create_registers(bits)

    def create_registers(self, bits: int):
        """Create n-bit registers."""

        self.registers = {
            "AX": [0 for _ in range(bits)],  # Accumulator
            "CX": [0 for _ in range(bits)],  # Counter
            "IX": [0 for _ in range(bits)],  # Instruction
            "DX": [0 for _ in range(bits)],  # Data
            "PC": [0 for _ in range(bits)],  # Program Counter
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
        self, address: int, length: int = 8, pos: int = 0, return_type: str = "b"
    ) -> Any:
        """Load a value from memory."""

        return self.memory.load(address, length, pos, return_type)

    def store_in_memory(
        self, address: int, value: Any, length: int = 8, pos: int = 0
    ) -> None:
        """Store a value in memory."""

        self.memory.store(address, value, length, pos)

    def store(self, regid: str, value: Any) -> None:
        """Store a value in a register."""

        if regid not in self.registers:
            raise Exception(f"Register {regid} does not exist")

        if isinstance(value, int):
            value = dec2bin(value, self.bits)

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
        self.store("IX", next_instruction)
        self.store("PC", next_instruction_location + 1)


class Machine:
    cpu: CPU

    memory: Memory

    def __init__(self):
        self.memory = Memory(16, 2)  # 16 Memory Locations of 2 bytes each = 32 bytes
        self.cpu = CPU(self.memory)

    def dump(self) -> str:
        """Dump the machine state."""

        dump = self.cpu.dump()
        dump += self.memory.dump()

        return dump
