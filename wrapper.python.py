#! /usr/bin/env python3

# ultimux
from lib.ultimux import Ultimux

config = {}

for window in ['win1', 'win2']:
    config[window] = {}
    config[window]['sections'] = [
        {'cmds': 'ls'}, # pane at the top
        {'cmds': ['w', 'whoami']}, # two panes next to eachother
        {'cmds': 'ssh northstar; w'}, # pane at the bottom
    ]
           
session_name = 'my_dict_test'
utmx = Ultimux(config, session_name)
utmx.set_focus('0.1')
utmx.set_interactive(True)
utmx.create()
# utmx.out()
utmx.attach()
