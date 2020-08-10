import toymachine


def main():
    machine = toymachine.Machine()
    print(machine.dump(), end="\n\n")

    # Instruction to store 42 in AC
    machine.store_in_memory(0, "0b00000000000000000000000000101010")

    # Temporary execution environment
    while True:
        cmd = input("$ ")
        if cmd == "":
            machine.cpu.load_next_instruction()
            machine.cpu.execute_current_instruction()

        elif "mem" in cmd:
            print(machine.load_from_memory(int(cmd.split()[1]), "d"))

        elif "reg" in cmd:
            print(machine.cpu.load(cmd.split()[1].upper(), "d"))

        elif cmd == "dump":
            print(machine.dump())

        elif cmd == "q" or cmd == "e":
            break


if __name__ == "__main__":
    main()
