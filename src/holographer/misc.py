#!/usr/bin/env python
"""Provide misc common functions to the rest of the CLI."""

# Imports
import logging
from pathlib import Path
import hashlib
import gzip

import pandas as pd
import ruamel.yaml as yaml

log = logging.getLogger(__name__)


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Functions
def load_csv(csv, **kwargs):
    try:
        return pd.read_csv(gzip.open(csv), **kwargs)

    except (pd.io.common.CParserError, OSError):
        return pd.read_csv(csv, **kwargs)

    except pd.io.common.EmptyDataError:
        msg = "File was empty: {f}.".format(f="/".join(Path(csv).parts[-2:]))
        log.error(msg)
        raise


def update_configs(directory, to_update=None):
    """Collect, combine, and return all *.yaml files in `directory`."""
    confs = Path(directory).glob('*.yaml')

    confs = {p.stem.upper(): p for p in confs}

    if to_update is None:
        to_update = Munch()

    for name, conf in confs.items():
        c = process_config(config=conf)
        to_update.update(Munch({name: c}))

    return to_update


def process_config(config=None):
    """Prepare single config file."""
    if config is None:
        return Munch()
    else:
        if isinstance(config, str):
            config = Path(config)
        return munchify(yaml.safe_load(config.open()))



def chunk_md5(path, size=1024000):
    """Calculate and return the md5-hexdigest of a file in chunks of `size`."""
    p = Path(path)
    md5 = hashlib.md5()

    with p.open('rb') as f:
        while 1:
            data = f.read(size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()
