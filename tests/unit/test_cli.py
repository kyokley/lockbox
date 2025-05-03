import pytest

from pathlib import Path
from src.lockbox.cli import (
    cli_encrypt,
    cli_decrypt,
)


class TestCliEncrypt:
    @pytest.fixture(autouse=True)
    def setUp(self, mocker, temp_dir):
        self.temp_dir = temp_dir

        self.mock_getpass = mocker.patch("src.lockbox.cli.getpass.getpass")
        self.mock_encrypt = mocker.patch("src.lockbox.cli.encrypt")
        self.mock_encrypt_file = mocker.patch("src.lockbox.cli.encrypt_file")
        self.mock_encrypt_directory = mocker.patch("src.lockbox.cli.encrypt_directory")
        self.mock_print = mocker.patch("src.lockbox.cli.print")

        self.passphrase = b"test_passphrase"
        self.mock_getpass.return_value = "test_passphrase"

        self.infile = Path("test_infile")
        self.outfile = Path("test_outfile")

    def test_input_from_string(self):
        expected = None
        actual = cli_encrypt(self.passphrase, outfile=self.outfile, data="test_string")

        assert expected == actual
        self.mock_encrypt.assert_called_once_with(
            self.passphrase, "test_string", outfile=self.outfile
        )
        assert not self.mock_encrypt_file.called
        self.mock_print.assert_called_once_with(
            self.mock_encrypt.return_value.decode.return_value
        )


class TestCliDecrypt:
    @pytest.fixture(autouse=True)
    def setUp(self, mocker, temp_dir):
        self.temp_dir = temp_dir

        self.mock_getpass = mocker.patch("src.lockbox.cli.getpass.getpass")
        self.mock_decrypt = mocker.patch("src.lockbox.cli.decrypt")

        self.mock_decrypt_file = mocker.patch("src.lockbox.cli.decrypt_file")

        self.mock_decrypt_directory = mocker.patch("src.lockbox.cli.decrypt_directory")

        self.mock_print = mocker.patch("src.lockbox.cli.print")

        self.passphrase = b"test_passphrase"
        self.mock_getpass.return_value = "test_passphrase"

        self.infile = Path("test_infile")
        self.outfile = Path("test_outfile")

    def test_input_from_string(self):
        expected = None
        actual = cli_decrypt(
            self.passphrase, outfile=self.outfile, data="test_encrypted_string"
        )

        assert expected == actual
        self.mock_decrypt.assert_called_once_with(
            self.passphrase, "test_encrypted_string", outfile=self.outfile
        )
        self.mock_print.assert_called_once_with(
            self.mock_decrypt.return_value.decode.return_value
        )
        assert not self.mock_decrypt_file.called
        assert not self.mock_decrypt_directory.called
