#!/usr/bin/env python3
from dprojectstools.commands import command, CommandsManager
from dprojectstools.secrets import SecretsManager
import subprocess
import sys
import os
import shutil

# # prepare environment
# pip install --upgrade build
# py -m pip install --upgrade twine
#
# # increase version
# ... manuallly
#
# # build
# py -m build
#
# # publish package to index
# py -m twine upload dist/*


# secrets 
secrets = SecretsManager("dprojectstools")

# controllers
@command("Package build", index = 10)
def package_build():
    shutil.rmtree("./dist")
    subprocess.run("py -m build")

@command("Package build and publish")
def package_build_and_publish():
    # build
    package_build()
    #publish
    myenv = os.environ.copy()
    myenv["TWINE_PASSWORD"] = secrets.get("TWINE_PASSWORD")
    subprocess.run("py -m twine upload dist/*", env = myenv)

@command("Git status", index = 90)
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
