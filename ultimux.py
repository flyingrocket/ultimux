#! /usr/bin/env python3

import argparse
import datetime
import os
import sys

# -----------------------------------------------
# Include functions
# -----------------------------------------------
from _app import *
from _ultimux import *

script_dir = os.path.dirname(os.path.abspath(__file__))
script_time = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

# -----------------------------------------------
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description="Ultimux, a tmux wrapper.")

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
    "--debug",
    help="debug mode",
    required=False,
    default=False,
    action="store_true",
)

parser.add_argument(
    "-v",
    "--verbose",
    help="Set to verbose mode",
    required=False,
    default=False,
    action="store_true",
)

# -----------------------------------------------
# Subparser
# -----------------------------------------------
subparsers = parser.add_subparsers(dest="subcommand", required=True)

# -----------------------------------------------
# Run with config
# -----------------------------------------------
rparser = subparsers.add_parser("run")
# use config
rparser.add_argument(
    "-c",
    "--config-file",
    help="config (yaml) file",
    required=False,
    default=False,
)
rparser.add_argument("-s", "--session", help="select session", required=False)

# -----------------------------------------------
# Generate with template
# -----------------------------------------------
gparser = subparsers.add_parser("gen")

# directory stuff
group = gparser.add_mutually_exclusive_group()
group.add_argument("--dir", help="remote dir to cd in", required=False)
group.add_argument(
    "--select-dir",
    help="select remote dir to cd in",
    required=False,
    action="store_true",
)

# show all servers as flat list
gparser.add_argument(
    "--flatten",
    "-f",
    help="do not use server groups, show flat list.",
    required=False,
    action="store_true",
)
gparser.add_argument("--shell", help="remote command to run", required=False)

# use config
gparser.add_argument(
    "-c",
    "--config-file",
    help="config (yaml) file",
    required=False,
    default=False,
)

group = gparser.add_argument_group("tmux options")
# synchronize
group.add_argument(
    "--sync", help="synchronize panes", required=False, action="store_true"
)

# tiled
group.add_argument(
    "--tiled", help="spread panes evenly", required=False, action="store_true"
)

args = parser.parse_args()

# -----------------------------------------------
# Initiate app
# -----------------------------------------------
if args.subcommand == "run":
    app = RunApp(args)
elif args.subcommand == "gen":
    app = GenApp(args)
else:
    sys.exit("Illegal subcommand!")

# -----------------------------------------------
# Instantiate ultimux class
# -----------------------------------------------
session_name = f"utmx_{args.subcommand}_{script_time}"
session_config = app.get_session_config(session_name)

utmx = Ultimux(session_config, f"utmx_{args.subcommand}", True)

for flag in ["debug", "interactive", "sync", "tiled"]:
    if hasattr(args, flag) and getattr(args, flag):
        func = getattr(utmx, f"set_{flag}")
        func(getattr(args, flag))

options = {}
for config_type in ["shell", "dir"]:

    if hasattr(args, config_type):
        options[config_type] = getattr(args, config_type)

utmx.create(options)
utmx.exec()
