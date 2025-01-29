from pathlib import Path
import os
import json
import keyring
from typing import Annotated
from ..commands import command, CommandsManager
from .. import PATH_DPROJECTSTOOLS

# consts
PATH_DPROJECTSTOOLS_CONFIGS = PATH_DPROJECTSTOOLS / "configs"

# class
class ConfigManager():


    # vars
    _path = ""
    _dict = {}
    

    # ctr
    def __init__(self, name):
        folder = PATH_DPROJECTSTOOLS_CONFIGS
        folder.mkdir(parents=True, exist_ok=True)
        self._path = Path(folder, name + ".json")
        self._load()


    # methods
    def get(self, name):
        value = self._dict.get(name)
        if value is None:
            value = self.set(name, value)
        return str(value)
   

    # methods
    def _load(self):
        if os.path.isfile(self._path):
            with open(self._path, "r") as file:
                text = file.read()
                self._dict = json.loads(text)
        pass


