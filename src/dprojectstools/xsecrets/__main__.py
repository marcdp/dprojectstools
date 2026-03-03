from pprint import pformat
import sys
import getpass
import json
from dotenv import dotenv_values
import secrets as secrets_module
from typing import Annotated
from .xsecrets import XSecrets
from dprojectstools.commands import command, Argument, Flag, CommandsManager
from dprojectstools.utils.env import format_env_line


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
    xsecrets = XSecrets(dbname, password = password, create = True)    
    # print
    info = xsecrets.info()
    print(f"Store created: {dbname}")
    print(f"Path: {xsecrets.getPath()}")
    print(f"Status: {'locked' if xsecrets.is_locked() else 'unlocked'}")


@command("List secrets dbs", alias=["list"], examples=[
    "xsecrets list",
    "xsecrets list dev"
])
def listcmd(
    dbname: Annotated[str,  Argument("NAME")] = None
    ):
    if dbname:
        if XSecrets.exists_db(dbname):
            xsecrets = XSecrets(dbname)
            keys = xsecrets.keys()
            width = max(len(key) for key in keys) if keys else 0
            for key in keys:
                entry = xsecrets.get(key)
                print(f"{key:<{width}}   {entry.type}")
        else:
            error(f"Secrets db '{dbname}' not found.")
    else:
        db_names = XSecrets.get_db_names()
        width = max(len(db_name) for db_name in db_names) if db_names else 0
        for db_name in db_names:
            xsecrets = XSecrets(db_name)
            keys_count = len(xsecrets.keys())
            locked = xsecrets.is_locked()
            print(f"{db_name:<{width}}   {keys_count} {'key ' if keys_count == 1 else 'keys'}  {'locked' if locked else 'unlocked'}")


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
    exists = secrets.exists(key)
    if exists and not force:
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
    # log
    if exists:
        print(f"{key} updated")
    else:
        print(f"{key} created")


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
    # log
    print(f"{key} removed")


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
    # log
    print(f"Secrets db '{dbname}' deleted.")


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
    # log
    print(f"Secrets db '{dbname}' unlocked.")


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
    # log
    print(f"Secrets db '{dbname}' locked.")


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


@command("Export secrets", examples=[
    "xsecrets export dev",
    "xsecrets export dev --format env",
    "xsecrets export dev --format json",
    "xsecrets export dev --format xsecrets"
])
def export(
        dbname: Annotated[str,  Argument("NAME")],
        format: Annotated[str,  Flag(' ', "format")] = "env"
    ):
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # ask for password if interactive and not provided
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # create instance
    xsecrets = XSecrets(dbname, password = password)
    # action
    if format == "json":
        # .json
        dict = {}
        for key in xsecrets.keys():
            entry = xsecrets.get(key)
            dict[key] = entry.value
        print(json.dumps(dict, indent=2))
    elif format == "env":
        # .env
        for key in xsecrets.keys():
            entry = xsecrets.get(key)
            print(format_env_line(key, entry.value))
    elif format == "xsecrets":
        # .xsecrets (internal format)
        print(xsecrets.to_json())
    else:
        error(f"Unsupported export format '{format}'. Supported formats are: json, env, xsecrets.")
        return -1


@command("Import secrets into db", alias=["import"], examples=[
    "xsecrets import dev ./secrets-key-value.json",
    "xsecrets import dev ./secrets-key-value.env --force"
])
def imports(
        dbname: Annotated[str,  Argument("NAME")],
        filename: Annotated[str,  Argument("FILE")],
        force: Annotated[bool, Flag('f', "force")] = False,
        format: Annotated[str,  Flag(' ', "format")] = "auto",
        verbose: Annotated[bool, Flag('v', "verbose")] = False,

    ):
    # validation
    if not XSecrets.exists_db(dbname):
        error(f"Secrets db '{dbname}' not found.")
        return -1
    # ask for password if interactive and not provided
    password = None
    if XSecrets.is_locked_db(dbname):
        password = ask_password()
    # create instance
    xsecrets = XSecrets(dbname, password = password)
    # auto detect format based on file extension
    if format == "auto":
        if filename.endswith(".json"):
            format = "json"
        elif filename.endswith(".env"):
            format = "env"
        elif filename.endswith(".xsecrets"):
            format = "xsecrets"
        else:
            error(f"Cannot auto detect format from file extension. Please specify the format using --format flag.")
            return -1
    # action
    new_count = 0
    updated_count = 0
    skipped_count = 0
    untouched_count = 0
    if format == "json":
        # .json
        with open(filename, "r") as f:
            dict = json.load(f) 
            print(f"Importing {len(dict)} secrets into '{dbname}' ...")
            if verbose:
                print()
            for key, value in dict.items():
                if xsecrets.exists(key):
                    if not force:
                        if verbose:
                            print(f"! {key} (exists, skipping)")
                        skipped_count += 1
                        continue
                    current_value = xsecrets.getValue(key)
                    if current_value == value:
                        if verbose:
                            print(f"= {key}")
                        untouched_count += 1
                    else:
                        if verbose:
                            print(f"~ {key}")
                        xsecrets.set(key, value)
                        updated_count += 1
                else:
                    if verbose:
                        print(f"+ {key}.")
                    xsecrets.set(key, value)
                    new_count += 1
    elif format == "env":
        # .env
        dict = dotenv_values(filename)
        print(f"Importing {len(dict)} secrets into '{dbname}' ...")
        if verbose:
            print()
        for key, value in dict.items():
            if xsecrets.exists(key):
                if not force:
                    if verbose:
                        print(f"! {key} (exists, skipping)")
                    skipped_count += 1
                    continue
                current_value = xsecrets.getValue(key)
                if current_value == value:
                    if verbose:
                        print(f"= {key}")
                    untouched_count += 1
                else:
                    if verbose:
                        print(f"~ {key}")
                    xsecrets.set(key, value)
                    updated_count += 1
            else:
                if verbose:
                    print(f"+ {key}.")
                xsecrets.set(key, value)
                new_count += 1
    elif format == "xsecrets":
        # .xsecrets (internal format)
        with open(filename, "r") as f:
            text = f.read()
            tmp = XSecrets.from_json(text)
            print(f"Importing {len(tmp.secrets.items())} secrets into '{dbname}' ...")
            if verbose:
                print()
            for key, entry in tmp.secrets.items():
                tmp_value = tmp.getValue(key)
                if xsecrets.exists(key):
                    if not force:
                        if verbose:
                            print(f"! {key} (exists, skipping)")
                        skipped_count += 1
                        continue
                    current_value = xsecrets.getValue(key)
                    if current_value == entry.value:
                        if verbose:
                            print(f"= {key}")
                        untouched_count += 1
                    else:
                        if verbose:
                            print(f"~ {key}")
                        xsecrets.set(key, tmp_value, type = entry.type, services = entry.services, meta = entry.meta, description = entry.description)
                        updated_count += 1
                else:
                    if verbose:
                        print(f"+ {key}.")
                    xsecrets.set(key, tmp_value, type = entry.type, services = entry.services, meta = entry.meta, description = entry.description)
                    new_count += 1
    if verbose:
        print()
    print(f"Done. {new_count} new, {updated_count} updated, {untouched_count} untouched, {skipped_count} skipped..")


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



