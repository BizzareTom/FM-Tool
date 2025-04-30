import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import configparser
from platformdirs import user_config_dir
from importlib.resources import files
from PIL import Image, ImageTk, ImageGrab
import sys
import pyperclip
import io
import requests

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fm_tool.processions.cities import *
from fm_tool.processions.stadiums import *
from fm_tool.processions.badges import *
from fm_tool.processions.custom import *

def main():
    # ============================
    # KONFIGURATION
    # ============================
    CONFIG_DIR = user_config_dir("FM-Tool", ensure_exists=True)
    INI_FILE = os.path.join(CONFIG_DIR, "directories.ini")

    def load_directories():
        config = configparser.ConfigParser()
        if not os.path.exists(INI_FILE):
            save_directories("", "")
            return "", ""
        config.read(INI_FILE)
        return (
            config.get("Directories", "fm_main_dir", fallback=""),
            config.get("Directories", "fm_graphics_dir", fallback="")
        )

    def save_directories(fm_main_dir, fm_graphics_dir):
        config = configparser.ConfigParser()
        config["Directories"] = {
            "fm_main_dir": fm_main_dir,
            "fm_graphics_dir": fm_graphics_dir
        }
        with open(INI_FILE, "w") as configfile:
            config.write(configfile)

    def choose_directory(entry):
        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)

    # ============================
    # GUI SETUP
    # ============================
    root = tk.Tk()
    root.title("Modding App für Fußballmanager")
    root.geometry("1080x608")
    root.configure(bg="#d8d8d8")

    #=============================
    # PROGRAMM ICON
    #=============================
    icon_path = os.path.join(os.path.dirname(__file__),"img", "Tooledit.ico")
    root.iconbitmap(icon_path)
    
    # ============================
    # OBEN: LOGO UND PFADANGABEN
    # ============================
    base_dir = os.path.dirname(__file__)
    img_path = os.path.join(base_dir, "img", "Tooledit.png")
    try:
        logo_img = Image.open(img_path)
        logo_tk = ImageTk.PhotoImage(logo_img)
        image_label = tk.Label(root, image=logo_tk, bg="#d8d8d8")
        image_label.image = logo_tk
        image_label.place(x=10, y=10)
        y_offset = logo_tk.height() + 20
    except Exception:
        y_offset = 100

    fm_main_dir, fm_graphics_dir = load_directories()

    fm_main_dir_label = tk.Label(root, text="FM Hauptverzeichnis:", bg="#d8d8d8")
    fm_main_dir_label.pack(pady=5)
    fm_main_dir_entry = tk.Entry(root, width=50)
    fm_main_dir_entry.insert(0, fm_main_dir)
    fm_main_dir_entry.pack(pady=5)
    ttk.Button(root, text="Verzeichnis auswählen", command=lambda: choose_directory(fm_main_dir_entry)).pack(pady=5)

    fm_graphics_dir_label = tk.Label(root, text="FM Graphics Verzeichnis:", bg="#d8d8d8")
    fm_graphics_dir_label.pack(pady=5)
    fm_graphics_dir_entry = tk.Entry(root, width=50)
    fm_graphics_dir_entry.insert(0, fm_graphics_dir)
    fm_graphics_dir_entry.pack(pady=5)
    ttk.Button(root, text="Verzeichnis auswählen", command=lambda: choose_directory(fm_graphics_dir_entry)).pack(pady=5)

    # ============================
    # BUTTON-FUNKTIONEN
    # ============================
    def quit_program():
        save_directories(fm_main_dir_entry.get(), fm_graphics_dir_entry.get())
        root.quit()

    def button_click(button_name):
        if button_name == "Cities":
            open_cities_dialog(root, fm_graphics_dir_entry.get())
        elif button_name == "Stadiums":
            open_stadiums_dialog(root, fm_graphics_dir_entry.get())
        elif button_name == "Badges Club Roh":
            open_badges_dialog(root, fm_graphics_dir_entry.get())
        elif button_name == "Custom":
            open_custom_dialog(root, fm_graphics_dir_entry.get())
        else:
            print(f"{button_name} wurde gedrückt")

    # ============================
    # BUTTON-LAYOUT-BEREICH
    # ============================
    content = tk.Frame(root, bg="#d8d8d8")
    content.pack(fill="both", expand=True, padx=10, pady=(y_offset, 10))

    def section_with_label(parent, title):
        frame = tk.Frame(parent, bg="#d8d8d8")
        label = tk.Label(frame, text=title, bg="#d8d8d8", font=("Arial", 12, "bold"))
        label.pack(anchor="w")
        return frame

    def add_button(parent, text, command):
        btn = ttk.Button(parent, text=text, command=lambda: button_click(text))
        btn.pack(anchor="w", pady=2, fill="x")

    def add_separator(parent):
        separator = ttk.Separator(parent, orient="vertical")
        separator.pack(side="left", fill="y", padx=10)

    main_frame = tk.Frame(content, bg="#d8d8d8")
    main_frame.pack(fill="both", expand=True)

    # === Section 1: Badges ===
    frame_badges = section_with_label(main_frame, "Badges")
    frame_badges.pack(side="left", fill="y", expand=True)
    add_button(frame_badges, "Club roh (Alpha)", button_click)
    add_button(frame_badges, "Club präpariert", button_click)
    add_button(frame_badges, "League roh (Alpha)", button_click)
    add_button(frame_badges, "League präpariert", button_click)
    add_separator(main_frame)

    # === Section 2: Clubbuilding ===
    frame_clubbuilding = section_with_label(main_frame, "Clubbuilding")
    frame_clubbuilding.pack(side="left", fill="y", expand=True)
    add_button(frame_clubbuilding, "Cities", button_click)
    add_button(frame_clubbuilding, "Stadiums", button_click)
    add_button(frame_clubbuilding, "Custom", button_click)
    add_separator(main_frame)

    # === Section 3: Functionality ===
    frame_functionality = section_with_label(main_frame, "Functionality")
    frame_functionality.pack(side="left", fill="y", expand=True)
    for name in ["TrainingCamps", "Sponsors", "Skins", "AI Faces", "Personal Items", "Desktop", "Aktien (Stocks)"]:
        add_button(frame_functionality, name, button_click)
    add_separator(main_frame)

    # === Section 4: Further ===
    frame_further = section_with_label(main_frame, "Further")
    frame_further.pack(side="left", fill="y", expand=True)
    for row in [["Trophies (roh)", "Trophies präpariert", "AI Trophies"],
                ["Portraits"],
                ["Flags"],
                ["Country Flags", "Country Maps"],
                ["Vereinsheim", "Maskottchen"]]:
        row_frame = tk.Frame(frame_further, bg="#d8d8d8")
        row_frame.pack(anchor="w", pady=2, fill="x")
        for label in row:
            ttk.Button(row_frame, text=label, command=lambda l=label: button_click(l)).pack(side="left", padx=2)

    # ============================
    # FOOTER ELEMENTE
    # ============================
    quit_button = ttk.Button(root, text="Beenden", command=quit_program)
    quit_button.place(x=18, y=y_offset)

    sign_label = tk.Label(root, text="by SlideSheapness", bg="#d8d8d8", fg="black", font=("Arial", 10, "bold"))
    sign_label.place(relx=1.0, rely=1.0, anchor="se")

    root.mainloop()


if __name__ == "__main__":
    main()
