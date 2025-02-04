#!/usr/bin/env python3
from dprojectstools.commands import command, CommandsManager
from dprojectstools.secrets import SecretsManager
from dprojectstools.git import GitManager
from dprojectstools.editor import Editor
import subprocess
import sys
import os
import shutil

# # prepare environment:
# pip install --upgrade build
# py -m pip install --upgrade twine
#
# # increase version
# ... manuallly

# # build:
# py -m build
#
# # publish package to index
# py -m twine upload dist/*

# install as development package:
# pip install -e .


# secrets 
secrets = SecretsManager("dprojectstools")

# controllers
@command("Package build", index = 10)
def package_build():
    shutil.rmtree("./dist")
    subprocess.run("py -m build")

@command("Package build and publish")
def package_publish():
    # build
    package_build()
    # publish
    myenv = os.environ.copy()
    myenv["TWINE_PASSWORD"] = secrets.get("PYPI_AUTH_TOKEN")
    subprocess.run("py -m twine upload dist/*", env = myenv)

@command("Package install as development pacakge", index = 15)
def package_install():
    # install
    subprocess.run("pip install -e .")

# execute
commandsManager = CommandsManager()
commandsManager.register()
commandsManager.register(GitManager())
commandsManager.execute(sys.argv)
