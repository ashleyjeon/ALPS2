from pathlib import Path
from typing import List, Union
import pickle
import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


FORMAT_DATA = ('.p', '.csv', '.txt')
FORMAT_IMG_OUT = ('png', 'jpg', 'pdf')

DIR_PROJECT = Path(__file__).parent.parent
DIR_SRC = DIR_PROJECT / 'src'
DIR_BIN = DIR_PROJECT / 'bin'
DIR_SAMPLE_DATA = DIR_PROJECT / 'data'


def setup_local(data_dir: Path):
    """Create the temp and out directories for locally stored data"""
    temp = data_dir / 'temp'
    out = data_dir / 'out'
    temp.mkdir(exist_ok=True)
    out.mkdir(exist_ok=True)

    return temp, out


def setup_remote(data_dir: Path):
    """Create temp directory in ghub's current session"""
    temp = data_dir / 'temp'
    temp.mkdir(exist_ok=True)

    return temp


try:
    # Ghub server directories generated each time a tool is run
    SESSION = os.environ['SESSION']
    DIR_SESS_DATA = Path(os.environ['SESSIONDIR'])
    DIR_SESS_TDATA = setup_remote(DIR_SESS_DATA)
    DIR_SESS_RESULTS = Path(os.environ['RESULTSDIR'])
except KeyError:
    # Local path alternatives
    SESSION = None
    DIR_SESS_DATA = DIR_SAMPLE_DATA
    DIR_SESS_TDATA, DIR_SESS_RESULTS = setup_local(DIR_SESS_DATA)


def clear_temp():
    """Clear the temp data directory -- as per official Ghub recommendations"""
    for file in DIR_SESS_TDATA.iterdir():
        file.unlink()


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
        data = load_csv(p)

    return data


def load_pickle_arr(path: Path):
    if path.suffix != '.p':
        raise ValueError(f'Path file is not pickle format: {path.name}')

    with open(path, 'rb') as f:
        return pickle.load(f)


def load_csv(path: Path) -> pd.DataFrame:
    """Read a CSV file from @path"""
    data = pd.read_csv(path, sep=',', header='infer')
    return data


def dump_array(filename, data, bytes=False):
    """Upload data to the user save (DIR_SESS_TDATA) directory"""
    fname = Path(filename)
    ftype = fname.suffix

    if ftype not in FORMAT_DATA:
        raise ValueError(f'Invalid data type ({ftype}): {filename}')

    if ftype == '.p':
        dump_pickle_arr(filename, data, bytes)
    elif ftype == '.csv':
        dump_csv_arr(filename, data, bytes)


def dump_csv_arr(filename, data, bytes=False):
    """Save @data as a CSV file"""
    if len(Path(filename).suffix) == 0:
        filename = filename + '.csv'

    fp = DIR_SESS_TDATA / filename

    try:
        if bytes:
            # bytes -> list of strings
            data = data.decode('utf-8').splitlines()

        with open(fp, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            for entry in data:
                d = entry.split(',')
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