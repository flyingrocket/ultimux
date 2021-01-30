#! /usr/bin/env python3

import datetime, os, re, subprocess, sys

class Ultimux:
        
    tmux_cmds = []

    config = {}
    
    session_name = ''

    app_name = 'ultimux'

    version = '1.0'

    focus = '0.0'

    synchronize = False

    def __init__(self, config, session_name = ''):

        #########################################
        # Check if tmux is installed
        ######################################### 
        try:    
            subprocess.call(['tmux', '-V'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:    
            print ('Tmux is not installed...')   
        
        #########################################
        # Set config
        #########################################
        datestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.now())
        
        self.config = config
        
        if not session_name == '':
            self.session_name = session_name + '_' + datestamp
        else:
            self.session_name = self.app_name + '_' + datestamp
        
        # validate session name
        if re.search('(\.|\:|\ )+',self.session_name):
            print('Session name may not contain .: or spaces!')
            sys.exit()
        
        #########################################
        # Set defaults
        #########################################
        self.tmux_cmds = []

        self.focus = '0.0'

        # echo commands before running 
        self.interactive = False

        # set unique session name 
        self.set_session_unique_id = True
        
        # sycnchronize panes
        self.synchronize = False
        
    def set_focus(self, focus):

        if not re.match('^[0-9]+\.[0-9]+$', focus):
            print('Focus must be {number}.{number}!')
            sys.exit()

        self.focus = focus

    def set_interactive(self, interactive):

        if not type(interactive) == bool:
            print('Directive interactive must be boolean!')
            sys.exit()

        self.interactive = interactive

    # def set_session_unique_id(self, set_session_unique_id):

    #     self.set_session_unique_id = set_session_unique_id

    def set_synchronize(self, synchronize):

        if not type(synchronize) == bool:
            print('Directive synchronize must be boolean!')
            sys.exit()

        self.synchronize = synchronize

    def create(self):
           
        config = self.config
        # print(config)
        
        # create a session, the first time you give the name of the first window with -n option
        self.tmux_cmds.append('tmux new-session -d -A -s ' + self.session_name + ' -n ' + list(self.config.keys())[0])
        
        # window counter
        i = 0

        for window in config.keys():
            
            # first window is alreay set, skip
            if i > 0:
                self.tmux_cmds.append('tmux new-window -n ' + window + ' -t ' + self.session_name)
            
            # pane counter
            ii = 0
            
            for command in config[window]['cmds']:
                
                if ii > 0:
                    self.tmux_cmds.append('tmux split-window -f -t ' + self.session_name)
            
                # split window vertically
                if isinstance(command, list):
                    
                    # split counter
                    iii = 0
                
                    for comm in command: 
                        
                        if iii > 0:
                            self.tmux_cmds.append('tmux split-window -h -t ' +self.session_name)
                        
                        target = self.session_name + ':' + str(i) + '.' + str(ii)
                        self.parse_command(comm, target)
                        
                        iii += 1
                        ii += 1
                            
                # no vertical split
                else:
                    #print('single')
                    comm = command
                    target = self.session_name + ':' + str(i) + '.' + str(ii)
                    self.parse_command(comm, target)
                    #print(comm)    
            
                    ii += 1
            i += 1

        if self.synchronize:        
            self.tmux_cmds.append('tmux set-option -t ' +self.session_name + ' synchronize-panes on')


        self.tmux_cmds.append('tmux select-pane -t ' +self.session_name + ':' + self.focus)
        self.tmux_cmds.append('tmux attach -t ' +self.session_name + ':' + self.focus)
        
    def parse_command(self, command, target): 
        
        # check if multiple commands are given
        commands = command.split(';')
        #print('commands')
        #print(commands)
        
        for comm in commands:
            comm = comm.strip(' ')
            enter = ''
            enter = 'C-m'
            self.tmux_cmds.append("tmux send-keys -t " + target + " '" + comm + "' " + enter)
        
    def out(self):
        for tcomm in self.tmux_cmds:
            print(tcomm)
    
    def attach(self):
        
        if self.interactive:
            
            self.out()

            print()
            print('Execute these commands? [Y/n]')
            answer = input()

            if answer != 'Y' and answer != '':
                sys.exit()

        for tcomm in self.tmux_cmds:
            os.system(tcomm)
            