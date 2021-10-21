# ultimux

## Description

Start tmux sessions based on yaml config. A configuration (yaml) file may be passed to the script with the -c flag. Alternatively, you can browse and interact with ultimux with the -b flag. In that case, yaml files are expected to reside in ~/.ultimux/conf.d or /etc/ultimux/conf.d.

## Installation

Install tmux, e.g. in Ubuntu:

```bash
sudo apt install tmux
```

Install pip packages:

```bash
pip install -r requirements.txt
```

## Usage

See -h for options:

```bash
./ultimux.wrapper.py -h
```

Output:

```text
usage: ultimux [-h] [-s SESSION] [--sync] [--tiled] (-c CONFIGFILE | -b | -d CONFIGDIR) [-l] [-i] [--debug]

Ultimux - tmux wrapper

optional arguments:
  -h, --help            show this help message and exit
  -s SESSION, --session SESSION
                        select session
  --sync                synchronize panes
  --tiled               spread panes evenly
  -c CONFIGFILE, --configfile CONFIGFILE
                        config yaml file
  -b, --browse          browse through all available configs
  -d CONFIGDIR, --configdir CONFIGDIR
                        browse through given config dir
  -l, --list            list sessions
  -i, --interactive     interactive mode
  --debug               debug mode
```

## Examples

See examples in conf.d/ dir.

Run session "full_layout" from file ./conf.d/example.ssh.yml

```bash
./ultimux.wrapper.py -c ./conf.d/example.ssh.yml -s full_layout -i
```
