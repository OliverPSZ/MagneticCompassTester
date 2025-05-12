import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
import random
from math import atan2, degrees, radians
import csv

# === CONTROL VAR ===
ani = None
is_running = False

# === CONFIG ===
MAX_POINTS = 100

# === Simulated data buffers ===
x_data = deque(maxlen=MAX_POINTS)
y_data = deque(maxlen=MAX_POINTS)
z_data = deque(maxlen=MAX_POINTS)
heading_data = deque(maxlen=MAX_POINTS)  # New deque for heading

# === STYLES ===
BG_COLOR = "#f0f0f0"

# === GUI SETUP ===
root = tk.Tk()
root.title("Simulated HMC5883L Dashboard")
root.configure(bg=BG_COLOR)
root.geometry("900x600")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

mainframe = ttk.Frame(root)
mainframe.grid(row=0, column=0, sticky="nsew")
mainframe.columnconfigure(0, weight=3)
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(4, weight=1)

# === Style config (transparent look) ===
style = ttk.Style()
style.theme_use('default')
style.configure("TLabel", background=BG_COLOR)

# === Label Frame ===
label_frame = ttk.Frame(mainframe)
label_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10, padx=10)
label_frame.columnconfigure(0, weight=1)
label_frame.columnconfigure(1, weight=0)
label_frame.columnconfigure(2, weight=1)

# Left labels (X, Y, Z)
left_labels = ttk.Frame(label_frame)
left_labels.grid(row=0, column=0, sticky="w")

label_style = {"font": ('Arial', 16, 'bold'), "background": BG_COLOR}
x_label = tk.Label(left_labels, text="X: --- µT", fg='red', **label_style)
y_label = tk.Label(left_labels, text="Y: --- µT", fg='green', **label_style)
z_label = tk.Label(left_labels, text="Z: --- µT", fg='blue', **label_style)

x_label.grid(row=0, column=0, sticky="w")
y_label.grid(row=1, column=0, sticky="w")
z_label.grid(row=2, column=0, sticky="w")

# Right side: Compass + Button
right_labels = ttk.Frame(label_frame)
right_labels.grid(row=0, column=2, sticky="e")

compass_label = tk.Label(right_labels, text="Heading: ---°", fg='purple', font=('Arial', 18, 'bold'), bg=BG_COLOR)
compass_label.grid(row=0, column=0, padx=(0, 10), sticky="e")

# Initial Button Text to '▶ Start' and set the button to start in Stop mode
button = tk.Button(root, text="▶ Start", font=('Arial', 14), command=lambda: (
    ani.event_source.stop(),
    button.config(text="▶ Start") if is_running else ani.event_source.start(),
    button.config(text="⏸ Stop") if not is_running else None,
    save_data_to_csv(x_data, y_data, z_data, heading_data) if is_running else None,
    globals().__setitem__('is_running', not is_running)
))
button.grid(row=0, column=1, sticky="e")

# === Graph for X, Y, Z ===
fig_data, ax_data = plt.subplots()
ax_data.set_title("Magnetic Field (Simulated)")
ax_data.set_ylabel("Value")
ax_data.set_xlabel("Time")
line_x, = ax_data.plot([], [], label="X", color='red')
line_y, = ax_data.plot([], [], label="Y", color='green')
line_z, = ax_data.plot([], [], label="Z", color='blue')
ax_data.legend()

canvas_data = FigureCanvasTkAgg(fig_data, master=mainframe)
canvas_data.get_tk_widget().grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

# === Compass Needle Plot ===
fig_compass = plt.figure(figsize=(3, 3))
ax_compass = fig_compass.add_subplot(111, polar=True)
ax_compass.set_title("Compass")
ax_compass.set_theta_zero_location('N')
ax_compass.set_theta_direction(-1)
needle, = ax_compass.plot([0, 0], [0, 1], color='purple', linewidth=3)

canvas_compass = FigureCanvasTkAgg(fig_compass, master=mainframe)
canvas_compass.get_tk_widget().grid(row=4, column=1, sticky="nsew", padx=10, pady=10)


# === UPDATE FUNCTION ===
def update(frame):
    x = random.uniform(-50, 50)
    y = random.uniform(-50, 50)
    z = random.uniform(-50, 50)

    heading_rad = atan2(y, x)
    heading_deg = (degrees(heading_rad) + 360) % 360

    x_label.config(text=f"X: {x:.2f} µT")
    y_label.config(text=f"Y: {y:.2f} µT")
    z_label.config(text=f"Z: {z:.2f} µT")
    compass_label.config(text=f"Heading: {heading_deg:.2f}°")

    x_data.append(x)
    y_data.append(y)
    z_data.append(z)
    heading_data.append(heading_deg)  # Track heading data

    line_x.set_data(range(len(x_data)), list(x_data))
    line_y.set_data(range(len(y_data)), list(y_data))
    line_z.set_data(range(len(z_data)), list(z_data))
    ax_data.relim()
    ax_data.autoscale_view()
    canvas_data.draw()

    needle.set_data([0, radians(heading_deg)], [0, 1])
    canvas_compass.draw()


# Function to save data to CSV (x, y, z, heading)
def save_data_to_csv(x_data, y_data, z_data, heading_data):
    filename = "sensor_data.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['X', 'Y', 'Z', 'Heading'])  # Column headers

        # Write data
        for x, y, z, heading in zip(x_data, y_data, z_data, heading_data):
            writer.writerow([x, y, z, heading])  # Save x, y, z, heading data to CSV

    print(f"Data saved to {filename}")


# Initialize the animation but don't start it immediately
ani = animation.FuncAnimation(fig_data, update, interval=500)
ani.event_source.stop()  # Start in STOPPED state

root.mainloop()