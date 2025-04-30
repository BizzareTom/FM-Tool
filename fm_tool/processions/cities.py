from PIL import Image, ImageTk, ImageGrab
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import pyperclip
import io
import requests
import certifi
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ============================
# CITIES_DIALOG
# ============================

# Zielgröße für Cities-Bilder
CITIES_TARGET_WIDTH = 615
CITIES_TARGET_HEIGHT = 461

# cities.py (am Ende hinzufügen)

def open_cities_dialog(root, graphics_dir):
    dialog = tk.Toplevel(root)
    dialog.title("Cities")
    dialog.geometry("775x400")
    dialog.configure(bg="#d8d8d8")

    # === Titel ===
    title_label = tk.Label(dialog, text="Cities", font=("Helvetica", 16, "bold"), bg="#d8d8d8")
    title_label.pack(pady=10)

    # === Main Frame mit zwei Spalten ===
    main_frame = tk.Frame(dialog, bg="#d8d8d8")
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # === Linker Bereich ===
    left_frame = tk.Frame(main_frame, bg="#d8d8d8")
    left_frame.pack(side="left", fill="both", padx=(0, 40), expand=True)
    
    # Wrapper-Frame für vertikale Zentrierung
    left_inner = tk.Frame(left_frame, bg="#d8d8d8")
    left_inner.pack(expand=True)
    left_inner.place(relx=0.5, rely=0.5, anchor="center") # Vertikal zentriert
    
    entry_row = tk.Frame(left_inner, bg="#d8d8d8")
    entry_row.pack(pady=(0,10))

    # Direktlink Eingabefeld
    entry_field = tk.Entry(entry_row, width=30)
    entry_field.insert(0, "Direktlink")
    entry_field.bind("<FocusIn>", lambda event: entry_field.delete(0, tk.END))
    entry_field.pack(side="left")

    # Buttonzeile: Suchen + Zwischenablage
    button_row = tk.Frame(left_inner, bg="#d8d8d8")
    button_row.pack()

    # Suchfunktion
    def open_file_dialog(entry_field, graphics_dir):
        file_path = filedialog.askopenfilename(filetypes=[("Bilder", "*.png;*.jpg;*.jpeg;*.bmp;*.tga")])
        if file_path:
            entry_field.delete(0, tk.END)
            entry_field.insert(0, file_path)
            try:
                img = Image.open(file_path)
                process_cities_image(img, graphics_dir)
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

    search_button = ttk.Button(button_row, text="Suchen", command=lambda: open_file_dialog(entry_field, graphics_dir))
    search_button.pack(side="left", padx=5)

    paste_button = ttk.Button(button_row, text="Aus Zwischenablage", command=lambda: paste_image(entry_field, graphics_dir))
    paste_button.pack(side="left", padx=5)

    # Ausführen-Button (nur falls Link eingegeben wurde)
    execute_button = ttk.Button(entry_row, text="Ausführen", command=lambda: process_cities_image(download_image(entry_field.get().strip()), graphics_dir))
    execute_button.pack(side="left", padx=0)

    # === Rechter Bereich: Deaktiviertes Drag & Drop ===
    right_frame = tk.Frame(main_frame, bg="#d8d8d8")
    right_frame.pack(side="right", fill="both", expand=True)

    drop_frame = tk.Label(
        right_frame,
        text="(Drag & Drop hier später möglich)",
        relief="solid",
        bg="#f0f0f0",
        bd=2,
        width=11,
        height=10,
        justify="center",
        anchor="center",
        font=("Arial", 12, "italic")
    )
    drop_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # === Zurück-Button ===
    cancel_button = ttk.Button(dialog, text="Zurück", command=dialog.destroy)
    cancel_button.pack(pady=10)


    # Stileffekt: gestrichelt → durchgehend bei Drag
    def on_drag_enter(event):
        drop_frame.config(relief="ridge", bd=3)

    def on_drag_leave(event):
        drop_frame.config(relief="solid", bd=2)

    def on_drop(event):
        file_path = event.data.strip().strip("{").strip("}")
        if os.path.isfile(file_path):
            try:
                img = Image.open(file_path)
                process_cities_image(img, fm_graphics_dir_entry.get())
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht verarbeitet werden:\n{e}")

    # drop_frame.drop_target_register(DND_FILES)
    # drop_frame.dnd_bind("<<DropEnter>>", on_drag_enter)
    # drop_frame.dnd_bind("<<DropLeave>>", on_drag_leave)
    # drop_frame.dnd_bind("<<Drop>>", on_drop)

# Funktion zum Öffnen eines Verzeichnisses
def choose_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

# Funktion für Zwischenablage
def paste_image(entry_field, graphics_dir):
    try:
        clipboard_data = pyperclip.paste()
        if clipboard_data.startswith("http"):  # Falls ein Link in der Zwischenablage ist
            entry_field.delete(0, tk.END)
            entry_field.insert(0, clipboard_data)
        else:
            img = ImageGrab.grabclipboard()  # Bild aus Zwischenablage
            if img:
                entry_field.delete(0, tk.END)
                entry_field.insert(0, "Bild aus Zwischenablage")
                process_cities_image(img, graphics_dir)
            else:
                messagebox.showerror("Fehler", "Kein gültiges Bild in der Zwischenablage!")
    except Exception as e:
        messagebox.showerror("Fehler", f"Zwischenablage konnte nicht gelesen werden: {e}")

# Funktion zum Download eines Bildes von einer URL
def download_image(url):
    if not url:
        messagebox.showerror("Fehler", "Kein Link angegeben!")
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, stream=True, verify=False)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except requests.RequestException as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")
        return None
            
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