#!/usr/bin/env python3
from dprojectstools.commands import command, CommandsManager
from dprojectstools.secrets import SecretsManager 
import os
import subprocess
import sys

# controllers
@command("Status", index = 90)
def git_status():
    return subprocess.run("git status --short")

@command("Add")
def git_add():
    return subprocess.run("git add . --all")

@command("Commit")
def git_commit():
    return subprocess.run("git commit -a")

# execute
commandsManager = CommandsManager()
commandsManager.register()
commandsManager.execute(sys.argv)



# git
#function menuitem_git_pull --index 90
#    git pull 
#end 
#function menuitem_git_status
#    git status --short
#end 
#function menuitem_git_add
#    git add . --all
#end
#function menuitem_git_commit
#    read --prompt "Enter changes: " GIT_COMMIT_MESSAGE
#    git commit -a -m "$GIT_COMMIT_MESSAGE"
#end
## 
#function menuitem_git_push 
#    git push
#end
