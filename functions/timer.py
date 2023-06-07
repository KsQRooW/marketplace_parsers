from time import time


def timer(func):
    def wrapper(*args, **kwargs):
        time_start = time()
        res = func(*args, **kwargs)
        print(f"time_end_{func.__name__}: {time() - time_start}")
        return res

    return wrapper
