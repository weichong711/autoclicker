import tkinter as tk
import pyautogui
import threading
import time
import keyboard
import mouse  # new dependency for detecting mouse click

clicking = False
targets = [(0, 0)] * 4

def update_target(index):
    try:
        x = int(entries_x[index].get())
        y = int(entries_y[index].get())
        targets[index] = (x, y)
    except ValueError:
        pass

def start_clicking():
    global clicking
    clicking = True
    for i in range(4):
        update_target(i)
    threading.Thread(target=click_loop, daemon=True).start()

def stop_clicking():
    global clicking
    clicking = False

def toggle_clicking():
    global clicking
    if clicking:
        stop_clicking()
        print("Autoclicker stopped.")
    else:
        start_clicking()
        print("Autoclicker started.")

def click_loop():
    while clicking:
        for x, y in targets:
            if not clicking:
                break
            pyautogui.moveTo(x, y)
            pyautogui.click()
            time.sleep(0.01)  # Changed to 10 ms (0.01 sec)

def pick_location(index):
    def capture_click():
        print(f"Waiting for screen click for Target {index+1}...")
        mouse.wait(button='left', target_types=('down',))
        x, y = pyautogui.position()
        entries_x[index].delete(0, tk.END)
        entries_x[index].insert(0, str(x))
        entries_y[index].delete(0, tk.END)
        entries_y[index].insert(0, str(y))
        print(f"Captured Target {index+1} at: ({x}, {y})")
        root.deiconify()

    root.withdraw()  # Hide the app window
    threading.Thread(target=capture_click, daemon=True).start()

def listen_hotkey():
    keyboard.add_hotkey('f6', toggle_clicking)  # Changed hotkey to F6
    keyboard.wait()

# GUI Setup
root = tk.Tk()
root.title("4-Target Autoclicker (F6 to Start/Stop)")

entries_x = []
entries_y = []

for i in range(4):
    tk.Label(root, text=f"Target {i+1} X:").grid(row=i, column=0)
    entry_x = tk.Entry(root, width=7)
    entry_x.insert(0, "0")
    entry_x.grid(row=i, column=1)
    entries_x.append(entry_x)

    tk.Label(root, text=f"Y:").grid(row=i, column=2)
    entry_y = tk.Entry(root, width=7)
    entry_y.insert(0, "0")
    entry_y.grid(row=i, column=3)
    entries_y.append(entry_y)

    btn_pick = tk.Button(root, text="Pick Location", command=lambda i=i: pick_location(i))
    btn_pick.grid(row=i, column=4)

tk.Button(root, text="Start Clicking", command=start_clicking).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="Stop Clicking", command=stop_clicking).grid(row=5, column=2, columnspan=2)

# Start hotkey listener
threading.Thread(target=listen_hotkey, daemon=True).start()

root.mainloop()
