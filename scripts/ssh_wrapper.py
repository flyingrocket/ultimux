#! /usr/bin/env python3

import argparse
import getpass
import glob
import inquirer
from jinja2 import Template
import os
import re
import sys
import yaml

# -----------------------------------------------
# Variables
# -----------------------------------------------
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

generic_session_name = "tmux_ssh_wrapper"
homedir = os.path.abspath(os.getenv("HOME"))
script_user = getpass.getuser()
cache_base_dir = f"/tmp/{script_user}"

# -----------------------------------------------
# Arguments
# -----------------------------------------------
parser = argparse.ArgumentParser(description="Ultimux ssh wrapper...")

parser.add_argument("-c", "--config-file", help="servers (txt) file", required=True)

parser.add_argument("--shell", help="remote command to run", required=False)

group2 = parser.add_argument_group("tmux options")

# synchronize
group2.add_argument(
    "--sync", help="synchronize panes", required=False, action="store_true"
)

# tiled
group2.add_argument(
    "--tiled", help="spread panes evenly", required=False, action="store_true"
)

# interactive
parser.add_argument(
    "-i",
    "--interactive",
    help="Set to verbose mode",
    required=False,
    default=False,
    action="store_true",
)

# debug
parser.add_argument(
    "--debug",
    help="Debug mode",
    required=False,
    default=False,
    action="store_true",
)

# verbose
parser.add_argument(
    "-v",
    "--verbose",
    help="Set to verbose mode",
    required=False,
    default=False,
    action="store_true",
)

args = parser.parse_args()

# -----------------------------------------------
# Functions
# -----------------------------------------------
def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


# -----------------------------------------------
# Get server file
# -----------------------------------------------
if not args.config_file:
    sys.exit()

server_file = os.path.abspath(args.config_file)

if not re.match("^.*txt$", server_file):
    sys.exit("Server file must be a txt file!")

server_fh = open(server_file, "r")
hostname_list = server_fh.read().split("\n")
hostname_list = list(filter(None, hostname_list))
for hostname in hostname_list:
    hostname = hostname.rstrip(" ")
    if not is_valid_hostname(hostname) or hostname[-1] == ".":
        sys.exit(f"Illegal hostname: '{hostname}'")
    # if re.search(" ", line):
    #     sys.exit(f"Illegal hostname. May not contain spaces: '{line}'")
    # print(line)
server_fh.close()

questions = [
    inquirer.Checkbox(
        "selected",
        message=f"Select server(s). Use spacebar",
        choices=hostname_list,
    ),
]

answers = inquirer.prompt(questions)

selected_hostnames = []

# select multiple
if isinstance(answers["selected"], list):
    selected_hostnames = answers["selected"]
else:
    selected_hostnames.append(answers["selected"])

if not len(selected_hostnames):
    sys.exit("Select a host!")

# -----------------------------------------------
# Create template
# -----------------------------------------------
data = {}
templates = {}

data["hostnames"] = selected_hostnames
data["session_name"] = generic_session_name

if args.shell:
    data["shell_cmd"] = args.shell
data["synchronize"] = args.sync
data["tiled"] = args.tiled

template = """---
{{ session_name }}:
{%- if tiled %}
  layout: 'tiled'
{%- endif %}
{%- if synchronize %}
  synchronize: true
{%- else %}
  synchronize: false
{%- endif %}
  panes:
{%- for hostname in hostnames %}
  - ssh:
      server: {{ hostname }}
{%- if shell_cmd %}
    shell: '{{ shell_cmd -}}'
{% endif %}
{% endfor -%}
"""

j2_template = Template(template)
config = j2_template.render(data)

# remove blank lines
config = text = "".join([s for s in config.splitlines(True) if s.strip("\r\n")])
if args.debug:
    print(config)
    sys.exit()

ultimux_conffile = f"/tmp/{script_user}/{generic_session_name}.yml"

f = open(ultimux_conffile, "w")
f.write(config)
f.close()

# -----------------------------------------------
# Run ultimux
# -----------------------------------------------
ultimux_options = []

for argument in ["sync", "tiled"]:

    # check if argument exists
    if getattr(args, argument):
        ultimux_options.append(f"--{argument}")

ultimux_options = " ".join(ultimux_options)

cmd = f"{dname}/../ultimux.py -c {ultimux_conffile} -s {generic_session_name} {ultimux_options}"
if args.verbose:
    print(cmd)

if args.interactive:
    print(config)
    print()
    print(cmd)
    print()
    answ = input("Continue? (y/N)")
    if answ.upper() == "Y":
        os.system(cmd)
else:
    os.system(cmd)
