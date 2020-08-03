from timeit import timeit

import toymachine


def main():
    machine = toymachine.Machine()
    machine.cpu.store("AC", 42)
    machine.cpu.store_in_memory(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0])

    print("AC Register:", machine.cpu.load("AC", "d"))
    print("Memlocation 0:", machine.cpu.load_from_memory(0, return_type="d"))

    # Temporary execution environment
    while True:
        cmd = input("$ ")
        if cmd == "":
            machine.cpu.load_next_instruction()
            machine.cpu.execute_current_instruction()

        elif cmd == "dump":
            print(f"{machine.dump()}")

        elif cmd == "q" or cmd == "e":
            break


if __name__ == "__main__":
    main()
