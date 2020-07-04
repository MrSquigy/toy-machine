from src.toymachine.machine import Machine


def main():
    machine = Machine()
    machine.cpu.store("AX", 56)
    machine.cpu.store_in_memory(0, 56)

    print("AX Register:", machine.cpu.load("AX", "d"))
    print("Memlocation 0:", machine.cpu.load_from_memory(0, return_type="d"))

    machine.cpu.load_next_instruction()
    print(f"\n{machine.dump()}")


if __name__ == "__main__":
    main()
