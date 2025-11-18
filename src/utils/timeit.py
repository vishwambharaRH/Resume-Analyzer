import time
import functools
import logging

logger = logging.getLogger(__name__)


def timeit(label="Execution"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # ms
            logger.info(f"{label} took {duration:.2f} ms")
            return result

        return wrapper

    return decorator
