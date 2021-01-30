#! /usr/bin/env python3

# ultimux
from lib.ultimux import Ultimux

config = {}

for window in ['win1', 'win2']:
    config[window] = {}
    config[window]['cmds'] = [
    'ls', # pane at the top
    ['w', 'whoami'], # two panes next to eachother
    'ssh northstar; w' # pane at the bottom
    ]
           
session_name = 'my_dict_test'
utmx = Ultimux(config, session_name)
utmx.set_focus('0.1')
utmx.create()
utmx.out()
# utmx.attach()
