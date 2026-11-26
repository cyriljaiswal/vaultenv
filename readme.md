# envvault

A lightweight, passphrase-encrypted local CLI vault for storing environment variables, API keys, and recurring shell/Git snippets without risking accidental `.env` or secret commits to Git.

## Features

- **Add & Update Entries:** Store named secrets, environment values, or command snippets with comma-separated tags.
- **Passphrase Encryption:** Encrypts vault data at rest using **PBKDF2HMAC (SHA-256)** for key derivation and **Fernet** symmetric encryption (`~/.envvault/vault.enc.json`).
- **Fast Lookup & Search:** List entries (with optional tag filtering) or search by entry name and tags.
- **Clipboard Support:** Print values to stdout or copy directly to the clipboard with `--copy`.
- **Delete Entries:** Remove obsolete keys or snippets cleanly from the vault.

## Project Structure

```text
envvault/
├── envvault.py
├── requirements.txt
├── .gitignore
└── README.md