# file: main.py

import threading
import keyboard
from mouse_gui import launch_gui
from mouse_mode import mouse_control_loop, toggle_mode

def start_mouse_mode():
    threading.Thread(target=mouse_control_loop, daemon=True).start()

def start_trigger_listener():
    keyboard.add_hotkey('shift+right', toggle_mode)
    print("🔁 Press Shift + Right Arrow to toggle mouse mode.")


if __name__ == "__main__":
    print("🎮 Starting Mouse Mode System...")
    print("🔀 Toggle Mouse Mode: Shift + Right Arrow")
    print("🔍 Search UI Elements: Ctrl + Shift + F")
    print("🖥️ GUI will open for configuration.\n")

    start_mouse_mode()
    start_trigger_listener()

    # IMPORTANT: GUI should remain in the main thread
    launch_gui()
