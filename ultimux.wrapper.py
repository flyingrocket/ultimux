#! /usr/bin/env python3
# parse cli arguments
import argparse
# os module
import os
# import the Regex module
import re
# sys
import sys
# yaml supprt
import yaml

# ultimux
from lib.ultimux import Ultimux

# -----------------------------------------------
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description='plone cluster manager')
# show server info
parser.add_argument('-s', '--session', help='select session', required=True)
# show cluster info
parser.add_argument('-c', '--configfile', help='config yaml file', required=True)

# interactive mode
parser.add_argument('-i', '--interactive', help='interactive mode', required=False, default=False, action='store_true')

# debug
parser.add_argument('-d', '--debug', help='debug mode', required=False, default=False, action='store_true')


args = parser.parse_args()

# default check arguments - this is redundant
if len(sys.argv) == 1:
    print('Need argument')
    sys.exit()

# -----------------------------------------------
# Read yaml file
# -----------------------------------------------
homedir = os.getenv("HOME")
config_file = args.configfile

full_paths = []

if re.match("^~\/", config_file):
    full_paths.append(os.path.abspath(config_file.replace('~', homedir)))
elif re.match("^\.\/", config_file) or re.match("^\/", config_file):
    full_paths.append(os.path.abspath(config_file))
else:
    full_paths.append(os.path.abspath('./' + config_file))
    full_paths.append(os.path.abspath(homedir + '/conf.d/ultimux/' + config_file))
    full_paths.append('/etc/ultimux/conf.d/' + config_file)

config_file_found = False

# print(full_paths)
# sys.exit()

for full_path in full_paths:


    # print('try ' + full_path)

    if os.path.exists(full_path):
        config_file_found = True

        # set base for file
        file_path = full_path

        break

if not config_file_found:
    sys.exit('Config file "{}" not found!'.format(args.configfile))

# read the yaml file
with open(file_path) as file:
    # config = yaml.load(file, Loader=yaml.SafeLoader)

    if re.search('.+\.ya?ml$', file_path):
        try:
            yaml_config = yaml.load(file, Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            print(e)
            sys.exit('Exception in parsing yaml file ' + file_path + '!')
    else:
        sys.exit('{} file not supported!'.format(file_path))

if not args.session in yaml_config.keys():
    print('Session not found!')
    sys.exit()


session_config = yaml_config[args.session]

# -----------------------------------------------
# Instantiate ultimux class
# ----------------------------------------------- 
session_name = args.session
utmx = Ultimux(session_config, session_name)

if args.interactive:
    utmx.set_interactive(True)

if args.debug:
    utmx.set_debug(True)

utmx.create()
utmx.exec()
