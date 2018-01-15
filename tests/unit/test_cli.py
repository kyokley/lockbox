import mock
import pytest

from lockbox import LockBoxException
from lockbox.cli import (cli_encrypt,
                         cli_decrypt,
                         )

class TestCliEncrypt(object):
    def setup_method(self):
        self.getpass_patcher = mock.patch('lockbox.cli.getpass.getpass')
        self.mock_getpass = self.getpass_patcher.start()

        self.encrypt_patcher = mock.patch('lockbox.cli.encrypt')
        self.mock_encrypt = self.encrypt_patcher.start()

        self.encrypt_file_patcher = mock.patch('lockbox.cli.encrypt_file')
        self.mock_encrypt_file = self.encrypt_file_patcher.start()

        self.encrypt_directory_patcher = mock.patch('lockbox.cli.encrypt_directory')
        self.mock_encrypt_directory = self.encrypt_directory_patcher.start()

        self.print_patcher = mock.patch('lockbox.cli.print')
        self.mock_print = self.print_patcher.start()

        self.isfile_patcher = mock.patch('lockbox.cli.os.path.isfile')
        self.mock_isfile = self.isfile_patcher.start()

        self.isdir_patcher = mock.patch('lockbox.cli.os.path.isdir')
        self.mock_isdir = self.isdir_patcher.start()

        self.passphrase = b'test_passphrase'
        self.mock_getpass.return_value = 'test_passphrase'

        self.infile = 'test_infile'
        self.outfile = 'test_outfile'

    def teardown_method(self):
        self.getpass_patcher.stop()
        self.encrypt_patcher.stop()
        self.print_patcher.stop()
        self.encrypt_file_patcher.stop()
        self.isfile_patcher.stop()
        self.encrypt_directory_patcher.stop()
        self.isdir_patcher.stop()

    def test_passphrase_does_not_match(self):
        self.mock_getpass.return_value = 'incorrect_passphrase'

        expected = None
        actual = cli_encrypt(self.passphrase,
                             self.infile,
                             self.outfile)

        assert expected == actual
        self.mock_print.assert_called_once_with('passphrases do not match')
        assert not self.mock_encrypt.called
        assert not self.mock_encrypt_file.called

    def test_input_from_string(self):
        expected = None
        actual = cli_encrypt(self.passphrase,
                             self.infile,
                             self.outfile,
                             data='test_string')

        assert expected == actual
        self.mock_encrypt.assert_called_once_with(self.passphrase,
                                                  'test_string',
                                                  outfile=self.outfile)
        assert not self.mock_encrypt_file.called
        self.mock_print.assert_called_once_with(self.mock_encrypt.return_value.decode.return_value)

    def test_input_file(self):
        self.mock_isfile.return_value = True
        self.mock_isdir.return_value = False

        expected = None
        actual = cli_encrypt(self.passphrase,
                             self.infile,
                             self.outfile,
                             )

        assert expected == actual
        assert not self.mock_encrypt.called
        self.mock_encrypt_file.assert_called_once_with(self.passphrase,
                                                       self.infile,
                                                       output_file=self.outfile,
                                                       remove_original=False)
        assert not self.mock_print.called

    def test_input_directory_no_recursive(self):
        self.mock_isfile.return_value = False
        self.mock_isdir.return_value = True

        with pytest.raises(LockBoxException):
            cli_encrypt(self.passphrase,
                        self.infile,
                        self.outfile,
                        recursive=False
                        )

        assert not self.mock_encrypt.called
        assert not self.mock_encrypt_file.called
        assert not self.mock_print.called

    def test_input_directory_recursive(self):
        self.mock_isfile.return_value = False
        self.mock_isdir.return_value = True

        expected = None
        actual = cli_encrypt(self.passphrase,
                             self.infile,
                             self.outfile,
                             recursive=True
                             )

        assert expected == actual
        assert not self.mock_encrypt.called
        assert not self.mock_encrypt_file.called
        self.mock_encrypt_directory.assert_called_once_with(self.passphrase, self.infile)
        assert not self.mock_print.called

class TestCliDecrypt(object):
    def setup_method(self):
        self.decrypt_patcher = mock.patch('lockbox.cli.decrypt')
        self.mock_decrypt = self.decrypt_patcher.start()

        self.decrypt_file_patcher = mock.patch('lockbox.cli.decrypt_file')
        self.mock_decrypt_file = self.decrypt_file_patcher.start()

        self.decrypt_directory_patcher = mock.patch('lockbox.cli.decrypt_directory')
        self.mock_decrypt_directory = self.decrypt_directory_patcher.start()

        self.isfile_patcher = mock.patch('lockbox.cli.os.path.isfile')
        self.mock_isfile = self.isfile_patcher.start()

        self.isdir_patcher = mock.patch('lockbox.cli.os.path.isdir')
        self.mock_isdir = self.isdir_patcher.start()

        self.print_patcher = mock.patch('lockbox.cli.print')
        self.mock_print = self.print_patcher.start()

        self.passphrase = b'test_passphrase'

        self.infile = 'test_infile'
        self.outfile = 'test_outfile'

    def teardown_method(self):
        self.decrypt_patcher.stop()
        self.print_patcher.stop()
        self.decrypt_file_patcher.stop()
        self.decrypt_directory_patcher.stop()
        self.isfile_patcher.stop()
        self.isdir_patcher.stop()

    def test_input_from_string(self):
        expected = None
        actual = cli_decrypt(self.passphrase,
                             self.infile,
                             self.outfile,
                             data='test_encrypted_string')

        assert expected == actual
        self.mock_decrypt.assert_called_once_with(self.passphrase,
                                                  'test_encrypted_string',
                                                  outfile=self.outfile)
        self.mock_print.assert_called_once_with(self.mock_decrypt.return_value.decode.return_value)
        assert not self.mock_decrypt_file.called
        assert not self.mock_decrypt_directory.called

    def test_input_file(self):
        self.mock_isfile.return_value = True
        self.mock_isdir.return_value = False

        expected = None
        actual = cli_decrypt(self.passphrase,
                             self.infile,
                             self.outfile)

        assert expected == actual
        self.mock_decrypt_file.assert_called_once_with(self.passphrase,
                                                       self.infile,
                                                       output_file=self.outfile,
                                                       remove_original=False)
        assert not self.mock_print.called
        assert not self.mock_decrypt.called
        assert not self.mock_decrypt_directory.called

    def test_input_directory_no_recursive(self):
        self.mock_isfile.return_value = False
        self.mock_isdir.return_value = True

        with pytest.raises(LockBoxException):
            cli_decrypt(self.passphrase,
                        self.infile,
                        self.outfile,
                        recursive=False)

        assert not self.mock_decrypt_file.called
        assert not self.mock_print.called
        assert not self.mock_decrypt.called
        assert not self.mock_decrypt_directory.called

    def test_input_directory_with_recursive(self):
        self.mock_isfile.return_value = False
        self.mock_isdir.return_value = True

        expected = None
        actual = cli_decrypt(self.passphrase,
                             self.infile,
                             self.outfile,
                             recursive=True)

        assert expected == actual
        assert not self.mock_decrypt_file.called
        assert not self.mock_print.called
        assert not self.mock_decrypt.called
        self.mock_decrypt_directory.assert_called_once_with(self.passphrase, self.infile)
