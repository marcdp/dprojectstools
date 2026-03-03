from pprint import pformat
import sys
import getpass
import secrets as secrets_module
from typing import Annotated
from .xsecrets import XSecrets
from dprojectstools.commands import command, Argument, Flag, CommandsManager


# utils
def error(message: str) -> None:
    RED = "\033[31m"
    RESET = "\033[0m"
    print(f"{RED}{message}{RESET}", file=sys.stderr)

def ask_password(confirm: bool = False, min_length: int = 8) -> str:
    result = getpass.getpass("Enter password: ", echo_char="*")
    if confirm:
        if len(result) < min_length:
            error(f"Password must be at least {min_length} characters long.")
            sys.exit(1)
        result_confirm = getpass.getpass("Confirm password: ", echo_char="*")
        if result != result_confirm:
            error("Passwords do not match.")
            sys.exit(1)
    return result


# main
@command("Create secrets db", examples=[
    "xsecrets create dev",
    "xsecrets create dev --force"
])
def create(
        dbname: Annotated[str,  Argument("NAME")],
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    # validation
    if XSecrets.exists_db(dbname):
        if not force:
            confirm = input(f"Secrets db '{dbname}' already exists. Do you want to overwrite it? [y/n] ")
            if confirm.strip().lower() not in ("y", "yes"):
                error("Aborting creation.")
                return -1
        XSecrets.delete_db(dbname)
    # ask for password 
    password = ask_password(confirm=True) 
    # create instance (will create empty store if not exists)
    XSecrets(dbname, password = password, create = True)    


@command("List secrets dbs", alias=["list"], examples=[
    "xsecrets list",
    "xsecrets list dev"
])
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

@command("Edit secrets dbs", examples=[
    "xsecrets edit",
    "xsecrets edit dev"
])
def edit(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")] = ""
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # ask for password if interactive and not provided
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # create instance
    secrets = XSecrets(dbname, password = password)
    # action
    if key:
        secrets.edit_secret(key)
    else:
        secrets.edit()

@command("Get secret value from db", examples=[
    "xsecrets get dev mysecret"
])
def get(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")]
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # ask for password if interactive and not provided
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # create instance
    secrets = XSecrets(dbname, password = password)
    # action
    if secrets.exists(key):
        entry = secrets.get(key)
        print(entry.value)
    else:
        error(f"Secret '{key}' not found.") 
        return -1

@command("Set secret value from db", examples=[
    "xsecrets set dev mysecret",
    "xsecrets set dev mysecret myvalue",
    "xsecrets set dev mysecret myvalue --description 'My secret' --services api1,backend1 --type password --force",
    "xsecrets set dev mysecret --generate --length 64",
    "echo myvalue | xsecrets set dev mysecret"
])
def set(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")],
        value: Annotated[str,  Argument("VALUE")] = None,
        type_name: Annotated[str,  Flag('t', "type", alias="type")] = "",
        services: Annotated[str,  Flag('s', "services")] = "",
        description: Annotated[str,  Flag('d', "description")] = "",
        meta: Annotated[dict,  Flag('m', "meta")] = {},
        generate: Annotated[bool,  Flag('g', "generate")] = False,
        length: Annotated[int,  Flag('l', "length")] = 32,
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    # validation
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    if value and generate:        
        error("Cannot specify both value and generate.")
        return -1
    # check interactive
    interactive = sys.stdin.isatty() and value is None
    # generate value if requested
    if value is None and generate:        
        value = secrets_module.token_urlsafe(length)
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
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # init store
    secrets = XSecrets(dbname, password = password)
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
                meta=meta,
                description = description)

@command("Remove secret value from db", examples=[
    "xsecrets remove dev mysecret",
    "xsecrets remove dev mysecret --force"
])
def remove(
        dbname: Annotated[str,  Argument("NAME")],
        key: Annotated[str,  Argument("KEY")],  
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # ask for password if interactive and not provided
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # create instance
    secrets = XSecrets(dbname)
    # validate
    if not secrets.exists(key):
        error(f"Secret '{key}' not found.")
        return -1
    if not force:
        confirm = input(f"Are you sure you want to remove the secret '{key}'? [y/n] ")
        if confirm.strip().lower() not in ("y", "yes"):
            error("Aborting deletion.")
            return -1
    # action
    secrets.remove(key)


@command("Dump secrets dbs", examples=[
    "xsecrets dump dev"
])
def dump(
        dbname: Annotated[str,  Argument("NAME")]
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # ask for password if interactive and not provided
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # create instance
    secrets = XSecrets(dbname, password = password)
    # action
    text = secrets.to_json()
    # print
    print(text)

@command("Delete secrets db", examples=[
    "xsecrets delete dev",
    "xsecrets delete dev --force"
])
def delete(
        dbname: Annotated[str,  Argument("NAME")],
        force: Annotated[bool,  Flag('f', "force")] = False
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # create instance 
    xsecrets = XSecrets(dbname)
    # confirm
    if not force:
        confirm = input(f"Are you sure you want to delete the secrets db '{dbname}'? [y/n] ")
        if confirm.strip().lower() not in ("y", "yes"):
            error("Aborting deletion.")
            return -1
    # action
    xsecrets.delete()


@command("Unlock secrets db", examples=[
    "xsecrets unlock dev"
])
def unlock(
        dbname: Annotated[str,  Argument("NAME")]
    ):
    # validation
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    if not XSecrets.is_locked_db(dbname):
        error(f"Secrets db '{dbname}' is not locked.")
        return -1
    # ask for password if interactive and not provided
    password = ask_password()
    # create instance 
    xsecrets = XSecrets(dbname, password = password)
    # action
    xsecrets.unlock()

@command("Lock secrets db", examples=[
    "xsecrets lock dev"
])
def lock(
        dbname: Annotated[str,  Argument("NAME")]
    ):
    # validation
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    if XSecrets.is_locked_db(dbname):
        error(f"Secrets db '{dbname}' is already locked.")
        return -1    
    # create instance 
    xsecrets = XSecrets(dbname)
    # action
    xsecrets.lock()

@command("Show secrets db info", examples=[
    "xsecrets info dev"
])
def info(
        dbname: Annotated[str,  Argument("NAME")]
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # create instance 
    xsecrets = XSecrets(dbname)
    # action
    info = xsecrets.info()
    # print
    width = max(len(k) for k in info.keys())
    print(f"Secrets db info:")
    print("-" * (width + 2))
    for k, v in info.items():
        print(f"{k:<{width}} : {v}")

# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(module = sys.modules[__name__])
    try:
        commandsManager.execute(sys.argv, default_show_help = True)
    except Exception as e:        
        error(f"{e}")
        sys.exit(1)
if __name__ == "__main__":
    main()


# todo
# - type values (password, apikey, certificate, file, etc.)
# - add TTL to cached keys



