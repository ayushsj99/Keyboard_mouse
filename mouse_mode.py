import pyautogui
import keyboard
import threading
import time
import json
import os

# === Configuration ===
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
    "tap_threshold": 0.1
}

# Keys to suppress while mouse mode is active
SUPPRESSED_KEYS = [
    "w", "a", "s", "d",
    "i", "j", "k", "m"
]

# Load config from file if exists
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = default_config

mode_active = False

# === Mouse Control Logic ===
def mouse_control_loop():
    global mode_active
    key_hold_times = {key: 0 for key in config["movement_keys"]}

    while True:
        if mode_active:
            for key, direction in config["movement_keys"].items():
                if keyboard.is_pressed(key):
                    key_hold_times[key] += 0.05
                    hold_time = key_hold_times[key]

                    if hold_time < config["tap_threshold"]:
                        dynamic_speed = config["tap_speed"]
                    elif config["acceleration_enabled"]:
                        dynamic_speed = min(
                            config["mouse_speed"] + int(config["acceleration_factor"] * (hold_time / 0.1)),
                            config["max_speed"]
                        )
                    else:
                        dynamic_speed = config["mouse_speed"]

                    dx = direction[0] * dynamic_speed
                    dy = direction[1] * dynamic_speed
                    pyautogui.moveRel(dx, dy)
                else:
                    key_hold_times[key] = 0

            # Clicks
            if keyboard.is_pressed(config["left_click_combo"]):
                pyautogui.click(button='left')
                time.sleep(0.2)
            if keyboard.is_pressed(config["right_click_combo"]):
                pyautogui.click(button='right')
                time.sleep(0.2)

            # Scrolling
            if keyboard.is_pressed(config["scroll_up_combo"]):
                pyautogui.scroll(config["scroll_speed"])
            if keyboard.is_pressed(config["scroll_down_combo"]):
                pyautogui.scroll(-config["scroll_speed"])

        time.sleep(0.05)

# === Toggle Mode ===
def toggle_mode():
    global mode_active
    mode_active = not mode_active

    if mode_active:
        for key in SUPPRESSED_KEYS:
            keyboard.block_key(key)
        print("\n🔱 Mouse Mode: ✅ ON (keys blocked)")
    else:
        for key in SUPPRESSED_KEYS:
            keyboard.unblock_key(key)
        print("\n🔱 Mouse Mode: ❌ OFF (keys unblocked)")

# === Settings CLI ===
def settings_menu():
    while True:
        print("\n🛠️ Settings Menu:")
        print("1. Set mouse speed")
        print("2. Set scroll speed")
        print("3. Toggle acceleration (currently {})".format("ON" if config["acceleration_enabled"] else "OFF"))
        print("4. Set acceleration factor (currently {})".format(config["acceleration_factor"]))
        print("5. Set max speed (currently {})".format(config["max_speed"]))
        print("6. Set tap speed (currently {})".format(config["tap_speed"]))
        print("7. Set tap threshold (currently {})".format(config["tap_threshold"]))
        print("8. Exit settings")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                config["mouse_speed"] = int(input("Enter mouse speed (pixels per step): "))
            elif choice == "2":
                config["scroll_speed"] = int(input("Enter scroll speed (lines): "))
            elif choice == "3":
                config["acceleration_enabled"] = not config["acceleration_enabled"]
            elif choice == "4":
                config["acceleration_factor"] = int(input("Set acceleration factor: "))
            elif choice == "5":
                config["max_speed"] = int(input("Set max speed: "))
            elif choice == "6":
                config["tap_speed"] = int(input("Set tap speed (pixels): "))
            elif choice == "7":
                config["tap_threshold"] = float(input("Set tap threshold (seconds): "))
            elif choice == "8":
                break
            else:
                print("Invalid choice. Try again.")
        except Exception as e:
            print("Error:", e)

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("✅ Settings saved.")

# === Listener ===
def listen_for_trigger():
    keyboard.add_hotkey('shift+right', toggle_mode)
    print("🔁 Press Shift + Right Arrow to toggle mouse mode.")
    keyboard.wait()

# === Start Everything ===
if __name__ == "__main__":
    print("\n🔀 Press Shift + Right Arrow to toggle mouse mode.")
    print("⚙️  Type 'settings' to open config menu.\n")

    threading.Thread(target=mouse_control_loop, daemon=True).start()

    def menu_listener():
        while True:
            cmd = input().strip().lower()
            if cmd == "settings":
                settings_menu()

    threading.Thread(target=menu_listener, daemon=True).start()

    listen_for_trigger()
