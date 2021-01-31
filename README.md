# Installation

Install tmux
```
sudo apt install tmux
```

# Use class in a python script

```
./wrapper.python.py
```

# Use the yaml wrapper

Create a session with 3 windows, override setup for widow 3. Set default ssh options. Overwrite options for some servers.
```
./wrapper.yaml.py -c ./example.ssh.yml -s ssh_yml_full -i
```

Ssh into 2 machines and synchronize:
```
./wrapper.yaml.py -c ./example.ssh.yml -s ssh_yml_minimal 
```