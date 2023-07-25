#! /usr/bin/env python3

import os
import sys
import tempfile

from jinja2 import Template

# -----------------------------------------------
# Include functions
# -----------------------------------------------
from _helpers import *
from _ultimux import *

# -----------------------------------------------
# Arguments
# -----------------------------------------------
config_dirs = f"/etc/{appname}/servers.d/,{homedir}/.{appname}/servers.d/"
args = get_argparse(description="Ultimux ssh wrapper", config_dirs=config_dirs)

# -----------------------------------------------
# Get config file
# -----------------------------------------------
file_path = get_config_file(args)

if not os.path.exists(file_path):
    sys.exit(f'Config file "{file_path}" not found!')

print(f"Use {file_path}...")

# -----------------------------------------------
# Read config file
# -----------------------------------------------
yaml_config = get_yaml_config(file_path)

# -----------------------------------------------
# Get cluster name
# -----------------------------------------------
if "cluster" in yaml_config:
    server_groups = select_sections(yaml_config, "cluster")
else:
    server_groups = select_sections(yaml_config, "servergroups")


# -----------------------------------------------
# Select hostnames
# -----------------------------------------------
choices_list = []
for server_group in server_groups:
    for item in yaml_config[server_group]:

        description = ""

        if isinstance(item, dict):
            hostname = item["hostname"]
            description = item["description"]
        else:
            hostname = item.rstrip(" ")
        if not is_valid_hostname(hostname) or hostname[-1] == ".":
            sys.exit(f"Illegal hostname: '{hostname}'")

        choices_list.append(f"{hostname}; {description}")

# remove empty
choices_list = list(filter(None, choices_list))
# sort
choices_list = natural_sort(choices_list)

questions = [
    inquirer.Checkbox(
        "selected",
        message=f"Select server(s). Use spacebar",
        choices=choices_list,
    ),
]

answers = inquirer.prompt(questions)

selected_hostnames_tmp = []

# select multiple
if isinstance(answers["selected"], list):
    selected_hostnames_tmp = answers["selected"]
else:
    selected_hostnames_tmp.append(answers["selected"])

if not len(selected_hostnames_tmp):
    sys.exit("Select a host!")

if len(selected_hostnames_tmp) > 9:
    sys.exit("Max number is 9!")

selected_hostnames = []
for entry in selected_hostnames_tmp:
    selected_hostnames.append(entry.split(";")[0].strip())

# -----------------------------------------------
# Create template
# -----------------------------------------------
data = {}
templates = {}

data["hostnames"] = selected_hostnames
data["session_name"] = ultimux_session_name

if args.shell:
    data["shell_cmd"] = args.shell
if args.dir:
    data["directory"] = args.dir
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
{%- if directory %}
    dir: '{{ directory -}}'
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

# create temp file
tmp_file = tempfile.NamedTemporaryFile(suffix=".yml", delete=False)
print(f"Write config to {tmp_file.name}...")

# Open the file for writing.
with open(tmp_file.name, "w") as f:
    f.write(config)

# -----------------------------------------------
# Run ultimux
# -----------------------------------------------
ultimux_options = []

for argument in ["sync", "tiled"]:

    # check if argument exists
    if getattr(args, argument):
        ultimux_options.append(f"--{argument}")

ultimux_options = " ".join(ultimux_options)

interactive = "-i" if args.interactive else ""

cmd = f"{dname}/ultimux.py -c {tmp_file.name} -s {ultimux_session_name} {ultimux_options} {interactive}"
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
