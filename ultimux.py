#! /usr/bin/env python3

import argparse
import glob
import importlib
import inquirer
import os
import re
import sys
import yaml

# ultimux
from lib.ultimux import Ultimux

# -----------------------------------------------
# Variables
# -----------------------------------------------
abspath = os.path.realpath(__file__)
dname = os.path.dirname(abspath)

appname = "ultimux"
homedir = os.path.abspath(os.getenv("HOME"))
default_browse_dirs = f"{homedir}/.{appname}/conf.d/"
default_browse_dirs = f"/etc/{appname}/conf.d/,{homedir}/.{appname}/conf.d/"

# -----------------------------------------------
# Include functions
# -----------------------------------------------
import importlib.util

spec = importlib.util.spec_from_file_location("wrapper.py", f"{dname}/lib/wrapper.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)

# -----------------------------------------------
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description="Ultimux tmux wrapper...")

# use config
group0 = parser.add_mutually_exclusive_group(required=True)

group0.add_argument("-c", "--config-file", help="config (yaml) file", required=False)

# browse configuration files
group0.add_argument(
    "-b",
    "--browse",
    help=f"browse mode. defaults to browsing in dirs {default_browse_dirs}",
    default=False,
    required=False,
    action="store_true",
)

# browse configuration files
parser.add_argument(
    "--browse-dirs",
    help=f"browse dir(s) - seperated by comma - for available config files. defaults to {default_browse_dirs}",
    default=default_browse_dirs,
    required=False,
)

group1 = parser.add_mutually_exclusive_group()
# list sessions
group1.add_argument("--list", help="list sessions", required=False, action="store_true")

group1.add_argument("-s", "--session", help="select session", required=False)

group2 = parser.add_argument_group("tmux options")
# synchronize
group2.add_argument(
    "--sync", help="synchronize panes", required=False, action="store_true"
)

# tiled
group2.add_argument(
    "--tiled", help="spread panes evenly", required=False, action="store_true"
)

# interactive mode
parser.add_argument(
    "-i",
    "--interactive",
    help="interactive mode",
    required=False,
    default=False,
    action="store_true",
)

# debug
parser.add_argument(
    "--debug", help="debug mode", required=False, default=False, action="store_true"
)

args = parser.parse_args()

# -----------------------------------------------
# Get config file
# -----------------------------------------------

file_path = wrapper.get_config_file(args, default_browse_dirs)

if not os.path.exists(file_path):
    sys.exit(f'Config file "{file_path}" not found!')

# -----------------------------------------------
# Read config file
# -----------------------------------------------

yaml_config = wrapper.get_yaml_config(file_path)

# -----------------------------------------------
# List sessions
# -----------------------------------------------
if args.list:
    print("\n".join(list(yaml_config.keys())))
    sys.exit()

# -----------------------------------------------
# Get session name
# -----------------------------------------------
if args.session:
    session_name = args.session
else:
    session_name = wrapper.get_section(yaml_config, "session")

# -----------------------------------------------
# Instantiate ultimux class
# -----------------------------------------------
session_config = yaml_config[session_name]

utmx = Ultimux(session_config, session_name)

if args.interactive:
    utmx.set_interactive(True)

if args.debug:
    utmx.set_debug(True)

if args.sync:
    utmx.set_sync(True)

if args.tiled:
    utmx.set_tiled(True)

utmx.create()
utmx.exec()
