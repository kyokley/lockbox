from unittest import mock
import pytest

from pathlib import Path
from cryptography.fernet import InvalidToken

from lockbox.main import (encrypt,
                          SALT_LENGTH,
                          decrypt,
                          LockBoxException,
                          )

class TestEncrypt:
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.mock_token_bytes = mocker.patch('lockbox.main.secrets.token_bytes')
        self.mock_token_bytes.return_value = b'0' * SALT_LENGTH #  This is a really terrible salt

        self.mock_get_fernet = mocker.patch('lockbox.main._get_fernet')
        self.mock_get_fernet.return_value.encrypt.return_value = b'test_cipher_data'

        self.mock_urlsafe_b64encode = mocker.patch('lockbox.main.base64.urlsafe_b64encode')
        self.mock_urlsafe_b64encode.return_value = b'test_encoded_salt'

        self.mock_qrcode = mocker.patch('lockbox.main.qrcode')

        self.mock_open = mocker.patch('lockbox.main.open', mock.mock_open())

        self.password = b'password'
        self.plaintext = b'plaintext'

    def test_password_is_str(self):
        expected = b'test_encoded_salt$test_cipher_data'
        actual = encrypt('test_password', self.plaintext)

        assert expected == actual

        self.mock_token_bytes.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(b'test_password', self.mock_token_bytes.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_token_bytes.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called
        assert not self.mock_open.called

    def test_data_is_str(self):
        expected = b'test_encoded_salt$test_cipher_data'
        actual = encrypt(self.password, 'test_data')

        assert expected == actual

        self.mock_token_bytes.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_token_bytes.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(b'test_data')
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_token_bytes.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called
        assert not self.mock_open.called

    def test_no_outfile(self):
        expected = b'test_encoded_salt$test_cipher_data'
        actual = encrypt(self.password, self.plaintext)

        assert expected == actual

        self.mock_token_bytes.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_token_bytes.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_token_bytes.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called
        assert not self.mock_open.called

    def test_outfile_no_qr_code(self):
        expected = None
        actual = encrypt(self.password, self.plaintext, outfile=Path('test_outfile.txt'))

        assert expected == actual

        self.mock_token_bytes.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_token_bytes.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_token_bytes.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called

        self.mock_open.assert_called_once_with(Path('test_outfile.txt'), 'wb')
        self.mock_open.return_value.write.assert_called_once_with(b'test_encoded_salt$test_cipher_data')

    def test_outfile_qr_code(self):
        expected = None
        actual = encrypt(self.password, self.plaintext, outfile=Path('test_outfile.png'))

        assert expected == actual

        self.mock_token_bytes.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_token_bytes.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_token_bytes.return_value)

        self.mock_qrcode.make.assert_called_once_with(b'test_encoded_salt$test_cipher_data')
        self.mock_qrcode.make.return_value.save.assert_called_once_with(Path('test_outfile.png'))

        assert not self.mock_open.called

class TestDecrypt:
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.mock_get_fernet = mocker.patch('lockbox.main._get_fernet')
        self.mock_get_fernet.return_value.decrypt.return_value = b'test_plaintext_data'

        self.mock_urlsafe_b64decode = mocker.patch('lockbox.main.base64.urlsafe_b64decode')
        self.mock_urlsafe_b64decode.return_value = b'test_decoded_salt'

        self.mock_open = mocker.patch('lockbox.main.open', mock.mock_open())

        self.password = b'password'
        self.ciphertext = b'encoded_salt$ciphertext'

    def test_password_is_str_raises(self):
        expected = b'test_plaintext_data'
        actual = decrypt('password', self.ciphertext)

        assert expected == actual

        self.mock_urlsafe_b64decode.assert_called_once_with(b'encoded_salt')
        self.mock_get_fernet.assert_called_once_with(self.password, b'test_decoded_salt')
        self.mock_get_fernet.return_value.decrypt.assert_called_once_with(b'ciphertext')

        assert not self.mock_open.called

    def test_cipher_data_is_str_raises(self):
        expected = b'test_plaintext_data'
        actual = decrypt(self.password, 'encoded_salt$ciphertext')

        assert expected == actual

        self.mock_urlsafe_b64decode.assert_called_once_with(b'encoded_salt')
        self.mock_get_fernet.assert_called_once_with(self.password, b'test_decoded_salt')
        self.mock_get_fernet.return_value.decrypt.assert_called_once_with(b'ciphertext')

        assert not self.mock_open.called

    def test_invalid_token_raises(self):
        self.mock_get_fernet.return_value.decrypt.side_effect = InvalidToken()

        with pytest.raises(LockBoxException):
            decrypt(self.password, self.ciphertext)

        self.mock_urlsafe_b64decode.assert_called_once_with(b'encoded_salt')
        self.mock_get_fernet.assert_called_once_with(self.password, b'test_decoded_salt')
        self.mock_get_fernet.return_value.decrypt.assert_called_once_with(b'ciphertext')

        assert not self.mock_open.called

    def test_no_outfile(self):
        expected = b'test_plaintext_data'
        actual = decrypt(self.password, self.ciphertext)

        assert expected == actual

        self.mock_urlsafe_b64decode.assert_called_once_with(b'encoded_salt')
        self.mock_get_fernet.assert_called_once_with(self.password, b'test_decoded_salt')
        self.mock_get_fernet.return_value.decrypt.assert_called_once_with(b'ciphertext')

        assert not self.mock_open.called

    def test_outfile(self):
        expected = None
        actual = decrypt(self.password, self.ciphertext, outfile='test_outfile.txt')

        assert expected == actual

        self.mock_urlsafe_b64decode.assert_called_once_with(b'encoded_salt')
        self.mock_get_fernet.assert_called_once_with(self.password, b'test_decoded_salt')
        self.mock_get_fernet.return_value.decrypt.assert_called_once_with(b'ciphertext')

        self.mock_open.return_value.write.assert_called_once_with(b'test_plaintext_data')
