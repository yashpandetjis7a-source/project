# Password Generator & Vault

A beginner-friendly Python desktop application that generates strong random passwords and stores website login details in an encrypted local vault.

## Features

- Generate random passwords from 8 to 64 characters.
- Include or exclude symbols.
- Copy generated passwords to the clipboard.
- Save website/app names, usernames, and passwords.
- Encrypt saved vault entries using the `cryptography` library.
- Unlock the vault with a master password.
- View or delete saved login entries through a Tkinter GUI.

## Requirements

- Python 3.9 or newer recommended
- `cryptography` Python package
- Tkinter (included with most standard Python installations)

## Installation

1. Install Python from [python.org](https://www.python.org/downloads/) if it is not already installed.
2. Download or clone this project.
3. Open a terminal in the project folder.
4. Install the dependency:

   ```bash
   python -m pip install cryptography
   ```

## Run the Application

Run this command from the folder containing `password_vault.py`:

```bash
python password_vault.py
```

On some Windows installations, you may need to use:

```bash
py password_vault.py
```

The first time you launch the app, create a master password of at least 12 characters. On later launches, enter the same master password to unlock the vault.

## How to Use

1. **Generate a password:** Choose a length between 8 and 64, choose whether to include symbols, and click **Generate**.
2. **Copy a password:** Click **Copy** to copy the generated password to the clipboard.
3. **Fill the password field:** Click **Use Generated** to place the generated password in the login form.
4. **Save a login:** Enter the website/app name, username/email, and password, then click **Save Login**.
5. **View a saved password:** Select a saved login and click **View Selected Password**.
6. **Delete a login:** Select an entry and click **Delete Selected**, then confirm.
7. **Refresh the list:** Click **Refresh** to reload the visible list from the current in-memory vault data.

## Project Structure

```text
Password-Generator-Vault/
├── password_vault.py       # Main Python application
├── README.md               # Project documentation
└── password_vault.json     # Created automatically when the vault is first created
```

The `password_vault.json` file stores a salt and encrypted vault data. It is generated automatically in the current working directory when the application first runs.

## Technologies Used

- **Python** — application logic
- **Tkinter** — desktop graphical user interface
- **secrets** — cryptographically strong random password generation
- **cryptography (Fernet)** — encryption and integrity protection for vault data
- **PBKDF2-HMAC-SHA256** — derives an encryption key from the master password
- **JSON** — file format for the encrypted vault container

## Security Notes and Limitations

- Use a long, unique master password and do not share it.
- The master password is not stored by the application. If you forget it, the vault cannot be unlocked by this program.
- Keep a secure backup of `password_vault.json`. Losing it means losing the saved entries.
- The application copies generated passwords to the system clipboard when you use **Copy**. Other applications may be able to read clipboard contents, so avoid leaving sensitive passwords there.
- Passwords are shown in a dialog when you choose **View Selected Password**.
- This is an educational project, not an independently audited password manager. Do not rely on it as the only storage location for critical credentials.
- The current version does not provide password recovery, automatic clipboard clearing, multi-user support, or cloud synchronization.
- Store backups securely and avoid committing a real `password_vault.json` file containing your personal encrypted vault to a public repository.

## Troubleshooting

### `ModuleNotFoundError: No module named 'cryptography'`

Install the dependency:

```bash
python -m pip install cryptography
```

### Tkinter is missing

Most Windows and macOS Python installers include Tkinter. On some Linux distributions, install the system package for Tkinter (for example, `python3-tk`) using your distribution's package manager.

### The master password is rejected

Check that you entered the same master password used when the vault was created. There is no password reset or recovery function in this version.

## Possible Future Improvements

- Add password search and sorting.
- Add a password-strength meter.
- Add an option to reveal/hide the password field.
- Add automatic clipboard clearing.
- Add encrypted export and backup tools.
- Add unit tests and improved error handling.

## License

This project is provided for educational use. Add a license file if you plan to distribute or publish it publicly.
