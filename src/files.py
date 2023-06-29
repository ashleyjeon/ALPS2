from pathlib import Path
from typing import List, Union
import pickle
import csv
import os

import matplotlib.pyplot as plt
import numpy as np

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


def load_data(path: Union[str, Path]):
    """Read the data located in @path"""
    p = Path(path)
    ftype = p.suffix

    data = None

    if ftype not in FORMAT_DATA:
        raise ValueError(f'Invalid file type passed ({ftype}): {p}')

    if ftype == '.p':
        data = load_pickle_arr(p)
    elif ftype == '.csv':
        data = load_csv_arr(p)

    return data


def load_pickle_arr(path: Path):
    if path.suffix != '.p':
        raise ValueError(f'Path file is not a pickle file: {path.name}')

    with open(path, 'rb') as f:
        return pickle.load(f)


def load_csv_arr(path: Path) -> np.ndarray:
    """Read a CSV file from @path and """
    arr = np.genfromtxt(path, delimiter=',')
    return arr


def dump_array(filename, data, bytes=False):
    """Upload data to the user save (DIR_SESS_DATA) directory"""
    fname = Path(filename)
    ftype = fname.suffix

    if ftype not in FORMAT_DATA:
        raise ValueError(f'Invalid data type ({ftype}): {filename}')

    if ftype == '.p':
        dump_pickle_arr(filename, data, bytes)
    elif ftype == '.csv':
        dump_csv_arr(filename, data, bytes)


def dump_csv_arr(filename, data, bytes=False):
    """Save @data as a CSV file; @data must be a 1-d or 2-d numerical array"""
    fp = Path(filename)
    if len(fp.suffix) == 0:
        filename = filename + '.csv'

    try:
        if bytes:
            # bytes -> list of strings
            data = data.decode('utf-8').splitlines()

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            for point in data:
                d = point.split(',')
                writer.writerow(d)
    except ValueError as e:
        raise ValueError(f'Passed data: {data}') from e


def dump_pickle_arr(filename, data, bytes=False):
    """
    Pickle data to DIR_SESS_DATA; specify whether data source is @byte
    """
    path = DIR_SESS_DATA / filename
    try:
        mode = 'wb' if bytes else 'w'
        with open(path, mode) as f:
            if bytes:
                d = pickle.loads(data)
                pickle.dump(d, f)
            else:
                # TODO 6/29: might not work as inteded; haven't tested for
                #   non-byte objects
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