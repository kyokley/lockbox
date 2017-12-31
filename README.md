# LockBox [![Build Status](https://travis-ci.org/kyokley/lockbox.svg?branch=master)](https://travis-ci.org/kyokley/lockbox)
Simple Passphrase-based AES Encryption

## Purpose
Lockbox is a wrapper around [cryptography's](https://cryptography.io/en/latest/) fernet symmetric key encryption implementation. The goal is to be as simple as possible. The only inputs required are a passphrase and the data to be encrypted/decrypted.

## Usage:
### Basic Examples
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

### Other Examples
Lockbox also works against files
```
from lockbox import encrypt_file, decrypt_file
encrypt_file(b'password', '/path/to/file', output_file='/path/to/file.enc')

decrypt_file(b'password', '/path/to/file.enc', output_file='/path/to/decrypted')
```
In the example above, after completing the decryption step, the files */path/to/file* and */path/to/decrypted* should have the same contents.

## Installation:
Currently, this package is not available on PYPI so the easiest way to install it is to use pip and install from git

From inside a virtualenv, run the following:
```
$ pip install git+https://github.com/kyokley/lockbox/
```

Alternatively, it is possible to compile from source.
```
$ git clone https://github.com/kyokley/lockbox.git
$ cd lockbox
$ python setup.py install
```

## Technical Details
From the cryptography implementation details, the fernet specification is implemented as follows:

> Fernet is built on top of a number of standard cryptographic primitives. Specifically it uses:
>
> - AES in CBC mode with a 128-bit key for encryption; using PKCS7 padding.
> - HMAC using SHA256 for authentication.
> - Initialization vectors are generated using os.urandom().

## Other Considerations
**NOTE:** I have written this package as a way to simplify a common cryptographic process. I make no claims to be a cryptography expert so use this code **AT YOUR OWN RISK**. That being said, if you notice any glaring issues, send me an email or open an issue against the project.
