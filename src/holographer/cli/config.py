#!/usr/bin/env python
"""Provide functions used in cli.config."""

# Imports
from pathlib import Path
import datetime as dt
import shutil

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


def replace_config(name, factory_resets, user_conf_dir):
    """Replace existing config file or generate initial one.

    Backup existing file.
    """
    if not user_conf_dir.exists():
        user_conf_dir.mkdir(parents=True, exist_ok=True)

    default_path = factory_resets / name
    conf_path = user_conf_dir / name

    # print(default_path)
    # print(conf_path)
    # print(bk_path)

    stamp = dt.datetime.today().isoformat()
    if conf_path.exists():
        bk_path = Path('{name}.bkdup_on_{stamp}'.format(name=str(conf_path),
                                                        stamp=stamp))
        shutil.move(src=str(conf_path), dst=str(bk_path))

    shutil.copy(src=str(default_path), dst=str(conf_path))
