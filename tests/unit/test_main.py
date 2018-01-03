from unittest import mock
import pytest

from cryptography.fernet import InvalidToken

from lockbox.main import (encrypt,
                          SALT_LENGTH,
                          decrypt,
                          LockBoxException,
                          encrypt_file,
                          _split_encrypted_file,
                          decrypt_file,
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

    def test_password_is_str(self):
        expected = b'test_encoded_salt$test_cipher_data'
        actual = encrypt('test_password', self.plaintext)

        assert expected == actual

        self.mock_urandom.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(b'test_password', self.mock_urandom.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(self.plaintext)
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_urandom.return_value)

        assert not self.mock_qrcode.make.called
        assert not self.mock_qrcode.make.return_value.save.called
        assert not self.mock_open.called

    def test_data_is_str(self):
        expected = b'test_encoded_salt$test_cipher_data'
        actual = encrypt(self.password, 'test_data')

        assert expected == actual

        self.mock_urandom.assert_called_once_with(SALT_LENGTH)
        self.mock_get_fernet.assert_called_once_with(self.password, self.mock_urandom.return_value)
        self.mock_get_fernet.return_value.encrypt.assert_called_once_with(b'test_data')
        self.mock_urlsafe_b64encode.assert_called_once_with(self.mock_urandom.return_value)

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
        self.mock_get_fernet.return_value.decrypt.return_value = b'test_plaintext_data'

        self.urlsafe_b64decode_patcher = mock.patch('lockbox.main.base64.urlsafe_b64decode')
        self.mock_urlsafe_b64decode = self.urlsafe_b64decode_patcher.start()
        self.mock_urlsafe_b64decode.return_value = b'test_decoded_salt'

        self.open_patcher = mock.patch('lockbox.main.open', mock.mock_open())
        self.mock_open = self.open_patcher.start()

        self.password = b'password'
        self.ciphertext = b'encoded_salt$ciphertext'

    def teardown_method(self):
        self._get_fernet_patcher.stop()
        self.urlsafe_b64decode_patcher.stop()
        self.open_patcher.stop()

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

class TestEncryptFile(object):
    def setup_method(self):
        self.exists_patcher = mock.patch('lockbox.main.os.path.exists')
        self.mock_exists = self.exists_patcher.start()

        self.open_patcher = mock.patch('lockbox.main.open', mock.mock_open(read_data=b'lorem ipsum'))
        self.mock_open = self.open_patcher.start()

        self.mock_exists.return_value = True

        self.print_patcher = mock.patch('lockbox.main.print')
        self.mock_print = self.print_patcher.start()

        self.encrypt_patcher = mock.patch('lockbox.main.encrypt')
        self.mock_encrypt = self.encrypt_patcher.start()

        self.password = b'password'
        self.input_file = 'test_input_file.txt'

    def teardown_method(self):
        self.exists_patcher.stop()
        self.open_patcher.stop()
        self.print_patcher.stop()
        self.encrypt_patcher.stop()

    def test_input_file_does_not_exist(self):
        self.mock_exists.return_value = False

        with pytest.raises(LockBoxException):
            encrypt_file(self.password, self.input_file)

        self.mock_exists.assert_called_once_with(self.input_file)

    def test_no_outfile(self):
        expected = None
        actual = encrypt_file(self.password, self.input_file)

        assert expected == actual
        self.mock_encrypt.assert_called_once_with(self.password, b'lorem ipsum')
        self.mock_print.assert_called_once_with(self.mock_encrypt.return_value.decode.return_value)
        self.mock_encrypt.return_value.decode.assert_called_once_with('utf-8')

        assert not self.mock_open.return_value.write.called

    def test_outfile(self):
        expected = None
        actual = encrypt_file(self.password, self.input_file, output_file='output_file.txt')

        assert expected == actual
        self.mock_encrypt.assert_called_once_with(self.password, b'lorem ipsum')
        assert not self.mock_print.called
        self.mock_open.return_value.write.assert_called_once_with(self.mock_encrypt.return_value + b'\n')

class TestDecryptFile(object):
    def setup_method(self):
        self.exists_patcher = mock.patch('lockbox.main.os.path.exists')
        self.mock_exists = self.exists_patcher.start()
        self.mock_exists.return_value = True

        self.decrypt_patcher = mock.patch('lockbox.main.decrypt')
        self.mock_decrypt = self.decrypt_patcher.start()
        self.mock_decrypt.side_effect = [b'decrypted_line1',
                                         b'decrypted_line2',
                                         b'decrypted_line3',
                                         ]

        self._split_encrypted_file_patcher = mock.patch('lockbox.main._split_encrypted_file')
        self.mock_split_encrypted_file = self._split_encrypted_file_patcher.start()
        self.mock_split_encrypted_file.return_value = ['line1', 'line2', 'line3']

        self.open_patcher = mock.patch('lockbox.main.open', mock.mock_open())
        self.mock_open = self.open_patcher.start()

        self.print_patcher = mock.patch('lockbox.main.print')
        self.mock_print = self.print_patcher.start()

        self.password = b'password'
        self.input_file = 'test_input_file.txt'

    def teardown_method(self):
        self.exists_patcher.stop()
        self.decrypt_patcher.stop()
        self._split_encrypted_file_patcher.stop()
        self.open_patcher.stop()
        self.print_patcher.stop()

    def test_input_file_does_not_exist(self):
        self.mock_exists.return_value = False

        with pytest.raises(LockBoxException):
            decrypt_file(self.password, self.input_file)

    def test_no_output_file(self):
        expected = None
        actual = decrypt_file(self.password, self.input_file)

        assert expected == actual
        self.mock_split_encrypted_file.assert_called_once_with(self.input_file)
        self.mock_decrypt.assert_has_calls([mock.call(self.password, 'line1'),
                                            mock.call(self.password, 'line2'),
                                            mock.call(self.password, 'line3'),
                                            ])
        self.mock_print.assert_has_calls([mock.call('decrypted_line1'),
                                          mock.call('decrypted_line2'),
                                          mock.call('decrypted_line3'),
                                          ])
        assert not self.mock_open.called

    def test_with_output_file(self):
        expected = None
        actual = decrypt_file(self.password, self.input_file, output_file='output_file.txt')

        assert expected == actual
        self.mock_split_encrypted_file.assert_called_once_with(self.input_file)
        self.mock_decrypt.assert_has_calls([mock.call(self.password, 'line1'),
                                            mock.call(self.password, 'line2'),
                                            mock.call(self.password, 'line3'),
                                            ])
        assert not self.mock_print.called
        self.mock_open.return_value.write.assert_has_calls([mock.call(b'decrypted_line1'),
                                                            mock.call(b'decrypted_line2'),
                                                            mock.call(b'decrypted_line3'),
                                                            ])
