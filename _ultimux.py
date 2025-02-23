#! /usr/bin/env python3

import ast, datetime, os, re, subprocess, sys


class Ultimux:

    # -----------------------------------------------
    # Application properties
    # -----------------------------------------------
    tmux_commands = []

    session_config = {}

    session_name = ""

    app_name = "utmx"

    version = "2.0"

    # -----------------------------------------------
    # Dynamic properties
    # -----------------------------------------------

    col = False

    debug = False

    focus = "0.0"

    sync = False

    validated_destinations = []

    def __init__(self, session_config, session_name="", add_timestamp=False):

        self.session_config = session_config

        # -----------------------------------------------
        # Check if tmux is installed
        # -----------------------------------------------
        try:
            subprocess.call(
                ["tmux", "-V"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except OSError:
            print("Tmux is not installed...")

        # -----------------------------------------------
        # Set session name
        # -----------------------------------------------
        datestamp = "{:%Y%m%d_%H%M%S%f}".format(datetime.datetime.now())

        if not session_name:
            self.session_name = self.app_name + datestamp
        else:
            self.session_name = session_name

        if add_timestamp:
            self.session_name += "_" + datestamp

        # validate session name
        if re.search(r"(\.|\:|\ )+", self.session_name):
            self.fail("Session name may not contain .: or spaces!")

        # -----------------------------------------------
        # Set defaults
        # -----------------------------------------------
        self.tmux_commands = []

        self.focus = "0.0"

        # echo commands before running
        self.interactive = False

        # set unique session name
        self.set_session_unique_id = True

        # sycnchronize panes
        self.sync = False

        # columns
        self.tiled = False

    def fail(self, message=""):
        print(message)
        sys.exit(1)

    def set_debug(self, debug):

        if not type(debug) == bool:
            self.fail("Directive debug must be boolean!")

        self.debug = debug

    def set_focus(self, focus):

        if not re.match(r"^[0-9]+\.[0-9]+$", focus):
            self.fail("Focus must be {number}.{number}!")

        self.focus = focus

    def set_interactive(self, interactive):

        if not type(interactive) == bool:
            self.fail("Directive interactive must be boolean!")

        self.interactive = interactive

    def set_tiled(self, tiled):

        if not type(tiled) == bool:
            self.fail("Directive tiled must be boolean!")

        self.tiled = tiled

    def set_sync(self, sync):

        if not type(sync) == bool:
            self.fail("Directive sync must be boolean!")

        self.sync = sync

    def create(self, options={}):

        session_config = self.session_config

        # ---------------------------------------
        # Global options
        # ---------------------------------------
        if "interactive" in session_config:
            self.set_interactive(session_config.get("interactive"))

        if "config" in session_config:
            self.set_focus(session_config.get("focus"))

        # ---------------------------------------
        # Create window if required
        # ---------------------------------------
        # check if window
        if not "windows" in session_config:

            window_config = {"name": "ultimux"}

            if "panes" in session_config:
                window_config["panes"] = session_config["panes"]

            session_config["windows"] = []
            session_config["windows"].append(window_config)

        # ---------------------------------------
        # Iterate windows
        # ---------------------------------------
        # window counter
        i = 0

        for window in session_config["windows"]:

            # ---------------------------------------
            # Set window name
            # ---------------------------------------
            if "name" in window.keys():
                window_name = window["name"]
            elif "ssh" in window.keys():
                window_name = window["ssh"]
            else:
                window_name = window["win{}".format(i)]

            # ---------------------------------------
            # Create tmux session/window
            # ---------------------------------------
            # first loop: create a session + window with -n option
            if i == 0:
                self.tmux_commands.append(
                    "tmux new-session -d -A -s {} -n '{}'".format(
                        self.session_name, window_name
                    )
                )
            # first window is alreay set, skip
            else:
                self.tmux_commands.append(
                    "tmux new-window -t '{}' -n '{}' ".format(
                        self.session_name, window_name
                    )
                )

            # pane counter
            ii = 0

            # ---------------------------------------
            # Default to global pane
            # ---------------------------------------
            # global panes
            if window.get("panes"):
                panes = window["panes"]
            elif session_config.get("panes"):
                panes = session_config["panes"]
            else:
                if "shell" in session_config:
                    panes = [{"shell": session_config.get("shell")}]
                else:
                    self.fail("Panes or shell are not defined!")

            if type(panes) != list:
                self.fail("Could not parse panes, not a list!")

            # ---------------------------------------
            # Iterate panes
            # ---------------------------------------
            for pane in panes:

                # full split for new pane (row)
                if ii > 0:
                    self.tmux_commands.append(
                        "tmux split-window -f -t '{}'".format(self.session_name)
                    )

                if type(pane) == dict:
                    for config_type in ["dir", "shell"]:
                        if config_type not in pane.keys():
                            if config_type in options:
                                pane[config_type] = options[config_type]
                            elif window.get(config_type):
                                pane[config_type] = self.parse_shell(
                                    window.get(config_type)
                                )
                            elif session_config.get(config_type):
                                pane[config_type] = self.parse_shell(
                                    session_config.get(config_type)
                                )
                            else:
                                pane[config_type] = [""]
                else:
                    yml_cmds = self.parse_shell(pane)
                    pane = {}
                    pane["shell"] = yml_cmds

                cmds = []

                shell_cmds = self.parse_shell(pane["shell"])

                if pane["dir"] and pane["dir"] != [""]:
                    cmds = [f"cd {pane['dir']}; {shell_cmds[0]}"]
                else:
                    cmds = self.parse_shell(pane["shell"])

                if type(cmds) != list:
                    self.fail("Could not parse cmds, not a list!")

                # split counter
                iii = 0

                for cmd in cmds:

                    # print(cmd)
                    split = "-h"
                    command = cmd

                    if type(cmd) == dict:
                        command = cmd["shell"]

                        if "split" in cmd.keys():
                            split = cmd["split"]

                    if not split in ["-v", "-h"]:
                        self.fail("Illegal split! Use -v or -h...")

                    if iii > 0:
                        self.tmux_commands.append(
                            "tmux split-window {} -t '{}'".format(
                                split, self.session_name
                            )
                        )

                    target = self.session_name + ":" + str(i) + "." + str(ii)

                    self.parse_command(command, pane, window, target)

                    iii += 1
                    ii += 1

            synchronize_panes = False

            if self.sync:
                synchronize_panes = True
            elif "synchronize" in window.keys():
                if window.get("synchronize"):
                    synchronize_panes = True
            elif session_config.get("synchronize"):
                synchronize_panes = True

            if synchronize_panes:
                self.tmux_commands.append(
                    "tmux set-option -t '{}' synchronize-panes on".format(
                        self.session_name
                    )
                )

            layout = ""

            if "layout" in window.keys():
                if window.get("layout"):
                    layout = window.get("layout")
            elif session_config.get("layout"):
                layout = session_config.get("layout")

            if self.tiled:
                layout = "tiled"

            # layout
            if not layout == "":
                self.tmux_commands.append("tmux select-layout {}".format(layout))

            i += 1  # window

        # ---------------------------------------
        # Set options and attach
        # ---------------------------------------
        self.tmux_commands.append("tmux set-option -g status-style bg=blue")

        # support 256 colors
        self.tmux_commands.append("tmux set -g default-terminal 'screen-256color'")

        # set focus
        self.tmux_commands.append(
            "tmux select-pane -t '{}:{}'".format(self.session_name, self.focus)
        )
        self.tmux_commands.append(
            "tmux attach -t '{}:{}'".format(self.session_name, self.focus)
        )

    def parse_shell(self, shell_command=""):

        # if only a command or list is specified
        if shell_command == None:
            formatted = [""]
        elif type(shell_command) == str:
            formatted = [shell_command]
        else:  # type(shell_command) == list:
            formatted = shell_command

        return formatted

    def parse_command(self, command, pane, window, target):

        session_config = self.session_config
        # ---------------------------------------
        # Get ssh config options
        # ---------------------------------------
        ssh_options = {}

        # merge these options
        ssh_options1 = {}
        if type(session_config) == dict and "ssh" in session_config.keys():
            pane_ssh = session_config["ssh"]
            if not type(pane_ssh) == dict:
                ssh_options1["server"] = pane_ssh
            else:
                ssh_options1 = session_config["ssh"]

        ssh_options2 = {}
        if type(window) == dict and "ssh" in window.keys():
            pane_ssh = window["ssh"]
            if not type(pane_ssh) == dict:
                ssh_options2["server"] = pane_ssh
            else:
                ssh_options2 = window["ssh"]

        ssh_options3 = {}
        if type(pane) == dict and "ssh" in pane.keys():
            pane_ssh = pane["ssh"]
            if not type(pane_ssh) == dict:
                ssh_options3["server"] = pane_ssh
            else:
                ssh_options3 = pane["ssh"]

        ssh_options = {**ssh_options1, **ssh_options2, **ssh_options3}

        # ---------------------------------------
        # Compile ssh commands
        # ---------------------------------------
        if ssh_options:

            if not ssh_options.get("server"):
                self.fail("Ssh server must be specified!")

            if ssh_options.get("user"):
                destination = "{}@{}".format(
                    ssh_options.get("user"), ssh_options.get("server")
                )
            else:
                destination = ssh_options.get("server")

            options = ["-o ConnectTimeout=0"]
            options = []

            # compile ssh command
            ssh_command = "ssh {}{}".format(" ".join(options), destination)

            # ---------------------------------------
            # Check connectivity
            # ---------------------------------------
            if not destination in self.validated_destinations and not self.debug:

                # first check
                if not len(self.validated_destinations):
                    print("Check ssh connectivity...")

                subcommand = "{} {}".format(ssh_command, "echo ok")
                try:
                    # split string into pieces
                    subprocess.check_output(
                        subcommand.split(), stderr=subprocess.STDOUT
                    )
                except subprocess.CalledProcessError as e:
                    # print(e)
                    print(destination.ljust(60, "."), "FAIL")
                    self.fail("Failed connectivity check: {}".format(destination))

                print(destination.ljust(60, "."), "OK")
                self.validated_destinations.append(destination)

            # ---------------------------------------
            # Ssh remote or login
            # ---------------------------------------
            # run ssh command remotely or login
            seperator = ";"
            # if "login" in ssh_options and not ssh_options.get("login"):
            #     seperator = ""

            # add ssh prefix to command
            command = "{}{} {}".format(ssh_command, seperator, command)

        # ---------------------------------------
        # String of commands
        # ---------------------------------------
        tcommands = command.split(";")

        for tcommand in tcommands:
            tcommand = tcommand.strip()

            # no empty commands allowed
            if not tcommand:
                continue

            if self.debug:
                tcommand = "# " + tcommand
                enter = ""
            else:
                enter = "C-m"

            self.tmux_commands.append(
                "tmux send-keys -t " + target + " '" + tcommand + "' " + enter
            )

    def out(self):
        print()

        for tcomm in self.tmux_commands:
            print(tcomm)

    def exec(self):

        if self.interactive:

            self.out()

            print()
            answer = input("Execute these commands? [Y/n] ")

            if answer != "Y" and answer != "":
                self.fail()

        for subcommand in self.tmux_commands:
            os.system(subcommand)
