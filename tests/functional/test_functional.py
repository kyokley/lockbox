from lockbox.main import _get_fernet

from cryptography.fernet import Fernet

class TestGetFernet(object):
    def test_returns_fernet(self):
        fernet_obj = _get_fernet(b'password', b'0' * 16)
        assert isinstance(fernet_obj, Fernet)
