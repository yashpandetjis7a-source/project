import os
import json
import base64
import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


VAULT_FILE = "password_vault.json"
ITERATIONS = 600_000


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive an encryption key from the master password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))


def generate_password(length=16, use_symbols=True):
    """Generate a password containing uppercase, lowercase, and digits."""
    if length < 8:
        raise ValueError("Choose a password length of at least 8 characters.")

    alphabet = string.ascii_letters + string.digits
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]

    if use_symbols:
        symbols = "!@#$%^&*()-_=+[]{}?"
        alphabet += symbols
        required.append(secrets.choice(symbols))

    remaining = [secrets.choice(alphabet) for _ in range(length - len(required))]
    password_chars = required + remaining
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


class PasswordVault:
    def __init__(self, master_password):
        self.master_password = master_password
        self.salt = None
        self.fernet = None
        self.entries = []
        self._open_or_create()

    def _open_or_create(self):
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, "r", encoding="utf-8") as file:
                saved = json.load(file)

            self.salt = base64.b64decode(saved["salt"])
            key = derive_key(self.master_password, self.salt)
            self.fernet = Fernet(key)

            try:
                decrypted = self.fernet.decrypt(saved["data"].encode("utf-8"))
                self.entries = json.loads(decrypted.decode("utf-8"))
            except (InvalidToken, ValueError, json.JSONDecodeError):
                raise ValueError("Incorrect master password or damaged vault.")
        else:
            self.salt = os.urandom(16)
            key = derive_key(self.master_password, self.salt)
            self.fernet = Fernet(key)
            self.entries = []
            self.save()

    def save(self):
        plaintext = json.dumps(self.entries).encode("utf-8")
        encrypted = self.fernet.encrypt(plaintext)
        saved = {
            "salt": base64.b64encode(self.salt).decode("ascii"),
            "data": encrypted.decode("ascii"),
        }

        # Write to a temporary file before replacing the vault file.
        temporary = VAULT_FILE + ".tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(saved, file)
        os.replace(temporary, VAULT_FILE)

    def add_entry(self, website, username, password):
        self.entries.append({
            "website": website.strip(),
            "username": username.strip(),
            "password": password,
        })
        self.save()

    def delete_entry(self, index):
        del self.entries[index]
        self.save()


class VaultApp:
    def __init__(self, root, vault):
        self.root = root
        self.vault = vault
        self.root.title("Password Generator & Vault")
        self.root.geometry("760x520")
        self.root.minsize(650, 420)

        main = ttk.Frame(root, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main, text="Password Generator & Vault", font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(0, 12))

        generator = ttk.LabelFrame(main, text="Password Generator", padding=10)
        generator.pack(fill="x", pady=(0, 12))

        ttk.Label(generator, text="Length (8–64):").grid(row=0, column=0, sticky="w")
        self.length_var = tk.IntVar(value=16)
        ttk.Spinbox(
            generator, from_=8, to=64, textvariable=self.length_var, width=6
        ).grid(row=0, column=1, padx=6, sticky="w")

        self.symbols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            generator, text="Include symbols", variable=self.symbols_var
        ).grid(row=0, column=2, padx=6, sticky="w")

        self.generated_var = tk.StringVar()
        ttk.Entry(
            generator, textvariable=self.generated_var, width=34
        ).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        ttk.Button(
            generator, text="Generate",
            command=self.on_generate
        ).grid(row=0, column=3, padx=6)
        ttk.Button(
            generator, text="Copy",
            command=self.copy_generated
        ).grid(row=1, column=3, padx=6, pady=(8, 0))

        add_frame = ttk.LabelFrame(main, text="Save a Login", padding=10)
        add_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(add_frame, text="Website / App").grid(row=0, column=0, sticky="w")
        ttk.Label(add_frame, text="Username / Email").grid(row=0, column=1, sticky="w")
        ttk.Label(add_frame, text="Password").grid(row=0, column=2, sticky="w")

        self.website_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Entry(add_frame, textvariable=self.website_var).grid(
            row=1, column=0, padx=(0, 8), sticky="ew"
        )
        ttk.Entry(add_frame, textvariable=self.username_var).grid(
            row=1, column=1, padx=(0, 8), sticky="ew"
        )
        ttk.Entry(add_frame, textvariable=self.password_var, show="*").grid(
            row=1, column=2, padx=(0, 8), sticky="ew"
        )
        ttk.Button(add_frame, text="Use Generated", command=self.use_generated).grid(
            row=1, column=3, padx=(0, 6)
        )
        ttk.Button(add_frame, text="Save Login", command=self.add_login).grid(
            row=1, column=4
        )

        for column in range(3):
            add_frame.columnconfigure(column, weight=1)

        list_frame = ttk.LabelFrame(main, text="Saved Logins", padding=8)
        list_frame.pack(fill="both", expand=True)

        columns = ("website", "username")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tree.heading("website", text="Website / App")
        self.tree.heading("username", text="Username / Email")
        self.tree.column("website", width=220)
        self.tree.column("username", width=300)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="View Selected Password", command=self.view_password).pack(
            side="left"
        )
        ttk.Button(actions, text="Delete Selected", command=self.delete_selected).pack(
            side="left", padx=8
        )
        ttk.Button(actions, text="Refresh", command=self.refresh).pack(side="right")

        self.refresh()

    def on_generate(self):
        try:
            length = int(self.length_var.get())
            self.generated_var.set(generate_password(length, self.symbols_var.get()))
        except (ValueError, tk.TclError) as error:
            messagebox.showerror("Invalid length", str(error))

    def copy_generated(self):
        password = self.generated_var.get()
        if not password:
            messagebox.showinfo("No password", "Generate a password first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def use_generated(self):
        password = self.generated_var.get()
        if not password:
            messagebox.showinfo("No password", "Generate a password first.")
            return
        self.password_var.set(password)

    def add_login(self):
        website = self.website_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not website or not username or not password:
            messagebox.showwarning(
                "Missing details", "Enter a website, username, and password."
            )
            return

        self.vault.add_entry(website, username, password)
        self.website_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.refresh()
        messagebox.showinfo("Saved", "Login saved in the encrypted vault.")

    def selected_index(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a login first.")
            return None
        return int(selected[0])

    def view_password(self):
        index = self.selected_index()
        if index is None:
            return
        entry = self.vault.entries[index]
        messagebox.showinfo(
            "Saved password",
            f"Website: {entry['website']}\n"
            f"Username: {entry['username']}\n\n"
            f"Password: {entry['password']}",
        )

    def delete_selected(self):
        index = self.selected_index()
        if index is None:
            return
        entry = self.vault.entries[index]
        if messagebox.askyesno(
            "Confirm deletion", f"Delete the login for {entry['website']}?"
        ):
            self.vault.delete_entry(index)
            self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, entry in enumerate(self.vault.entries):
            self.tree.insert(
                "", "end", iid=str(index),
                values=(entry["website"], entry["username"])
            )


def main():
    root = tk.Tk()
    root.withdraw()

    if os.path.exists(VAULT_FILE):
        prompt = "Enter your master password to unlock the vault:"
    else:
        prompt = (
            "Create a master password for your new vault "
            "(use a long, unique password):"
        )

    master_password = simpledialog.askstring(
        "Unlock Password Vault", prompt, show="*", parent=root
    )

    if master_password is None:
        root.destroy()
        return
    if len(master_password) < 12:
        messagebox.showwarning(
            "Master password too short",
            "For this project, use a master password with at least 12 characters.",
            parent=root,
        )
        root.destroy()
        return

    try:
        vault = PasswordVault(master_password)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        messagebox.showerror("Cannot open vault", str(error), parent=root)
        root.destroy()
        return

    root.deiconify()
    VaultApp(root, vault)
    root.mainloop()


if __name__ == "__main__":
    main()
