# XOR_OTP

A small command-line tool that encrypts and decrypts data with a **one-time pad** (XOR).

Give it a string or a file and it produces two files:

1. the **encrypted output** (the input XORed with the pad), and
2. a freshly generated, cryptographically secure **one-time pad** of the same length.

Give it the encrypted file and the pad and it restores the original.

> **Educational tool.** A one-time pad is only secure when it is used correctly. Read [Security notes](#security-notes) before relying on it for anything real.

## Requirements

- Python 3.6 or newer
- No third-party packages (standard library only)

## Usage

```
python xor_.py (-s STRING | -f FILE) -o OUTPUT [-p PADOUT | -k KEYFILE] [--force]
```

| Option | Description |
|---|---|
| `-s`, `--string` | Text to encrypt (encryption only) |
| `-f`, `--file` | File to encrypt or decrypt |
| `-o`, `--output` | Where to save the result (required) |
| `-p`, `--padout` | Where to save the newly generated pad (required when encrypting) |
| `-k`, `--keyfile` | Existing pad file; providing this switches to decryption |
| `--force` | Allow overwriting existing files (otherwise they are never overwritten) |

Run with no arguments to print the help text.

### Encrypt a string

```
python xor_.py -s "My Secret Data" -o encrypted.bin -p secret.pad
```

### Encrypt a file

```
python xor_.py -f document.pdf -o document.enc -p document.pad
```

### Decrypt

```
python xor_.py -f encrypted.bin -k secret.pad -o restored.txt
```

## Safety checks built in

- Refuses to overwrite existing files unless `--force` is given.
- Refuses to run if the output, pad, input or key paths overlap, so the pad can't be destroyed by accident.
- On decryption, the pad must be exactly the same length as the encrypted file; a mismatch almost always means the wrong pad.
- `-s` cannot be combined with `-k`, and `-p` cannot be combined with `-k`.
- Empty input is rejected.
- The pad file is created with owner-only permissions (`0600`) on Unix-like systems.

## Security notes

- **Never reuse a pad.** Reusing a pad for two messages lets an attacker XOR the two ciphertexts together and recover information about both plaintexts. Generate a new pad for every encryption (the tool does this automatically).
- **Keep the pad secret and separate.** Anyone who holds both the encrypted file and the pad can recover the original. Transport and store them through different channels.
- **No integrity or authentication.** XOR encryption does not detect tampering. Someone who can modify the ciphertext can flip chosen bits in the decrypted result.
- **Length is not hidden.** The encrypted file is exactly as long as the original.
- **The pad is as big as the data**, so this is impractical for large files, and the whole input is read into memory at once.
- **Deleting files does not securely erase them.** Remove the pad and plaintext with care once you no longer need them.
- The pad comes from `os.urandom`, which is the operating system's cryptographically secure random source.

## Verifying the download

A `SHA256SUMS` file is published with each release. After downloading, check the script:

```
sha256sum -c SHA256SUMS
```

If the release is GPG-signed, also verify the signature:

```
gpg --verify xor_.py.asc xor_.py
```

## Contributing

Issues and pull requests are welcome. Please keep the tool dependency-free.

## License

MIT. See the `LICENSE` file.
