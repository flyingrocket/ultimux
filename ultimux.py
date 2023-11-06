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
script_time = datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")

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

# tiled
parser.add_argument(
    "--name", help="tmux session name", required=False
)

# -----------------------------------------------
# Subparser
# -----------------------------------------------
subparsers = parser.add_subparsers(dest="subcommand", required=True)

# -----------------------------------------------
# Run with config
# -----------------------------------------------
rparser = subparsers.add_parser("run", help="Run tmux session from config file")

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
gparser = subparsers.add_parser(
    "gen", aliases=["generate"], help="Generate and run ad hoc configs for ssh"
)

# directory stuff
gparser.add_argument(
    "--dir",
    "-d",
    nargs="?",
    help="remote dir to cd in, leave empty to select",
    required=False,
    const="select",
)

gparser.add_argument(
    "--group-match",
    "-g",
    help="(glob) match group",
    required=False,
)

gparser.add_argument(
    "--host-match",
    "-m",
    help="(glob) match host",
    required=False,
)

# show all servers as flat list
gparser.add_argument(
    "--flatten",
    "-n",
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
    config_index = args.session
elif args.subcommand == "gen":
    app = GenApp(args)
    config_index = f"utmx_gen_{script_time}"
else:
    sys.exit("Illegal subcommand!")

# -----------------------------------------------
# Instantiate ultimux class
# -----------------------------------------------
session_config = app.get_session_config(config_index)

if not args.name:
    tmux_session_name = f"utmx_{args.subcommand}"
else:
    tmux_session_name = args.name

utmx = Ultimux(session_config, tmux_session_name, True)

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
