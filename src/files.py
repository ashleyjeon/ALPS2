from pathlib import Path
from typing import List, Union
import pickle
import csv
import os

import matplotlib.pyplot as plt

FORMAT_DATA = ('.p', '.csv', '.txt')
FORMAT_IMG_OUT = ('png', 'jpg', 'pdf')

DIR_PROJECT = Path(__file__).parent.parent
DIR_SRC = DIR_PROJECT / 'src'
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


def get_path_relative_to(a: Path, b: Path):
    """
    Get a path to @a relative to @b, including '..' where moving up the tree is
      necessary; required for opening javascript windows
      REF: https://stackoverflow.com/a/43613742/13557629
    """
    return Path(os.path.relpath(a, b))


def load_data(paths: List[Union[str, Path]]):
    """Read the data located in @paths if it's CSV, pickle, or text"""
    paths = [Path(p) for p in paths]

    data = []
    for p in paths:
        ft = p.suffix

        if ft not in FORMAT_DATA:
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


def upload_plt_plot(fig: plt.Figure, filename: str):
    """
    Save figure plot and return the path to the save
    NOTE: must be called BEFORE call to plt.show() otherwise saved file will
      be blank
    """
    path = DIR_SESS_RESULTS / filename

    fig.savefig(path, bbox_inches='tight')
    return path


# if __name__ == '__main__':
#     dd = widg.Dropdown(
#         options=['1', '2'],
#         description='Hello:'
#     )
#     dd