import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import threading

try:
    import darkdetect
except ImportError:
    darkdetect = None

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None

CONFIG_FILE = "mouse_mode_config.json"

# === Default config ===
default_config = {
    "mouse_speed": 20,
    "scroll_speed": 100,
    "left_click_combo": "j",
    "right_click_combo": "k",
    "scroll_up_combo": "i",
    "scroll_down_combo": "m",
    "movement_keys": {
        "w": [0, -1],
        "s": [0, 1],
        "a": [-1, 0],
        "d": [1, 0]
    },
    "acceleration_enabled": True,
    "acceleration_factor": 100,
    "max_speed": 200,
    "tap_speed": 15,
    "tap_threshold": 0.1,
    "auto_start": False
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return default_config.copy()

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=4)

class MouseSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🖱️ Mouse Controller Settings")
        self.root.geometry("500x500")
        self.config = load_config()
        self.entries = {}

        self._style = ttk.Style()
        if darkdetect and darkdetect.isDark():
            self._apply_dark_mode()

        self._build_gui()

        if pystray:
            self._init_tray_icon()

    def _apply_dark_mode(self):
        self.root.configure(bg="#2e2e2e")
        self._style.theme_use('clam')
        self._style.configure('.', background='#2e2e2e', foreground='white', fieldbackground='#2e2e2e')

    def _build_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(padx=10, pady=10, fill='both', expand=True)

        general_tab = ttk.Frame(notebook)
        advanced_tab = ttk.Frame(notebook)
        actions_tab = ttk.Frame(notebook)

        notebook.add(general_tab, text="General")
        notebook.add(advanced_tab, text="Advanced")
        notebook.add(actions_tab, text="Actions")

        # === General Tab ===
        self._add_spinbox(general_tab, "Mouse Speed", "mouse_speed", 1, 500)
        self._add_spinbox(general_tab, "Scroll Speed", "scroll_speed", 1, 500)

        ttk.Label(general_tab, text="Key Mappings:").pack(anchor='w', pady=10)
        ttk.Label(general_tab, text="Movement: W/A/S/D", foreground="gray").pack(anchor='w')
        ttk.Label(general_tab, text="Scroll: I (Up), M (Down)", foreground="gray").pack(anchor='w')
        ttk.Label(general_tab, text="Click: J (Left), K (Right)", foreground="gray").pack(anchor='w')

        # === Advanced Tab ===
        self.accel_var = tk.BooleanVar(value=self.config.get("acceleration_enabled", True))
        ttk.Checkbutton(advanced_tab, text="Enable Acceleration", variable=self.accel_var).pack(anchor='w', pady=5)

        self.auto_var = tk.BooleanVar(value=self.config.get("auto_start", False))
        ttk.Checkbutton(advanced_tab, text="Auto-launch on Startup", variable=self.auto_var).pack(anchor='w', pady=5)

        self._add_spinbox(advanced_tab, "Acceleration Factor", "acceleration_factor", 1, 1000)
        self._add_spinbox(advanced_tab, "Max Speed", "max_speed", 1, 1000)
        self._add_spinbox(advanced_tab, "Tap Speed", "tap_speed", 1, 100)
        self._add_entry(advanced_tab, "Tap Threshold (seconds)", "tap_threshold", value_type=float)

        # === Actions Tab ===
        ttk.Button(actions_tab, text="💾 Save Settings", command=self._save).pack(pady=10, fill='x')
        ttk.Button(actions_tab, text="🔄 Reset to Default", command=self._reset_defaults).pack(pady=5, fill='x')
        ttk.Button(actions_tab, text="❌ Exit", command=self.root.quit).pack(pady=5, fill='x')

    def _add_spinbox(self, parent, label, key, min_val, max_val):
        ttk.Label(parent, text=label).pack(anchor='w')
        var = tk.IntVar(value=self.config.get(key, 0))
        spin = ttk.Spinbox(parent, from_=min_val, to=max_val, textvariable=var)
        spin.pack(fill='x', pady=2)
        self.entries[key] = (var, int)

    def _add_entry(self, parent, label, key, config_path=None, value_type=str):
        ttk.Label(parent, text=label).pack(anchor='w')
        value = self.config[key] if not config_path else self.config[config_path][key]
        entry = ttk.Entry(parent)
        entry.insert(0, str(value))
        entry.pack(fill='x', pady=2)
        self.entries[(key, config_path)] = (entry, value_type)

    def _save(self):
        try:
            for k, (widget, value_type) in self.entries.items():
                key, path = k if isinstance(k, tuple) else (k, None)
                value = value_type(widget.get())
                if path:
                    self.config[path][key] = value
                else:
                    self.config[key] = value

            self.config["acceleration_enabled"] = self.accel_var.get()
            self.config["auto_start"] = self.auto_var.get()

            if self.config["auto_start"]:
                self._enable_auto_start()

            save_config(self.config)
            messagebox.showinfo("✅ Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def _reset_defaults(self):
        self.config = default_config.copy()
        save_config(self.config)
        messagebox.showinfo("Reset", "Settings reset to default. Please reopen the app.")
        self.root.quit()

    def _enable_auto_start(self):
        if os.name == 'nt':
            import winreg
            exe = sys.executable
            key = winreg.HKEY_CURRENT_USER
            path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, path, 0, winreg.KEY_SET_VALUE) as reg:
                winreg.SetValueEx(reg, "MouseController", 0, winreg.REG_SZ, exe)

    def _init_tray_icon(self):
        def quit_action(icon, item):
            icon.stop()
            self.root.quit()

        def open_gui(icon, item):
            self.root.deiconify()

        icon_image = Image.new('RGB', (64, 64), "black")
        draw = ImageDraw.Draw(icon_image)
        draw.ellipse((10, 10, 54, 54), fill="white")

        menu = (pystray.MenuItem('Open Settings', open_gui),
                pystray.MenuItem('Exit', quit_action))

        icon = pystray.Icon("MouseControl", icon_image, "Mouse Control", menu)
        threading.Thread(target=icon.run, daemon=True).start()

def launch_gui():
    root = tk.Tk()
    app = MouseSettingsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
