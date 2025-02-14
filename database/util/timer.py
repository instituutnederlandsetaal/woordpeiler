from time import perf_counter
from contextlib import ContextDecorator


# https://stackoverflow.com/a/70778563
class timer(ContextDecorator):
    msg: str

    def __init__(self, msg: str):
        self.msg = msg

    def __enter__(self):
        print(f"{self.msg}", flush=True)
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        elapsed = perf_counter() - self.time
        print(f"    Took {elapsed:.3f} seconds", flush=True)
