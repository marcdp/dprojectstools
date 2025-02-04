from pathlib import Path
import os
import json
import keyring
import getpass
from typing import Annotated
from ..editor import Editor
from ..crypto import aes_decrypt, aes_encrypt, password_generate
from .. import PATH_DPROJECTSTOOLS

# consts
KEYRING_APP = "dprojectstools"
PATH_DPROJECTSTOOLS_SECRETS = PATH_DPROJECTSTOOLS / "secrets"

# class
class SecretsManager():


    # vars
    _password = None
    _path = ""
    _dict = {}
    

    # ctr
    def __init__(self, dbname, password = "keyring:", create = False):
        folder = PATH_DPROJECTSTOOLS_SECRETS
        folder.mkdir(parents=True, exist_ok=True)
        self._path = Path(folder, dbname + ".json.aes")
        # validate
        if os.path.exists(self._path):
            if create:
                raise ValueError("Unable to create db: already exists:", dbname)
        else:
            if not create:
                raise ValueError("Unable to open db: db not found:", dbname)
        # password
        if password.startswith("keyring:"):
            username = password[password.index(":") + 1:]
            if username == "":
                username = getpass.getuser()
            password = keyring.get_password(KEYRING_APP, username)
            if password is None:
                password = password_generate()
                keyring.set_password(KEYRING_APP, username, password)
        self._password = password
        self._load()
        # save if required
        if create:
            self._save()


    # methods
    def get(self, name):
        value = self._dict.get(name)
        if value is None:
            value = self.set(name, value)
        return str(value)
    
    def keys(self):
        return self._dict.keys()
    
    def set(self, name, value=None):
        if value is None:
            value = input("Enter secret '{0}' value: ".format(name))
        self._dict[name] = str(value)
        self._save()
        return value

    def delete(self, name):
        del self._dict[name]
        self._save()

    def edit(self):
        editor = Editor()
        text = json.dumps(self._dict, indent=4)
        result = editor.editText(text, format = "json")
        if result != None:
            self._dict = json.loads(result)
            self._save()
            return True
        return False

    # static methods
    @staticmethod
    def get_db_names():
        folder = PATH_DPROJECTSTOOLS_SECRETS
        folder.mkdir(parents=True, exist_ok=True)
        files = [entry.name.replace(".json.aes", "") for entry in os.scandir(folder) if entry.is_file()]
        return files


    # private methods
    def _load(self):
        if os.path.isfile(self._path):
            with open(self._path, "r") as file:
                text = file.read()
                if not self._password is None:
                    text = aes_decrypt(text, self._password);
                self._dict = json.loads(text)
        pass

    def _save(self):
        text = json.dumps(self._dict, indent=4)
        if not self._password is None:
            text = aes_encrypt(text, self._password);
        with open(self._path, "w") as file:
            file.write(text)
    
    
    # commands
    #@command("List secrets", index = 85)
    #def secrets_list(self):
    #    for key in self.keys():
    #        print("{0}: {1}".format(key, self.get(key)))
    #@command("Set secret")
    #def secrets_set(self, 
    #        name: Annotated[str, "Name"],
    #        value: Annotated[str, "Value"]
    #    ):
    #    self.set(name, value)
    #@command("Get secret")
    #def secrets_get(self, 
    #        name: Annotated[str, "Name"]
    #    ):
    #    value = self.get(name)
    #    print(value)
    #@command("Del secret")
    #def secrets_delete(self, 
    #        name: Annotated[str, "Name"]
    #    ):
    #    self.delete(name)
    #
    #    # methods
    #def exec(self, argv):
    #    commandsManager = CommandsManager()
    #    commandsManager.register(self)
    #    return commandsManager.execute(argv)        

