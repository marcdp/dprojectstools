#!/usr/bin/env python3
from dprojectstools.commands import command, CommandsManager
import subprocess
import sys

# controllers
@command("Giet status", index = 90)
def git_status():
    return subprocess.run("git status --short")

@command("Git add")
def git_add():
    return subprocess.run("git add . --all")

@command("Git commit")
def git_commit():
    message = input("Enter changes: ")
    return subprocess.run("git commit -a -m \"{0}\"".format(message))

@command("Git push")
def git_push():
    return subprocess.run("git push")


# execute
commandsManager = CommandsManager()
commandsManager.register()
commandsManager.execute(sys.argv)
