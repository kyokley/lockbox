import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_LENGTH = 16
KEY_LENGTH = 32
HASH_ITERATIONS = 100000

def encrypt(password, input_data):
    if not isinstance(password, bytes):
        raise ValueError('password must be of type bytes')

    if not isinstance(input_data, bytes):
        raise ValueError('input_data must be of type bytes')

    salt = os.urandom(SALT_LENGTH)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=KEY_LENGTH,
                     salt=salt,
                     iterations=HASH_ITERATIONS,
                     backend=default_backend())

    key = base64.urlsafe_b64encode(kdf.derive(password))

    f = Fernet(key)
    output_data = f.encrypt(input_data)

    encoded_salt = base64.urlsafe_b64encode(salt)

    return encoded_salt + b'$' + output_data

def decrypt(password, ciphertext):
    if not isinstance(password, bytes):
        raise ValueError('password must be of type bytes')

    if not isinstance(ciphertext, bytes):
        raise ValueError('ciphertext must be of type bytes')

    encoded_salt, data = ciphertext.split(b'$')

    salt = base64.urlsafe_b64decode(encoded_salt)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=KEY_LENGTH,
                     salt=salt,
                     iterations=HASH_ITERATIONS,
                     backend=default_backend())

    key = base64.urlsafe_b64encode(kdf.derive(password))

    f = Fernet(key)
    plaintext = f.decrypt(data)

    return plaintext
