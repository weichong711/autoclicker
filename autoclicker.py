import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
import datetime
import keyboard
import mouse
import requests  # For HTTP request to get server time
# use this as prime autoclicker

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Target Autoclicker with Time Control and Hotkey (F6 / F1)")

        self.clicking = False
        self.targets = []
        self.entries_x = []
        self.entries_y = []

        self.interval_ms = 100  # default interval 100 ms
        self.server_offset = 0.0  # offset in seconds (local time - server time)

        self.create_widgets()
        threading.Thread(target=self.listen_hotkey, daemon=True).start()

    def create_widgets(self):
        # Number of targets selection
        tk.Label(self.root, text="Number of Targets:").grid(row=0, column=0)
        self.num_targets_var = tk.IntVar(value=4)
        self.num_targets_entry = tk.Entry(self.root, textvariable=self.num_targets_var, width=5)
        self.num_targets_entry.grid(row=0, column=1)

        btn_set_targets = tk.Button(self.root, text="Set Targets", command=self.set_targets)
        btn_set_targets.grid(row=0, column=2)

        # Interval input
        tk.Label(self.root, text="Click Interval (ms):").grid(row=0, column=3)
        self.interval_entry = tk.Entry(self.root, width=7)
        self.interval_entry.insert(0, str(self.interval_ms))
        self.interval_entry.grid(row=0, column=4)

        # Start Time input (HH:MM)
        tk.Label(self.root, text="Start Time (HH:MM):").grid(row=1, column=0)
        self.start_time_entry = tk.Entry(self.root, width=7)
        self.start_time_entry.insert(0, "00:00")
        self.start_time_entry.grid(row=1, column=1)

        # End Time input (HH:MM)
        tk.Label(self.root, text="End Time (HH:MM):").grid(row=1, column=2)
        self.end_time_entry = tk.Entry(self.root, width=7)
        self.end_time_entry.insert(0, "00:01")
        self.end_time_entry.grid(row=1, column=3)

        # Status label
        self.status_label = tk.Label(self.root, text="Status: Not Ready", fg="red")
        self.status_label.grid(row=2, column=0, columnspan=5, pady=5)

        # Container for target inputs
        self.targets_frame = tk.Frame(self.root)
        self.targets_frame.grid(row=3, column=0, columnspan=5)

        # Buttons
        self.btn_start = tk.Button(self.root, text="Start Clicking", command=self.start_clicking, state='normal')
        self.btn_start.grid(row=99, column=0, columnspan=2, pady=10)

        self.btn_stop = tk.Button(self.root, text="Stop Clicking", command=self.stop_clicking, state='disabled')
        self.btn_stop.grid(row=99, column=2, columnspan=2, pady=10)

        # NEW BUTTON: Check Server Time & Ready
        self.btn_check_server = tk.Button(self.root, text="Check Server Time & Ready", command=self.check_server_time_and_ready)
        self.btn_check_server.grid(row=99, column=4, pady=10)

        self.set_targets()

    def set_targets(self):
        try:
            num = int(self.num_targets_var.get())
            if num <= 0 or num > 20:
                messagebox.showerror("Error", "Please enter a number between 1 and 20 for targets.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of targets.")
            return

        # Clear previous widgets
        for widget in self.targets_frame.winfo_children():
            widget.destroy()

        self.targets = [(0, 0)] * num
        self.entries_x.clear()
        self.entries_y.clear()

        for i in range(num):
            tk.Label(self.targets_frame, text=f"Target {i+1} X:").grid(row=i, column=0)
            entry_x = tk.Entry(self.targets_frame, width=7)
            entry_x.insert(0, "0")
            entry_x.grid(row=i, column=1)
            self.entries_x.append(entry_x)

            tk.Label(self.targets_frame, text="Y:").grid(row=i, column=2)
            entry_y = tk.Entry(self.targets_frame, width=7)
            entry_y.insert(0, "0")
            entry_y.grid(row=i, column=3)
            self.entries_y.append(entry_y)

            btn_pick = tk.Button(self.targets_frame, text="Pick Location", command=lambda i=i: self.pick_location(i))
            btn_pick.grid(row=i, column=4)

        self.update_status("Not Ready", "red")
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')

    def update_status(self, text, color="black"):
        self.status_label.config(text=f"Status: {text}", fg=color)

    def update_targets(self):
        new_targets = []
        for i in range(len(self.entries_x)):
            try:
                x = int(self.entries_x[i].get())
                y = int(self.entries_y[i].get())
                if (x, y) != (0, 0):
                    new_targets.append((x, y))
            except ValueError:
                messagebox.showerror("Error", f"Invalid coordinates at Target {i+1}.")
                return None
        if not new_targets:
            messagebox.showerror("Error", "No valid target positions selected.")
            return None
        return new_targets

    def start_clicking(self):
        new_targets = self.update_targets()
        if new_targets is None:
            return

        try:
            interval_input = int(self.interval_entry.get())
            if interval_input < 1:
                messagebox.showerror("Error", "Interval must be at least 1 ms.")
                return
            self.interval_ms = interval_input
        except ValueError:
            messagebox.showerror("Error", "Invalid interval value.")
            return

        try:
            start_str = self.start_time_entry.get()
            end_str = self.end_time_entry.get()
            start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM.")
            return

        self.targets = new_targets
        self.clicking = True
        self.update_status("Waiting for start time...", "blue")
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')

        threading.Thread(target=self.timed_click_loop, args=(start_time, end_time), daemon=True).start()

    def stop_clicking(self):
        self.clicking = False
        self.update_status("Stopped", "orange")
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')

    def force_stop_clicking(self):
        if self.clicking:
            self.clicking = False
            self.update_status("Force Stopped (F1)", "red")
            self.btn_start.config(state='normal')
            self.btn_stop.config(state='disabled')
            print("Autoclicker force-stopped by F1.")

    def timed_click_loop(self, start_time, end_time):
        offset_seconds = 0.651  # Your original offset baseline

        while self.clicking:
            now = datetime.datetime.now()
            # Apply server offset correction: local time corrected = local - offset
            corrected_now = now - datetime.timedelta(seconds=self.server_offset)

            start_dt = corrected_now.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
            end_dt = corrected_now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)

            if end_dt <= start_dt:
                end_dt += datetime.timedelta(days=1)

            if corrected_now > end_dt:
                self.stop_clicking()
                break

            trigger_dt = start_dt - datetime.timedelta(seconds=offset_seconds)
            if corrected_now < trigger_dt:
                time_left = (trigger_dt - corrected_now).total_seconds()
                self.update_status(f"Running Ready - Offset: {self.server_offset:.3f}s - Waiting for start time... {time_left:.1f}s", "blue")
                time.sleep(min(1, time_left))
                continue

            self.update_status("Running...", "green")
            while self.clicking and datetime.datetime.now() < end_dt:
                for x, y in self.targets:
                    if not self.clicking or datetime.datetime.now() >= end_dt:
                        break
                    try:
                        pyautogui.click(x, y)
                    except Exception as e:
                        print(f"Click failed at ({x},{y}): {e}")
                    time.sleep(self.interval_ms / 1000)

            self.stop_clicking()
            break

    def pick_location(self, index):
        self.root.attributes("-disabled", True)
        messagebox.showinfo("Info", f"After closing this message, click anywhere on screen to pick location for Target {index+1}")

        def capture_click():
            mouse.wait(button='left', target_types=('down',))
            x, y = pyautogui.position()
            self.entries_x[index].delete(0, tk.END)
            self.entries_x[index].insert(0, str(x))
            self.entries_y[index].delete(0, tk.END)
            self.entries_y[index].insert(0, str(y))
            self.root.attributes("-disabled", False)
            self.root.lift()
            print(f"Captured Target {index+1} at ({x}, {y})")

        threading.Thread(target=capture_click, daemon=True).start()

    def listen_hotkey(self):
        keyboard.add_hotkey('f6', self.toggle_clicking)
        keyboard.add_hotkey('f1', self.force_stop_clicking)
        keyboard.wait()

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
            print("Autoclicker stopped by hotkey.")
        else:
            self.start_clicking()
            print("Autoclicker started by hotkey.")

    # --- NEW METHOD ---
    def check_server_time_and_ready(self):
        # Disable button while processing
        self.btn_check_server.config(state='disabled')
        self.update_status("Checking server time...", "orange")

        def fetch_and_calculate_offset():
            try:
                url = "https://sportsuum.skedda.com"
                response = requests.head(url, timeout=5)
                server_date_str = response.headers.get('Date')
                if not server_date_str:
                    raise ValueError("No Date header in response")

                # Parse server date, e.g. 'Wed, 03 Jun 2020 12:00:00 GMT'
                server_time = datetime.datetime.strptime(server_date_str, '%a, %d %b %Y %H:%M:%S GMT')
                server_time = server_time.replace(tzinfo=datetime.timezone.utc)

                # Local time in UTC
                local_time_utc = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

                # Calculate offset (local - server) in seconds
                offset = (local_time_utc - server_time).total_seconds()

                self.server_offset = offset

                # Calculate time left to start time considering offset
                try:
                    start_str = self.start_time_entry.get()
                    start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
                except Exception:
                    self.update_status("Invalid start time format!", "red")
                    self.btn_check_server.config(state='normal')
                    return

                now_local = datetime.datetime.now()
                corrected_now = now_local - datetime.timedelta(seconds=offset)
                start_dt = corrected_now.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)

                if start_dt < corrected_now:
                    start_dt += datetime.timedelta(days=1)

                time_left = (start_dt - corrected_now).total_seconds()

                self.update_status(f"Ready - Offset: {offset:.3f}s - Waiting for start time... {time_left:.1f}s", "green")

            except Exception as e:
                self.update_status(f"Error fetching server time: {e}", "red")
                print("Error fetching server time:", e)
            finally:
                self.btn_check_server.config(state='normal')

        threading.Thread(target=fetch_and_calculate_offset, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
