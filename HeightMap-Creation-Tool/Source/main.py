import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from noise import pnoise2
import os
import webbrowser

def open_website(event):
    webbrowser.open("https://example.com")

# --- Generate Heightmap ---
def generate_heightmap(width, height, scale, octaves, persistence, lacunarity, seed):
    data = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            data[y][x] = pnoise2(
                nx,
                ny,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=seed
            )
    # Normalize 0–255
    data = (data - data.min()) / (data.max() - data.min())
    img = Image.fromarray(np.uint8(data * 255), 'L')
    return img

# --- GUI Update ---
def update_image(force=False):
    global update_pending, current_image
    if not force:
        if update_pending is not None:
            root.after_cancel(update_pending)
        update_pending = root.after(300, lambda: update_image(force=True))
        return

    width = int(width_slider.get())
    height = int(height_slider.get())
    scale = float(scale_slider.get())
    octaves = int(octaves_slider.get())
    persistence = float(persistence_slider.get())
    lacunarity = float(lacunarity_slider.get())

    try:
        seed = int(seed_entry.get())
    except ValueError:
        seed = 0

    current_image = generate_heightmap(width, height, scale, octaves, persistence, lacunarity, seed)
    preview = current_image.copy()
    preview.thumbnail((400, 400))
    tk_img = ImageTk.PhotoImage(preview)
    img_label.config(image=tk_img)
    img_label.image = tk_img

# --- Export Function ---
def export_image():
    if current_image is None:
        messagebox.showinfo("No Image", "Please generate an image first.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
    )
    if file_path:
        current_image.save(file_path)
        messagebox.showinfo("Saved", f"Heightmap saved to:\n{file_path}")

# --- Reset Function ---
def reset_defaults():
    defaults = {
        width_slider: 256,
        height_slider: 256,
        scale_slider: 100,
        octaves_slider: 4,
        persistence_slider: 0.5,
        lacunarity_slider: 2.0
    }
    for slider, value in defaults.items():
        slider.set(value)
    seed_entry.delete(0, tk.END)
    seed_entry.insert(0, "0")
    update_image(force=True)

# --- GUI Setup ---
root = tk.Tk()
root.title("Heightmap Generator")
root.geometry("520x780")

# Set window icon if icon.png exists
if os.path.exists("icon.png"):
    try:
        icon_img = Image.open("icon.png")
        icon_photo = ImageTk.PhotoImage(icon_img)
        root.iconphoto(False, icon_photo)
    except Exception as e:
        print(f"Could not load icon.png: {e}")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

update_pending = None
current_image = None

def add_slider(label, from_, to, row, resolution=1, default=None):
    ttk.Label(frame, text=label).grid(column=0, row=row, sticky="w")
    slider = ttk.Scale(frame, from_=from_, to=to, orient="horizontal",
                       command=lambda e: update_image())
    slider.grid(column=1, row=row, sticky="ew", padx=5)
    frame.columnconfigure(1, weight=1)
    if default is not None:
        slider.set(default)
    return slider

width_slider = add_slider("Width", 64, 1024, 0, default=256)
height_slider = add_slider("Height", 64, 1024, 1, default=256)
scale_slider = add_slider("Scale", 10, 500, 2, default=100)
octaves_slider = add_slider("Octaves", 1, 8, 3, default=4)
persistence_slider = add_slider("Persistence", 0.1, 1.0, 4, resolution=0.05, default=0.5)
lacunarity_slider = add_slider("Lacunarity", 1.0, 5.0, 5, resolution=0.1, default=2.0)

# Seed input
ttk.Label(frame, text="Seed").grid(column=0, row=6, sticky="w")
seed_entry = ttk.Entry(frame)
seed_entry.insert(0, "0")
seed_entry.grid(column=1, row=6, sticky="ew", padx=5)
seed_entry.bind("<KeyRelease>", lambda e: update_image())

# Buttons
button_frame = ttk.Frame(frame)
button_frame.grid(column=0, row=7, columnspan=2, pady=10)
ttk.Button(button_frame, text="Export Heightmap", command=export_image).pack(side="left", padx=5)
ttk.Button(button_frame, text="Reset to Default", command=reset_defaults).pack(side="left", padx=5)

# Image display
img_label = ttk.Label(frame)
img_label.grid(column=0, row=8, columnspan=2, pady=20)

credit_label = ttk.Label(frame, text="Created by chillyastronox", font=("Arial", 8), foreground="blue", cursor="hand2")
credit_label.grid(column=0, row=9, columnspan=2, pady=250)
credit_label.bind("<Button-1>", open_website)

# Initial render
update_image(force=True)

root.mainloop()
