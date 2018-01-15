import os
import getpass

from lockbox import (encrypt,
                     decrypt,
                     encrypt_file,
                     decrypt_file,
                     encrypt_directory,
                     decrypt_directory,
                     LockBoxException,
                     )

def cli_encrypt(passphrase,
                infile,
                outfile,
                data=None,
                recursive=False):
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
            encrypt_file(passphrase, infile, output_file=outfile)
        elif os.path.isdir(infile):
            if not recursive:
                raise LockBoxException('{} is a directory but --recursive has not been specified'.format(infile))
            else:
                encrypt_directory(passphrase, infile)

def cli_decrypt(passphrase,
                infile,
                outfile,
                data=None,
                recursive=False):
    if data:
        stdout_data = decrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        if os.path.isfile(infile):
            decrypt_file(passphrase, infile, output_file=outfile)
        elif os.path.isdir(infile):
            if not recursive:
                raise LockBoxException('{} is a directory but --recursive has not been specified'.format(infile))
            else:
                decrypt_directory(passphrase, infile)
