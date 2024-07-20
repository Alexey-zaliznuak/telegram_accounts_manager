from typing import Iterable, TypeVar


T = TypeVar("T")


def args_to_list(*args: list[T] | T) -> list[T]:
    """
    ```python
    await args_to_list(1)  # [1]
    await args_to_list(1, 2)  # [1, 2]
    await args_to_list(1, [2, 3])  # [1, 2, 3]
    ```
    """
    result = []

    for arg in args:
        if isinstance(arg, Iterable):
            result.extend(arg)
            continue

        result.append(arg)

    return result
