#!/usr/bin/env python
"""Provide the basic logic used across subcommands."""

# Imports
import logging

from pathlib import Path
import shutil
from os.path import normpath
from collections import namedtuple

import pandas as pd

from holographer.misc import chunk_md5
from holographer import errors as e

log = logging.getLogger(__name__)

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# classes
SourcePathRow = namedtuple('SourcePathRow', ["source_path",
                                             "exists",
                                             "kind",
                                             "cksum"])


# Functions
def resolve(path):
    """Return the fully resolved path even if it does not exist.

    Args:
        path (Path): the Path object to resolve.

    Returns:
        Path: fully resolved ``Path`` object.
    """
    try:
        resolved = path.resolve()
    except FileNotFoundError:
        resolved = Path(normpath(str(path.absolute())))

    return resolved


def get_path_kind(path):
    """Return a string describing which kind of path we have.

    Args:
        path (Path): A Path object.

    Returns:
        str
    """
    if not path.exists():
        return 'nonexistent'
    elif path.is_dir():
        return 'dir'
    elif path.is_file():
        return 'file'
    elif path.is_symlink():
        return 'symlink'
    else:
        return 'other'


def get_cksum(path, kind='md5'):
    """Return a checksum digest fingerprint of kind ``kind`` for the path given.

    Args:
        path (Path): A Path object.
        kind (str): name of the checksum algorithm to generate the checksum.

    Returns:
        str
    """
    algos = {"md5": chunk_md5}

    try:
        cksum = algos[kind](path=path)
    except KeyError:
        raise e.ValidationError("unsupported cksum kind: '{k}'. Choose from {kinds}".format(k=kind, kinds=algos.keys()))
    except IsADirectoryError:
        cksum = "IsADirectoryError"
    except FileNotFoundError:
        cksum = "FileNotFoundError"

    return cksum


def copy_from_table_row(row, clobber=False):
    """Perform a single copy operation using information from a single row of a copy_table.

    Args:
        param1 (type): The first parameter.
        param2 (type): The second parameter.

    Returns:
        Path: destination path returned by respective copy function.
    """
    if row['kind'] == 'dir':
        return row["desti_path"].mkdir(parents=True, exist_ok=True)
    elif row['kind'] == 'file':
        return Path(copy_file(src=row["source_path"], dst=row["desti_path"], clobber=clobber))
    elif row['kind'] == 'symlink':
        # TODO: write a ``copy_symlink`` after deciding how to treat those.
        return Path(copy_file(src=row["source_path"], dst=row["desti_path"], clobber=clobber))
    elif row['kind'] == 'other':
        # TODO: decide how to treat these.
        return Path(copy_file(src=row["source_path"], dst=row["desti_path"], clobber=clobber))
    else:
        raise NotImplementedError("Gus needs to write a copy function for kind: '{kind}'".format(kind=row['kind']))


def copy_file(src, dst, clobber=False):
    """Copy a single file from src to dst..

    Args:
        src (Path): Path object representing a single file.
        dst (Path): Path object representing the destination file.
        clobber (bool): If True, existing file at dst will be clobbered.

    Returns:
        type: The return value. True for success, False otherwise.
    """
    if not (src.is_file() and src.exists()):
        msg = "src must be a file that exists."
        raise e.ValidationError(msg)

    if (not clobber) and dst.exists():
        msg = "dst exists and clobber is set to False."
        raise e.ValidationError(msg)

    src = resolve(path=src)
    dst = resolve(path=dst)

    return shutil.copy2(src=str(src),
                        dst=str(dst))


def source_path_table(path):
    """Return a dataframe representing information for the source paths.

    Args:
        path (Path): A Path object.

    Returns:
        DataFrame
    """
    if path.is_file():
        paths = [path]

    elif path.is_dir():
        paths = list(path.glob('**/*'))

    path_rows = []
    for p in paths:
        path = resolve(path=p.absolute())
        exists = path.exists()
        cksum = get_cksum(path=path, kind='md5')
        kind = get_path_kind(path=path)

        path_rows.append(SourcePathRow(source_path=path,
                                       exists=exists,
                                       kind=kind,
                                       cksum=cksum))

    path_rows = pd.DataFrame(path_rows).set_index("source_path")
    return path_rows


def desti_path_table(source_table, desti_dir):
    """Return a dataframe representing information for the destination paths.

    Args:
        source_table (DataFrame): Table containing info about the source paths.
        desti_dir (Path): Path object representing the directory where we should
            copy the paths represented in ``source_table``.

    Returns:
        DataFrame
    """
    desti_dir = resolve(desti_dir)

    # Does desti_dir exist and IS it a directory?
    if desti_dir.exists() and (not desti_dir.is_dir()):
        msg = "destination path exists but is NOT a directory."
        raise e.ValidationError(msg)

    desti_table = source_table.reset_index()[["source_path"]]

    desti_table["desti_path"] = desti_table["source_path"].apply(lambda src: desti_dir / str(src).lstrip('/'))
    desti_table["exists"] = desti_table["desti_path"].apply(lambda desti_path: desti_path.exists())
    desti_table["kind"] = desti_table["desti_path"].apply(get_path_kind)
    desti_table["cksum"] = desti_table["desti_path"].apply(get_cksum)

    desti_table = desti_table.set_index("source_path")
    return desti_table


def copy_from_tables(source_table, desti_table, clobber=False):
    """Perform path-by-path copy functions described in the source and destination tables.

    Returns a DataFrame representing the copy operations and whether the checksums match afterwards.

    Args:
        source_table (DataFrame): Table containing info about the source paths.
        desti_table (DataFrame): Table containing info about the destination paths.
        clobber (bool): If ``True`` overwrite existing files in the destination paths.

    Returns:
        DataFrame
    """
    source_table = source_table.sort_index()
    desti_table = desti_table.sort_index()
    copy_table = pd.DataFrame(index=source_table.index)
    copy_table["desti_path"] = desti_table["desti_path"]
    copy_table["kind"] = source_table["kind"]

    # do the copies
    copy_table.reset_index().apply(lambda row: copy_from_table_row(row=row, clobber=clobber), axis=1)

    # collect the cksums
    copy_table["cksum"] = desti_table["desti_path"].apply(get_cksum)

    copy_table['copy_success'] = copy_table["cksum"] == source_table["cksum"]

    return copy_table
