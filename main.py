import toymachine
from typing import List
import os


def load_program(file_name: str) -> List[str]:
    program: List[str]

    if not (os.path.exists(file_name) and os.path.isfile(file_name)):
        raise Exception(
            f"Program `{file_name}` not found. Is it in the correct directory?"
        )

    with open(file_name) as prog_file:
        program = prog_file.read().split("\n")[:-1]  # drop empty line

    return program


def main():
    machine = toymachine.Machine()
    print(machine.dump(), end="\n\n")

    # Temporary execution environment
    while True:
        cmd = input("$ ")
        if cmd == "":
            machine.cpu.load_next_instruction()
            machine.cpu.execute_current_instruction()

        elif "mem" in cmd:
            try:
                print(machine.load_from_memory(int(cmd.split()[1]), "d"))
            except Exception as e:
                print(e)

        elif "reg" in cmd:
            try:
                print(machine.cpu.load(cmd.split()[1].upper(), "d"))
            except Exception as e:
                print(e)

        elif "load" in cmd:
            try:
                program = load_program(cmd.split()[1])
                machine.load_program(program)
                print(f"Successfully loaded {cmd.split()[1]}")
            except Exception as e:
                print(e)

        elif cmd == "dump":
            print(machine.dump())

        elif cmd == "q" or cmd == "e":
            break


if __name__ == "__main__":
    main()
