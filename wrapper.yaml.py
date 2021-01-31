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

# synchronize
parser.add_argument('-y', '--synchronize', help='synchronize panes', required=False, default=False, action='store_true')


args = parser.parse_args()

# default check arguments - this is redundant
if len(sys.argv) == 1:
    print('Need argument')
    sys.exit()

# -----------------------------------------------
# Read yaml file
# -----------------------------------------------

file_path = args.configfile

if not os.path.isfile(file_path):
    sys.exit('{} file not found!'.format(file_path))

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

print(yaml_config)

if not args.session in yaml_config.keys():
    print('Session not found!')
    sys.exit()


if not 'windows' in yaml_config[args.session].keys():
    yaml_config[args.session]['windows'] = ['default']
    # sys.exit()

# -----------------------------------------------
# Iterate window configs
# -----------------------------------------------
config = {}
# iterate windows from config
for window_item in yaml_config[args.session]['windows']:

    # -----------------------------------------------
    # Commands at window level
    # -----------------------------------------------
    if type(window_item) == dict:
        # sections defined on window level
        window_name = window_item['name']

        config[window_name] = {}
        # config[window_name] = yaml_config[args.session]['windows']
        config[window_name]['sections'] = []

        if 'sections' in window_item.keys():
            for section_config in window_item['sections']:
                print(section_config)
                if not 'cmds' in section_config.keys():
                    print('Section in {} needs a cmds index!'.format(window_name))
                    sys.exit()
                else:
                    config[window_name]['sections'].append(section_config)

        # sections defined at main level
        elif 'sections' in yaml_config[args.session].keys():
            for section_config in yaml_config[args.session]['sections']:
                if not 'cmds' in section_config.keys():
                    print('Main section needs a cmds index!'.format(window_name))
                    sys.exit()
                else:
                    config[window_name]['sections'] = yaml_config[args.session]['sections']

        # config[index] = {}
        # config[index]['cmds'] = cmd # yaml_config[args.session]['windows'][index]['cmds']
    else:
        print('Window must be dict!')
        sys.exit()

print('YAML')
print(config)
# sys.exit()
# -----------------------------------------------
# Instantiate ultimux class
# ----------------------------------------------- 
session_name = args.session
utmx = Ultimux(config, session_name)

if args.interactive:
    utmx.set_interactive(True)

if args.synchronize:
    utmx.set_synchronize(True)

utmx.create()
utmx.attach()
