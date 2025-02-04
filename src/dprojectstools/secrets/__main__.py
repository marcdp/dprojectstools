import sys
from typing import Annotated
from .secrets import SecretsManager
from dprojectstools.editor import Editor
from dprojectstools.commands import command, Argument, Flag, CommandsManager

# main
@command("Create secrets db")
def create(
        dbname: Annotated[str,  Argument("NAME")]
    ):
    secrets = SecretsManager(dbname, create = True)


@command("List secrets dbs")
def list():
    for db_name in SecretsManager.get_db_names():
        print(db_name)

@command("Edit secrets dbs")
def edit(
        dbname: Annotated[str,  Argument("NAME")] = ""
    ):
    secrets = SecretsManager(dbname)
    secrets.edit()


# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(module = sys.modules[__name__])
    commandsManager.execute(sys.argv, default_show_help = True)
if __name__ == "__main__":
    main()






