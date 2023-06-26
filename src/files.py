from pathlib import Path
from typing import List, Union
import pickle
import csv
import os


VALID_DATATYPES = ['.p', '.csv', '.txt']

DIR_PROJECT = Path(__file__).parent.parent
DIR_BIN = DIR_PROJECT / 'bin'
DIR_SAMPLE_DATA = DIR_PROJECT / 'data'

try:
    # Ghub server directories generated each time a tool is run
    SESSION = os.environ['SESSION']
    DIR_SESS_DATA = os.environ['SESSIONDIR']
    DIR_SESS_RESULTS = os.environ['RESULTSDIR']
except KeyError:
    # Local path alternatives
    SESSION = None
    DIR_SESS_DATA = DIR_SAMPLE_DATA / 'temp'
    DIR_SESS_RESULTS = DIR_SAMPLE_DATA / 'out'


def load_data(paths: List[Union[str, Path]]):
    """Read the data located in @paths if it's CSV, pickle, or text"""
    paths = [Path(p) for p in paths]

    data = []
    for p in paths:
        ft = p.suffix

        if ft not in VALID_DATATYPES:
            print(f'{p} is not a valid filetype')
            continue

        if ft == '.p':
            d = load_pickle(p)
            data.append((p.relative_to(DIR_SESS_DATA), d))
        elif ft == '.csv':
            pass
        elif ft == '.txt':
            pass

    return data


def load_pickle(path: Path):
    if path.suffix != '.p':
        raise ValueError(f'Path file is not a pickle file: {path.name}')

    with open(path, 'rb') as f:
        return pickle.load(f)


def dump_pickle(path: Path, data, bytes=False):
    """
    Pickle data to @path; specify whether data source is @bytes
    """
    try:
        mode = 'wb' if bytes else 'w'
        with open(path, mode) as f:
            pickle.dump(data, f)

    except ValueError:
        raise


# if __name__ == '__main__':
#     dd = widg.Dropdown(
#         options=['1', '2'],
#         description='Hello:'
#     )
#     dd