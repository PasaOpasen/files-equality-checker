
from typing import Union, Sequence, Dict, TypedDict, List, Optional

import os
from pathlib import Path
import difflib


TAB = '    '


#region TYPES

class PythoRegion(TypedDict):
    """the region info for python file"""
    in_source: str
    in_dest: str


class CompRequest(TypedDict):
    """the request to compare 2 files"""
    source: str
    dest: str
    regions: Optional[List[PythoRegion]]

#endregion

#region UTILS

#region FILES


def is_binary(path: str) -> bool:
    """
    >>> is_binary('fec.py')
    False
    """
    from binaryornot.check import is_binary
    return is_binary(path)


def read_text(result_path: Union[str, os.PathLike], encoding: str = 'utf-8'):
    return Path(result_path).read_text(encoding=encoding, errors='ignore')


def read_bytes(path: Union[str, os.PathLike]) -> bytes:
    return Path(path).read_bytes()


def stat(path: Union[str, os.PathLike]) -> str:
    return str(Path(path).stat())

#endregion


#region FUNCS

def filter_empty_lines(text: str) -> str:
    return '\n'.join(
        s for s in text.split('\n')
        if s.strip()
    )


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


def text_diff(text1: str, text2: str, label1: str = 'text1', label2: str = 'text2') -> str:
    """
    compares 2 texts and returns diff result string
    Args:
        text1:
        text2:
        label1: name of the text1 source
        label2:

    Returns:

    >>> s = text_diff('a', 'a')
    >>> assert not s, f"must be no diffs"
    >>> print(text_diff('a134', 'a13'))
    --- text1
    <BLANKLINE>
    +++ text2
    <BLANKLINE>
    @@ -1 +1 @@
    <BLANKLINE>
    -a134
    +a13

    """
    diff = difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        fromfile=label1,
        tofile=label2,
    )
    return '\n'.join(diff)

#endregion


#endregion

def file_comp_total(source: str, dest: str) -> str:
    """
    >>> _ = file_comp_total
    >>> assert _('fec.py', 'fec.py') == ''
    >>> diff = filter_empty_lines(_('tests/data/p1.txt', 'tests/data/p2.txt'))
    >>> print(diff)
    file tests/data/p1.txt content is not equal to file tests/data/p2.txt content:
        --- tests/data/p1.txt
        +++ tests/data/p2.txt
        @@ -3,4 +3,4 @@
         text
        -file
        +file with different text

    """

    s = source
    d = dest

    sb = is_binary(s)
    db = is_binary(d)
    if sb != db:
        return (
            f"{s} file {'is' if sb else 'is not'} binary but "
            f"{d} file {'is' if db else 'is not'} binary"
        )

    message = f'file {s} content is not equal to file {d} content'
    diff_info = ''

    if sb:  # both files are binary
        sc = read_bytes(s)
        dc = read_bytes(d)
        if sc != dc:
            diff_info = (
                f"{TAB}{s}: {stat(s)}\n"
                f"{TAB}{d}: {stat(d)}"
            )
    else:  # both files are text
        sc = read_text(s)
        dc = read_text(d)
        if sc != dc:
            diff_info = text_diff(
                sc, dc,
                label1=s,
                label2=d
            ).replace('\n', f'\n{TAB}')

    if diff_info:
        return f"{message}:\n{TAB}{diff_info}"
    return ''


def file_comp(request: CompRequest) -> str:
    s = request['source']
    if not os.path.exists(s):
        return f"source file {s} does not exist"
    d = request['dest']
    if not os.path.exists(d):
        return f"destination file {d} does not exist"

    regions = request['regions']
    if not regions:  # compare files fully
        return file_comp_total(s, d)





    return ''


