"""Save a provider credential outside the repo via hidden interactive input."""
import argparse
import getpass
import os
from pathlib import Path
import re
import sys
import tempfile


def save_key(provider, value, directory=None, replace=False):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', provider):
        raise ValueError('Use a lowercase provider name, such as comfy or higgsfield')
    if not value.strip() or any(c in value for c in ('\n', '\r', '\x00')):
        raise ValueError('Enter one nonempty credential')
    directory = Path(directory or Path.home() / '.config/siljangnim-shorts')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = directory / (provider + '-token')
    if target.exists() and not replace:
        raise ValueError('A key already exists; use --replace only when replacing it')
    fd, name = tempfile.mkstemp(dir=directory, prefix='.key-')
    try:
        with os.fdopen(fd, 'w') as file:
            os.fchmod(file.fileno(), 0o600)
            file.write(value.strip() + '\n')
        if replace:
            os.replace(name, target)
        else:
            os.link(name, target)  # Fail if another writer created the key in the meantime.
    finally:
        Path(name).unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('provider')
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args()
    if not sys.stdin.isatty():
        parser.error('Run in an interactive terminal; paste the key into the hidden prompt, not the chat or command line')
    try:
        path = save_key(args.provider, getpass.getpass('API key (hidden): '), replace=args.replace)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f'Key saved to {path}. API access has not yet been validated.')


if __name__ == '__main__':
    main()
