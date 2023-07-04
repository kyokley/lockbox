#!/usr/bin/env python
"""
Usage:
    lockbox encrypt (--string=STRING | [-] | <INPUT> [--remove-original]) [--output=FILE] [--recursive] [--force]
    lockbox decrypt (--string=STRING | [-] | <INPUT> [--remove-original]) [--output=FILE] [--recursive] [--force]
    lockbox --version
    lockbox --help

Arguments:
    INPUT  file or directory to be used for input
           specify '-' to use stdin

Options:
    -s STRING --string=STRING   STRING to be used as the input data for encrypting/decrypting
    -o FILE --output=FILE       file to be used for outputted data
                                specifying an output file with a '.png'
                                extension will write a QR code to FILE
    -r --recursive              recursively encrypt all files in the directory given as input
    --remove-original           delete input file after encrypt/decrypt is completed
    -f --force                  ignore warnings and force action
    -h --help                   display this help

Without -o FILE given, lockbox will display data to stdout

Be careful using the -s STRING option on the command line as your unencrypted plaintext may be stored in your history.
Also, when using the -s option, any data provided through stdin will be ignored.
"""
import getpass
import sys

from docopt import docopt
from blessings import Terminal

from lockbox import LockBoxException
from lockbox._version import get_versions
from lockbox.cli import (cli_encrypt,
                         cli_decrypt)

VERSION = get_versions()['version']

term = Terminal()

def main(args):
    infile = args['<INPUT>']
    outfile = args['--output']
    string = args['--string']
    recursive = args['--recursive']
    remove_original = args['--remove-original']
    force = args['--force']

    if string:
        string = string.encode('utf-8')

    stdin_data = None
    if not string and (not infile or infile == '-'):
        stdin_data = sys.stdin.read().encode('utf-8')
    data = stdin_data or string

    passphrase = getpass.getpass('Enter passphrase: ').encode('utf-8')

    if args['encrypt']:
        cli_encrypt(passphrase,
                    infile=infile,
                    outfile=outfile,
                    data=data,
                    recursive=recursive,
                    remove_original=remove_original,
                    force=force)
    elif args['decrypt']:
        cli_decrypt(passphrase,
                    infile=infile,
                    outfile=outfile,
                    data=data,
                    recursive=recursive,
                    remove_original=remove_original,
                    force=force)


def run():
    args = docopt(__doc__, version=VERSION)

    if args['--version']:
        print(VERSION)
    else:
        try:
            main(args)
        except LockBoxException as e:
            print(term.red(str(e)))
        except KeyboardInterrupt:
            print(term.red('Aborted'))

if __name__ == '__main__':
    run()
