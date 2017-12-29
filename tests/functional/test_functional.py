import os
import tempfile
import hashlib
from lockbox.main import (_get_fernet,
                          encrypt,
                          decrypt,
                          encrypt_file,
                          decrypt_file,
                          )

from cryptography.fernet import Fernet

ONE_MB = 1024 * 1024 # 1MB

def _get_hash(filename):
    sha256 = hashlib.sha256()

    with open(filename, 'rb') as f:
        chunk = f.read(1024)
        while chunk:
            sha256.update(chunk)
            chunk = f.read(1024)

    return sha256.hexdigest()


class TestGetFernet(object):
    def test_returns_fernet(self):
        fernet_obj = _get_fernet(b'password', b'0' * 16)
        assert isinstance(fernet_obj, Fernet)

class TestEncryptDecryptRoundTrip(object):
    def test_run(self):
        password = b'super secret passphrase'
        plaintext = b'this is a sample plaintext to be encrypted'

        ciphertext = encrypt(password, plaintext)

        assert plaintext != ciphertext

        returned_plaintext = decrypt(password, ciphertext)

        assert plaintext == returned_plaintext

class TestEncryptFileDecryptFileRoundTrip(object):
    def setup_method(self):
        self.password = b'super secret passphrase'
        self.plaintext = b'this is a sample plaintext to be encrypted'

    def test_small_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            plaintext_filename = os.path.join(tmp_dir, 'plaintext_filename.txt')
            encrypted_filename = os.path.join(tmp_dir, 'encrypted_filename.txt')

            with open(plaintext_filename, 'wb') as f:
                f.write(self.plaintext)

            encrypt_file(self.password, plaintext_filename, output_file=encrypted_filename)

            test_filename = os.path.join(tmp_dir, 'test_filename.txt')
            decrypt_file(self.password, encrypted_filename, output_file=test_filename)

            assert _get_hash(plaintext_filename) == _get_hash(test_filename)

    def test_large_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            plaintext_filename = os.path.join(tmp_dir, 'plaintext_filename')
            encrypted_filename = os.path.join(tmp_dir, 'encrypted_filename')

            with open(plaintext_filename, 'wb') as f:
                for i in range(50):
                    f.write(os.urandom(ONE_MB))

            encrypt_file(self.password, plaintext_filename, output_file=encrypted_filename)

            test_filename = os.path.join(tmp_dir, 'test_filename')
            decrypt_file(self.password, encrypted_filename, output_file=test_filename)

            assert _get_hash(plaintext_filename) == _get_hash(test_filename)
