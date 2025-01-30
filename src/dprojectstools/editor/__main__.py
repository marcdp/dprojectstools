import sys
from typing import Annotated
from dprojectstools.editor import Editor
from dprojectstools.commands import command, Argument, Flag, CommandsManager

# main
@command("Simple file editor")
def edit( filename: Annotated[str,  Argument("PATH")] = ""):
    editor = Editor()
    return editor.editFile(filename)

# main
if __name__ == "__main__":
    commandsManager = CommandsManager()
    commandsManager.register()
    commandsManager.execute(sys.argv)
