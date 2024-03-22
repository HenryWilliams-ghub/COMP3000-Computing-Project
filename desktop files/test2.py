from pynput import keyboard

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char:
            print(f"Key {key.char} pressed")
    except Exception as e:
        print(f"Error in on_press: {e}")

print("Starting keyboard listener. Press keys to test, and ESC to stop.")

with keyboard.Listener(on_press=on_press) as listener:
    try:
        listener.join()
    except Exception as e:
        print(f"Listener stopped: {e}")
