import base64
from pathlib import Path
import os
import copy
from argon2.low_level import hash_secret_raw, Type
from typing import Optional
from ..editor import Editor
from ..crypto import aes_decrypt, aes_encrypt, password_generate
from .model import SecretEntry, SecretsMeta, SecretsStore
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# consts
KEYRING_APP = "xsecrets"
GIT_FOLDER = ".secrets"
FILE_EXTENSION = ".json"
ENC_PREFIX = "enc:"
CHECK_VALUE = "xsecrets"

# class
class XSecrets():


    # ctr
    def __init__(self, dbname, password = None, create = False):
        # get path
        self._path = XSecrets._get_store_path(dbname)
        # validate
        if os.path.exists(self._path):
            if create:
                raise ValueError(f"Unable to create db: already exists: {dbname}")
        else:
            if not create:
                raise ValueError(f"Unable to open db: db not found: {dbname}")
        # password
        self._password = password
        # key
        self._key = None
        # load
        self._load()
        # save if required
        if create:
            if self._password is None:
                raise ValueError("Password is required to create a new secrets db")            
            self._save()


    # methods
    def delete(self):
        os.remove(self._path)

    def get(self, name):
        entry = self._store.get(name)
        entryCloned = copy.deepcopy(entry)
        entryCloned.value = self._decrypt_value(entryCloned.value)
        return entryCloned

    def exists(self, name):
        return self._store.exists(name)

    def set(self, name, value, type: str = None, services: Optional[list] = None, description: str = ""):
        self._validate_password()
        if self._store.exists(name):
            entry = self._store.get(name)
        else:
            entry = SecretEntry(
                key         = name,
                type        = "password",
                services    = [],
                value       = "",
                description = ""
            )
        if type:
            entry.type = type
        if services is not None:
            entry.services = services
        if description:
            entry.description = description
        entry.value = self._encrypt_value(value)
        self._store.set(entry)
        self._save()
        return value
    
    def keys(self):
        return self._store.list_keys()
    
    def remove(self, name):
        self._validate_password()
        entry = self._store.get(name)
        self._store.remove(name)
        self._save()
        
    def edit(self):
        tmp = copy.deepcopy(self._store)
        for entry in tmp.secrets.values():
            entry.value = self._decrypt_value(entry.value)
        editor = Editor()
        text = tmp.to_json()
        result = editor.editText(text, format = "json")
        if result != None:
            tmp = SecretsStore.from_json(self._path.stem, result)
            for entry in tmp.secrets.values():
                entry.value = self._encrypt_value(entry.value)
            self._store = tmp
            self._save()
            return True
        return False
    
    def edit_secret(self, name):
        entry = self._store.get(name)
        editor = Editor()
        text = entry.value
        text = self._decrypt_value(text)
        if text == "":
            text = " "
        result = editor.editText(text, format = entry.type)
        if result != None:
            entry.value = self._encrypt_value(result)
            self._store.set(entry)
            self._save()
            return True
        return False

    def to_json(self):
        tmp = copy.deepcopy(self._store)
        for entry in tmp.secrets.values():
            entry.value = self._decrypt_value(entry.value)
        return tmp.to_json()


    # static methods
    @staticmethod
    def get_db_names():
        folder = XSecrets._get_folder_path()
        return [f.stem for f in folder.rglob(f"*{FILE_EXTENSION}") if f.is_file()]
    @staticmethod
    def delete_db(dbname: str) -> bool:
        path = XSecrets._get_store_path(dbname)
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False
    @staticmethod
    def exists_db(dbname: str) -> bool:
        path = XSecrets._get_store_path(dbname)
        return os.path.isfile(path)
    

    # read/write utils
    def _load(self):
        if os.path.isfile(self._path):
            with open(self._path, "r") as file:
                text = file.read()
                self._store = SecretsStore.from_json(self._path.stem, text)
        else:
            # empty 
            self._store = SecretsStore(
                name=self._path.stem,
                meta=SecretsMeta(
                    salt = os.urandom(16).hex()
                ),
            )
            self._store.meta.check = self._encrypt_value(CHECK_VALUE)
    
    def _save(self):
        text = self._store.to_json()
        with open(self._path, "w") as file:
            file.write(text)


    # path utils
    def _get_store_path(dbname: str) -> Path:
        return Path(XSecrets._get_folder_path(), dbname + FILE_EXTENSION)
    
    def _get_folder_path(start_path: Optional[Path] = None) -> Optional[Path]:
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
    def _validate_password(self):
        # try to decrypt meta.check to validate password
        try:
            value = self._decrypt_value(self._store.meta.check)
        except Exception as e:
            raise ValueError("Invalid password") from e
        if value != CHECK_VALUE:
            raise ValueError("Invalid password")
    
    def _get_key(self):
        if self._key is not None:
            return self._key
        if not self._password:
            raise ValueError("Store is locked. Password required.")
        if self._key is None:
            # deriva la key
            if self._store.meta.crypto_version == 1:
                # v1: argon2id + AES-256
                self._key = hash_secret_raw(
                    secret      = self._password.encode(),
                    salt        = bytes.fromhex(self._store.meta.salt),
                    time_cost   = 3,
                    memory_cost = 65536, 
                    parallelism = 4,
                    hash_len    = 32,
                    type        = Type.ID
                )
            else:
                raise ValueError(f"Unsupported crypto version in meta: {self._store.meta.crypto_version}")
        # clear password from memory
        self._password = None
        # return
        return self._key
    
    def _decrypt_value(self, encrypted_value):
        key = self._get_key()
        if self._store.meta.crypto_version == 1:
            # schema 1: AES-GCM with random nonce
            if not encrypted_value.startswith(ENC_PREFIX + "v" + str(self._store.meta.crypto_version) + ":"):
                raise ValueError("Invalid encrypted format")
            encoded = encrypted_value[len(ENC_PREFIX + "v" + str(self._store.meta.crypto_version) + ":"):]
            encrypted_blob = base64.b64decode(encoded)
            nonce = encrypted_blob[:12]
            ciphertext = encrypted_blob[12:]
            aesgcm = AESGCM(key)
            plaintext_bytes = aesgcm.decrypt(
                nonce,
                ciphertext,
                None
            )
            return plaintext_bytes.decode("utf-8")
        # error
        raise ValueError("Invalid crypto version")
    
    def _encrypt_value(self, value):
        key = self._get_key()
        if self._store.meta.crypto_version == 1:
            # scheme 1: AES-GCM with random nonce
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)  # 96-bit nonce (recommended for GCM)
            plaintext_bytes = value.encode("utf-8")
            ciphertext = aesgcm.encrypt(
                nonce,
                plaintext_bytes,
                None  # optional associated data
            )
            # Store nonce + ciphertext together
            encrypted_blob = nonce + ciphertext
            # Encode to base64 so it fits in JSON
            return ENC_PREFIX + "v" + str(self._store.meta.crypto_version) + ":" + base64.b64encode(encrypted_blob).decode("utf-8")
        # error
        raise ValueError("Invalid crypto version")
