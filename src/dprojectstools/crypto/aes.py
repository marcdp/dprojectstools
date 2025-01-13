from pathlib import Path
from cryptography.fernet import Fernet # pip install cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import io
import os
import struct
import random
import hashlib
import random
import string

# utils
def password_generate(min=10, max=32):
    length = random.randint(min, max)
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# utils
def aes_encrypt(text: str, password: str):
    iterations = 0
    saltLength = 16
    ivLength = 16
    blockSize = 16
    paddingMode = "PKCS7"
    cipherMode = "CBC"
    keySize = 32
    encoding = "base64"
    separator = ','
    version = ""
    fold = 76
    # salt
    salt = os.urandom(saltLength)
    # iterations
    iterations = int(random.uniform(50000, 50000))
    # derive key
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',           # HMAC-SHA256
        password=password.encode(),   # Password as bytes
        salt=salt,                    # Salt as bytes
        iterations=iterations,        # Iteration count
        dklen=keySize                 # Length of the derived key
    )
    # iv
    iv = os.urandom(ivLength)
    # ms
    body_ms = io.BytesIO();
    # write iv
    body_ms.write(iv)
    # write salt
    body_ms.write(salt)
    # write iterations
    body_ms.write(bytearray(iterations.to_bytes(4, byteorder='little')))    
    # cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    # encript
    encryptor = cipher.encryptor()
    # Pad the plaintext to a multiple of 16 bytes
    padder = padding.PKCS7(blockSize * 8).padder()
    padded_plaintext = padder.update(base64.b64encode(salt) + text.encode()) + padder.finalize()
    #print(padded_plaintext)
    # crypt
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    body_ms.write(ciphertext)
    # read
    body_ms.seek(0)
    body = body_ms.read()
    body_ms.close()
    # result
    result = "aes:" + separator + base64.b64encode(body).decode()
    # fold
    result = "\n".join(
        result[i:i + fold] for i in range(0, len(result), fold)
    )
    # return    
    return result
    
def aes_decrypt(text: str, password: str):
    iterations = 0
    saltLength = 16
    ivLength = 16
    blockSize = 16
    paddingMode = "PKCS7"
    cipherMode = "CBC"
    keySize = 32
    encoding = "base64"
    separator = ','
    version = ""
    # header
    header = text[:text.index(",")]
    # body
    body = text[text.index(",")+1:]
    body_bytes = base64.b64decode(body)
    stream = io.BytesIO(body_bytes)
    # read iv
    iv = stream.read(ivLength)
    # read salt
    salt = stream.read(saltLength)
    # read iterations
    iterations = struct.unpack('<I', stream.read(4))[0]
    # derive key
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',           # HMAC-SHA256
        password=password.encode(),   # Password as bytes
        salt=salt,                    # Salt as bytes
        iterations=iterations,        # Iteration count
        dklen=keySize              # Length of the derived key
    )
    # cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    # decryptor
    decryptor = cipher.decryptor()
    # decrypt
    decrypted_result = decryptor.update(stream.read()) + decryptor.finalize()
    # remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_result = unpadder.update(decrypted_result) + unpadder.finalize()
    # decode
    result = decrypted_result.decode()
    # skip salt
    result = result[int(saltLength*1.5):]
    # return    
    return result
    