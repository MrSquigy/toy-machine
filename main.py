from src.toymachine.machine import Machine


def main():
    machine = Machine()
    machine.cpu.store("AX", 5)
    print(machine.dump())


if __name__ == "__main__":
    main()