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


