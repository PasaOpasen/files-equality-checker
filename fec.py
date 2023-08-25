
from typing import Union

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


#endregion


#endregion




