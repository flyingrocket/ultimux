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
gparser.add_argument("--dir", help="remote dir to cd in", required=False)
gparser.add_argument(
    "--flatten",
    "-f",
    help="do not use server groups",
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

group2 = gparser.add_argument_group("tmux options")
# synchronize
group2.add_argument(
    "--sync", help="synchronize panes", required=False, action="store_true"
)

# tiled
group2.add_argument(
    "--tiled", help="spread panes evenly", required=False, action="store_true"
)

args = parser.parse_args()

# -----------------------------------------------
# Initiate app
# -----------------------------------------------
if args.subcommand == "run":
    app = RunApp(args)
    session_name = args.session
elif args.subcommand == "gen":
    app = GenApp(args)
    session_name = f"utmx_gen_{script_time}"
else:
    sys.exit("Illegal subcommand!")

# -----------------------------------------------
# Instantiate ultimux class
# -----------------------------------------------
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
