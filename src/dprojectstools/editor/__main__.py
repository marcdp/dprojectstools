import sys
from typing import Annotated
from dprojectstools.editor import Editor
from dprojectstools.commands import command, Argument, Flag, CommandsManager

def optional():
    return 123

# main
#def setup_openvpn_connect():    
@command("Edit file", 
         examples = [
             "Example 1",
             "Example 2",
             "Example 3"
         ])
def edit(
        filename: Annotated[str,  Argument("PATH", "xxx")],
        flag0:    Annotated[str,  Flag('a', "Flag a", "dir")],
        flag1:    Annotated[bool, Flag('b', "Flag b")] = False,
        flag2:    Annotated[int,  Flag('c', "Flag c","count")] = 123,
    ):
    print("AAAAA")
    #if (len(argv) == 1):
    #    # new file
    #    editor = Editor()
    #    return editor.editFile("")
    #    # try read from stdin
    #    # ...
    #
    #elif (len(argv) > 1):
    #    # existing file
    #    editor = Editor()
    #    return editor.editFile(argv[1])
@command("Edit aaa")
def edit_aa(
        filename: Annotated[str,  Argument("path")] = "",
        flag1:    Annotated[bool, Flag('f', "Flag 1")] = False,
    ):
    print("AAAAA")

@command("Edit aaa")
def edit_bb(
        filename: Annotated[str,  Argument("path")] = "",
        flag1:    Annotated[bool, Flag('f', "Flag 1")] = False,
    ):
    print("AAAAA")


# main
if __name__ == "__main__":
    commandsManager = CommandsManager()
    commandsManager.register()
    commandsManager.execute(sys.argv)
    #main(sys.argv)
