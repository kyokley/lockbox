import os
import sys
import getpass

from six.moves import input
from lockbox import (encrypt,
                     decrypt,
                     encrypt_file,
                     decrypt_file,
                     encrypt_directory,
                     decrypt_directory,
                     LockBoxException,
                     )

from blessings import Terminal

term = Terminal()
YES = ('y', 'yes')

def cli_encrypt(passphrase,
                infile,
                outfile,
                data=None,
                recursive=False,
                remove_original=False,
                force=False):
    confirm_passphrase = getpass.getpass('Confirm passphrase: ').encode('utf-8')

    if passphrase != confirm_passphrase:
        print('passphrases do not match')
        return

    if data:
        stdout_data = encrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        if os.path.isfile(infile):
            if remove_original and not force:
                if not outfile:
                    print(term.red('WARNING: No output file has been specified. After removing original, data will only be displayed on stdout\n'))
                confirm = input(term.yellow('Are you absolutely sure you want to delete {} after encryption is complete? [y/N] '.format(infile)))
                if confirm.lower() not in YES:
                    return
            encrypt_file(passphrase,
                         infile,
                         output_file=outfile,
                         remove_original=remove_original)
        elif os.path.isdir(infile):
            if not recursive:
                raise LockBoxException('{} is a directory but --recursive has not been specified'.format(infile))
            else:
                encrypt_directory(passphrase, infile)

def cli_decrypt(passphrase,
                infile,
                outfile,
                data=None,
                recursive=False,
                remove_original=False,
                force=False):
    if data:
        stdout_data = decrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        if os.path.isfile(infile):
            if remove_original and not force:
                if not outfile:
                    print(term.red('WARNING: No output file has been specified. After removing original, data will only be displayed on stdout\n'))
                confirm = input(term.yellow('Are you absolutely sure you want to delete {} after decryption is complete? [y/N] '.format(infile)))
                if confirm.lower() not in YES:
                    return
            decrypt_file(passphrase,
                         infile,
                         output_file=outfile,
                         remove_original=remove_original)
        elif os.path.isdir(infile):
            if not recursive:
                raise LockBoxException('{} is a directory but --recursive has not been specified'.format(infile))
            else:
                decrypt_directory(passphrase, infile)
