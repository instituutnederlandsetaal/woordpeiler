import sys


def ask_confirmation():
    while True:
        response = input("Are you sure? (y/n): ").strip().lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print("Please enter 'y' or 'n'.")


def eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)
