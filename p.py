#!/usr/bin/env python3
from dprojectstools.commands import command, CommandsManager
from dprojectstools.secrets import SecretsManager
from dprojectstools.git import GitManager
from dprojectstools.editor import Editor
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
    # publish
    myenv = os.environ.copy()
    myenv["TWINE_PASSWORD"] = secrets.get("PYPI_AUTH_TOKEN")
    subprocess.run("py -m twine upload dist/*", env = myenv)

@command("Edit license", index = 20)
def edit():
    #editor = Editor()
    #editor.editFile("LICENSE")
    editor = Editor()
    editor.editText("hello world\nhow are you")

# execute
commandsManager = CommandsManager()
commandsManager.register()
commandsManager.register(GitManager())
commandsManager.execute(sys.argv)
