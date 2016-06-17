#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

def morning(self):
      response = 'Good morning ' + self.adminName + ' it is ' + self.time() + '\n\n'
      response += self.weather() + '\n\n'
      response += self.word_of_the_day() + '\n\n'
      #response += self.expenses_remaining() + '\n\n'
      response += self.news()
      return response

def time(self):
    return datetime.datetime.now().strftime('%I:%M %p')

def command_list(self):
    response = "Available commands:\n"

    for key, val in self.commandList:
        response += key + "\n"
    print response
    return response
    
def update_self(self):
    # pull from git
    directory = self.dir
    g = git.cmd.Git(directory)
    g.pull()
    
    # Update owner of files to prevent permission issues
    uid = pwd.getpwnam("pi").pw_uid
    gid = grp.getgrnam("pi").gr_gid
    for root, dirs, files in os.walk(directory):  
      for momo in dirs:  
        os.chown(os.path.join(root, momo), uid, gid)
      for momo in files:
        os.chown(os.path.join(root, momo), uid, gid)
    
    # Check if the file has changed.
    # If so, restart the application.
    if os.path.getmtime(__file__) > self.last_mtime:
        # Restart the application (os.execv() does not return).
        os.execv(__file__, sys.argv)
        
    return 'Updated to version: ' + str(self.last_mtime)