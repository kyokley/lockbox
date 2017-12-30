# LockBox
Simple Passphrase-based AES Encryption

## Purpose
Lockbox is a wrapper around [cryptography's](https://cryptography.io/en/latest/) fernet symmetric key encryption implementation. The goal is to be as simple as possible. The only inputs required are a passphrase and the data to be encrypted/decrypted.

## Usage:
```
>>> from lockbox import encrypt, decrypt

>>> ciphertext = encrypt(b'password', b'this is a secret')
>>> ciphertext
b'vMFVfjg...'

>>> decrypt(b'password', ciphertext)
b'this is a secret'
```
Or using the CLI,
```bash
$ lockbox encrypt -s 'this is a secret'
Enter passphrase:
Confirm passphrase:
vMFVfjg...

$ lockbox decrypt 'vMFVfjg...'
Enter passphrase:
this is a string

$ lockbox -h
Usage:
    lockbox <cmd> [<input>] [options]
    lockbox --version
    lockbox --help

Arguments:
    cmd    encrypt or decrypt
    input  file to be used for input
           specify '-' to use stdin

Options:
    -s STRING --string=STRING   STRING to be used as the input data for encrypting/decrypting
    -o FILE --output=FILE       file to be used for outputted data
                                specifying an output file with a '.png'
                                extension will write a QR code to FILE
    -h --help                   display this help

Without -o FILE given, lockbox will display data to stdout

Be careful using the -s STRING option on the command line as your unencrypted plaintext may be stored in your history.
Also, when using the -s option, any data provided through stdin will be ignored.
```
