# files-equality-checker

The purpose of this script is to perform many checks on the files that must be equal totally or partially depending on a target (configuration) criteria.

Now it supports next checks:
* equality of binary files (requires installed `requirements.txt`)
* equality of text files with usual diff output
* equality of **regions** in text files (usually `*.py` files)

## CLI

```bash
python fec.py --help
usage: fec.py [-h] [-r] CONFIG_FILE

Script which which checks if the files are equal totally or partially depending on target criteria

positional arguments:
  CONFIG_FILE           json file with the comparing configuration

optional arguments:
  -h, --help            show this help message and exit
  -r, --raise-on-errors
                        whether to raise an Exception when some differences are found (default: False)
```


## Example

[Text file](/tests/data/regions.py):
```python


#region RG 1
1
1
1
#endregion


# region RG 2
2
2
2
# endregion

#region RG 3

# region RG 3.1
3.1
#endregion

#region RG 3.2
3.2
#endregion

# endregion


```

[Config file](/tests/data/config.json):
```json
[
    {
        "source": "tests/data/regions.py",
        "dest": "tests/data/regions.py"
    },
    {
        "source": "tests/data/regions.py",
        "dest": "tests/data/regions.py",
        "regions": [
            {
                "in_source": "RG 1",
                "in_dest": "RG 1"
            },
            {
                "in_source": "RG 1",
                "in_dest": "RG 3"
            }
        ]
    }
]
```

**Command**:
```bash
python fec.py tests/data/config.json
```

**Output**:
```s
Reading the config from tests/data/config.json...


Comparing tests/data/regions.py <---> tests/data/regions.py    OK
Comparing tests/data/regions.py <---> tests/data/regions.py
     Comparing regions 'RG 1' <---> 'RG 1'     OK
     Comparing regions 'RG 1' <---> 'RG 3'     FAILURE
        --- region 'RG 1' in tests/data/regions.py (chars [15:21])

        +++ region 'RG 3' in tests/data/regions.py (chars [80:144])

        @@ -1,3 +1,9 @@

        -1
        -1
        -1
        +
        +# region RG 3.1
        +3.1
        +#endregion
        +
        +#region RG 3.2
        +3.2
        +#endregion
        +

SOME DIFFS FOUND
```
