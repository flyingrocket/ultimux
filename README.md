# ultimux

## Description

Start tmux sessions based on yaml config.

## Installation

Install tmux, e.g. in Ubuntu:
```
sudo apt install tmux
```

Install pip packages:
```bash
pip install -r requirements.txt
```

## Usage

See -h for options

```bash
./ultimux.wrapper.py -h
```

## Examples

Create a session with 3 windows, override setup for widow 3. Set default ssh options. Overwrite options for some servers.
```
./ultimux.wrapper.py -c ./example.ssh.yml -s ssh_yml_full -i
```

Ssh into 2 machines and synchronize:
```
./ultimux.wrapper.py -c ./example.ssh.yml -s ssh_yml_minimal 
```
