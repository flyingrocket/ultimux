#!/usr/bin/env python3

import argparse
import datetime
import glob
import inquirer
import os
import re
import sys
import yaml

# -----------------------------------------------
# Variables
# -----------------------------------------------
abspath = os.path.realpath(__file__)
dname = os.path.dirname(abspath)

appname = "ultimux"
homedir = os.path.abspath(os.getenv("HOME"))
datestamp = "{:%Y-%m-%d_%H%M%S}".format(datetime.datetime.now())

ultimux_session_name = f"ultimux_{datestamp}"


def get_argparse(description="Ultimux tmux wrapper", config_dirs=[]):

    parser = argparse.ArgumentParser(description=description)

    # use config
    parser.add_argument(
        "-c", "--config-file", help="config (yaml) file", required=False
    )

    # browse configuration files
    parser.add_argument(
        "--config-dirs",
        help=f"config dir(s) - seperated by comma - for available config files. defaults to {config_dirs}",
        default=config_dirs,
        required=False,
    )

    parser.add_argument("-s", "--session", help="select session", required=False)

    parser.add_argument("--shell", help="remote command to run", required=False)
    parser.add_argument("--dir", help="remote dir to cd in", required=False)

    parser.add_argument(
        "-u",
        "--unique",
        help="create a session without a timestamp",
        required=False,
        default=False,
        action="store_true",
    )

    group2 = parser.add_argument_group("tmux options")
    # synchronize
    group2.add_argument(
        "--sync", help="synchronize panes", required=False, action="store_true"
    )

    # tiled
    group2.add_argument(
        "--tiled", help="spread panes evenly", required=False, action="store_true"
    )

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
        "--debug", help="debug mode", required=False, default=False, action="store_true"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Set to verbose mode",
        required=False,
        default=False,
        action="store_true",
    )

    args = parser.parse_args()

    return args


def get_config_file(args):

    if args.config_file:
        # do not use abspath here
        # it does not work with single quotes
        config_file = args.config_file

        # relative path to ~
        if re.match("^~\/", config_file):
            homedir = os.path.abspath(os.getenv("HOME"))
            file_path = os.path.abspath(config_file.replace("~", homedir))
        # relative or absolute path
        elif re.match("^\.\/", config_file) or re.match("^\/", config_file):
            file_path = os.path.abspath(config_file)
        # just a filename without path
        else:
            file_path = os.path.abspath("./" + config_file)

    else:
        # search paths
        config_dirs_found = []

        for path in args.config_dirs.split(","):
            if os.path.exists(path):
                config_dirs_found.append(os.path.abspath(path))

        if not len(config_dirs_found):
            sys.exit(f"No config dirs found.")

        print(f"Browse '{args.config_dirs}' directories...")

        config_files = []
        for path in config_dirs_found:
            path = path.rstrip("/")
            config_files += glob.glob(f"{path}/*.yml")

        if not len(config_files):
            sys.exit(f"No config files found!")

        config_files.sort()

        if len(config_files) == 1:
            file_path = config_files[0]
        else:
            questions = [
                inquirer.List(
                    "select_path",
                    message=f"Select config file:",
                    choices=config_files,
                ),
            ]
            answers = inquirer.prompt(questions)
            file_path = answers["select_path"]

    return file_path


def get_yaml_config(file_path):
    # read the yaml file
    with open(file_path) as file:

        if re.search(".+\.ya?ml$", file_path):
            try:
                yaml_config = yaml.load(file, Loader=yaml.SafeLoader)
            except yaml.YAMLError as e:
                print(e)
                sys.exit("Exception in parsing yaml file " + file_path + "!")
        else:
            sys.exit("{} file not supported!".format(file_path))

    return yaml_config


def select_sections(yaml_config, section_name="session"):
    questions = [
        inquirer.Checkbox(
            "selected",
            message=f"Select {section_name}:",
            choices=yaml_config.keys(),
        ),
    ]
    answers = inquirer.prompt(questions)
    sections = answers["selected"]

    for section_name in sections:
        if not section_name in yaml_config.keys():
            print(f"{section_name} not found!")
            sys.exit()

    return sections


def natural_sort(l):

    convert = lambda text: int(text) if text.isdigit() else text.lower()

    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(l, key=alphanum_key)


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))
