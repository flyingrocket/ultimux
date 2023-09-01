#!/usr/bin/env python3

import datetime
import getpass
import glob
import inquirer
import jinja2
import os
import re
import sys
import tempfile
import yaml

from iterfzf import iterfzf
from natsort import natsorted

# -----------------------------------------------
# Class
# -----------------------------------------------
class App:
    def __init__(self, args):

        self.appname = "utmx"
        self.args = args
        self.datestamp = "{:%Y-%m-%d_%H%M%S}".format(datetime.datetime.now())
        self.homedir = os.path.abspath(os.getenv("HOME"))
        self.run_username = getpass.getuser()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_time = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        self.tmux_name = f"{self.appname}_{self.datestamp}"

        # get configuration for utmx app
        self.app_config = self.get_app_config_yaml()

    def get_app_config_yaml(self):
        default_config_file_path = f"{self.script_dir}/ultimux.yml"
        config = self.read_yaml_config(default_config_file_path)

        custom_config_file_path = os.path.expanduser("~/.ultimux/ultimux.yml")
        if os.path.isfile(custom_config_file_path):

            custom_config = self.read_yaml_config(custom_config_file_path)

            if custom_config:
                config = config | custom_config

        return config

    def get_cli_config_file(self):

        args = self.args
        app_config = self.app_config

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

            for path in app_config["config_dirs"]:

                path = os.path.abspath(os.path.expanduser(path))

                if os.path.exists(path):
                    config_dirs_found.append(path)

            if not len(config_dirs_found):
                sys.exit(f"No config dirs found.")

            print(f"Browse {','.join(app_config['config_dirs'])} directories...")

            config_files = []

            config_file_pattern = f"*.{args.subcommand}.yml"

            for path in config_dirs_found:

                config_files += glob.glob(f"{path}/{config_file_pattern}")

            if not len(config_files):
                sys.exit(
                    f"No config files found matching pattern '{config_file_pattern}'!"
                )

            config_files.sort()

            if len(config_files) == 1:
                file_path = config_files[0]
            else:
                file_path = iterfzf(
                    config_files,
                    multi=False,
                    exact=True,
                    prompt="Select a config file:",
                )

        if not os.path.exists(file_path):
            sys.exit(f"Config file '{file_path}' not found!")

        return file_path

    def read_yaml_config(self, file_path):
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

    def select_sections(self, yaml_config, section_name="session", multi_select=True):

        sections_available = yaml_config.keys()

        sections = iterfzf(
            sections_available,
            multi=multi_select,
            exact=True,
            prompt="Select a section:",
        )

        if type(sections) == str:
            sections = [sections]

        for section_name in sections:
            if not section_name in yaml_config.keys():
                print(f"{section_name} not found!")
                sys.exit()

        return sections

    def is_valid_hostname(self, hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]  # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))


class GenApp(App):
    def get_session_config(self, session_name):

        args = self.args

        yaml_config = self.read_yaml_config(self.get_cli_config_file())

        if args.flatten:
            server_groups = yaml_config["groups"]
        else:
            server_groups = self.select_sections(yaml_config["groups"], "group")

        # -----------------------------------------------
        # Select hostnames
        # -----------------------------------------------
        choices_list = []
        for server_group in server_groups:
            for item in yaml_config["groups"][server_group]:

                description = ""

                if isinstance(item, dict):
                    hostname = item["hostname"]
                    if "description" in item:
                        description = item["description"]
                else:
                    hostname = item.rstrip(" ")
                if not self.is_valid_hostname(hostname) or hostname[-1] == ".":
                    sys.exit(f"Illegal hostname: '{hostname}'")

                choices_list.append(f"{hostname}; {description}")

        # remove empty
        choices_list = list(filter(None, choices_list))

        # sort
        choices_list = natsorted(choices_list)

        hostnames0 = iterfzf(
            choices_list,
            multi=True,
            exact=True,
            prompt="Select (multiple with tab/shift+tab) server(s):",
        )

        if type(hostnames0) == str:
            hostnames0 = [hostnames0]

        if not len(hostnames0):
            sys.exit("Select a host!")

        if len(hostnames0) > 9:
            sys.exit("Max number is 9!")

        hostnames = []
        for entry in hostnames0:
            hostnames.append(entry.split(";")[0].strip())

        # -----------------------------------------------
        # Create template
        # -----------------------------------------------
        session_name
        data = {}
        data["hostnames"] = hostnames
        data["session_name"] = session_name
        data["created_by"] = self.run_username
        data["timestamp"] = self.script_time

        if args.shell:
            data["shell_cmd"] = args.shell
        if args.dir:
            data["directory"] = args.dir
        data["synchronize"] = args.sync
        data["tiled"] = args.tiled

        template_file = "generated_config.j2"
        templateLoader = jinja2.FileSystemLoader(searchpath=self.script_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(template_file)
        config = template.render(
            data
        )  # this is where to put args to the template renderer

        # remove blank lines
        config = "".join([s for s in config.splitlines(True) if s.strip("\r\n")])
        if args.debug:
            print(config)
            sys.exit()

        # create temp file
        tmp_file = tempfile.NamedTemporaryFile(suffix=".yml", delete=False)
        print(f"Write config to {tmp_file.name}...")

        # Open the file for writing.
        with open(tmp_file.name, "w") as f:
            f.write(config)

        return self.read_yaml_config(tmp_file.name)[session_name]


class RunApp(App):
    def get_session_config(self, session_name):

        yaml_config = self.read_yaml_config(self.get_cli_config_file())

        if not session_name:
            session_name = self.select_sections(yaml_config, "session", False)[0]

        if not session_name:
            sys.exit("Illegal session name!")

        return yaml_config[session_name]
