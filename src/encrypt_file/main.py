import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt(password, input_data):
    if not isinstance(password, bytes):
        raise ValueError('password must be of type bytes')

    if not isinstance(input_data, bytes):
        raise ValueError('input_data must be of type bytes')

    import pdb; pdb.set_trace()
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=default_backend())

    key = base64.urlsafe_b64encode(kdf.derive(password))

    f = Fernet(key)
    output_data = f.encrypt(input_data)

    encoded_salt = base64.urlsafe_b64encode(salt)

    return encoded_salt + b'$' + output_data
