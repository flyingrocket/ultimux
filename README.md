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

Create a session with 3 windows, last one has different setup:
```
./wrapper.yaml.py -c example.sessions.yml -s my_yaml_test2 -i     
```

Ssh into multiple machines and synchronize:
```
/wrapper.yaml.py -c example.synchronize.yml -s my_yaml_test -i -y 
```