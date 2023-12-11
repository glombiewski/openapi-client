'''
Utility functions for post-processing
'''

from itertools import tee
from pathlib import Path
from typing import Callable, Generator, List


def pairwise(iterable):
    '''from `itertools` 3.10'''
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def modify_file(input_path: Path,
                modify_fn: Callable[[List[str]], Generator[str, None, None]]) -> None:
    '''Modify a file by passing its contents to a function and writing the result back to the
       file.'''

    with open(input_path, 'r', encoding='utf-8') as f:
        file_contents = f.readlines()

    with open(input_path, 'w', encoding='utf-8') as f:
        for line in modify_fn(file_contents):
            f.write(line)
