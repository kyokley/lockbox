import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import qrcode

SALT_LENGTH = 16
KEY_LENGTH = 32
HASH_ITERATIONS = 100000

CHUNK_SIZE = 1024 * 1024 * 10 # 10 MB

QR_CODE_EXTENSIONS = ('.png',
                      )

class LockBoxException(Exception):
    pass

def _get_fernet(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=KEY_LENGTH,
                     salt=salt,
                     iterations=HASH_ITERATIONS,
                     backend=default_backend())

    key = base64.urlsafe_b64encode(kdf.derive(password))

    return Fernet(key)

def encrypt(password, plain_data, outfile=None):
    if not isinstance(password, bytes):
        password = password.encode('utf-8')

    if not isinstance(plain_data, bytes):
        plain_data = plain_data.encode('utf-8')

    salt = os.urandom(SALT_LENGTH)
    fernet = _get_fernet(password, salt)
    cipher_data = fernet.encrypt(plain_data)

    encoded_salt = base64.urlsafe_b64encode(salt)

    output_data = encoded_salt + b'$' + cipher_data

    if not outfile:
        return output_data
    else:
        if os.path.splitext(outfile)[1] in QR_CODE_EXTENSIONS:
            img = qrcode.make(output_data)
            img.save(outfile)
        else:
            with open(outfile, 'wb') as f:
                f.write(output_data)

def decrypt(password, cipher_data, outfile=None):
    if not isinstance(password, bytes):
        password = password.encode('utf-8')

    if not isinstance(cipher_data, bytes):
        cipher_data = cipher_data.encode('utf-8')

    encoded_salt, data = cipher_data.split(b'$')

    salt = base64.urlsafe_b64decode(encoded_salt)
    fernet = _get_fernet(password, salt)

    try:
        plaintext = fernet.decrypt(data)
    except InvalidToken:
        raise LockBoxException('Invalid Token has been provided')

    if not outfile:
        return plaintext
    else:
        with open(outfile, 'wb') as f:
            f.write(plaintext)

def encrypt_file(password, input_file, output_file=None):
    if not os.path.exists(input_file):
        raise LockBoxException('{} does not exist'.format(input_file))

    with open(input_file, 'rb') as infile:
        if output_file:
            with open(output_file, 'wb') as outfile:
                chunk = infile.read(CHUNK_SIZE)

                while chunk:
                    encrypted_data = encrypt(password, chunk)
                    outfile.write(encrypted_data + b'\n')

                    chunk = infile.read(CHUNK_SIZE)
        else:
            chunk = infile.read(CHUNK_SIZE)
            while chunk:
                encrypted_data = encrypt(password, chunk)
                print(encrypted_data.decode('utf-8'))
                chunk = infile.read(CHUNK_SIZE)

def _split_encrypted_file(infile):
    with open(infile, 'rb') as f:
        for line in f:
            yield line

def decrypt_file(password, encrypted_file, output_file=None):
    if not os.path.exists(encrypted_file):
        raise LockBoxException('{} does not exist'.format(encrypted_file))

    file_lines = _split_encrypted_file(encrypted_file)

    if output_file:
        with open(output_file, 'wb') as outfile:
            for line in file_lines:
                data = decrypt(password, line)
                outfile.write(data)
    else:
        for line in file_lines:
            data = decrypt(password, line)
            print(data.decode('utf-8'))

def encrypt_directory(password, directory):
    if not os.path.exists(directory):
        raise LockBoxException('{} does not exist'.format(directory))
    if not os.path.isdir(directory):
        raise LockBoxException('{} is not a directory'.format(directory))

    for root, dirs, files in os.walk(directory):
        for file in files:
            fullpath = os.path.join(root, file)

            if os.path.islink(fullpath):
                continue

            output_file = '{}.lockbox'.format(fullpath)
            encrypt_file(password, fullpath, output_file=output_file)

def decrypt_directory(password, directory):
    pass
