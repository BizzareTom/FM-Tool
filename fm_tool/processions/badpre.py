import os
import io
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ImageGrab
import requests
import numpy as np

def open_badpre_dialog(root, graphics_path):
    dialog = tk.Toplevel(root)
    dialog.title("Club präpariert")
    dialog.geometry("500x275")
    dialog.configure(bg="#d8d8d8")

    image_data = {"img": None}

    def is_image_valid(img):
        return max(img.width, img.height) >= 256 and img.mode == "RGBA"

    def load_image_object(img):
        if not is_image_valid(img):
            messagebox.showerror("Ungültiges Bild", "Das Bild muss mindestens 256px groß sein und einen transparenten Hintergrund haben.")
            return
        image_data["img"] = img
        ttk.Label(dialog, text=f"Bild geladen: {img.width}x{img.height}", background="#d8d8d8").pack()

    def load_file():
        path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png;*.tga")])
        if path:
            img = Image.open(path).convert("RGBA")
            load_image_object(img)

    def load_from_clipboard():
        try:
            img = ImageGrab.grabclipboard()
            if img:
                img = img.convert("RGBA")
                load_image_object(img)
            else:
                messagebox.showerror("Fehler", "Keine gültige Zwischenablage erkannt.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def load_from_url():
        url = url_var.get().strip()
        if not url.startswith("http"):
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            load_image_object(img)
        except Exception as e:
            messagebox.showerror("Fehler beim Laden", str(e))

    def on_url_entry_click(event):
        if url_entry.get() == "Direktlink":
            url_entry.delete(0, tk.END)

    def on_url_change(*args):
        url = url_var.get().strip()
        if url.startswith("http"):
            load_from_url()

    def center_and_resize(img, size):
        alpha = img.split()[-1]
        alpha_data = np.array(alpha)
        mask = alpha_data > 0
        if not np.any(mask):
            return Image.new("RGBA", (size, size), (0, 0, 0, 0))

        coords = np.argwhere(mask)
        top, left = coords.min(axis=0)
        bottom, right = coords.max(axis=0)
        cropped = img.crop((left, top, right + 1, bottom + 1))

        scale = min(size / cropped.width, size / cropped.height)
        new_w, new_h = int(cropped.width * scale), int(cropped.height * scale)
        resized = cropped.resize((new_w, new_h), Image.LANCZOS)

        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(resized, ((size - new_w) // 2, (size - new_h) // 2), resized)
        return result

    def process_and_save():
        img = image_data.get("img")
        if not img:
            messagebox.showerror("Fehler", "Kein gültiges Bild geladen.")
            return

        name = simpledialog.askstring("Dateiname", "Bitte Namen für das Badge eingeben:")
        if not name:
            messagebox.showerror("Fehler", "Kein Name eingegeben.")
            return

        save_dir = os.path.join(graphics_path, "Badges", "Clubs")
        os.makedirs(save_dir, exist_ok=True)
        sizes = [256, 128, 64, 32]

        for s in sizes:
            folder = os.path.join(save_dir, f"{s}x{s}")
            os.makedirs(folder, exist_ok=True)
            final = center_and_resize(img, s)
            final.save(os.path.join(folder, f"{name}.tga"), format="TGA")

        messagebox.showinfo("Erfolg", "Badge gespeichert!")

    # GUI-Elemente
    control_frame = tk.Frame(dialog, bg="#d8d8d8")
    control_frame.pack(pady=10)

    url_var = tk.StringVar()
    url_var.trace_add("write", lambda *args: on_url_change())

    url_entry = tk.Entry(control_frame, textvariable=url_var, width=50)
    url_entry.insert(0, "Direktlink")
    url_entry.bind("<FocusIn>", on_url_entry_click)
    url_entry.pack(side="left", padx=5)

    ttk.Button(control_frame, text="Aus Zwischenablage", command=load_from_clipboard).pack(side="left", padx=5)
    ttk.Button(control_frame, text="Suchen", command=load_file).pack(side="left", padx=5)

    ttk.Button(dialog, text="Speichern", command=process_and_save).pack(pady=20)
    ttk.Button(dialog, text="Zurück", command=dialog.destroy).pack(pady=5)
