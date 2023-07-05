import os
import getpass
from pathlib import Path

from lockbox import (encrypt,
                     decrypt,
                     encrypt_file,
                     decrypt_file,
                     encrypt_directory,
                     decrypt_directory,
                     LockBoxException,
                     LOCKBOX_SUFFIX,
                     )

from blessings import Terminal

term = Terminal()
YES = ('y', 'yes')

def cli_encrypt(passphrase,
                infile=None,
                outfile=None,
                data=None,
                recursive=False,
                remove_original=False,
                force=False):
    if infile:
        infile = Path(infile)

    if outfile:
        outfile = Path(outfile)
    else:
        if infile:
            outfile = infile.parent / f'{infile.name}{LOCKBOX_SUFFIX}'

    _validate_files(infile, outfile, force)
    _confirm_passphrase(passphrase)

    if data:
        stdout_data = encrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        if infile.is_file():
            encrypt_file(passphrase,
                         infile,
                         output_file=outfile,
                         remove_original=remove_original)
        elif infile.is_dir():
            if not recursive:
                raise LockBoxException('{} is a directory but --recursive has not been specified'.format(infile))
            else:
                encrypt_directory(passphrase, infile)

def _validate_files(infile, outfile, force):
    if infile and not infile.exists():
        raise LockBoxException(f'{infile} does not exist')
    if outfile and not force and outfile.exists():
        print(
            term.yellow(
                f'WARNING: {outfile} already exists\n'))
        confirm = input(
            term.yellow(
                f'Are you absolutely sure you want to delete {outfile}? [y/N] '))
        if confirm.lower() not in YES:
            raise LockBoxException('Overwrite not allowed')


def _confirm_passphrase(passphrase):
    confirm_passphrase = getpass.getpass('Confirm passphrase: ').encode('utf-8')

    if passphrase != confirm_passphrase:
        print('passphrases do not match')
        raise LockBoxException('Passphrases do not match')


def cli_decrypt(passphrase,
                infile=None,
                outfile=None,
                data=None,
                recursive=False,
                remove_original=False,
                force=False):
    if infile:
        infile = Path(infile)

    if outfile:
        outfile = Path(outfile)
    else:
        if infile and infile.suffix == LOCKBOX_SUFFIX:
            outfile = infile.parent / infile.stem
        elif not data:
            raise LockBoxException(
                f'Could not automatically determine output file name for {infile}')

    _validate_files(infile, outfile, force)
    _confirm_passphrase(passphrase)

    if data:
        stdout_data = decrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        if infile.is_file():
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
