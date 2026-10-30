#!/usr/bin/env python3
"""XOR One-Time Pad encryption & decryption tool.

Encrypt:  input (string or file) -> XORed output file + newly generated pad file
Decrypt:  XORed file + pad file  -> original data

Educational tool. A one-time pad is only secure if the pad is truly random,
kept secret, as long as the message, and NEVER reused.
"""

import argparse
import os
import sys


def generate_one_time_pad(length: int) -> bytes:
    """Generates a cryptographically secure random key (the pad)."""
    return os.urandom(length)


def xor_bytes(data: bytes, key: bytes) -> bytes:
    """XORs two equal-length byte strings together."""
    if len(data) != len(key):
        raise ValueError("data and key must be the same length")
    n = len(data)
    return (int.from_bytes(data, "big") ^ int.from_bytes(key, "big")).to_bytes(n, "big")


def fail(message: str) -> None:
    print(f"[!] Error: {message}", file=sys.stderr)
    sys.exit(1)


def same_path(a: str, b: str) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def write_file(path: str, data: bytes, force: bool, mode: int = 0o666) -> None:
    """Writes bytes to a file. Refuses to overwrite unless force is set."""
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_BINARY", 0)
    flags |= os.O_TRUNC if force else os.O_EXCL
    try:
        fd = os.open(path, flags, mode)
    except FileExistsError:
        fail(f"'{path}' already exists. Use --force to overwrite it.")
    except OSError as e:
        fail(f"could not write '{path}': {e}")
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def build_parser() -> argparse.ArgumentParser:
    prog = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        prog=prog,
        description="🛡️ XOR One-Time Pad Encryption & Decryption Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples of Usage:
  1. Encrypt a raw text string:
     python {prog} -s "My Secret Data" -o encrypted.bin -p secret.pad

  2. Encrypt a file:
     python {prog} -f document.pdf -o document.enc -p document.pad

  3. Decrypt using the files created:
     python {prog} -f encrypted.bin -k secret.pad -o restored.txt

Notes:
  - Never reuse a pad, and store it separately from the encrypted file.
  - The whole input is read into memory, so very large files are not suitable.
  - Existing files are never overwritten unless --force is given.
""",
    )

    group_input = parser.add_mutually_exclusive_group(required=True)
    group_input.add_argument(
        "-s", "--string", help="Raw message string to encrypt (encryption only)"
    )
    group_input.add_argument(
        "-f", "--file", help="Path to a file to encrypt or decrypt"
    )

    parser.add_argument(
        "-k",
        "--keyfile",
        help="Path to an existing pad file (provide this to decrypt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path where the processed output file will be saved",
    )
    parser.add_argument(
        "-p",
        "--padout",
        help="Path to save the newly generated pad (required when encrypting)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting existing output/pad files",
    )
    return parser


def main() -> None:
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    decrypting = args.keyfile is not None

    # --- Step 1: Validate argument combinations ---
    if decrypting:
        if args.string is not None:
            fail("-s/--string can only be used for encryption, not with -k/--keyfile.")
        if args.padout:
            fail("-p/--padout is only for encryption; it can't be used with -k/--keyfile.")
    elif not args.padout:
        fail("you must specify a destination for the new pad using '-p' or '--padout'.")

    # --- Step 2: Make sure no path will clobber another ---
    paths = {"output": args.output}
    if args.padout:
        paths["pad output"] = args.padout
    if args.file:
        paths["input file"] = args.file
    if decrypting:
        paths["key file"] = args.keyfile

    names = list(paths)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if same_path(paths[a], paths[b]):
                fail(f"{a} and {b} must be different paths ('{paths[a]}').")

    # --- Step 3: Read input data ---
    if args.string is not None:
        input_bytes = args.string.encode("utf-8")
        print(f"[*] Processing input string ({len(input_bytes)} bytes)")
    else:
        if not os.path.isfile(args.file):
            fail(f"target file '{args.file}' not found.")
        with open(args.file, "rb") as f:
            input_bytes = f.read()
        print(f"[*] Read target file '{args.file}' ({len(input_bytes)} bytes)")

    if not input_bytes:
        fail("input is empty; nothing to process.")

    # --- Step 4: Obtain the pad ---
    if decrypting:
        if not os.path.isfile(args.keyfile):
            fail(f"key/pad file '{args.keyfile}' not found.")
        with open(args.keyfile, "rb") as f:
            pad_bytes = f.read()

        if len(pad_bytes) != len(input_bytes):
            fail(
                f"pad length ({len(pad_bytes)} bytes) does not match the input "
                f"length ({len(input_bytes)} bytes). This is probably the wrong pad."
            )
        print(f"[*] Reversing XOR stream using pad: '{args.keyfile}'")
    else:
        print("[*] Generating unique cryptographically secure One-Time Pad...")
        pad_bytes = generate_one_time_pad(len(input_bytes))

    # --- Step 5: XOR ---
    processed_bytes = xor_bytes(input_bytes, pad_bytes)

    # --- Step 6: Write results ---
    # The pad is a secret, so it is created readable/writable by the owner only.
    if not decrypting:
        write_file(args.padout, pad_bytes, args.force, mode=0o600)
        print(f"[+] Security pad saved to: '{args.padout}'")

    write_file(args.output, processed_bytes, args.force)
    print(f"[+] Processed output saved to: '{args.output}'")


if __name__ == "__main__":
    main()
