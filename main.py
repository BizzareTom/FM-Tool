import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import requests
from PIL import Image, ImageTk, ImageGrab
import io
import os
import pyperclip
import configparser
from io import BytesIO
from processions.cities import*
from processions.stadiums import*
from processions.badges import*

# ============================
# UPSETTEN DER KONFIGURATIONSDATEI
# ============================
INI_FILE="directories.ini"

def load_directories():
    """ Lädt die gespeicherten Verzeichnisse aus einer .INI Datei. """
    config = configparser.ConfigParser()
    
    if not os.path.exists(INI_FILE):
        save_directories("", "")  # Erstellt Datei mit leeren Werten
        return "", ""
        
    config.read(INI_FILE)
    
    fm_main_dir = config.get("Directories", "fm_main_dir", fallback="")
    fm_graphics_dir = config.get("Directories", "fm_graphics_dir", fallback="")

    return fm_main_dir, fm_graphics_dir

def save_directories(fm_main_dir, fm_graphics_dir):
    """ Speichert die Verzeichnisse in einer .INI Datei. """
    config = configparser.ConfigParser()
    config["Directories"] = {
        "fm_main_dir": fm_main_dir,
        "fm_graphics_dir": fm_graphics_dir
    }

    with open(INI_FILE, "w") as configfile:
        config.write(configfile)

# ============================
# HAUPTMENÜ
# ============================

# HAUPTMASKE
root = tk.Tk()
root.title("Modding App für Fußballmanager")
root.geometry("1080x608")
root.configure(bg="#d8d8d8")

IMG_FOLDER = "img"

# Bild oben links - Signaturbild
def load_image(image_path):
    try:
        image = Image.open(image_path)
        image_tk = ImageTk.PhotoImage(image)
        return image_tk
    except Exception as e:
        print(f"Fehler beim Laden des Bildes: {e}")
        return None
        
#"Beenden"-Button hinzufügen
def quit_program():
    # Aktuelle Pfade aus den Eingabefeldern holen
    fm_main_dir = fm_main_dir_entry.get()
    fm_graphics_dir = fm_graphics_dir_entry.get()
    
    # Pfade speichern
    save_directories(fm_main_dir, fm_graphics_dir)
    
    """ Schließt das Programm. """
    root.quit()

img_tk = load_image(os.path.join(IMG_FOLDER, "Tooledit.png"))
if img_tk:
    image_label = tk.Label(root, image=img_tk, bg="#d8d8d8")
    image_label.image = img_tk
    image_label.place(x=10, y=10)
else:
    print("Das Bild Tooledit.png konnte nicht geladen werden. Stellen Sie sicher, dass es im richtigen Verzeichnis vorhanden ist.")

# Laden der Verzeichnisse
fm_main_dir, fm_graphics_dir = load_directories()

# Label für den FM Hauptverzeichnis
fm_main_dir_label = tk.Label(root, text="FM Hauptverzeichnis:", bg="#d8d8d8", fg="white")
fm_main_dir_label.pack(pady=5)

fm_main_dir_entry = tk.Entry(root, width=50)
fm_main_dir_entry.insert(0, fm_main_dir)  # Setze das geladene Verzeichnis
fm_main_dir_entry.pack(pady=5)

fm_main_dir_button = ttk.Button(root, text="Verzeichnis auswählen", command=lambda: choose_directory(fm_main_dir_entry))
fm_main_dir_button.pack(pady=5)

# Label für das FM Graphics Verzeichnis
fm_graphics_dir_label = tk.Label(root, text="FM Graphics Verzeichnis:", bg="#d8d8d8", fg="white")
fm_graphics_dir_label.pack(pady=5)

fm_graphics_dir_entry = tk.Entry(root, width=50)
fm_graphics_dir_entry.insert(0, fm_graphics_dir)  # Setze das geladene Verzeichnis
fm_graphics_dir_entry.pack(pady=5)

fm_graphics_dir_button = ttk.Button(root, text="Verzeichnis auswählen", command=lambda: choose_directory(fm_graphics_dir_entry))
fm_graphics_dir_button.pack(pady=5)

quit_button = ttk.Button(root, text="Beenden", command=quit_program)
quit_button.place(x=18, y=img_tk.height() + 20)  # Position direkt unter dem Bild, mit etwas Abstand

# Schaltflächen erstellen
buttons = ["Badges", "Cities", "Portraits", "Stadiums", "TrainingCamps", "Trophies", "Dummy 1", "Dumme Penisnutte", "Elende Fotzschlampe", "Dummy 4", "Dummy 5"]
for button in buttons:
    btn = ttk.Button(root, text=button, command=lambda b=button: button_click(b))
    btn.pack(pady=5)
    
try:
    img_path = os.path.join(IMG_FOLDER, "cty.png")
    image = Image.open(img_path).resize((30, 30), Image.LANCZOS)  # <-- Größe anpassen hier
    img_tk = ImageTk.PhotoImage(image)

    image_label = tk.Label(root, image=img_tk, bg="#d8d8d8")
    image_label.image = img_tk  # Referenz behalten!
    image_label.place(x=450, y=223)
except Exception as e:
    print(f"Das Bild cty.png konnte nicht geladen werden: {e}")
    
try:
    img_path = os.path.join(IMG_FOLDER, "stdm.png")
    image = Image.open(img_path).resize((22, 22), Image.LANCZOS)  # <-- Größe anpassen hier
    img_tk = ImageTk.PhotoImage(image)

    image_label = tk.Label(root, image=img_tk, bg="#d8d8d8")
    image_label.image = img_tk  # Referenz behalten!
    image_label.place(x=460, y=299)
except Exception as e:
    print(f"Das Bild stdm.png konnte nicht geladen werden: {e}")
    
try:
    img_path = os.path.join(IMG_FOLDER, "bdg.ico")
    image = Image.open(img_path).resize((20, 20), Image.LANCZOS)  # <-- Größe anpassen hier
    img_tk = ImageTk.PhotoImage(image)

    image_label = tk.Label(root, image=img_tk, bg="#d8d8d8")
    image_label.image = img_tk  # Referenz behalten!
    image_label.place(x=460, y=194)
except Exception as e:
    print(f"Das Bild bdg.ico konnte nicht geladen werden: {e}")
    
# Funktion für Button-Klicks
    # Funktion des Cities-Buttons
def button_click(button_name):
    print(f"{button_name} wurde gedrückt")

    if button_name == "Cities":
        open_cities_dialog()
    elif button_name == "Stadiums":
        open_stadiums_dialog()
    elif button_name == "Badges":
        open_badges_dialog(root, fm_graphics_dir_entry.get())
    else:
        print(f"Keine Aktion für Button '{button_name}' definiert.")


# ============================
# CITIES_DIALOG
# ============================

# Zielgröße für Cities-Bilder
CITIES_TARGET_WIDTH = 615
CITIES_TARGET_HEIGHT = 461

# Funktion zum Öffnen eines Verzeichnisses
def choose_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

# Funktion für Zwischenablage
def paste_image(entry_field):
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
                process_cities_image(img, fm_graphics_dir_entry.get())
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
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except requests.RequestException as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")
        return None

# ============================
# STADIUMS DIALOG
# ============================

def open_stadiums_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Dialog_Stadiums")
    dialog.geometry("800x400")
    dialog.configure(bg="#d8d8d8")

    # Layout: Link-Textfeld und Buttons
    frame = tk.Frame(dialog, bg="#d8d8d8")
    frame.pack(pady=20)

    entry_field = tk.Entry(frame, width=40)
    entry_field.insert(0, "Direktlink")
    entry_field.bind("<FocusIn>", lambda e: entry_field.delete(0, tk.END))
    entry_field.pack(side="left", padx=5)

    execute_button = ttk.Button(frame, text="Ausführen", command=lambda: process_stadiums_image(download_image(entry_field.get().strip())))
    execute_button.pack(side="left", padx=5)

    paste_button = ttk.Button(dialog, text="Aus Zwischenablage einfügen", command=lambda: paste_stadiums_image(entry_field, fm_graphics_dir_entry))
    paste_button.pack(pady=5)

    search_button = ttk.Button(dialog, text="Suchen", command=lambda:  s(entry_field))
    search_button.pack(pady=5)

    cancel_button = ttk.Button(dialog, text="Abbrechen", command=dialog.destroy)
    cancel_button.pack(pady=5)
    


# Funktion zum Öffnen des Cities-Dialogs
def open_cities_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Dialog_Cities")
    dialog.geometry("800x400")  # Fenstergröße angepasst
    dialog.configure(bg="#d8d8d8")

    # Layout: Link-Textfeld und Button
    left_frame = tk.Frame(dialog, bg="#d8d8d8")
    left_frame.pack(side="left", padx=20)

    # Direktlink Textfeld
    entry_label = tk.Label(left_frame, text="Direktlink:", bg="#d8d8d8", fg="white")
    entry_label.pack(pady=5)

    entry_field = tk.Entry(left_frame, width=40)
    entry_field.insert(0, "Direktlink")  # Platzhaltertext
    entry_field.bind("<FocusIn>", lambda event: entry_field.delete(0, tk.END))  # Text löschen bei Fokus
    entry_field.pack(pady=5, side="left")

    execute_button = ttk.Button(left_frame, text="Ausführen", command=lambda: process_cities_image(download_image(entry_field.get().strip()), fm_graphics_dir_entry.get()))
    execute_button.pack(pady=5, side="left")

    paste_button = ttk.Button(left_frame, text="Aus Zwischenablage einfügen", command=lambda: paste_image(entry_field))
    paste_button.pack(pady=5)

    # Suchbutton zum Öffnen von Dateimanager
    search_button = ttk.Button(left_frame, text="Suchen", command=lambda: open_file_dialog(entry_field))
    search_button.pack(pady=5)

    # OK Button
    ok_button = ttk.Button(dialog, text="OK", command=lambda: process_cities_image("dummy_image", fm_graphics_dir_entry.get()))  # Dummy image für das Beispiel
    ok_button.pack(pady=10)

    # Abbrechen Button
    cancel_button = ttk.Button(dialog, text="Abbrechen", command=dialog.destroy)
    cancel_button.pack(pady=10)

# Funktion für das Öffnen des Dateimanagers
def open_file_dialog(entry_field):
    file_path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png;*.jpg;*.jpeg;*.bmp;*.tga")])
    if file_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, file_path)
        img = Image.open(file_path)
        process_cities_image(img, fm_graphics_dir_entry.get())
        
# Signatur im Hauptfenster
sign_label = tk.Label(root, text="by SlideSheapness", bg="#d8d8d8", fg="black", font=("Arial", 10, "bold"))
sign_label.place(relx=1.0, rely=1.0, anchor="se")  # Ohne padx und pady

# GUI starten
root.mainloop()
