import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
from math import atan2, degrees, radians
import csv
import serial
import threading

# === CONFIG ===
MAX_POINTS = 100
SERIAL_PORT = 'COM7'
BAUD_RATE = 9600

# === STATE VARS ===
ani = None
is_running = False
latest_reading = {'x': 0, 'y': 0, 'z': 0}

# === Serial Thread ===
def read_serial():
    global latest_reading
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("x:"):
                parts = line.replace("x: ", "").replace(" y: ", ",").replace(" z: ", ",").split(',')
                if len(parts) == 3:
                    x, y, z = map(int, parts)
                    latest_reading = {'x': x, 'y': y, 'z': z}
    except Exception as e:
        print("Serial read error:", e)

serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

# === Data Buffers ===
x_data = deque(maxlen=MAX_POINTS)
y_data = deque(maxlen=MAX_POINTS)
z_data = deque(maxlen=MAX_POINTS)

# === GUI SETUP ===
root = tk.Tk()
root.title("HMC5883L Live Dashboard")
root.geometry("900x600")
root.configure(bg="#f0f0f0")

mainframe = ttk.Frame(root)
mainframe.grid(row=1, column=0, columnspan=2, sticky="nsew")
mainframe.columnconfigure(0, weight=3)
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(4, weight=1)

style = ttk.Style()
style.theme_use('default')
style.configure("TLabel", background="#f0f0f0")

label_frame = ttk.Frame(root)
label_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
label_frame.columnconfigure(0, weight=1)
label_frame.columnconfigure(1, weight=0)
label_frame.columnconfigure(2, weight=1)

left_labels = ttk.Frame(label_frame)
left_labels.grid(row=0, column=0, sticky="w")
label_style = {"font": ('Arial', 16, 'bold'), "background": "#f0f0f0"}
x_label = tk.Label(left_labels, text="X: --- µT", fg='red', **label_style)
y_label = tk.Label(left_labels, text="Y: --- µT", fg='green', **label_style)
z_label = tk.Label(left_labels, text="Z: --- µT", fg='blue', **label_style)
x_label.grid(row=0, column=0, sticky="w")
y_label.grid(row=1, column=0, sticky="w")
z_label.grid(row=2, column=0, sticky="w")

right_labels = ttk.Frame(label_frame)
right_labels.grid(row=0, column=2, sticky="e")
compass_label = tk.Label(right_labels, text="Heading: ---°", fg='purple', font=('Arial', 18, 'bold'), bg="#f0f0f0")
compass_label.grid(row=0, column=0, padx=(0, 10), sticky="e")

# === Graph ===
fig_data, ax_data = plt.subplots()
ax_data.set_title("Magnetic Field")
ax_data.set_ylabel("Value")
ax_data.set_xlabel("Time")
line_x, = ax_data.plot([], [], label="X", color='red')
line_y, = ax_data.plot([], [], label="Y", color='green')
line_z, = ax_data.plot([], [], label="Z", color='blue')
ax_data.legend()
canvas_data = FigureCanvasTkAgg(fig_data, master=mainframe)
canvas_data.get_tk_widget().grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

# === Compass ===
fig_compass = plt.figure(figsize=(3.5, 3.5))
ax_compass = fig_compass.add_subplot(111, polar=True)
ax_compass.set_title("Compass")
ax_compass.set_theta_zero_location('N')
ax_compass.set_theta_direction(-1)
needle, = ax_compass.plot([0, 0], [0, 1], color='purple', linewidth=3)
canvas_compass = FigureCanvasTkAgg(fig_compass, master=mainframe)
canvas_compass.get_tk_widget().grid(row=4, column=1, sticky="nsew", padx=10, pady=10)

# === CSV Save ===
def save_data_to_csv():
    with open("sensor_data.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['X', 'Y', 'Z', 'Heading'])
        for i in range(len(x_data)):
            heading = calculate_heading(x_data[i], y_data[i])

            writer.writerow([x_data[i], y_data[i], z_data[i], heading])
    print("Data saved to sensor_data.csv")

def calculate_heading(x, y):
    heading_rad = atan2(y, x)
    heading_deg = degrees(heading_rad)
    if heading_deg < 0:
        heading_deg += 360
    return heading_deg

# === Update Plot ===
def update(frame):
    x = latest_reading['x']
    y = latest_reading['y']
    z = latest_reading['z']
    heading = calculate_heading(x, y)

    x_label.config(text=f"X: {x:.2f} µT")
    y_label.config(text=f"Y: {y:.2f} µT")
    z_label.config(text=f"Z: {z:.2f} µT")
    compass_label.config(text=f"Heading: {heading:.2f}°")

    x_data.append(x)
    y_data.append(y)
    z_data.append(z)

    line_x.set_data(range(len(x_data)), list(x_data))
    line_y.set_data(range(len(y_data)), list(y_data))
    line_z.set_data(range(len(z_data)), list(z_data))
    ax_data.relim()
    ax_data.autoscale_view()
    canvas_data.draw()

    needle.set_data([0, atan2(y, x)], [0, 1])
    canvas_compass.draw()

# === Start/Stop Button ===
def toggle_animation():
    global is_running
    if is_running:
        ani.event_source.stop()
        save_data_to_csv()
        button.config(text="▶ Start")
    else:
        ani.event_source.start()
        button.config(text="⏸ Stop")
    is_running = not is_running

button = tk.Button(root, text="▶ Start", font=('Arial', 14), command=toggle_animation)
button.grid(row=0, column=1, sticky="e", padx=10)

# === Animation Init ===
ani = animation.FuncAnimation(fig_data, update, interval=500)
ani.event_source.stop()

root.mainloop()