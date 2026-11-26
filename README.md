# 🔐 envvault

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Cryptography](https://img.shields.io/badge/Encryption-PBKDF2_%2B_Fernet-10B981?style=flat-square)
![CLI](https://img.shields.io/badge/Interface-CLI-18181B?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-6366F1?style=flat-square)

A lightweight, **passphrase-encrypted local CLI vault** built in Python for securely storing environment variables, API keys, and recurring shell/Git snippets—eliminating the risk of accidentally committing `.env` files or plaintext secrets to Git.

---

## ✨ Key Features

* **🔒 Strong Local Encryption at Rest:** Derives a cryptographic key from your master passphrase using **PBKDF2HMAC (SHA-256, 480,000 iterations)** with a unique random salt, and encrypts vault payloads with **Fernet** (`~/.envvault/vault.enc.json`).
* **⚡ Fast Add & Update:** Store named secrets, environment values, or multi-step terminal commands with comma-separated tags.
* **🏷️ Tag-Based Filtering & Search:** Quickly list all saved keys, filter by specific tags, or search across entry names and tags.
* **📋 One-Flag Clipboard Copy:** Print a secret directly to `stdout` or copy it straight to your system clipboard (`--copy`) across Windows, macOS, and Linux.
* **🗑️ Clean Deletion:** Remove outdated tokens or snippets from your encrypted store anytime.
* **🤖 Non-Interactive Support:** Supports `ENVVAULT_PASS` environment variable for automated scripts and unit testing.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ (`argparse`, `getpass`, `json`, `pathlib`) |
| **Encryption & KDF** | `cryptography` (`Fernet` + `PBKDF2HMAC` with `SHA-256`) |
| **Storage Format** | Local JSON envelope (`~/.envvault/vault.enc.json`) |
| **Testing** | Python `unittest` |

---

## 📂 Project Structure

```text
envvault/
├── envvault.py        # Main CLI entrypoint, encryption logic & command handlers
├── test_envvault.py   # Automated unit tests for encryption & CLI workflows
├── requirements.txt   # Python dependencies (cryptography)
├── .gitignore         # Ignores virtual environments, caches, and .env files
└── README.md          # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.10+** and `pip`

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/cyriljaiswal/vaultenv.git
   cd vaultenv
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 CLI Usage

On your first run, `envvault` will prompt you to create and confirm a master passphrase. For non-interactive shells or tests, you can optionally export `ENVVAULT_PASS`.

### 1. Add or update a secret/snippet

```bash
python envvault.py add RENDER_API_KEY "rnd_your_secret_key" --tags api,deploy
python envvault.py add GIT_SYNC_MAIN "git checkout -B main && git add . && git commit -m 'chore: update' && git push -u origin main" --tags git,workflow
```

### 2. List saved entries

```bash
python envvault.py list
python envvault.py list --tag git
```

### 3. Search by keyword or tag

```bash
python envvault.py search deploy
```

### 4. Retrieve or copy a value

```bash
python envvault.py get RENDER_API_KEY
python envvault.py get GIT_SYNC_MAIN --copy
```

### 5. Delete an entry

```bash
python envvault.py delete RENDER_API_KEY
```

---

## 🧪 Running Tests

Run the unit test suite to verify encryption, wrong-passphrase rejection, and CLI commands:

```bash
python -m unittest discover -v
```

---

## 🛡️ Security Notes

* **No Passphrase Recovery:** Because keys are derived strictly from your master passphrase via PBKDF2, losing your passphrase means the encrypted vault cannot be recovered.
* **Keep Vault Files Local:** Never commit `~/.envvault/vault.enc.json` or plaintext `.env` files to version control.
* **Use High-Entropy Passphrases:** Choose a strong, unique passphrase to maximize resistance against offline brute-force attacks.

---

## 🔮 Roadmap

* [x] Passphrase-based encryption (`PBKDF2HMAC` + `Fernet`)
* [x] Cross-platform clipboard copy support (`--copy`)
* [ ] Unit test suite (`test_envvault.py`)
* [ ] Bulk `.env` file import and export (`import-env` / `export-env`)
* [ ] Master passphrase rotation command (`passwd`)
