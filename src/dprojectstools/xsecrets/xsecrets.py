from pathlib import Path
import os
import json
import keyring
import getpass
from typing import Annotated, Optional
from ..editor import Editor
from ..crypto import aes_decrypt, aes_encrypt, password_generate
from .model import SecretEntry, SecretValue, SecretsMeta, SecretsStore

# consts
KEYRING_APP = "dprojectstools"
GIT_FOLDER = ".secrets"
FILE_EXTENSION = ".json"

# class
class XSecrets():


    # vars
    _path = ""
    _password = None
    _key = None
    _store = None
    

    # ctr
    def __init__(self, dbname, password = None, create = False):
        # get path
        self._path = XSecrets._get_git_secrets_store_path(dbname)
        # validate
        if os.path.exists(self._path):
            if create:
                raise ValueError("Unable to create db: already exists:", dbname)
        else:
            if not create:
                raise ValueError("Unable to open db: db not found:", dbname)
        # password
        self._password = password
        # load
        self._load()
        # save if required
        if create:
            self._save()


    # methods
    def delete(self):
        os.remove(self._path)

    def get(self, name):
        return self._store.get(name)

    def exists(self, name):
        return self._store.exists(name)

    def set(self, name, value, type: str = None, services: Optional[list] = None, description: str = ""):
        if self._store.exists(name):
            entry = self._store.get(name)
        else:
            entry = SecretEntry(
                key=name,
                type="password",
                services=[],
                value=SecretValue(content=""),
                description=""
            )
        if type:
            entry.type = type
        if services:
            entry.services = services if services is not None else []
        if description:
            entry.description = description
        entry.value = SecretValue(content=value)
        self._store.set(entry)
        self._save()
        return value
    
    def keys(self):
        return self._store.list_keys()
    
    def remove(self, name):
        entry = self._store.get(name)
        self._store.remove(name)
        self._save()
        
    def edit(self):
        editor = Editor()
        text = self._store.to_json()
        result = editor.editText(text, format = "json")
        if result != None:
            self._store = SecretsStore.from_json(self._path.stem, result)
            self._save()
            return True
        return False
    
    def edit_secret(self, name):
        entry = self._store.get(name)
        editor = Editor()
        text = entry.value.content
        if text == "":
            text = " "
        result = editor.editText(text, format = entry.type)
        if result != None:
            entry.value.content = result
            self._store.set(entry)
            self._save()
            return True
        return False

    def to_json(self):
        return self._store.to_json()


    # static methods
    @staticmethod
    def get_db_names():
        folder = XSecrets._get_git_secrets_folder_path()
        return [f.stem for f in folder.rglob(f"*{FILE_EXTENSION}") if f.is_file()]
    @staticmethod
    def delete_db(dbname: str) -> bool:
        path = XSecrets._get_git_secrets_store_path(dbname)
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False
    @staticmethod
    def exists_db(dbname: str) -> bool:
        path = XSecrets._get_git_secrets_store_path(dbname)
        return os.path.isfile(path)
    

    # read/write utils
    def _load(self):
        if os.path.isfile(self._path):
            with open(self._path, "r") as file:
                text = file.read()
                #if not self._password is None:
                #    text = aes_decrypt(text, self._password)
                self._store = SecretsStore.from_json(self._path.stem, text)
        else:
            # empty 
            self._store = SecretsStore(
                name=self._path.stem,
                meta=SecretsMeta(),
            )
    
    def _save(self):
        text = self._store.to_json()
        #if not self._password is None:
        #    text = aes_encrypt(text, self._password);
        with open(self._path, "w") as file:
            file.write(text)

    # password
    def _ask_for_password(self, name):
        password = getpass.getpass("Enter your password: ")
        if not password:
            raise ValueError("Password cannot be empty")
        return password


    # path utils
    def _get_git_secrets_store_path(dbname: str) -> Path:
        return Path(XSecrets._get_git_secrets_folder_path(), dbname + FILE_EXTENSION)
    
    def _get_git_secrets_folder_path(start_path: Optional[Path] = None) -> Optional[Path]:
        if start_path is None:
            current_path = Path.cwd()
        else:
            current_path = Path(start_path).resolve()
        for parent in [current_path] + list(current_path.parents):
            git_dir = parent / ".git"
            if git_dir.exists() and git_dir.is_dir():
                result = parent / GIT_FOLDER
                result.mkdir(parents=True, exist_ok=True)
                return result
        raise FileNotFoundError(f"No Git repository found starting from '{current_path}'")
    
    # decrypt
    def _decrypt_value(self, value):
        pass
    def _encrypt_value(self, value):
        pass
    