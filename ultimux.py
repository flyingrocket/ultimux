#! /usr/bin/env python3

import os
import sys

# -----------------------------------------------
# Include functions
# -----------------------------------------------
from _helpers import *
from _ultimux import *

# -----------------------------------------------
# Arguments
# -----------------------------------------------
config_dirs = f"/etc/{appname}/conf.d/,{homedir}/.{appname}/conf.d/"
args = get_argparse(config_dirs=config_dirs)

# -----------------------------------------------
# Get config file
# -----------------------------------------------
config_file_path = get_config_file(args)

if not os.path.exists(config_file_path):
    sys.exit(f"Config file '{config_file_path}' not found!")

print(f"Use '{config_file_path}'...")

# -----------------------------------------------
# Read config file
# -----------------------------------------------
yaml_config = get_yaml_config(config_file_path)

# -----------------------------------------------
# Get session name
# -----------------------------------------------
if not args.session:
    args.session = select_sections(yaml_config, "session")[0]

# -----------------------------------------------
# Instantiate ultimux class
# -----------------------------------------------
session_config = yaml_config[args.session]

utmx = Ultimux(session_config, args.session, args.unique)

if args.interactive:
    utmx.set_interactive(True)

if args.debug:
    utmx.set_debug(True)

if args.sync:
    utmx.set_sync(True)

if args.tiled:
    utmx.set_tiled(True)

options = {}
for config_type in ["shell", "dir"]:
    if getattr(args, config_type):
        options[config_type] = getattr(args, config_type)

utmx.create(options)
utmx.exec()
