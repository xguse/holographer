#!/usr/bin/env python
"""Provide command line interface to holographer."""

# Imports
import logging.config
import logging
from logzero import logging as log

import os
from pathlib import Path
import datetime as dt
import shutil
import pprint as pp
import appdirs


from munch import Munch, munchify, unmunchify
import ruamel.yaml as yaml

import click
from click import echo

import holographer.cli.config as _config
from holographer.misc import process_config, update_configs
import holographer.errors as e


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"

FACTORY_RESETS = (Path(os.path.realpath(__file__)).parent / 'factory_resets/').resolve()
USER_CONFIG_DIR = Path(appdirs.user_config_dir())
USER_HOLO_DIR = USER_CONFIG_DIR / 'holographer'


@click.group(invoke_without_command=True)
@click.option('-c', '--config', default=None,
              help="Path to optional config directory. If `None`, {user_config_dir} is searched for *.yaml files.".format(user_config_dir=str(USER_CONFIG_DIR)), type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.pass_context
def run(ctx=None, config=None, home=None):
    """Command interface to the holographer.

    Holographer copies a filesytem object to a storage location and creates
    in its place a symlinked decoy pointing to the stored target. Think of when
    you run out of HDD space and need to move things to free up space but do
    not want to break everything that may expect to find your target in
    its old location

    For command specific help text, call the specific
    command followed by the --help option.
    """
    ctx.obj = Munch()
    ctx.obj.CONFIG = Munch()

    top_lvl_confs = FACTORY_RESETS

    # Load the factory_resets/logging.yaml as an absolute fall-back logging config
    # ctx.obj.CONFIG.LOGGING = process_config(config=top_lvl_confs / 'factory_resets/logging.yaml')

    ctx.obj.CONFIG = update_configs(directory=top_lvl_confs, to_update=ctx.obj.CONFIG)

    if config:
        ctx.obj.CONFIG = update_configs(directory=config, to_update=ctx.obj.CONFIG)




@run.command()
@click.option("-l", "--list", "list_",
              is_flag=True,
              default=False,
              help="Print the configuration values that will be used and exit.")
@click.option('-g', '--generate-config',
              is_flag=True,
              help="Copy one or more of the 'factory default' config files to the users "
              "config directory ({user_config_dir}). Back ups will be made of any existing config files.".format(user_config_dir=USER_HOLO_DIR),
              show_default=True,
              default=False)
@click.option('-k', '--kind',
              type=click.Choice(['all', 'main']),
              help="Which type of config should we replace?",
              show_default=True,
              default='all')
@click.pass_context
def configs(ctx, list_, generate_config, kind):
    """Manage configuration values and files."""
    if list_:
        conf_str = yaml.dump(unmunchify(ctx.obj.CONFIG), default_flow_style=False)
        echo(conf_str)
        exit(0)

    factory_resets = FACTORY_RESETS
    default_files = {"all": factory_resets.glob('*.yaml'),
                     "main": factory_resets / 'main.yaml',
                     "logging": factory_resets / 'logging.yaml',
                     }

    if generate_config:
        if kind == 'all':
            for p in default_files['all']:
                _config.replace_config(name=p.name, factory_resets=factory_resets, user_conf_dir=USER_HOLO_DIR)
        else:
            p = default_files[kind]
            _config.replace_config(name=p.name, factory_resets=factory_resets, user_conf_dir=USER_HOLO_DIR)


# Business
if __name__ == '__main__':
    run(obj=Munch())
