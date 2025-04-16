import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageGrab, ImageOps
from rembg import remove
import requests
import io
import pyperclip
import os
import numpy as np

MIN_SIZE = 256
FRAME_SIZE = 128
HANDLE_SIZE = 6
CANVAS_SIZE = 512
DISPLAY_SCALE = 1.0

# Angepasster Modellpfad (z. B. auf USB-Stick)
CUSTOM_MODEL_PATH = os.path.join("./models", "u2net.onnx")
os.environ["U2NET_HOME"] = os.path.abspath(os.path.dirname(CUSTOM_MODEL_PATH))


def open_badges_dialog(root, graphics_path):
    img_tk = None
    img_original = None
    img_displayed = None
    selection = None
    image_canvas_obj = None
    image_scale = 1.0
    image_offset = (0, 0)

    drag_data = {"x": 0, "y": 0, "type": None, "handle_index": None}

    dialog = tk.Toplevel(root)
    dialog.title("Dialog_Badges")
    dialog.geometry("1000x900")
    dialog.configure(bg="#d8d8d8")

    top_frame = tk.Frame(dialog, bg="#d8d8d8")
    top_frame.pack(pady=20)

    canvas_wrapper = tk.Frame(top_frame, bg="#d8d8d8")
    canvas_wrapper.pack(side="left")

    canvas = tk.Canvas(canvas_wrapper, bg="white", width=CANVAS_SIZE, height=CANVAS_SIZE,
                       highlightthickness=1, highlightbackground="black")
    canvas.pack()

    button_wrapper = tk.Frame(top_frame, bg="#d8d8d8", width=200)
    button_wrapper.pack(side="left", padx=20, fill="y")
    button_wrapper.pack_propagate(False)
    ttk.Button(button_wrapper, text="Verarbeiten", command=lambda: removebg_image()).pack(expand=True)

    control_frame = tk.Frame(dialog, bg="#d8d8d8")
    control_frame.pack(pady=10)

    url_entry = tk.Entry(control_frame, width=60)
    url_entry.insert(0, "Bildlink einfügen...")
    url_entry.pack(side="left", padx=5)

    ttk.Button(control_frame, text="Ausführen", command=lambda: load_from_url()).pack(side="left", padx=5)
    ttk.Button(control_frame, text="Aus Zwischenablage", command=lambda: load_from_clipboard()).pack(side="left", padx=5)

    ttk.Button(dialog, text="Bild laden (Datei)", command=lambda: load_file()).pack(pady=5)
    ttk.Button(dialog, text="Rahmen zurücksetzen", command=lambda: reset_frame()).pack(pady=5)
    ttk.Button(dialog, text="Abbrechen", command=dialog.destroy).pack(pady=10)

    def is_image_valid(img):
        return max(img.width, img.height) >= MIN_SIZE

    def pad_to_square(img):
        max_side = max(img.size)
        padded_img = Image.new("RGBA", (max_side, max_side), (255, 255, 255, 255))
        offset = ((max_side - img.width) // 2, (max_side - img.height) // 2)
        padded_img.paste(img, offset)
        return padded_img

    def load_image_from_object(img):
        nonlocal img_tk, img_original, selection, image_canvas_obj, img_displayed, image_scale, image_offset

        # Padding und Konvertierung zuerst
        img = pad_to_square(img.convert("RGBA"))

        # img_original ist jetzt das gepaddete Bild, wie es auf dem Canvas erscheint
        img_original = img.copy()

        scale = CANVAS_SIZE / max(img.width, img.height)
        image_scale = scale

        img_displayed = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        image_offset = ((CANVAS_SIZE - img_displayed.width) // 2, (CANVAS_SIZE - img_displayed.height) // 2)

        img_tk = ImageTk.PhotoImage(img_displayed)
        canvas.delete("all")
        image_canvas_obj = canvas.create_image(image_offset[0], image_offset[1], anchor="nw", image=img_tk)
        reset_frame()


    def reset_frame():
        nonlocal selection
        canvas.delete("Dolli")
        canvas.delete("handle")

        half = FRAME_SIZE // 2
        cx = CANVAS_SIZE // 2
        cy = CANVAS_SIZE // 2

        frame_x0 = cx - half
        frame_y0 = cy - half
        frame_x1 = cx + half
        frame_y1 = cy + half

        selection = canvas.create_rectangle(frame_x0, frame_y0, frame_x1, frame_y1,
                                            outline="red", width=2, tags="Dolli")
        draw_handles(frame_x0, frame_y0, frame_x1, frame_y1)

    def draw_handles(x0, y0, x1, y1):
        positions = [
            (x0, y0), (x1, y0),
            (x0, y1), (x1, y1),
            ((x0 + x1) // 2, (y0 + y1) // 2)
        ]
        for i, (px, py) in enumerate(positions):
            canvas.create_rectangle(
                px - HANDLE_SIZE, py - HANDLE_SIZE,
                px + HANDLE_SIZE, py + HANDLE_SIZE,
                fill="red" if i < 4 else "orange",
                tags=("handle", f"handle_{i}")
            )

    def clamp(val, min_val, max_val):
        return max(min_val, min(val, max_val))

    def on_press(event):
        clicked = canvas.find_overlapping(event.x, event.y, event.x, event.y)
        drag_data["type"] = None
        drag_data["handle_index"] = None
        for item in clicked:
            tags = canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag.startswith("handle_"):
                        idx = int(tag.split("_")[1])
                        drag_data["type"] = "move" if idx == 4 else "resize"
                        drag_data["handle_index"] = idx
                        break
            elif "Dolli" in tags and drag_data["type"] is None:
                drag_data["type"] = "move"
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def on_drag(event):
        if drag_data["type"] not in ("move", "resize"):
            return

        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]
        drag_data["x"] = event.x
        drag_data["y"] = event.y

        x0, y0, x1, y1 = map(int, canvas.coords(selection))

        if drag_data["type"] == "move":
            new_x0 = clamp(x0 + dx, 0, CANVAS_SIZE - (x1 - x0))
            new_y0 = clamp(y0 + dy, 0, CANVAS_SIZE - (y1 - y0))
            dx = new_x0 - x0
            dy = new_y0 - y0
            canvas.move("Dolli", dx, dy)
            canvas.move("handle", dx, dy)

        elif drag_data["type"] == "resize":
            idx = drag_data["handle_index"]
            if idx == 0:
                x0 = clamp(x0 + dx, 0, x1 - 1)
                y0 = clamp(y0 + dy, 0, y1 - 1)
            elif idx == 1:
                x1 = clamp(x1 + dx, x0 + 1, CANVAS_SIZE)
                y0 = clamp(y0 + dy, 0, y1 - 1)
            elif idx == 2:
                x0 = clamp(x0 + dx, 0, x1 - 1)
                y1 = clamp(y1 + dy, y0 + 1, CANVAS_SIZE)
            elif idx == 3:
                x1 = clamp(x1 + dx, x0 + 1, CANVAS_SIZE)
                y1 = clamp(y1 + dy, y0 + 1, CANVAS_SIZE)

            size = min(x1 - x0, y1 - y0)
            if idx in (0, 2):
                x0 = x1 - size
            else:
                x1 = x0 + size
            if idx in (0, 1):
                y0 = y1 - size
            else:
                y1 = y0 + size

            x0 = clamp(x0, 0, CANVAS_SIZE)
            y0 = clamp(y0, 0, CANVAS_SIZE)
            x1 = clamp(x1, 0, CANVAS_SIZE)
            y1 = clamp(y1, 0, CANVAS_SIZE)

            canvas.coords(selection, x0, y0, x1, y1)
            canvas.delete("handle")
            draw_handles(x0, y0, x1, y1)

    def on_release(event):
        drag_data["type"] = None
        drag_data["handle_index"] = None

    def load_file():
        path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png;*.jpg;*.jpeg;*.bmp;*.tga")])
        if path:
            img = Image.open(path)
            load_image_from_object(img)

    def load_from_url():
        url = url_entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Fehler", "Bitte eine gültige Bild-URL angeben.")
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            load_image_from_object(img)
        except Exception as e:
            messagebox.showerror("Fehler beim Laden des Bildes", str(e))

    def load_from_clipboard():
        try:
            clipboard = pyperclip.paste()
            if clipboard.startswith("http"):
                url_entry.delete(0, tk.END)
                url_entry.insert(0, clipboard)
                load_from_url()
                return
            img = ImageGrab.grabclipboard()
            if img:
                load_image_from_object(img)
            else:
                messagebox.showerror("Fehler", "Keine gültige Zwischenablage erkannt.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def center_and_resize(img, size):
        # Schritt 1: Alphakanal extrahieren
        alpha = img.split()[-1]
        alpha_data = np.array(alpha)

        # Schritt 2: Maske mit nicht-transparenten Pixeln
        mask = alpha_data > 0
        if not np.any(mask):
            return Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Schritt 3: Bounding Box des Objekts
        coords = np.argwhere(mask)
        top, left = coords.min(axis=0)
        bottom, right = coords.max(axis=0)

        # Schritt 4: Objekt ausschneiden
        cropped = img.crop((left, top, right + 1, bottom + 1))

        # Schritt 5: Skalierung
        cropped_w, cropped_h = cropped.size
        scale = min(size / cropped_w, size / cropped_h)
        new_w, new_h = int(cropped_w * scale), int(cropped_h * scale)
        resized = cropped.resize((new_w, new_h), Image.LANCZOS)

        # Schritt 6: Zentrierung
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        paste_x = (size - new_w) // 2
        paste_y = (size - new_h) // 2
        result.paste(resized, (paste_x, paste_y), resized)

        return result

    def removebg_image():
        nonlocal img_original, img_displayed, image_scale, image_offset
    
        if not img_original:
            messagebox.showerror("Fehler", "Kein Bild geladen.")
            return

        # Aktuelle Koordinaten des Auswahlrahmens auf der Canvas
        x0, y0, x1, y1 = map(int, canvas.coords(selection))

        # Koordinaten vom Canvas ins Originalbild zurückrechnen
        left = int((x0 - image_offset[0]) / image_scale)
        top = int((y0 - image_offset[1]) / image_scale)
        right = int((x1 - image_offset[0]) / image_scale)
        bottom = int((y1 - image_offset[1]) / image_scale)

        # Clamping: Stelle sicher, dass Werte im Bildbereich bleiben
        left = max(0, min(left, img_original.width))
        top = max(0, min(top, img_original.height))
        right = max(0, min(right, img_original.width))
        bottom = max(0, min(bottom, img_original.height))

        if right - left < 1 or bottom - top < 1:
            messagebox.showerror("Fehler", "Ungültiger Bildausschnitt.")
            return

        # Zuschneiden und Hintergrund entfernen
        cropped = img_original.crop((left, top, right, bottom)).convert("RGBA")
        removed = remove(cropped)

        sizes = [256, 128, 64, 32]
        save_images = [center_and_resize(removed, s) for s in sizes]

        name = simpledialog.askstring("Dateiname", "Bitte einen Namen für die Bilder eingeben:")
        if not name:
            messagebox.showerror("Fehler", "Kein Name eingegeben. Speichern abgebrochen.")
            return

        save_dir = os.path.join(graphics_path, "Badges", "Clubs")
        os.makedirs(save_dir, exist_ok=True)

        for size, img in zip(sizes, save_images):
            folder = os.path.join(save_dir, f"{size}x{size}")
            os.makedirs(folder, exist_ok=True)
            img.save(os.path.join(folder, f"{name}.tga"), format="TGA")

        messagebox.showinfo("Erfolg", "Bilder wurden gespeichert!")


    def on_ctrl_v(event):
        load_from_clipboard()
        return "break"

    dialog.bind_all("<Control-v>", on_ctrl_v)
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
