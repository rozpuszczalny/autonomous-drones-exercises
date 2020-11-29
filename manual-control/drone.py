import os
import tkinter as tk
from flight_thread import start
from control_state import ALL_KEYS, control_state, MODE_1, MODE_2, mode, FLIGHT_MODE_ALITIUDE, FLIGHT_MODE_POSITION, flight_mode, fence

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.bind_event_listeners()

    def on_key(self, event):
        if event.keysym in ALL_KEYS:
            control_state[event.keysym] = True
        if event.keysym == 'm':
            self.toggle_mode()

    def toggle_mode(self):
        mode['current'] = MODE_1 if mode['current'] == MODE_2 else MODE_2
        self.mode_status.delete("1.0", tk.END)
        self.mode_status.insert(tk.END, self.get_mode_text())

    def toggle_mode(self):
        mode['current'] = MODE_1 if mode['current'] == MODE_2 else MODE_2
        self.mode_status.delete("1.0", tk.END)
        self.mode_status.insert(tk.END, self.get_mode_text())

    def toggle_flight_mode(self):
        flight_mode['requested'] = FLIGHT_MODE_POSITION if flight_mode['requested'] == FLIGHT_MODE_ALITIUDE else FLIGHT_MODE_ALITIUDE
        self.set_flight_mode_text()

    def on_release(self, event):
        if event.keysym in ALL_KEYS:
            control_state[event.keysym] = False

    def bind_event_listeners(self):
        self.master.bind('<KeyPress>', self.on_key)
        self.master.bind('<KeyRelease>', self.on_release)

    def get_mode_text(self):
        return "MODE 2" if mode['current'] == MODE_2 else "MODE 1"

    def apply_polygon(self):
        self.size_in_meters = float(self.polygon_entry.get())
        self.polygon_size_label_text.set(f"Polygon size: {self.size_in_meters} m")
        print(self.size_in_meters)
        fence['requested'] = self.size_in_meters

    def create_polygon_input(self):
        self.polygon_entry = tk.Entry(self)
        self.polygon_apply_btn = tk.Button(self, text="Apply", command=self.apply_polygon)

    def set_flight_mode_text(self):
        self.flight_mode_text.set(f"Flight mode: {flight_mode['requested']}")

    def layout_widgets(self):
        tk.Label(self, text="Enter geofence square size [m]").grid(row=0)
        self.polygon_entry.grid(row=0, column=1)

        self.polygon_apply_btn.grid(row=1)
        self.mode_toggle.grid(row=1, column=1)

        self.flight_mode_toggle.grid(row=2, columnspan=2)

        self.polygon_size_label_text = tk.StringVar(self)
        tk.Label(self, textvariable=self.polygon_size_label_text).grid(row=3, columnspan=2)

        self.flight_mode_text = tk.StringVar(self)
        tk.Label(self, textvariable=self.flight_mode_text).grid(row=4, columnspan=2)

        self.set_flight_mode_text()
    
        self.mode_status.grid(row=5, columnspan=2)
        self.quit.grid(row=6, columnspan=2)

    def create_widgets(self):
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.mode_status = tk.Text(self, height=1, width=30)
        self.mode_status.insert(tk.END, self.get_mode_text())
        self.mode_toggle = tk.Button(self, text="Toggle mode", command=self.toggle_mode)
        self.flight_mode_toggle = tk.Button(self, text="Toggle flight mode", command=self.toggle_flight_mode)
        self.create_polygon_input()
        self.layout_widgets()

os.system('xset r off')
root = tk.Tk()

start()

app = Application(master=root)
app.mainloop()

os.system('xset r on')
