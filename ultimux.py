#! /usr/bin/env python3

import argparse
import glob
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
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

appname = "ultimux"
homedir = os.path.abspath(os.getenv("HOME"))
default_browse_dirs = f"{homedir}/.{appname}/conf.d/"
default_browse_dirs = f"/etc/{appname}/conf.d/,{homedir}/.{appname}/conf.d/"

# -----------------------------------------------
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description="Ultimux tmux wrapper")
# show server info
parser.add_argument("-s", "--session", help="select session", required=False)

# synchronize
parser.add_argument(
    "--sync", help="synchronize panes", required=False, action="store_true"
)

# tiled
parser.add_argument(
    "--tiled", help="spread panes evenly", required=False, action="store_true"
)

# use config
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--config-file", help="config yaml file", required=False)

# browse configuration files
group.add_argument(
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

# list sessions
parser.add_argument(
    "-l", "--list", help="list sessions", required=False, action="store_true"
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
config_file = args.config_file

if args.config_file:
    if re.match("^~\/", config_file):
        file_path = os.path.abspath(config_file.replace("~", homedir))
    elif re.match("^\.\/", config_file) or re.match("^\/", config_file):
        file_path = os.path.abspath(config_file)
    else:
        file_path = os.path.abspath("./" + config_file)
elif args.browse:
    # search paths

    config_dirs_found = []

    for path in args.browse_dirs.split(","):
        if os.path.exists(path):
            config_dirs_found.append(os.path.abspath(path))
        else:
            # only fail if specific paths are given
            if not args.browse_dirs == default_browse_dirs:
                sys.exit(f"Config dir {path} not found!")

    print(f"Browse '{args.browse_dirs}' directories...")

    if not len(config_dirs_found):
        sys.exit(f"No config dirs found. Search path(s): {args.browse_dirs}")

    config_files = []
    for path in config_dirs_found:
        path = path.rstrip("/")
        config_files += glob.glob(f"{path}/*.yml")

    if not len(config_files):
        sys.exit(f"No config files found!")

    questions = [
        inquirer.List(
            "select_path",
            message=f"Select config file:",
            choices=config_files,
        ),
    ]
    answers = inquirer.prompt(questions)
    file_path = answers["select_path"]
else:
    sys.exit()

if not os.path.exists(file_path):
    sys.exit(f'Config file "{file_path}" not found!')

# -----------------------------------------------
# Read config file
# -----------------------------------------------
# read the yaml file
with open(file_path) as file:

    if re.search(".+\.ya?ml$", file_path):
        try:
            yaml_config = yaml.load(file, Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            print(e)
            sys.exit("Exception in parsing yaml file " + file_path + "!")
    else:
        sys.exit("{} file not supported!".format(file_path))

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
    questions = [
        inquirer.List(
            "select_session",
            message=f"Select session:",
            choices=yaml_config.keys(),
        ),
    ]
    answers = inquirer.prompt(questions)
    session_name = answers["select_session"]

if not session_name in yaml_config.keys():
    print("Session not found!")
    sys.exit()

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
