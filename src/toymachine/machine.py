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

    for i in range(bits - len(val)):  # Pad the remaining bits
        val.insert(0, 0)

    return val


class CPU:
    bits: int

    registers: Dict[str, List[int]]

    def __init__(self, bits: int = 8):
        self.bits = bits
        self.create_registers(bits)

    def create_registers(self, bits: int):
        """Create n-bit registers."""

        self.registers = {
            "AX": [0 for _ in range(bits)],  # Accumulator
            "CX": [0 for _ in range(bits)],  # Counter
            "DX": [0 for _ in range(bits)],  # Data
            "PC": [0 for _ in range(bits)],  # Program Counter
        }

    def dump(self) -> str:
        """Dump the contents of the registers to a string."""

        regdump = f"Register Dump\n"
        for regid, register in self.registers.items():
            regdump += f"{regid}: {register}\n"

        return regdump

    def load(self, regid: int, return_type: str = "b") -> List[int]:
        """Load a value from a register."""

        if regid not in self.registers:
            raise Exception(f"register {regid} does not exist")

        value = self.registers[regid]
        if return_type == "d":
            value = bin2dec(value)

        return value

    def store(self, regid: int, value: Any) -> None:
        """Store a value in a register."""

        if regid not in self.registers:
            raise Exception(f"register {regid} does not exist")

        if isinstance(value, int):
            value = dec2bin(value, self.bits)

        self.registers[regid] = value


class Machine:
    cpu: CPU

    def __init__(self):
        self.cpu = CPU()

    def dump(self) -> str:
        """Dump the machine state."""

        return self.cpu.dump()
