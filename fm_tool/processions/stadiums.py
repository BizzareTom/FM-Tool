from PIL import Image, ImageTk, ImageGrab
import os
import tkinter as tk
import pyperclip
from tkinter import simpledialog, messagebox, ttk, filedialog
import requests
import io

# ============================
# STADIUMS DIALOG
# ============================

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

def open_stadiums_dialog(root, fm_graphics_dir):
    dialog = tk.Toplevel(root)
    dialog.title("Dialog_Stadiums")
    dialog.geometry("775x400")
    dialog.configure(bg="#d8d8d8")

    # === Titel ===
    title_label = tk.Label(dialog, text="Stadiums", font=("Helvetica", 16, "bold"), bg="#d8d8d8")
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
    left_inner.place(relx=0.5, rely=0.5, anchor="center")  # Vertikal zentriert
    
    # Linkseingabefeld für URL
    entry_row = tk.Frame(left_inner, bg="#d8d8d8")
    entry_row.pack(pady=(0, 10))

    entry_field = tk.Entry(entry_row, width=30)
    entry_field.insert(0, "Direktlink")
    entry_field.bind("<FocusIn>", lambda e: entry_field.delete(0, tk.END))
    entry_field.pack(side="left", padx=0)

    # === Buttons in einer Zeile ===
    button_row = tk.Frame(left_inner, bg="#d8d8d8")
    button_row.pack(pady=(10, 0))

    # Ausführen-Button (nur falls Link eingegeben wurde)
    execute_button = ttk.Button(entry_row, text="Ausführen", command=lambda: process_stadiums_image(download_image(entry_field.get().strip()), fm_graphics_dir))
    execute_button.pack(side="left", padx=0)

    paste_button = ttk.Button(button_row, text="Aus Zwischenablage einfügen", command=lambda: paste_stadiums_image(entry_field, fm_graphics_dir))
    paste_button.pack(side="left", padx=5)

    search_button = ttk.Button(button_row, text="Suchen", command=lambda: open_file_dialog_stadiums(entry_field, fm_graphics_dir))
    search_button.pack(side="left", padx=5)

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


# ============================
# IMAGE PROCESSION STADIUMS
# ============================

STADIUMS_SIZES = {
    "1920x1200": (1920, 1200),
    "800x600": (800, 600),
    "200x150": (200, 150)
}

MIN_WIDTH = 200
MIN_HEIGHT = 150

def paste_stadiums_image(entry_field, fm_graphics_dir_entry):
    try:
        clipboard_data = pyperclip.paste()
        if clipboard_data.startswith("http"):
            entry_field.delete(0, tk.END)
            entry_field.insert(0, clipboard_data)
            process_stadiums_image(download_image(clipboard_data), fm_graphics_dir_entry)
        else:
            img = ImageGrab.grabclipboard()
            if img:
                entry_field.delete(0, tk.END)
                entry_field.insert(0, "Bild aus Zwischenablage")
                process_stadiums_image(img, fm_graphics_dir_entry)
            else:
                messagebox.showerror("Fehler", "Kein gültiges Bild in der Zwischenablage!")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Zugriff auf die Zwischenablage:\n{e}")

def open_file_dialog_stadiums(entry_field, fm_graphics_dir_entry):
    file_path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png;*.jpg;*.jpeg;*.bmp;*.tga")])
    if file_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, file_path)
        img = Image.open(file_path)
        process_stadiums_image(img, fm_graphics_dir_entry)

def process_stadiums_image(image, fm_graphics_dir_entry):
    if image is None:
        return

    orig_width, orig_height = image.size
    if orig_width < MIN_WIDTH or orig_height < MIN_HEIGHT:
        messagebox.showerror("Fehler", f"Bild zu klein! Mindestgröße ist {MIN_WIDTH}x{MIN_HEIGHT}")
        return

    available_sizes = {}
    for label, (w, h) in STADIUMS_SIZES.items():
        if orig_width >= w and orig_height >= h:
            available_sizes[label] = (w, h)

    if not available_sizes:
        messagebox.showerror("Fehler", "Bild erfüllt keine Anforderungen für die Zielgrößen!")
        return

    def crop_center(img, target_w, target_h):
        ratio_target = target_w / target_h
        img_w, img_h = img.size
        ratio_img = img_w / img_h

        if ratio_img > ratio_target:  # Bild zu breit
            new_w = int(img_h * ratio_target)
            x = (img_w - new_w) // 2
            box = (x, 0, x + new_w, img_h)
        else:  # Bild zu hoch
            new_h = int(img_w / ratio_target)
            y = (img_h - new_h) // 2
            box = (0, y, img_w, y + new_h)

        return img.crop(box)

    preview_size = STADIUMS_SIZES["800x600"] if "800x600" in available_sizes else list(available_sizes.values())[0]
    preview_img = crop_center(image, *preview_size).resize(preview_size, Image.LANCZOS)

    # Vorschau anzeigen
    preview_win = tk.Toplevel()
    preview_win.title("Stadiums Vorschau")
    img_tk = ImageTk.PhotoImage(preview_img)
    label = tk.Label(preview_win, image=img_tk)
    label.image = img_tk
    label.pack(pady=5)

    def save_all():
        name = simpledialog.askstring("Speichern", "Dateiname (ohne .tga):")
        if not name:
            return
        base_path = os.path.join(fm_graphics_dir_entry, "Stadiums")
        for label, (w, h) in available_sizes.items():
            path = os.path.join(base_path, label)
            os.makedirs(path, exist_ok=True)
            processed_img = crop_center(image, w, h).resize((w, h), Image.LANCZOS)
            save_path = os.path.join(path, f"{name}.tga")
            processed_img.save(save_path)
        messagebox.showinfo("Erfolg", f"Alle passenden Bilder gespeichert als {name}.tga")
        preview_win.destroy()

    ok_btn = ttk.Button(preview_win, text="OK", command=save_all)
    ok_btn.pack(pady=5)
