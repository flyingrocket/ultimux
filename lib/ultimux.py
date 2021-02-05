#! /usr/bin/env python3

import datetime, os, re, subprocess, sys

class Ultimux:

    #########################################
    # Application properties
    #########################################    
    tmux_cmds = []

    session_config = {}
    
    session_name = ''

    app_name = 'ultimux'

    version = '1.0'

    #########################################
    # Dynamic properties
    #########################################
    
    debug = False

    focus = '0.0'

    synchronize = False

    validated_destinations = []

    def __init__(self, session_config, session_name = ''):

        #########################################
        # Check if tmux is installed
        ######################################### 
        try:    
            subprocess.call(['tmux', '-V'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:    
            print ('Tmux is not installed...')   
        
        #########################################
        # Set session_config
        #########################################
        datestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.now())
        
        self.session_config = session_config
        
        if not session_name == '':
            self.session_name = session_name + '_' + datestamp
        else:
            self.session_name = self.app_name + '_' + datestamp
        
        # validate session name
        if re.search('(\.|\:|\ )+',self.session_name):
            self.fail('Session name may not contain .: or spaces!')
        
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

    def fail(self, message = ''):
        print(message)
        sys.exit(1)

    def set_debug(self, debug):

        if not type(debug) == bool:
            self.fail('Directive debug must be boolean!')

        self.debug = debug
        
    def set_focus(self, focus):

        if not re.match('^[0-9]+\.[0-9]+$', focus):
            self.fail('Focus must be {number}.{number}!')

        self.focus = focus

    def set_interactive(self, interactive):

        if not type(interactive) == bool:
            self.fail('Directive interactive must be boolean!')

        self.interactive = interactive

    def create(self):
           
        session_config = self.session_config
        # ---------------------------------------
        # Global options
        # ---------------------------------------       
        if session_config.get('interactive'):
            self.set_interactive(session_config.get('interactive'))

        if session_config.get('focus'):
            self.set_focus(session_config.get('focus'))
       
        # ---------------------------------------
        # Create window if required
        # ---------------------------------------
        # check if window
        if not session_config.get('windows'):
            session_config['windows'] = []
            session_config['windows'].append({'name':'ultimux'})

        # ---------------------------------------
        # Iterate windows
        # ---------------------------------------
        # window counter
        i = 0
        
        for window in session_config['windows']:

            # ---------------------------------------
            # Set window name
            # ---------------------------------------
            if 'name' in window.keys():
                window_name = window['name']
            elif 'ssh' in window.keys():
                window_name = window['ssh']
            else:
                window_name = window['win{}'.format(i)]

            # ---------------------------------------
            # Create tmux session/window
            # ---------------------------------------
            # first window is alreay set, skip
            if i > 0:
                self.tmux_cmds.append("tmux new-window -t '{}' -n '{}' ".format(self.session_name, window_name))
            else:
                # first loop: create a session + window with -n option
                self.tmux_cmds.append("tmux new-session -d -A -s {} -n '{}'".format(self.session_name, window_name))
            
            # pane counter
            ii = 0

            # ---------------------------------------
            # Default to global section
            # ---------------------------------------
            # global sections
            if not window.get('sections'):
                sections = session_config['sections']
            else:
                sections = window['sections']

            # ---------------------------------------
            # Iterate sections
            # ---------------------------------------
            for section in sections:

                if ii > 0:
                    self.tmux_cmds.append("tmux split-window -f -t '{}'".format(self.session_name))


                # if only a command or list is specified
                if type(section) != dict:

                    value = section

                    section = {}
                    section['cmds'] = value
            
                # ---------------------------------------
                # Split section (row)
                # ---------------------------------------
                if section.get('cmds') and isinstance(section['cmds'], list):
                   
                    # split counter
                    iii = 0
                
                    for command in section['cmds']: 
                        
                        if iii > 0:
                            self.tmux_cmds.append("tmux split-window -h -t '{}'".format(self.session_name))
                        
                        target = self.session_name + ':' + str(i) + '.' + str(ii)

                        self.parse_command(command, section, window, target)
                        
                        iii += 1
                        ii += 1
                            
                # ---------------------------------------
                # Regular section (row)
                # ---------------------------------------
                else:
                    if section.get('cmds'):
                        command = section['cmds']
                    else:
                        # e.g. if only ssh is a key
                        command = ''

                    target = self.session_name + ':' + str(i) + '.' + str(ii)

                    self.parse_command(command, section, window, target)
            
                    ii += 1 # pane
            
            if 'synchronize' in window.keys():
                if window.get('synchronize'):        
                    self.tmux_cmds.append("tmux set-option -t '{}' synchronize-panes on".format(self.session_name))
            elif session_config.get('synchronize'):
                self.tmux_cmds.append("tmux set-option -t '{}' synchronize-panes on".format(self.session_name))

            layout = ''

            if 'layout' in window.keys():
                if window.get('layout'):        
                    layout = window.get('layout')
            elif session_config.get('layout'):
                    layout = session_config.get('layout')
            
            # layout
            if not layout == '':
                self.tmux_cmds.append('tmux select-layout {}'.format(layout))
            
            i += 1 # window


        # ---------------------------------------
        # Set options and attach
        # ---------------------------------------
        self.tmux_cmds.append('tmux set-option -g status-style bg=blue')

        # support 256 colors
        self.tmux_cmds.append("tmux set -g default-terminal 'screen-256color'")

        # bind key for synch
        # self.tmux_cmds.append('tmux set -g bind-key a set-window-option synchronize-panes\; display-message "synchronize-panes is now #{?pane_synchronized,on,off}"')


        # set focus
        self.tmux_cmds.append("tmux select-pane -t '{}:{}'".format(self.session_name, self.focus))
        self.tmux_cmds.append("tmux attach -t '{}:{}'".format(self.session_name, self.focus))
        
    def parse_command(self, command, section, window, target): 

        session_config = self.session_config
        # ---------------------------------------
        # Get ssh config options
        # ---------------------------------------
        ssh_options = {}
        for directive in ['user', 'server', 'login']:

            ## TODO clean this up
            # directive in section gets priority
            if type(section) == dict and section.get('ssh') and section['ssh'].get(directive):
                ssh_options[directive] = section['ssh'].get(directive)
            # directive in window 
            elif type(window) == dict and window.get('ssh') and window['ssh'].get(directive):
                ssh_options[directive] = window['ssh'].get(directive)
            # directive in session_config
            elif session_config.get('ssh') and session_config['ssh'].get(directive):
                ssh_options[directive] = session_config['ssh'].get(directive)
        # ---------------------------------------
        # Compile ssh commands
        # ---------------------------------------
        if ssh_options:

            if not ssh_options.get('server'):
                self.fail('Ssh server must be specified!')

            if ssh_options.get('user'):
                destination = '{}@{}'.format(ssh_options.get('user'), ssh_options.get('server'))
            else:
                destination = ssh_options.get('server')

            options = ['-o ConnectTimeout=0']
            options = []

            # compile ssh command 
            ssh_command = 'ssh {}{}'.format(' '.join(options), destination)
            

            # ---------------------------------------
            # Check connectivity
            # ---------------------------------------
            if not destination in self.validated_destinations and not self.debug:

                # first check
                if not len(self.validated_destinations):
                    print('Check ssh connectivity...')

                subcommand = '{} {}'.format(ssh_command, 'echo ok') 
                try:    
                    # split string into pieces
                    subprocess.check_output(subcommand.split(), stderr=subprocess.STDOUT)  
                except subprocess.CalledProcessError as e:
                    # print(e)
                    print(destination.ljust(60, '.'), 'FAIL')
                    self.fail('Failed connectivity check: {}'.format(destination))  

                print(destination.ljust(60, '.'), 'OK')
                self.validated_destinations.append(destination)

            # ---------------------------------------
            # Ssh remote or login 
            # ---------------------------------------
            # run ssh command remotely or login
            seperator = ''
            if ssh_options.get('login'):
                seperator = ';'

            # add ssh prefix to command 
            command = '{}{} {}'.format(ssh_command, seperator, command)

        # ---------------------------------------
        # String of commands
        # ---------------------------------------
        tcommands = command.split(';')
        
        for tcommand in tcommands:
            tcommand = tcommand.strip(' ')

            if self.debug:
                tcommand = '# ' + tcommand
                enter = ''
            else:
                enter = 'C-m'

            self.tmux_cmds.append("tmux send-keys -t " + target + " '" + tcommand + "' " + enter)
        
    def out(self):
        print()

        for tcomm in self.tmux_cmds:
            print(tcomm)
    
    def exec(self):
        
        if self.interactive:
            
            self.out()

            print()
            print('Execute these commands? [Y/n]')
            answer = input()

            if answer != 'Y' and answer != '':
                self.fail()

        for subcommand in self.tmux_cmds:
            os.system(subcommand)

            ## TODO: Does not work with spaces or semi-colons, etc
            # print(subcommand.split()) 
            # try:    
            #     # split the subcommand into a list
            #     subprocess.check_output(subcommand.split(), stderr=subprocess.STDOUT)  
            # except subprocess.CalledProcessError as e:
            #     print(e)
            #     self.fail('Failed tmux command!')  
        