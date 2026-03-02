import base64
from hashlib import sha256
from pathlib import Path
import os
import copy
from argon2.low_level import hash_secret_raw, Type
from typing import Optional

import keyring
from ..editor import Editor
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
            # validation
            if password == None:
                raise ValueError("Password is required to create a new secrets db")            
            # save
            self._save()
            # ensure is locked
            self.lock()


    # methods
    def delete(self):
        # delete
        os.remove(self._path)

    def get(self, name):
        # get entry value
        entry = self._store.get(name)
        entryCloned = copy.deepcopy(entry)
        entryCloned.value = self._decrypt_value(entryCloned.value)
        return entryCloned

    def exists(self, name):
        # exists entry
        return self._store.exists(name)

    def set(self, name, value, type: str = None, services: Optional[list] = None, description: str = "", meta: Optional[dict] = None):
        # set entry value
        self._validate_password()
        if self._store.exists(name):
            entry = self._store.get(name)
        else:
            entry = SecretEntry(
                key         = name,
                type        = "password",
                meta        = {},
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
        if meta is not None and len(meta) > 0:
            entry.meta = meta
        entry.value = self._encrypt_value(value)
        self._store.set(entry)
        self._save()
    
    def keys(self):
        # get keys list
        return self._store.list_keys()
    
    def remove(self, name):
        # remove entry
        self._validate_password()
        entry = self._store.get(name)
        self._store.remove(name)
        self._save()
        
    def edit(self):
        # edit
        tmp = copy.deepcopy(self._store)
        # decrypt
        for entry in tmp.secrets.values():
            entry.value = self._decrypt_value(entry.value)
        # edit
        editor = Editor()
        text = tmp.to_json()
        result = editor.editText(text, format = "json")
        # apply changes
        if result != None:
            # load
            tmp = SecretsStore.from_json(self._path.stem, result)
            # encrypt
            for key in tmp.list_keys():
                entry = tmp.get(key)                
                # check if changed
                if self._store.exists(key):
                    old_entry = self._store.get(key)
                    if entry.value == self._decrypt_value(old_entry.value):
                        entry.value = old_entry.value
                        continue
                # encrypt changed value only
                entry.value = self._encrypt_value(entry.value)       
            # reassign
            self._store = tmp
            # save
            self._save()
    
    def edit_secret(self, name):
        # edit single secret
        entry = self._store.get(name)
        # edit
        editor = Editor()
        text = entry.value
        text = self._decrypt_value(text)
        if text == "":
            text = " "
        result = editor.editText(text, format = entry.type)
        # apply changes
        if result != None:
            entry.value = self._encrypt_value(result)
            self._store.set(entry)
            self._save()

    def to_json(self):
        # to json
        tmp = copy.deepcopy(self._store)
        for entry in tmp.secrets.values():
            entry.value = self._decrypt_value(entry.value)
        return tmp.to_json()

    def unlock(self):
        # unlocking
        self._validate_password()
        key = self._get_key()
        encoded_key = base64.b64encode(key).decode()
        canonical_path = str(self._path.resolve())
        store_id = sha256(canonical_path.encode()).hexdigest()
        keyring.set_password(KEYRING_APP, store_id, encoded_key)

    def is_locked(self):
        # check if locked
        canonical_path = str(self._path.resolve())
        store_id = sha256(canonical_path.encode()).hexdigest()
        encoded_key = keyring.get_password(KEYRING_APP, store_id)
        return encoded_key is None
    
    def lock(self):
        # lock
        canonical_path = str(self._path.resolve())
        store_id = sha256(canonical_path.encode()).hexdigest()
        if not keyring.get_password(KEYRING_APP, store_id) is None:
            keyring.delete_password(KEYRING_APP, store_id)

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
    @staticmethod
    def is_locked_db(dbname: str) -> bool:
        secrets = XSecrets(dbname)
        return secrets.is_locked()
    

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
        # save
        text = self._store.to_json()
        with open(self._path, "w") as file:
            file.write(text)


    # path utils
    def _get_store_path(dbname: str) -> Path:
        # get path for dbname, based on git repo or current folder
        return Path(XSecrets._get_folder_path(), dbname + FILE_EXTENSION)
    
    def _get_folder_path(start_path: Optional[Path] = None) -> Optional[Path]:
        # get folder path based on git repo or current folder
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
        # get key, derive if not exists, or return cached
        if self._password is None and self._key is None:
            # try to get from keyring
            canonical_path = str(self._path.resolve())
            store_id = sha256(canonical_path.encode()).hexdigest()
            encoded_key = keyring.get_password(KEYRING_APP, store_id)
            if encoded_key:
                self._key = base64.b64decode(encoded_key)
        if self._key is not None:
            return self._key
        if not self._password:
            raise ValueError("Store is locked. Password required.")
        if self._key is None:
            # derive the key
            if self._store.meta.crypto_version == 1:
                # v1: argon2id + AES-256
                self._key = hash_secret_raw(
                    secret      = self._password.encode(),
                    salt        = bytes.fromhex(self._store.meta.salt),
                    time_cost   = 5,
                    memory_cost = 131072,  # 128Mb
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
        # decrypt value
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
        # encrypt value
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

    # store
    # encoded_key = base64.b64encode(self._key).decode()
    # keyring.set_password("xsecrets", store_name, encoded_key)

    # retrieve
    #encoded_key = keyring.get_password("xsecrets", store_name)
    #if encoded_key:
    #    self._key = base64.b64decode(encoded_key)

    # lock
    #keyring.delete_password("xsecrets", store_name)
    #self._key = None