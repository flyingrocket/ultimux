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
./ultimux.wrapper.py -c ./example.ssh.yml -s ssh_yml_full -i
```

Ssh into 2 machines and synchronize:
```
./ultimux.wrapper.py -c ./example.ssh.yml -s ssh_yml_minimal 
```

# Layout
```
     even-horizontal
             Panes are spread out evenly from left to right across the window.

     even-vertical
             Panes are spread evenly from top to bottom.

     main-horizontal
             A large (main) pane is shown at the top of the window and the remaining panes are spread from left to right in the leftover space at the bottom.  Use the
             main-pane-height window option to specify the height of the top pane.

     main-vertical
             Similar to main-horizontal but the large pane is placed on the left and the others spread from top to bottom along the right.  See the main-pane-width window option.

     tiled   Panes are spread out as evenly as possible over the window in both rows and columns.

```
