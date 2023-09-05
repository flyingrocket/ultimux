#! /usr/bin/env python3

import sys

# ultimux
from _ultimux import Ultimux

session_config = {}
session_config["windows"] = []

for window_name in ["win1", "win2"]:
    session_config["windows"].append(
        {
            "name": window_name,
            "panes": [
                {"shell": "ls"},  # pane at the top
                {"shell": ["w", "whoami"]},  # two panes next to eachother
                {"shell": "ssh northstar; w"},  # pane at the bottom
            ],
        }
    )

session_name = "my_dict_test"
utmx = Ultimux(session_config)
utmx.set_focus("0.1")
utmx.set_interactive(True)
utmx.create()
# utmx.out()
utmx.exec()
