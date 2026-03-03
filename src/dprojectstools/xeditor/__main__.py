import sys
from typing import Annotated
from dprojectstools.xeditor import XEditor
from dprojectstools.commands import command, Argument, Flag, CommandsManager

# main
@command("Simple file editor")
def edit( filename: Annotated[str,  Argument("PATH")] = ""):
    xeditor = XEditor()
    return xeditor.editFile(filename)

# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(module = sys.modules[__name__])
    commandsManager.execute(sys.argv)
if __name__ == "__main__":
    main()






