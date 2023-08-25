
from typing import Union, Sequence, Dict

import os
from pathlib import Path


#region UTILS

#region FILES

def is_binary(path: str) -> bool:
    """
    >>> is_binary('fec.py')
    False
    """
    from binaryornot.check import is_binary
    return is_binary(path)


def write_text(result_path: Union[str, os.PathLike], text: str, encoding: str = 'utf-8'):
    result_tmp = str(result_path) + '.tmp'
    Path(result_tmp).write_text(text, encoding=encoding, errors='ignore')
    if os.path.exists(result_path):
        os.remove(result_path)
    Path(result_tmp).rename(result_path)


def read_text(result_path: Union[str, os.PathLike], encoding: str = 'utf-8'):
    return Path(result_path).read_text(encoding=encoding, errors='ignore')

#endregion


#region FUNCS

def find_start_end_pairs(starts: Sequence[int], ends: Sequence[int]) -> Dict[int, int]:
    """
    for sequences of indexes of nested start and end point searches for their connections
    Args:
        starts:
        ends:

    Returns:
        dict {start index -> its end index}

    >>> _ = find_start_end_pairs
    >>> _([1], [2])
    {1: 2}
    >>> _([1, 2], [2, 3])
    {2: 2, 1: 3}
    >>> _([1, 2, 3], [2, 4, 6])
    {2: 2, 3: 4, 1: 6}
    >>> _([1, 2, 10], [2, 1, 11])
    {1: 1, 2: 2, 10: 11}
    """

    assert len(starts) == len(ends), (len(starts), len(ends))
    assert starts[0] <= ends[0], (starts[0], ends[0])
    assert starts[-1] <= ends[-1], (starts[-1], ends[-1])

    res = {}

    watched_starts = []
    for i, f in sorted(
        [(s, False) for s in starts] + [(e, True) for e in ends]
    ):
        if f:  # connect last start with end and save
            last_start = watched_starts.pop()
            res[last_start] = i

        else:  # append to starts
            watched_starts.append(i)

    return res

#endregion


#endregion




