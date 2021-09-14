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

appname = 'ultimux'

# -----------------------------------------------
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description='Ultimux - tmux wrapper')
# show server info
parser.add_argument('-s', '--session', help='select session', required=False)

# synchronize
parser.add_argument('--sync', help='synchronize panes', required=False, action='store_true')

# tiled
parser.add_argument('--tiled', help='spread panes evenly', required=False, action='store_true')

# use config
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-c', '--configfile', help='config yaml file', required=False)
group.add_argument('-b', '--browse', help='browse through all available configs', required=False, action='store_true')
group.add_argument('-d', '--configdir', help='browse through given config dir', required=False)

# list sessions
parser.add_argument('-l', '--list', help='list sessions', required=False, action='store_true')

# interactive mode
parser.add_argument('-i', '--interactive', help='interactive mode', required=False, default=False, action='store_true')

# debug
parser.add_argument('--debug', help='debug mode', required=False, default=False, action='store_true')

args = parser.parse_args()

# -----------------------------------------------
# Get config file
# -----------------------------------------------
homedir = os.getenv("HOME")
config_file = args.configfile

if args.configfile:
    if re.match("^~\/", config_file):
        file_path = os.path.abspath(config_file.replace('~', homedir))
    elif re.match("^\.\/", config_file) or re.match("^\/", config_file):
        file_path = os.path.abspath(config_file)
    else:
        file_path = os.path.abspath('./' + config_file)
else:
    # search paths
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)

    paths_found = []

    if args.configdir:
        paths_search = [args.configdir]
    else:
        confdir_current = dname + '/conf.d/'
        confdir_home = os.path.abspath(homedir) + f'/.{appname}/conf.d/'
        confdir_global = f'/etc/{appname}/conf.d/'

        paths_search = [confdir_home, confdir_global]

    for path in paths_search:
        if os.path.exists(path):
            paths_found.append(path)

    paths_search_display = ', '.join(paths_search)

    if not len(paths_found):
        sys.exit(f'No config dirs found: {paths_search_display}')

    config_files = []
    for path in paths_found:
        config_files += glob.glob(f"{path}*.yml")

    if not len(config_files):
        sys.exit(f'No config files found: {paths_search_display}')

    questions = [inquirer.List('select_path', message=f'Select config file:', choices=config_files,),]
    answers = inquirer.prompt(questions)
    file_path = answers['select_path']

if not os.path.exists(file_path):
    sys.exit(f'Config file "{file_path}" not found!')

# -----------------------------------------------
# Read yaml file
# -----------------------------------------------
# read the yaml file
with open(file_path) as file:

    if re.search('.+\.ya?ml$', file_path):
        try:
            yaml_config = yaml.load(file, Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            print(e)
            sys.exit('Exception in parsing yaml file ' + file_path + '!')
    else:
        sys.exit('{} file not supported!'.format(file_path))

# -----------------------------------------------
# List sessions
# -----------------------------------------------
if args.list:
    print('\n'.join(list(yaml_config.keys())))
    sys.exit()

# -----------------------------------------------
# Get session name
# -----------------------------------------------
if args.session:
    session_name = args.session
else:
    questions = [inquirer.List('select_session', message=f'Select session:', choices=yaml_config.keys(),),]
    answers = inquirer.prompt(questions)
    session_name = answers['select_session']

if not session_name in yaml_config.keys():
    print('Session not found!')
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
