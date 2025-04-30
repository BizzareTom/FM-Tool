import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageGrab
import pyperclip
import requests
import io

# Mindestgrößen für Custom Bilder
CUSTOM_MIN_WIDTH = 640
CUSTOM_MIN_HEIGHT = 480

# Variablen zur Speicherung des letzten Bildnamens und Counters
last_custom_name = ""
custom_counter = {}

# ========================
# Hilfsfunktionen
# ========================

# Funktion zum Öffnen eines Verzeichnisses
def choose_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

# Funktion zum Herunterladen eines Bildes von einer URL
def download_image(url):
    if not url:
        messagebox.showerror("Fehler", "Kein Link angegeben!")
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except requests.RequestException as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")
        return None

# Funktion zum Anpassen der Bildgröße auf exakt 640x480
def resize_and_crop(img, target_width=640, target_height=480):
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Bild ist breiter → Höhe passend skalieren
        new_height = target_height
        new_width = int(target_height * img_ratio)
    else:
        # Bild ist höher oder perfekt → Breite passend skalieren
        new_width = target_width
        new_height = int(target_width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Jetzt zuschneiden (Crop)
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    img = img.crop((left, top, right, bottom))
    return img

# ========================
# Hauptfunktionalität
# ========================

# Funktion zum Einfügen eines Bildes (Zwischenablage oder URL)
def paste_image(entry_field, graphics_dir):
    global last_custom_name, custom_counter
    try:
        clipboard_data = pyperclip.paste()
        img = None

        if clipboard_data.startswith("http"):  # URL eingefügt
            entry_field.delete(0, tk.END)
            entry_field.insert(0, clipboard_data)
            img = download_image(clipboard_data)
        else:  # Bild aus Zwischenablage
            img = ImageGrab.grabclipboard()
            if img:
                entry_field.delete(0, tk.END)
                entry_field.insert(0, "Bild aus Zwischenablage")

        if img:
            width, height = img.size
            if width < CUSTOM_MIN_WIDTH or height < CUSTOM_MIN_HEIGHT:
                messagebox.showerror("Fehler", f"Bild zu klein!\nMindestgröße: {CUSTOM_MIN_WIDTH}x{CUSTOM_MIN_HEIGHT}.\nDein Bild: {width}x{height}.")
                return

            # Name abfragen
            initial_value = last_custom_name if last_custom_name else "Name"
            name = simpledialog.askstring("Bildname", "Name für das Bild eingeben:", initialvalue=initial_value)
            if not name:
                messagebox.showerror("Fehler", "Kein Name angegeben!")
                return

            last_custom_name = name

            # Zielpfad erstellen
            save_dir = os.path.join(graphics_dir, "custom", "clubs", "640x480")
            os.makedirs(save_dir, exist_ok=True)

            # Zähler initialisieren, falls notwendig
            if name not in custom_counter:
                existing_files = [f for f in os.listdir(save_dir) if f.startswith(name + "_") and f.endswith(".jpg")]
                custom_counter[name] = len(existing_files)

            # Dateinamen erstellen
            filename = f"{name}_{custom_counter[name]:02d}.jpg"
            save_path = os.path.join(save_dir, filename)

            # Bild skalieren + zuschneiden
            img = resize_and_crop(img)

            # Bild speichern
            img.convert("RGB").save(save_path, "JPEG")
            messagebox.showinfo("Erfolg", f"Bild gespeichert als {filename}!")

            custom_counter[name] += 1

        else:
            messagebox.showerror("Fehler", "Kein gültiges Bild in der Zwischenablage oder ungültiger Link!")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Verarbeiten: {e}")

# Dialog-Fenster öffnen
def open_custom_dialog(root, graphics_dir):
    custom_window = tk.Toplevel(root)
    custom_window.title("Custom-Bilder einfügen")

    # Eingabefeld für Bildquelle
    label = tk.Label(custom_window, text="Bild-URL oder Zwischenablage:")
    label.pack(pady=5)

    entry_field = tk.Entry(custom_window, width=50)
    entry_field.pack(pady=5)

    # Button: Bild aus Zwischenablage/Link einfügen
    paste_button = tk.Button(custom_window, text="Bild einfügen", command=lambda: paste_image(entry_field, graphics_dir))
    paste_button.pack(pady=5)
    
    back_button = tk.Button(custom_window, text="Zurück", command=custom_window.destroy)
    back_button.pack(pady=5)
