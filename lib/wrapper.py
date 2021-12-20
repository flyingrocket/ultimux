#! /usr/bin/env python3

import glob
import inquirer
import os
import re
import sys
import yaml


def get_config_file(args, default_browse_dirs):
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

    elif args.browse:
        # search paths

        config_dirs_found = []

        for path in args.browse_dirs.split(","):
            if os.path.exists(path):
                config_dirs_found.append(os.path.abspath(path))
            else:
                # only fail if specific paths are given
                if not args.browse_dirs == default_browse_dirs:
                    sys.exit(f"Config dir {path} not found!")

        print(f"Browse '{args.browse_dirs}' directories...")

        if not len(config_dirs_found):
            sys.exit(f"No config dirs found.")

        config_files = []
        for path in config_dirs_found:
            path = path.rstrip("/")
            config_files += glob.glob(f"{path}/*.yml")

        if not len(config_files):
            sys.exit(f"No config files found!")

        questions = [
            inquirer.List(
                "select_path",
                message=f"Select config file:",
                choices=config_files,
            ),
        ]
        answers = inquirer.prompt(questions)
        file_path = answers["select_path"]
    else:
        sys.exit()

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


def get_section(yaml_config, section_name="session"):
    questions = [
        inquirer.List(
            "selected",
            message=f"Select {section_name}:",
            choices=yaml_config.keys(),
        ),
    ]
    answers = inquirer.prompt(questions)
    section_name = answers["selected"]

    if not section_name in yaml_config.keys():
        print(f"{section_name} not found!")
        sys.exit()

    return section_name


def natural_sort(l):

    convert = lambda text: int(text) if text.isdigit() else text.lower()

    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(l, key=alphanum_key)
