from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

# ============================
# IMAGE PROCESSION CITIES
# ============================

# Zielgröße für Cities-Bilder
CITIES_TARGET_WIDTH = 615
CITIES_TARGET_HEIGHT = 461

# Funktion zur Verarbeitung der Cities-Bilder
def process_cities_image(image, graphics_dir):
    if image is None:
        return

    orig_width, orig_height = image.size

    # Prüfen, ob Mindestgröße erreicht ist
    if orig_width < CITIES_TARGET_WIDTH or orig_height < CITIES_TARGET_HEIGHT:
        messagebox.showerror("Fehler", "Bild ist zu klein! Mindestgröße: 615x461")
        return

    # Zielverhältnis berechnen
    target_ratio = CITIES_TARGET_WIDTH / CITIES_TARGET_HEIGHT
    img_ratio = orig_width / orig_height

    if abs(img_ratio - target_ratio) < 0.01:  # FALL 1: Direkt skalieren
        img_resized = image.resize((CITIES_TARGET_WIDTH, CITIES_TARGET_HEIGHT), Image.LANCZOS)
    else:  # FALL 2: Zuschneiden & Skalieren
        if img_ratio > target_ratio:  # Bild ist zu breit
            new_width = int(orig_height * target_ratio)
            x_offset = (orig_width - new_width) // 2
            img_cropped = image.crop((x_offset, 0, x_offset + new_width, orig_height))
        else:  # Bild ist zu hoch
            new_height = int(orig_width / target_ratio)
            y_offset = (orig_height - new_height) // 2
            img_cropped = image.crop((0, y_offset, orig_width, y_offset + new_height))

        img_resized = img_cropped.resize((CITIES_TARGET_WIDTH, CITIES_TARGET_HEIGHT), Image.LANCZOS)

    # Vorschau anzeigen
    preview_window = tk.Toplevel()
    preview_window.title("Bildvorschau")
    img_tk = ImageTk.PhotoImage(img_resized)
    preview_label = tk.Label(preview_window, image=img_tk)
    preview_label.image = img_tk
    preview_label.pack()

    # OK & Abbrechen Buttons
    def save_image():
        name = simpledialog.askstring("Speichern", "Gib einen Namen für das Bild ein:")
        if name:
            save_path = os.path.join(graphics_dir, "Cities", "615x461")
            os.makedirs(save_path, exist_ok=True)
            img_resized.save(os.path.join(save_path, f"{name}.tga"))
            messagebox.showinfo("Erfolg", f"Bild gespeichert: {name}.tga")
            preview_window.destroy()

    ok_button = ttk.Button(preview_window, text="OK", command=save_image)
    ok_button.pack(pady=5)

    cancel_button = ttk.Button(preview_window, text="Abbrechen", command=preview_window.destroy)
    cancel_button.pack(pady=5)