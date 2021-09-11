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
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description='plone cluster manager')
# show server info
parser.add_argument('-s', '--session', help='select session', required=False)

# show cluster info
parser.add_argument('-c', '--configfile', help='config yaml file', required=False)

# interactive mode
parser.add_argument('-i', '--interactive', help='interactive mode', required=False, default=False, action='store_true')

# debug
parser.add_argument('-d', '--debug', help='debug mode', required=False, default=False, action='store_true')

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
    
    confdir_current = dname + '/conf.d/'
    confdir_home = os.path.abspath(homedir) + '/conf.d/ultimux/'
    confdir_global = '/etc/ultimux/conf.d/'

    paths_search = [confdir_home, confdir_global]

    for path in paths_search:
        if os.path.exists(path):
            paths_found.append(path)

    if not len(paths_found):
        paths_search_display = ', '.join(paths_search)
        sys.exit(f'No config files found in: {paths_search_display}')

    config_files = []
    for path in paths_found:
        config_files += glob.glob(f"{path}*.yml")

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

utmx.create()
utmx.exec()
