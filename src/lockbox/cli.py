import getpass

from lockbox import (encrypt,
                     decrypt,
                     encrypt_file,
                     decrypt_file,
                     )

def cli_encrypt(passphrase, infile, outfile, data=None):
    confirm_passphrase = getpass.getpass('Confirm passphrase: ').encode('utf-8')

    if passphrase != confirm_passphrase:
        print('passphrases do not match')
        return

    if data:
        stdout_data = encrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        encrypt_file(passphrase, infile, output_file=outfile)

def cli_decrypt(passphrase, infile, outfile, data=None):
    if data:
        stdout_data = decrypt(passphrase, data, outfile=outfile)
        if stdout_data:
            print(stdout_data.decode('utf-8'))
    else:
        decrypt_file(passphrase, infile, output_file=outfile)
