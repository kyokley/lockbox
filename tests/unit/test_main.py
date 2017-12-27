from unittest import mock
import pytest

from lockbox.main import (encrypt,
                          SALT_LENGTH,
                          decrypt,
                          )

class TestEncrypt(object):
    def setup_method(self):
        self.urandom_patcher = mock.patch('lockbox.main.os.urandom')
        self.mock_urandom = self.urandom_patcher.start()

        self.mock_urandom.return_value = b'0' * SALT_LENGTH #  This is a really terrible salt

        self._get_fernet_patcher = mock.patch('lockbox.main._get_fernet')
        self.mock_get_fernet = self._get_fernet_patcher.start()
        self.mock_get_fernet.return_value.encrypt.return_value = b'test_cipher_data'

        self.urlsafe_b64encode_patcher = mock.patch('lockbox.main.base64.urlsafe_b64encode')
        self.mock_urlsafe_b64encode = self.urlsafe_b64encode_patcher.start()
        self.mock_urlsafe_b64encode.return_value = b'test_encoded_salt'

        self.qrcode_patcher = mock.patch('lockbox.main.qrcode')
        self.mock_qrcode = self.qrcode_patcher.start()

        self.open_patcher = mock.patch('lockbox.main.open', mock.mock_open())
        self.mock_open = self.open_patcher.start()

        self.password = b'password'
        self.plaintext = b'plaintext'

    def teardown_method(self):
        self.urandom_patcher.stop()
        self._get_fernet_patcher.stop()
        self.urlsafe_b64encode_patcher.stop()
        self.qrcode_patcher.stop()
        self.open_patcher.stop()

    def test_password_is_str_raises(self):
        with pytest.raises(ValueError):
            encrypt('test_password', self.plaintext)

        assert not self.mock_urandom.called
        assert not self.mock_get_fernet.called
        assert not self.mock_get_fernet.return_value.encrypt.called
        assert not self.mock_urlsafe_b64encode.called

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called

        assert not self.mock_open.called

    def test_data_is_str_raises(self):
        with pytest.raises(ValueError):
            encrypt(self.password, 'test_data')

        assert not self.mock_urandom.called
        assert not self.mock_get_fernet.called
        assert not self.mock_get_fernet.return_value.encrypt.called
        assert not self.mock_urlsafe_b64encode.called

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called

        assert not self.mock_open.called

    def test_no_outfile(self):
        expected = b'test_encoded_salt$test_cipher_data'
        actual = encrypt(self.password, self.plaintext)

        assert expected == actual

        self.mock_urandom.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_urandom.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_urandom.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called
        assert not self.mock_open.called

    def test_outfile_no_qr_code(self):
        expected = None
        actual = encrypt(self.password, self.plaintext, outfile='test_outfile.txt')

        assert expected == actual

        self.mock_urandom.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_urandom.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_urandom.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called

        self.mock_open.assert_called_once_with('test_outfile.txt', 'wb')
        self.mock_open.return_value.write.assert_called_once_with(b'test_encoded_salt$test_cipher_data')

    def test_outfile_qr_code(self):
        expected = None
        actual = encrypt(self.password, self.plaintext, outfile='test_outfile.png')

        assert expected == actual

        self.mock_urandom.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_urandom.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_urandom.return_value)

        self.mock_qrcode.make.assert_called_once_with(b'test_encoded_salt$test_cipher_data')
        self.mock_qrcode.make.return_value.save.assert_called_once_with('test_outfile.png')

        assert not self.mock_open.called

class TestDecrypt(object):
    def setup_method(self):
        self._get_fernet_patcher = mock.patch('lockbox.main._get_fernet')
        self.mock_get_fernet = self._get_fernet_patcher.start()
        self.mock_get_fernet.return_value.encrypt.return_value = b'test_cipher_data'

        self.urlsafe_b64decode_patcher = mock.patch('lockbox.main.base64.urlsafe_b64decode')
        self.mock_urlsafe_b64decode = self.urlsafe_b64decode_patcher.start()
        self.mock_urlsafe_b64decode.return_value = b'test_decoded_salt'

        self.password = b'password'
        self.ciphertext = b'ciphertext'

    def teardown_method(self):
        self._get_fernet_patcher.stop()
        self.urlsafe_b64decode_patcher.stop()

    def test_password_is_str_raises(self):
        with pytest.raises(ValueError):
            decrypt('password', self.ciphertext)

        assert not self.mock_urlsafe_b64decode.called
        assert not self.mock_get_fernet.called

    def test_cipher_data_is_str_raises(self):
        with pytest.raises(ValueError):
            decrypt(self.password, 'ciphertext')

        assert not self.mock_urlsafe_b64decode.called
        assert not self.mock_get_fernet.called
