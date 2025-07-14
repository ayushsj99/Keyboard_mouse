import threading
import keyboard
from mouse_gui import launch_gui
from mouse_mode import mouse_control_loop, toggle_mode

# Start the mouse movement controller
def start_mouse_mode():
    threading.Thread(target=mouse_control_loop, daemon=True).start()

# Listen for Shift + Right Arrow to toggle mouse mode
def start_trigger_listener():
    keyboard.add_hotkey('shift+right', toggle_mode)
    print("🔁 Press Shift + Right Arrow to toggle mouse mode.")

# Launch everything
if __name__ == "__main__":
    print("🎮 Starting Mouse Mode System...")
    print("🔀 Trigger = Shift + Right Arrow")
    print("🖥️ GUI will open for configuration.\n")

    # Start background systems first
    start_mouse_mode()
    start_trigger_listener()

    # GUI must stay on main thread
    launch_gui()
