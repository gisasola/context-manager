import os
import sys
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

DEFAULT_CONTEXTS_DIR = os.path.expanduser("~/Documents/Contexts")
CONFIG_PATH = os.path.expanduser("~/.simple_context_manager_config.json")


class AddDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.grab_set()
        self.title("Add URL, File, or Folder Path")
        self.geometry("820x130")
        self.resizable(False, False)
        self.callback = callback

        tk.Label(self, text="Enter URL, file path, or folder path:").pack(
            anchor="w", padx=10, pady=(10, 3)
        )

        entry_frame = tk.Frame(self)
        entry_frame.pack(fill=tk.X, padx=10)

        self.entry = tk.Entry(entry_frame, width=60)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Browse buttons for file and folder
        tk.Button(entry_frame, text="Browse File", command=self.select_file).pack(
            side=tk.LEFT, padx=6
        )
        tk.Button(entry_frame, text="Browse Folder", command=self.select_folder).pack(
            side=tk.LEFT
        )

        self.entry.focus_set()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(
            btn_frame, text="OK", width=8, bg="#cff2d9", command=self.return_value
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            btn_frame, text="Cancel", width=8, bg="#ffe0e3", command=self.destroy
        ).pack(side=tk.LEFT)

    def select_file(self):
        path = filedialog.askopenfilename(title="Select file to add")
        if path:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, path)

    def select_folder(self):
        path = filedialog.askdirectory(title="Select folder to add")
        if path:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, path)

    def return_value(self):
        val = self.entry.get().strip()
        if val:
            self.callback(val)
            self.destroy()
        else:
            messagebox.showinfo("Info", "Please provide a URL or path.")


class SimpleContextManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Context Manager")
        self.geometry("860x720")
        self.resizable(0, 0)

        # Load config or use default contexts directory
        self.contexts_dir = DEFAULT_CONTEXTS_DIR
        self.load_config()
        os.makedirs(self.contexts_dir, exist_ok=True)

        self.items = []
        self.loaded_context = []
        self.current_context_file = None  # Track loaded file path for saving edits

        # Setup menus
        self.setup_menu()

        # Frames for screens
        self.welcome_frame = None
        self.create_frame = None
        self.load_frame = None
        self.open_frame = None
        self.edit_frame = None

        self.show_welcome()

    def setup_menu(self):
        menubar = tk.Menu(self)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help", command=self.show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)

        settingsmenu = tk.Menu(menubar, tearoff=0)
        settingsmenu.add_command(
            label="Change folder destination", command=self.show_settings
        )
        menubar.add_cascade(label="Settings", menu=settingsmenu)

        self.config(menu=menubar)

    def load_config(self):
        if os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    config = json.load(f)
                folder = config.get("contexts_dir")
                if folder and os.path.isdir(folder):
                    self.contexts_dir = folder
            except Exception:
                pass  # Ignore errors silently

    def save_config(self):
        config = {"contexts_dir": self.contexts_dir}
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f)
        except Exception:
            pass  # Ignore errors silently

    def show_settings(self):
        new_dir = filedialog.askdirectory(
            initialdir=self.contexts_dir, title="Select Default Contexts Directory"
        )
        if new_dir:
            self.contexts_dir = new_dir
            os.makedirs(self.contexts_dir, exist_ok=True)
            self.save_config()
            messagebox.showinfo(
                "Settings", f"Default folder set to:\n{self.contexts_dir}"
            )
            self.refresh_contexts_list()

    def show_help(self):
        help_text = (
            "Simple Context Manager Help:\n\n"
            "- On the Welcome screen, you can load, edit, or create contexts.\n"
            "- A context is a list of URLs, file paths, or folder paths to be managed.\n"
            "- In the Create or Edit screens, add items using the '+' button.\n"
            "- Remove items with the '–' button.\n"
            "- Save your context to a JSON file for later use.\n"
            "- Loaded contexts can be opened or edited as needed.\n"
            "- Use the Help menu anytime for this information."
        )
        messagebox.showinfo("Help", help_text)

    def clear_frames(self):
        for frame in (
            self.welcome_frame,
            self.create_frame,
            self.load_frame,
            self.open_frame,
            self.edit_frame,
        ):
            if frame:
                frame.pack_forget()

    # === Welcome Screen ===
    def show_welcome(self):
        self.clear_frames()
        self.load_frame = tk.Frame(self)
        self.load_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        title = tk.Label(
            self.load_frame,
            text="Welcome to Simple Context Manager",
            font=("Arial", 20, "bold"),
        )
        title.pack(pady=20)

        self.context_listbox = tk.Listbox(
            self.load_frame, font=("Arial", 12), width=40, height=14
        )
        self.context_listbox.pack(padx=12)

        btns_frame = tk.Frame(self.load_frame)
        btns_frame.pack(pady=(10, 0))

        tk.Button(
            self.load_frame,
            text="Load Context",
            width=14,
            command=self.load_selected_and_open,
        ).pack(pady=2)

        tk.Button(
            self.load_frame,
            text="Edit Context",
            width=14,
            command=self.edit_selected_context,
        ).pack(pady=2)

        tk.Button(
            self.load_frame,
            text="Load from file",
            width=14,
            command=self.browse_and_load_context,
        ).pack(pady=2)

        tk.Button(
            self.load_frame,
            text="Create New Context",
            width=14,
            command=self.show_create,
        ).pack(pady=2)

        self.loaded_context = []
        self.current_context_file = None
        self.refresh_contexts_list()

    # === Create Context Screen ===
    def show_create(self):
        self.clear_frames()
        self.items = []
        self.create_frame = tk.Frame(self)
        self.create_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        title_frame = tk.Frame(self.create_frame)
        title_frame.pack(anchor="w", pady=(0, 6), padx=12, fill=tk.X)

        tk.Button(
            title_frame,
            text="⬅️",
            font=("Arial", 16),
            command=self.show_welcome,
            relief="flat",
        ).pack(side=tk.LEFT, padx=(0, 10))

        title = tk.Label(title_frame, text="Create Context", font=("Arial", 18, "bold"))
        title.pack(side=tk.LEFT)

        info_button = tk.Button(
            title_frame,
            text="ℹ️",
            font=("Arial", 14),
            width=2,
            command=self.show_create_info,
            bg="#e0f0ff",
        )
        info_button.pack(side=tk.LEFT, padx=8)

        self.listbox = tk.Listbox(
            self.create_frame, selectmode=tk.EXTENDED, font=("Arial", 13), height=18
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=12)

        btns_frame = tk.Frame(self.create_frame)
        btns_frame.pack(pady=(6, 12))
        tk.Button(
            btns_frame,
            text="+",
            font=("Arial", 18),
            width=3,
            command=self.add_popup,
            bg="#e0f7fa",
        ).pack(side=tk.LEFT, padx=(0, 14))
        tk.Button(
            btns_frame,
            text="–",
            font=("Arial", 18),
            width=3,
            command=self.remove_selected,
            bg="#ffe0e3",
        ).pack(side=tk.LEFT)

        nav_frame = tk.Frame(self.create_frame)
        nav_frame.pack(pady=6)
        tk.Button(
            nav_frame, text="Save Context", width=16, command=self.save_context
        ).pack(side=tk.LEFT, padx=(0, 14))

    def show_create_info(self):
        info_text = (
            "In the Create Context screen, you can add URLs, file paths, or folder paths.\n\n"
            "- Use the '+' button to add items (Browse File / Browse Folder or paste).\n"
            "- Use the '–' button to remove selected items.\n"
            "- Once done, save your context for later use."
        )
        messagebox.showinfo("Create Context Info", info_text)

    # === Edit Context Screen ===
    def show_edit_context(self):
        if not self.loaded_context:
            messagebox.showinfo("Info", "No context loaded to edit.")
            return
        self.clear_frames()
        self.items = self.loaded_context.copy()
        self.edit_frame = tk.Frame(self)
        self.edit_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        title_frame = tk.Frame(self.edit_frame)
        title_frame.pack(anchor="w", pady=(0, 6), padx=12, fill=tk.X)

        tk.Button(
            title_frame,
            text="⬅️",
            font=("Arial", 16),
            command=self.show_welcome,
            relief="flat",
        ).pack(side=tk.LEFT, padx=(0, 10))

        title = tk.Label(
            title_frame,
            text="Which content would you like to load?",
            font=("Arial", 18, "bold"),
        )
        title.pack(side=tk.LEFT)

        self.listbox = tk.Listbox(
            self.edit_frame, selectmode=tk.EXTENDED, font=("Arial", 13), height=18
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=12)

        self.listbox.delete(0, tk.END)
        for item in self.items:
            self.listbox.insert(tk.END, item)

        btns_frame = tk.Frame(self.edit_frame)
        btns_frame.pack(pady=(6, 12))
        tk.Button(
            btns_frame,
            text="+",
            font=("Arial", 18),
            width=3,
            command=self.add_popup,
            bg="#e0f7fa",
        ).pack(side=tk.LEFT, padx=(0, 14))
        tk.Button(
            btns_frame,
            text="–",
            font=("Arial", 18),
            width=3,
            command=self.remove_selected,
            bg="#ffe0e3",
        ).pack(side=tk.LEFT)

        nav_frame = tk.Frame(self.edit_frame)
        nav_frame.pack(pady=6)
        tk.Button(
            nav_frame, text="Save Changes", width=16, command=self.save_edited_context
        ).pack(side=tk.LEFT, padx=(0, 14))

    # --- Shared methods ---

    def add_popup(self):
        AddDialog(self, self.add_entry)

    def add_entry(self, value):
        self.items.append(value)
        self.listbox.insert(tk.END, value)

    def remove_selected(self):
        selected = list(self.listbox.curselection())
        if not selected:
            messagebox.showinfo("Info", "No item selected.")
            return
        for idx in reversed(selected):
            self.listbox.delete(idx)
            del self.items[idx]

    def save_context(self):
        filename = filedialog.asksaveasfilename(
            initialdir=self.contexts_dir,
            title="Save Context",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.items, f, indent=2)
                messagebox.showinfo("Success", f"Context saved:\n{filename}")
                self.refresh_contexts_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def save_edited_context(self):
        if self.current_context_file:
            try:
                with open(self.current_context_file, "w", encoding="utf-8") as f:
                    json.dump(self.items, f, indent=2)
                messagebox.showinfo(
                    "Success", f"Context saved:\n{self.current_context_file}"
                )
                self.loaded_context = self.items.copy()
                self.show_welcome()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            self.save_context()

    def refresh_contexts_list(self):
        if hasattr(self, "context_listbox"):
            self.context_listbox.delete(0, tk.END)
            if not os.path.isdir(self.contexts_dir):
                return
            files = [f for f in os.listdir(self.contexts_dir) if f.endswith(".json")]
            files.sort()
            for f in files:
                self.context_listbox.insert(tk.END, os.path.splitext(f)[0])

    def load_selected_and_open(self):
        if not hasattr(self, "context_listbox"):
            return
        selection = self.context_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "No context selected.")
            return
        filename = self.context_listbox.get(selection[0]) + ".json"
        full_path = os.path.join(self.contexts_dir, filename)
        self.load_context_file(full_path)
        self.open_loaded_context()

    def edit_selected_context(self):
        if not hasattr(self, "context_listbox"):
            return
        selection = self.context_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "No context selected.")
            return
        filename = self.context_listbox.get(selection[0]) + ".json"
        full_path = os.path.join(self.contexts_dir, filename)
        self.load_context_file(full_path, showMessage=False)
        self.show_edit_context()

    def browse_and_load_context(self):
        filename = filedialog.askopenfilename(
            initialdir=self.contexts_dir,
            title="Select Context File",
            filetypes=[("JSON files", "*.json")],
        )
        if filename:
            self.load_context_file(filename)

    def load_context_file(self, file_path, showMessage=True):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.loaded_context = json.load(f)
            self.current_context_file = file_path
            if hasattr(self, "loaded_listbox"):
                self.loaded_listbox.delete(0, tk.END)
                for item in self.loaded_context:
                    self.loaded_listbox.insert(tk.END, item)
            if showMessage:
                messagebox.showinfo("Success", f"Context loaded:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    # --- Opening logic (URLs, files, and folders, cross-platform) ---

    @staticmethod
    def _is_url(s: str) -> bool:
        return s.lower().startswith(("http://", "https://", "file://"))

    @staticmethod
    def _open_target(target: str):
        """Open URL/file/folder cross-platform. Raises on failure."""
        if SimpleContextManager._is_url(target):
            # Let the default browser / handler deal with URLs (http/https/file)
            ok = webbrowser.open(target)
            if not ok:
                raise RuntimeError("No browser/handler could open the URL.")
            return

        # Expand ~ and environment vars for local paths
        p = os.path.expandvars(os.path.expanduser(target))
        if not os.path.exists(p):
            raise FileNotFoundError(f"Path does not exist: {p}")

        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", p])
        elif os.name == "nt":
            os.startfile(p)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", p])

    def open_loaded_context(self):
        if not self.loaded_context:
            messagebox.showinfo("Info", "No URLs or files/folders loaded to open.")
            return
        errors = []
        for item in self.loaded_context:
            try:
                self._open_target(item)
            except Exception as e:
                errors.append(f"{item}: {e}")
        if errors:
            messagebox.showwarning(
                "Warning", "Some items failed to open:\n" + "\n".join(errors)
            )
        else:
            messagebox.showinfo("Done", "All items opened successfully.")


if __name__ == "__main__":
    app = SimpleContextManager()
    app.mainloop()
