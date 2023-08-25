
from typing import Union, Sequence, TypedDict, List, Optional, Dict, Tuple, Any

import os
import sys
from pathlib import Path
import difflib
import re
import json
import argparse


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


def read_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def stat(path: Union[str, os.PathLike]) -> str:
    return str(Path(path).stat())

#endregion

#region STRINGS


def filter_empty_lines(text: str) -> str:
    return '\n'.join(
        s for s in text.split('\n')
        if s.strip()
    )


def find_regions(file_text: str) -> Dict[str, Tuple[int, int]]:
    """
    searches for regions in the text of the (python) file
    Args:
        file_text:

    Returns:
        dict {region name: (region start index, region end index)} where #region lines excluded

    >>> t = read_text('tests/data/regions.py')
    >>> dct = find_regions(t)
    >>> assert sorted(dct.keys()) == sorted(['RG 1', 'RG 2', 'RG 3', 'RG 3.1', 'RG 3.2'])
    >>> def show_part(region_name: str):
    ...     s, e = dct[region_name]
    ...     txt = t[s: e]
    ...     print(filter_empty_lines(txt))
    >>> show_part('RG 1')
    1
    1
    1
    >>> show_part('RG 3')
    # region RG 3.1
    3.1
    #endregion
    #region RG 3.2
    3.2
    #endregion
    """

    start_matches = list(
        re.finditer(r"^#\s?region\s", file_text, re.MULTILINE)
    )
    if not start_matches:
        return {}

    end_matches = list(
        re.finditer(r"^#\s?endregion\s", file_text, re.MULTILINE)
    )
    if not end_matches:
        return {}

    ends = [m.start() for m in end_matches]
    start_to_region: Dict[int, str] = {}
    """map {index of region start -> region name}"""

    for m in start_matches:
        start = file_text.find('\n', m.start()) + 1
        text = file_text[m.start(): start]
        name = text.split('region', 1)[1].strip()
        start_to_region[start] = name

    start_to_end = find_start_end_pairs(
        starts=list(start_to_region.keys()), ends=ends
    )

    return {
        start_to_region[start]: (start, end)
        for start, end in start_to_end.items()
    }


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


def shift_text(text: str, linesep: str = '\n', dept: int = 1) -> str:
    """
    >>> shift_text('t')
    '    t'
    >>> print(shift_text('t;tt', linesep=';'))
        t;    tt
    >>> 'a' + shift_text('b', dept=3)
    'a            b'
    """
    t = TAB * dept
    return t + f'{linesep}{t}'.join(text.split(linesep))

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

#region COMPARING

def print_status(status: str, dept: int = 1):
    """print the message about success or failure"""
    if status:
        print(f'{TAB}FAILURE\n' + shift_text(status, dept=dept))
    else:
        print(f"{TAB}OK")



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
                f"{s}: {stat(s)}\n"
                f"{d}: {stat(d)}"
            )
    else:  # both files are text
        sc = read_text(s)
        dc = read_text(d)
        if sc != dc:
            diff_info = text_diff(
                sc, dc,
                label1=s,
                label2=d
            )

    if diff_info:
        return f"{message}:\n{shift_text(diff_info)}"
    return ''


def compare_files_regions(sourse: str, dest: str, regions: Sequence[PythoRegion]) -> Union[str, bool]:

    s = read_text(sourse)
    d = read_text(dest)

    sreg = find_regions(s)
    dreg = find_regions(d)

    res = True

    for r in regions:
        ss = r['in_source']
        dd = r['in_dest']

        print(f"{TAB} Comparing regions '{ss}' <---> '{dd}' ", end='')

        for reg_name, regions_dict, file in (
            (ss, sreg, sourse),
            (dd, dreg, dest),
        ):
            if reg_name not in regions_dict:
                res = False
                print_status(
                    f"there is no region '{reg_name}' in {file}, available regions: {sorted(regions_dict.keys())}",
                    dept=2
                )
                break
        else:
            ss_start, ss_end = sreg[ss]
            dd_start, dd_end = dreg[dd]
            diff_info = text_diff(
                s[ss_start: ss_end],
                d[dd_start: dd_end],
                label1=f"region '{ss}' in {sourse} (chars [{ss_start}:{ss_end}])",
                label2=f"region '{dd}' in {dest} (chars [{dd_start}:{dd_end}])"
            )

            if diff_info:
                res = False
                print_status(diff_info, dept=2)
            else:
                print_status('', dept=2)

    return res


def file_comp(request: CompRequest) -> Union[str, bool]:
    s = request['source']
    if not os.path.exists(s):
        return f"source file {s} does not exist"
    d = request['dest']
    if not os.path.exists(d):
        return f"destination file {d} does not exist"

    print(
        f"Comparing {s} <---> {d}", end=''
    )

    regions = request.get('regions')
    if not regions:  # compare files fully
        r = file_comp_total(s, d)
        print_status(r)
        return r
    else:
        print()
        return compare_files_regions(s, d, regions)


def main(
    config: str,
    raise_on_errors: bool = True
):

    print(f"Reading the config from {config}...\n\n")
    config: List[CompRequest] = read_json(config)

    res = True
    for item in config:
        r = file_comp(item)
        res = res and r

    if not res:
        message = "SOME DIFFS FOUND"
        if raise_on_errors:
            raise Exception(message)
        else:
            print()
            print(message)


#endregion

#region CLI

parser = argparse.ArgumentParser(
    prog='fec.py',
    description=(
        'Script which which checks if the files are equal totally or partially depending on target criteria'
    ),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('CONFIG_FILE', type=str, help='json file with the comparing configuration')
parser.add_argument(
    '-r', '--raise-on-errors', action='store_true',
    help='whether to raise an Exception when some differences are found',
    dest='raise_on_errors'
)

#endregion


if __name__ == '__main__':

    parsed = parser.parse_args(sys.argv[1:])
    main(
        config=parsed.CONFIG_FILE,
        raise_on_errors=parsed.raise_on_errors
    )





