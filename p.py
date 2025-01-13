#!/usr/bin/env python3
from dprojectstools.commands import command, CommandsManager
import subprocess
import sys
import os
import shutil


# prepare environment
# pip install --upgrade build
# py -m pip install --upgrade twine

# increase version
# ... manuallly

# build
# py -m build

# deploy in test server
# py -m twine upload --repository testpypi dist/*

# install from test
# py -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U dprojects_xmenu

# deploy in prod server
# py -m twine upload dist/*

# install from test
# py -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U xmenu


# controllers
@command("Package build", index = 10)
def package_build():
    shutil.rmtree("./dist")
    subprocess.run("py -m build")

@command("Package build and publish")
def package_build_and_publish():
    # build
    package_build()
    subprocess.run("py -m twine upload dist/*")


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
