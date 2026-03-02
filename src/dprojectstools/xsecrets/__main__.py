import sys
import getpass
from typing import Annotated
from .xsecrets import XSecrets
from dprojectstools.commands import command, Argument, Flag, CommandsManager


# utils
def error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
def ask_password(confirm: bool = False) -> str:
    prompt = "Enter password: "
    result = getpass.getpass(prompt, echo_char="*")
    if confirm:
        prompt_confirm = "Confirm password: "
        result_confirm = getpass.getpass(prompt_confirm, echo_char="*")
        if result != result_confirm:
            error("Passwords do not match.")
            sys.exit(1)
    return result


# main
@command("Create secrets db")
def create(
        dbname: Annotated[str,  Argument("NAME")],
        password: Annotated[str,  Flag('p', "password")] = "",
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    if XSecrets.exists_db(dbname):
        if not force:
            confirm = input(f"Secrets db '{dbname}' already exists. Do you want to overwrite it? [y/n] ")
            if confirm.strip().lower() not in ("y", "yes"):
                error("Aborting creation.")
                return -1
        XSecrets.delete_db(dbname)
    XSecrets(dbname, password = password, create = True)


@command("List secrets dbs", alias=["list"])
def listcmd(
    dbname: Annotated[str,  Argument("NAME")] = None
    ):
    if dbname:
        if XSecrets.exists_db(dbname):
            secrets = XSecrets(dbname)
            for key in secrets.keys():
                print(key)
        else:
            error(f"Secrets db '{dbname}' not found.")
    else:
        for db_name in XSecrets.get_db_names():
            print(db_name)

@command("Edit secrets dbs")
def edit(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")] = ""
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    secrets = XSecrets(dbname)
    if key:
        secrets.edit_secret(key)
    else:
        secrets.edit()

@command("Get secret value from db")
def get(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")]
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    secrets = XSecrets(dbname)
    if secrets.exists(key):
        entry = secrets.get(key)
        print(entry.value)
    else:
        error(f"Secret '{key}' not found.") 
        return -1

@command("Set secret value from db")
def set(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")],
        value: Annotated[str,  Argument("VALUE")] = None,
        type_name: Annotated[str,  Flag('t', "type", alias="type")] = "",
        services: Annotated[str,  Flag('s', "services")] = "",
        description: Annotated[str,  Flag('d', "description")] = "",
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    interactive = sys.stdin.isatty() and value is None
    # if value is not provided, read from stdin or ask interactively
    if value is None:
        if sys.stdin.isatty():
            value1 = getpass.getpass(f"Enter secret value:   ", echo_char="*")
            value2 = getpass.getpass(f"Confirm secret value: ", echo_char="*")
            if value1 != value2:
                error("Aborting update: values do not match.")
                return -1
            value = value1
        else:
            value = sys.stdin.read()            
        value = value.rstrip("\n")
        if value == "":
            error("Aborting update: empty value.")
            return -1
    # ask for password if interactive and not provided
    password = ask_password()
    # init store
    secrets = XSecrets(dbname)
    # check if exists, will raise if not
    if secrets.exists(key) and not force:
        if not interactive:
            error(f"Secret '{key}' already exists. Use --force to overwrite it.")
            return -1
        confirm = input(f"Secret '{key}' already exists. Do you want to overwrite it? [y/n] ")
        if confirm.strip().lower() not in ("y", "yes"):
            error("Aborting update.")
            return -1
    # set    
    secrets.set(key, 
                value, 
                type = type_name, 
                services = [s.strip() for s in services.split(",") if s.strip()] if services else [], 
                description = description)

@command("Remove secret value from")
def remove(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")],  
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    secrets = XSecrets(dbname)
    if not secrets.exists(key):
        error(f"Secret '{key}' not found.")
        return -1
    if not force:
        confirm = input(f"Are you sure you want to remove the secret '{key}'? [y/n] ")
        if confirm.strip().lower() not in ("y", "yes"):
            error("Aborting deletion.")
            return -1
    secrets.remove(key)


@command("Dump secrets dbs")
def dump(
        dbname: Annotated[str,  Argument("NAME")]
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    secrets = XSecrets(dbname)
    text = secrets.to_json()
    print(text)

@command("Delete secrets db")
def delete(
        dbname: Annotated[str,  Argument("NAME")],
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    xsecrets = XSecrets(dbname)
    if not force:
        confirm = input(f"Are you sure you want to delete the secrets db '{dbname}'? [y/n] ")
        if confirm.strip().lower() not in ("y", "yes"):
            error("Aborting deletion.")
            return -1
    xsecrets.delete()

# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(module = sys.modules[__name__])
    try:
        commandsManager.execute(sys.argv, default_show_help = True)
    except Exception as e:
        error(f"Error: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()






