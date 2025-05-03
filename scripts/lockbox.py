import getpass
import sys
import argparse

from blessings import Terminal

from src.lockbox import LockBoxException
from src.lockbox._version import get_versions
from src.lockbox.cli import cli_encrypt, cli_decrypt

VERSION = get_versions()["version"]

term = Terminal()

parser = argparse.ArgumentParser(
    prog="lockbox",
    description="Simple cryptographic CLI",
)
parser.add_argument("--version", action="store_true")

subparsers = parser.add_subparsers(dest="subcommand")
encrypt_parser = subparsers.add_parser(
    "encrypt",
    description="Encrypt data",
    epilog="""
Be careful using the -s STRING option on the command line as your unencrypted plaintext may be stored in your history.
Also, when using the -s option, any data provided through stdin will be ignored.
        """,
)
input_group = encrypt_parser.add_mutually_exclusive_group()
input_group.add_argument(
    "-s",
    "--string",
    help="string to be used as the input data for encrypting",
)
input_group.add_argument(
    "-i",
    "--input",
    help="file or directory to be used for input",
)
encrypt_parser.add_argument(
    "-o",
    "--output",
    help="file to be used for outputted data, specifying an output file with a '.png' extension will write a QR code",
)
encrypt_parser.add_argument(
    "-r",
    "--recursive",
    help="recursively encrypt all files in the directory given as input",
    action="store_true",
)
encrypt_parser.add_argument(
    "--remove-original",
    help="delete input file after encryption is completed",
    action="store_true",
)
encrypt_parser.add_argument(
    "-f",
    "--force",
    help="ignore warnings and force action",
    action="store_true",
)

decrypt_parser = subparsers.add_parser(
    "decrypt",
    description="Decrypt data",
    epilog="""
Be careful using the -s STRING option on the command line as your unencrypted plaintext may be stored in your history.
Also, when using the -s option, any data provided through stdin will be ignored.
        """,
)
input_group = decrypt_parser.add_mutually_exclusive_group()
input_group.add_argument(
    "-s",
    "--string",
    help="string to be used as the input data for decrypting",
)
input_group.add_argument(
    "-i",
    "--input",
    help="file or directory to be used for input",
)
decrypt_parser.add_argument(
    "-o",
    "--output",
    help="file to be used for outputted data, specifying an output file with a '.png' extension will write a QR code",
)
decrypt_parser.add_argument(
    "-r",
    "--recursive",
    help="recursively decrypt all files in the directory given as input",
    action="store_true",
)
decrypt_parser.add_argument(
    "--remove-original",
    help="delete input file after decryption is completed",
    action="store_true",
)
decrypt_parser.add_argument(
    "-f",
    "--force",
    help="ignore warnings and force action",
    action="store_true",
)
args = parser.parse_args()


def main():
    if args.subcommand not in ("encrypt", "decrypt"):
        print(f"lockbox {VERSION}")
        return

    infile = args.input
    outfile = args.output
    string = args.string
    recursive = args.recursive
    remove_original = args.remove_original
    force = args.force

    if string:
        string = string.encode("utf-8")

    stdin_data = None
    if not string and (not infile or infile == "-"):
        stdin_data = sys.stdin.read().encode("utf-8")
    data = stdin_data or string

    passphrase = getpass.getpass("Enter passphrase: ").encode("utf-8")

    if args.subcommand == "encrypt":
        cli_encrypt(
            passphrase,
            infile=infile,
            outfile=outfile,
            data=data,
            recursive=recursive,
            remove_original=remove_original,
            force=force,
        )
    elif args.subcommand == "decrypt":
        cli_decrypt(
            passphrase,
            infile=infile,
            outfile=outfile,
            data=data,
            recursive=recursive,
            remove_original=remove_original,
            force=force,
        )


def run():
    try:
        main()
    except LockBoxException as e:
        print(term.red(str(e)))
    except KeyboardInterrupt:
        print(term.red("Aborted"))


if __name__ == "__main__":
    run()
