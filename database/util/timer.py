from time import perf_counter
from contextlib import ContextDecorator


# https://stackoverflow.com/a/70778563
class timer(ContextDecorator):
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        elapsed = perf_counter() - self.time
        print(f"{self.msg} took {elapsed:.3f} seconds")
