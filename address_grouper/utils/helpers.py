import time
import datetime


def get_runtime(func):
    def wrapper(*args, **kwargs):
        started = time.time()
        dataset = func(*args, **kwargs)
        elapsed = time.time() - started
        print(f"\n{func.__name__} -> Time elapsed: {str(datetime.timedelta(seconds=int(elapsed)))}")
        return dataset

    return wrapper
