from lockbox.main import (_get_fernet,
                          encrypt,
                          decrypt,
                          )

from cryptography.fernet import Fernet

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
