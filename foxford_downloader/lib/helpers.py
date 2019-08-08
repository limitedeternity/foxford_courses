from functools import reduce
from traceback import format_exc
from typing import Any, Callable, Dict, Tuple, Union


class Logger():
    @staticmethod
    def error(message: str) -> None:
        print(f"[\033[91mE\033[0m]: \033[1m{message}\033[0m")

    @staticmethod
    def warn(message: str) -> None:
        print(f"[\033[93mW\033[0m]: \033[1m{message}\033[0m")

    @staticmethod
    def log(message: str) -> None:
        print(f"[\033[94mL\033[0m]: \033[1m{message}\033[0m")


def pipe(*args: Tuple[Callable]) -> Callable:
    return lambda val: reduce(lambda prev, fn: fn(prev), args, val)


def error_handler(fn: Callable) -> Callable:
    def wrapper(*args: Tuple, **kwargs: Dict):
        try:
            result: Any = fn(*args, **kwargs)
            if isinstance(result, dict) and "fatal_error" in result:
                Logger.error(result["fatal_error"])
                exit(1)

            return result
        except Exception:
            Logger.error(format_exc())
            exit(1)

    return wrapper
