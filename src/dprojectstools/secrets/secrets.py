from pathlib import Path
import os
import json
import keyring
from typing import Annotated
from ..commands import command, CommandsManager
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
    def __init__(self, name, password = "keyring:"):
        folder = PATH_DPROJECTSTOOLS_SECRETS
        folder.mkdir(parents=True, exist_ok=True)
        self._path = Path(folder, name + ".json")
        if not password == "":
            if password.startswith("keyring:"):
                username = password[password.index(":") + 1:]
                if username == "":
                    username = os.getlogin()
                password = keyring.get_password(KEYRING_APP, username)
                if password is None:
                    password = password_generate()
                    keyring.set_password(KEYRING_APP, username, password)
            self._password = password
            self._path = Path(folder, name + ".json.aes")
        self._load()


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


    # methods
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
    @command("List secrets", index = 85)
    def secrets_list(self):
        for key in self.keys():
            print("{0}: {1}".format(key, self.get(key)))
    @command("Set secret")
    def secrets_set(self, 
            name: Annotated[str, "Name"],
            value: Annotated[str, "Value"]
        ):
        self.set(name, value)
    @command("Get secret")
    def secrets_get(self, 
            name: Annotated[str, "Name"]
        ):
        value = self.get(name)
        print(value)
    @command("Del secret")
    def secrets_delete(self, 
            name: Annotated[str, "Name"]
        ):
        self.delete(name)

    # methods
    def exec(self, argv):
        commandsManager = CommandsManager()
        commandsManager.register(self)
        return commandsManager.execute(argv)        

